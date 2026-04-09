"""
db.py — MongoDB Atlas integration for Pulse: Evolution
Handles all cloud saves, session locking, and leaderboard.
"""
import hashlib
import datetime
import threading

# pymongo is optional — if not installed, all functions degrade gracefully
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

MONGO_URI = "mongodb+srv://kbrto_db_user:OzHLUPU@cluster0.e8tq0vk.mongodb.net/?appName=Cluster0"
DB_NAME   = "pulse_evolution"

_client = None
_db     = None
_connected = False

def _get_tls_ca():
    """Return the path to a CA bundle that works both as a script and inside a PyInstaller exe."""
    import sys, os
    # When frozen by PyInstaller the bundle extracts to sys._MEIPASS
    if getattr(sys, 'frozen', False):
        # certifi is bundled; find its cacert.pem inside the extracted bundle
        try:
            import certifi
            return certifi.where()
        except Exception:
            pass
        # Fallback: look next to the exe
        exe_dir = os.path.dirname(sys.executable)
        for candidate in ["cacert.pem", os.path.join("certifi", "cacert.pem")]:
            p = os.path.join(exe_dir, candidate)
            if os.path.exists(p):
                return p
    else:
        try:
            import certifi
            return certifi.where()
        except Exception:
            return None
    return None

# ── CONNECTION ────────────────────────────────────────────────────────────────

def connect():
    """Connect to MongoDB Atlas. Safe to call multiple times."""
    global _client, _db, _connected
    if not MONGO_AVAILABLE:
        print("[DB] pymongo not installed — running offline.")
        return False
    if _connected:
        return True

    # Try twice: once fast (4 s), once with a slightly longer timeout in case
    # the first attempt hits a cold Atlas cluster.
    for attempt, timeout_ms in enumerate([4000, 7000], start=1):
        try:
            kwargs = {"serverSelectionTimeoutMS": timeout_ms}
            ca = _get_tls_ca()
            if ca:
                kwargs["tlsCAFile"] = ca
            _client = MongoClient(MONGO_URI, **kwargs)
            _client.admin.command("ping")
            _db = _client[DB_NAME]
            _connected = True
            print("[DB] Connected to MongoDB Atlas")
            return True
        except Exception as e:
            err_str = str(e)
            if attempt == 1:
                print(f"[DB] Attempt 1 failed, retrying… ({err_str[:80]})")
            else:
                # Give the developer an actionable hint for the most common cause
                # (IP not whitelisted in Atlas Network Access).
                if "connection" in err_str.lower() or "timeout" in err_str.lower():
                    print(
                        "[DB] Could not reach MongoDB Atlas.\n"
                        "     Most likely cause: this machine's IP is not whitelisted.\n"
                        "     Fix → Atlas dashboard ▸ Network Access ▸ Add IP ▸ 0.0.0.0/0\n"
                        f"     Raw error: {err_str[:120]}"
                    )
                else:
                    print(f"[DB] Could not connect: {err_str}")
                _connected = False
    return False

def is_connected():
    return _connected

# ── PASSWORD HASHING ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()

# ── ACCOUNT ───────────────────────────────────────────────────────────────────

def account_exists(username: str) -> bool:
    if not _connected:
        return False
    try:
        return _db.players.find_one({"username": username}, {"_id": 1}) is not None
    except Exception:
        return False

def check_password(username: str, plain_password: str) -> bool:
    if not _connected:
        return False
    try:
        doc = _db.players.find_one({"username": username}, {"password": 1})
        if doc:
            return doc["password"] == hash_password(plain_password)
        return False
    except Exception:
        return False

def create_account(username: str, plain_password: str) -> bool:
    """Create a brand-new account. Returns False if username taken."""
    if not _connected:
        return False
    try:
        if account_exists(username):
            return False
        _db.players.insert_one({
            "username": username,
            "password": hash_password(plain_password),
            "session_id": None,
            "characters": []
        })
        return True
    except Exception as e:
        print(f"[DB] create_account error: {e}")
        return False

def delete_account(username: str) -> bool:
    """Permanently delete an account and all its characters. Returns True on success."""
    if not _connected:
        return False
    try:
        result = _db.players.delete_one({"username": username})
        return result.deleted_count > 0
    except Exception as e:
        print(f"[DB] delete_account error: {e}")
        return False

# ── SESSION LOCK ──────────────────────────────────────────────────────────────

import uuid as _uuid

_my_session_id = str(_uuid.uuid4())   # unique ID for this game instance

def acquire_session(username: str) -> bool:
    """
    Try to claim a session for this username.
    Returns True if successful, False if another session is active.
    """
    if not _connected:
        return True   # offline — allow play
    try:
        doc = _db.players.find_one({"username": username}, {"session_id": 1, "session_ts": 1})
        if doc is None:
            return False

        existing = doc.get("session_id")
        ts = doc.get("session_ts")

        # If a session exists and is recent (< 15 s stale), deny
        if existing and existing != _my_session_id:
            if ts:
                age = (datetime.datetime.utcnow() - ts).total_seconds()
                if age < 15:
                    return False    # another live session

        # Claim it
        _db.players.update_one(
            {"username": username},
            {"$set": {"session_id": _my_session_id,
                       "session_ts": datetime.datetime.utcnow()}}
        )
        return True
    except Exception as e:
        print(f"[DB] acquire_session error: {e}")
        return True   # network error — allow play

def release_session(username: str):
    """Release the session lock on logout/quit."""
    if not _connected:
        return
    try:
        _db.players.update_one(
            {"username": username, "session_id": _my_session_id},
            {"$set": {"session_id": None, "session_ts": None}}
        )
    except Exception:
        pass

def heartbeat_session(username: str):
    """Call every ~5 s while playing to keep session alive."""
    if not _connected:
        return
    try:
        _db.players.update_one(
            {"username": username, "session_id": _my_session_id},
            {"$set": {"session_ts": datetime.datetime.utcnow()}}
        )
    except Exception:
        pass

def is_session_active(username: str) -> bool:
    """Returns True if someone else holds this account's session."""
    if not _connected:
        return False
    try:
        doc = _db.players.find_one({"username": username}, {"session_id": 1, "session_ts": 1})
        if not doc:
            return False
        sid = doc.get("session_id")
        ts  = doc.get("session_ts")
        if sid and sid != _my_session_id and ts:
            age = (datetime.datetime.utcnow() - ts).total_seconds()
            return age < 15
        return False
    except Exception:
        return False

# ── SAVE / LOAD ───────────────────────────────────────────────────────────────

def _build_char_doc(char_type: str, player, skill_tree) -> dict:
    """Build the character sub-document to embed in the player document."""
    skills_dict = {s["id"]: s["level"] for s in skill_tree.skills}
    return {
        "type":            char_type,
        "money":           player.money,
        "skill_points":    player.skill_points,
        "max_health":      player.max_health,
        "speed":           player.speed,
        "damage":          player.damage,
        "attack_radius":   player.attack_radius,
        "projectile_count":player.projectile_count,
        "base_cooldown":   player.base_cooldown,
        "max_energy":      player.max_energy,
        "magnet_range":    player.magnet_range,
        "dash_unlocked":   player.dash_unlocked,
        "armor":           player.armor,
        "lifesteal":       player.lifesteal,
        "crit_chance":     player.crit_chance,
        "thorns":          player.thorns,
        "regen":           player.regen,
        "gold_modifier":   getattr(player, "gold_modifier", 1.0),
        "highscore":       getattr(player, "highscore", 1),
        "skills":          skills_dict,
        "saved_at":        datetime.datetime.utcnow(),
    }

def save_character(username: str, char_type: str, player, skill_tree):
    """
    Upsert one character entry inside the player document.
    Runs in a background thread so it never blocks the game loop.
    """
    if not _connected:
        return

    def _do_save():
        try:
            char_doc = _build_char_doc(char_type, player, skill_tree)
            # Remove the existing entry for this char_type, then push the new one
            _db.players.update_one(
                {"username": username},
                {"$pull": {"characters": {"type": char_type}}}
            )
            _db.players.update_one(
                {"username": username},
                {"$push": {"characters": char_doc}}
            )
        except Exception as e:
            print(f"[DB] save_character error: {e}")

    threading.Thread(target=_do_save, daemon=True).start()

def load_character(username: str, char_type: str, player, skill_tree) -> bool:
    """
    Load a character from MongoDB into the player and skill_tree objects.
    Returns True if data was found, False otherwise.
    """
    if not _connected:
        return False
    try:
        doc = _db.players.find_one(
            {"username": username},
            {"characters": 1}
        )
        if not doc:
            return False

        for c in doc.get("characters", []):
            if c.get("type") == char_type:
                player.money           = c.get("money", 0)
                player.skill_points    = c.get("skill_points", 0)
                player.max_health      = c.get("max_health", 100.0)
                player.speed           = c.get("speed", 1.3)
                player.damage          = c.get("damage", 1.0)
                player.attack_radius   = c.get("attack_radius", 100.0)
                player.projectile_count= c.get("projectile_count", 1)
                player.base_cooldown   = c.get("base_cooldown", 25)
                player.max_energy      = c.get("max_energy", 10.0)
                player.magnet_range    = c.get("magnet_range", 60)
                player.dash_unlocked   = c.get("dash_unlocked", False)
                player.armor           = c.get("armor", 0)
                player.lifesteal       = c.get("lifesteal", 0)
                player.crit_chance     = c.get("crit_chance", 0)
                player.thorns          = c.get("thorns", 0)
                player.regen           = c.get("regen", 0.0)
                player.gold_modifier   = c.get("gold_modifier", 1.0)
                player.highscore       = c.get("highscore", 1)
                player.energy          = player.max_energy
                player.health          = player.max_health

                skills_dict = c.get("skills", {})
                for s in skill_tree.skills:
                    s["level"] = skills_dict.get(s["id"], 0)
                    if s["currency"] == "gold" and s["level"] > 0:
                        s["cost"] = int(s["base_cost"] * (1.5 ** s["level"]))
                    else:
                        s["cost"] = s["base_cost"]

                return True
        return False
    except Exception as e:
        print(f"[DB] load_character error: {e}")
        return False

# ── LEADERBOARD ───────────────────────────────────────────────────────────────

def get_leaderboard(limit: int = 6) -> list:
    """
    Returns list of (username, char_type, highscore) tuples sorted desc.
    Falls back to empty list on any error.
    """
    if not _connected:
        return []
    try:
        pipeline = [
            {"$unwind": "$characters"},
            {"$project": {
                "username": 1,
                "char_type": "$characters.type",
                "highscore": "$characters.highscore"
            }},
            {"$sort": {"highscore": -1}},
            {"$limit": limit}
        ]
        results = list(_db.players.aggregate(pipeline))
        return [(r["username"], r["char_type"], r.get("highscore", 0)) for r in results]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []