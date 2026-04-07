import pygame
import sys
import random
import csv
import os
import math
from player import Player
from enemy import Enemy
from action import Coin, SpecialCoin, HpCoin, Chest
from projectile import Projectile
from skill_tree import SkillTree
from boss import Boss

# Iegūst skripta direktoriju, lai izkrautos failus no pareizuma ceļa neatkarīgi no darba direktorijas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)  # Mainīt darba direktoriju uz skripta vietu

# funkcija get_path pieņem str tipa vērtību relative_path un atgriež str tipa vērtību full_path
def get_path(relative_path):
    # Atgriež pilnu ceļu, ņemot vērā skripta direktoriju
    return os.path.join(SCRIPT_DIR, relative_path)

# 1. INICIALIZĀCIJA
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_w, screen_h = screen.get_size()
pygame.display.set_caption("Pulse: Evolution")
clock = pygame.time.Clock()

# 2. SAGLABĀŠANAS/IELĀDES SISTĒMA
PLAYER_FILE = "data/players.csv"
if not os.path.exists("data"): 
    os.makedirs("data")

save_notification_timer = 0
save_notification_msg = ""
boss_drop_timer = 0
boss_drop_msg = ""
# --- CINEMATIC TRANSITION EFFECTS ---
transition_active = False
transition_timer = 0
transition_duration = 15  # frames for fade effects (0.25 seconds at 60 FPS)
transition_type = "fade"  # "fade", "wipe", "dissolve"
current_wave = 1
game_state, user_name = "menu", ""
user_password = ""
password_error_msg = ""
password_error_timer = 0
is_new_account = False
pause_save_btn = pygame.Rect(0, 0, 0, 0)
pause_resume_btn = pygame.Rect(0, 0, 0, 0)
pause_quit_btn = pygame.Rect(0, 0, 0, 0)

# funkcija player_exists_in_csv pieņem str tipa vērtību name un atgriež bool tipa vērtību exists
def player_exists_in_csv(name):
    # Pārbauda, vai spēlētājs ar doto vārdu jau eksistē CSV failā
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("name") == name:
                        return True
        except:
            pass
    return False

# funkcija check_password pieņem str tipa vērtību name un str tipa vērtību password un atgriež bool tipa vērtību is_correct
def check_password(name, password):
    # Pārbauda, vai parole sakrīt ar saglabāto paroli CSV failā
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("name") == name:
                        stored_password = row.get("password", "")
                        return stored_password == password
        except:
            pass
    return False

# funkcija apply_boss_drop pieņem Player tipa vērtību player un int tipa vērtību wave un atgriež None tipa vērtību None
def apply_boss_drop(player, wave):
    # Dod spēlētājam izlases spēka uzpūšanu, kad tas nogalina bosu
    # [SAREŽĢĪTA LOĢIKA]: Izlases buff izvēle no vairākām iespējām
    drop_type = random.choice(["damage", "speed", "health", "armor", "lifesteal"])
    
    if drop_type == "damage":
        bonus = int(2 + (wave * 0.5))
        player.damage += bonus
        trigger_boss_drop_anim(f"DAMAGE BOOST! +{bonus}")
    elif drop_type == "speed":
        bonus = round(1.5 + (wave * 0.2), 1)
        player.speed += bonus
        trigger_boss_drop_anim(f"SPEED BOOST! +{bonus}")
    elif drop_type == "health":
        health_boost = int(50 + (wave * 10))
        player.max_health += health_boost
        player.health += health_boost
        trigger_boss_drop_anim(f"HEALTH BOOST! +{health_boost}")
    elif drop_type == "armor":
        armor_boost = 2 + (wave // 2)
        player.armor = getattr(player, 'armor', 0) + armor_boost
        trigger_boss_drop_anim(f"ARMOR BOOST! +{armor_boost}")
    elif drop_type == "lifesteal":
        bonus = round(wave * 0.5, 1)
        player.lifesteal = getattr(player, 'lifesteal', 0) + bonus
        trigger_boss_drop_anim(f"LIFESTEAL BOOST! +{bonus}")


# PASTĀVĪGAIS TUMSAS (SHROUD) SLĀNIS
shroud = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

# --- ATTĒLU IELĀDĒTĀJI ---

# funkcija load_bg pieņem str tipa vērtību path un atgriež pygame.Surface tipa vērtību image
def load_bg(path):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (screen_w, screen_h))
    except:
        return None

# funkcija load_sprite pieņem str tipa vērtību path un tuple tipa vērtību size un atgriež pygame.Surface tipa vērtību img
def load_sprite(path, size=(280, 280)):
    try:
        img = pygame.image.load(path).convert_alpha()
        orig_w, orig_h = img.get_size()
        scale = min(size[0] / orig_w, size[1] / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        return pygame.transform.scale(img, (new_w, new_h))
    except:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((255, 0, 255))
        return surf

# funkcija load_logo pieņem str tipa vērtību path, int tipa vērtību max_w un int tipa vērtību max_h un atgriež pygame.Surface tipa vērtību img
def load_logo(path, max_w, max_h):
    try:
        img = pygame.image.load(path).convert_alpha()
        orig_w, orig_h = img.get_size()
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        return pygame.transform.scale(img, (new_w, new_h))
    except:
        return None

# --- IELĀDĒT VISUS AKTĪVUS ---
menu_bg        = load_bg(get_path("photos/menu_bg.png"))
char_select_bg = load_bg(get_path("photos/char_select_bg.png"))
game_bg        = load_bg(get_path("photos/bg.png"))
if game_bg:
    game_bg.set_alpha(180)

menu_logo = load_logo(get_path("photos/logo.png"), screen_w * 0.6, screen_h * 0.3)

# Varoņu spreiti
wizard_ui = load_sprite(get_path("photos/wizard_right.png"))
shadow_ui = load_sprite(get_path("photos/Shadow_up.png"))
dwarf_ui  = load_sprite(get_path("photos/dwarf_forward.png"))

freeze_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
freeze_surf.fill((0, 150, 255, 40))

class MeleeSwing:
    # funkcija __init__ pieņem MeleeSwing tipa vērtību self, Player tipa vērtību owner, list tipa vērtību enemies un int tipa vērtību damage un atgriež None tipa vērtību None
    def __init__(self, owner, enemies, damage):
        self.owner = owner
        self.angle = 0
        self.spin_speed = getattr(owner, 'rotation_speed', 20)
        self.radius = owner.attack_radius
        self.lifetime = 360 // self.spin_speed

        # [SAREŽĢĪTA LOĢIKA]: Tuvcīņas sadursmes un atsitiena aprēķins
        # Cikls iet cauri visiem ienaidniekiem, lai aprēķinātu to attālumu no spēlētāja centra
        # Izmanto Pitagora teorēmu (math.hypot), lai noteiktu eiklīda distanci.
        for e in enemies:
            dist = math.hypot(owner.rect.centerx - e.rect.centerx, owner.rect.centery - e.rect.centery)
            
            # Ja ienaidnieks atrodas ieroča rādiusā (+ 25 pikseļu kļūdas robeža)
            if dist <= self.radius + 25:
                enemy_armor = getattr(e, 'armor', 0)
                base_dmg = max(1, damage - enemy_armor) # Neļauj bojājumam būt mazākam par 1
                final_dmg = base_dmg
                
                # Kritiskā sitiena aprēķins
                if random.randint(1, 100) <= getattr(owner, 'crit_chance', 0):
                    final_dmg *= 2
                
                e.health -= final_dmg
                
                # Dzīvības zādzības (lifesteal) atjaunošana
                if getattr(owner, 'lifesteal', 0) > 0:
                    owner.health = min(owner.max_health, owner.health + owner.lifesteal)
                
                # Atsitiena (knockback) vektora aprēķins
                # Mēs noskaidrojam x un y virzienu no spēlētāja uz ienaidnieku,
                # un tad normalizējam to (dalot ar dist_kb), lai ienaidnieku atgrūstu tieši par 10 pikseļiem abās asīs.
                if hasattr(e, 'rect'):
                    dx = e.rect.centerx - owner.rect.centerx
                    dy = e.rect.centery - owner.rect.centery
                    dist_kb = math.hypot(dx, dy)
                    if dist_kb != 0:
                        e.rect.x += (dx / dist_kb) * 10
                        e.rect.y += (dy / dist_kb) * 10

        self.surface = pygame.Surface((70, 35), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, (100, 50, 0), (0, 12, 50, 10))
        pygame.draw.rect(self.surface, (200, 200, 200), (45, 0, 25, 35))

    # funkcija update pieņem MeleeSwing tipa vērtību self un atgriež None tipa vērtību None
    def update(self):
        self.angle += self.spin_speed
        self.lifetime -= 1

    # funkcija draw pieņem MeleeSwing tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        rotated_axe = pygame.transform.rotate(self.surface, -self.angle)
        rad = math.radians(self.angle)
        pos_x = self.owner.rect.centerx + math.cos(rad) * self.radius
        pos_y = self.owner.rect.centery + math.sin(rad) * self.radius
        rect = rotated_axe.get_rect(center=(pos_x, pos_y))
        surface.blit(rotated_axe, rect)

# funkcija trigger_save_anim pieņem str tipa vērtību msg un atgriež None tipa vērtību None
def trigger_save_anim(msg):
    global save_notification_timer, save_notification_msg
    save_notification_timer = 90
    save_notification_msg = msg

# funkcija trigger_boss_drop_anim pieņem str tipa vērtību msg un atgriež None tipa vērtību None
def trigger_boss_drop_anim(msg):
    global boss_drop_timer, boss_drop_msg
    boss_drop_timer = 180
    boss_drop_msg = msg

# funkcija start_transition pieņem str tipa vērtību trans_type un atgriež None tipa vērtību None
def start_transition(trans_type="fade"):
    global transition_active, transition_timer, transition_type
    transition_active = True
    transition_timer = transition_duration
    transition_type = trans_type

# funkcija render_transition pieņem pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
def render_transition(surface):
    global transition_active, transition_timer
    if not transition_active:
        return
    
    if transition_type == "fade":
        # Fade to black and back
        progress = 1.0 - (transition_timer / transition_duration)
        if progress > 0.5:
            alpha = int(255 * (2 * (progress - 0.5)))  # Second half: fade out
        else:
            alpha = int(255 * (1 - 2 * progress))  # First half: fade in
        
        fade_surf = pygame.Surface((screen_w, screen_h))
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(alpha)
        surface.blit(fade_surf, (0, 0))
    
    elif transition_type == "wipe":
        # Screen wipe from right
        progress = 1.0 - (transition_timer / transition_duration)
        wipe_x = int(screen_w * progress)
        wipe_surf = pygame.Surface((screen_w - wipe_x, screen_h))
        wipe_surf.fill((0, 0, 0))
        surface.blit(wipe_surf, (wipe_x, 0))
    
    elif transition_type == "dissolve":
        # Pixelated dissolve effect
        progress = 1.0 - (transition_timer / transition_duration)
        pixel_size = int(20 * progress)
        if pixel_size > 0:
            dissolve_surf = pygame.Surface((screen_w, screen_h))
            dissolve_surf.fill((0, 0, 0))
            for x in range(0, screen_w, pixel_size + 1):
                for y in range(0, screen_h, pixel_size + 1):
                    if random.random() < progress:
                        pygame.draw.rect(dissolve_surf, (0, 0, 0), (x, y, pixel_size, pixel_size))
            dissolve_surf.set_alpha(int(255 * progress))
            surface.blit(dissolve_surf, (0, 0))
    
    transition_timer -= 1
    if transition_timer <= 0:
        transition_active = False

# funkcija save_game_csv pieņem str tipa vērtību name, str tipa vērtību char_type, Player tipa vērtību p, SkillTree tipa vērtību s_tree un str tipa vērtību password un atgriež None tipa vērtību None
def save_game_csv(name, char_type, p, s_tree, password=""):
    # [SAREŽĢĪTA LOĢIKA]: CSV datu atjaunināšana
    # Šis kods vispirms nolasa visu CSV failu un pārvērš to par vārdnīcu sarakstu (list of dictionaries).
    # Tas ļauj saglabāt iepriekšējo spēlētāju datus neskartus, kamēr mēs atjauninām tikai konkrētā spēlētāja rindu.
    p_rows = []
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                p_rows = list(csv.DictReader(f))
        except: p_rows = []

    # Atiestatīt spēlētāja stats, lai noņemtu bosu dropu bonusus pirms saglabāšanas
    s_tree.sync_with_player(p)
    
    if globals().get('current_wave', 1) > getattr(p, 'highscore', 1):
        p.highscore = globals().get('current_wave', 1)

    # Izveido jaunu vārdnīcu ar aktuālajiem spēlētāja datiem
    new_p_data = {
        "name": name, "password": password, "char_type": char_type, "money": p.money,
        "max_health": p.max_health, "radius": p.attack_radius,
        "speed": p.speed, "damage": getattr(p, 'damage', 1.0),
        "multi": getattr(p, 'projectile_count', 1),
        "aspeed": getattr(p, 'base_cooldown', 25),
        "max_energy": getattr(p, 'max_energy', 10.0),
        "sp": getattr(p, 'skill_points', 0),
        "magnet": getattr(p, 'magnet_range', 60),
        "dash": int(getattr(p, 'dash_unlocked', False)),
        "armor": getattr(p, 'armor', 0),
        "lifesteal": getattr(p, 'lifesteal', 0),
        "crit_chance": getattr(p, 'crit_chance', 0),
        "thorns": getattr(p, 'thorns', 0),
        "regen": getattr(p, 'regen', 0.0),
        "gold_modifier": getattr(p, 'gold_modifier', 1.0),
        "highscore": getattr(p, 'highscore', 1)
    }

    for s in s_tree.skills:
        new_p_data[f"skill_{s['id']}"] = s["level"]

    # Meklējam, vai šis spēlētājs un varoņa klase jau eksistē datubāzē.
    # Ja eksistē, mēs pārrakstām veco rindu. Ja nē, mēs pievienojam to kā jaunu rindu saraksta beigās.
    found_p = False
    for i, row in enumerate(p_rows):
        if row.get("name") == name and row.get("char_type") == char_type:
            # Ja parole nav sniegta, saglabāt veco paroli
            if not password:
                password = row.get("password", "")
            new_p_data["password"] = password
            p_rows[i] = new_p_data
            found_p = True
            break
    if not found_p:
        p_rows.append(new_p_data)

    # Visbeidzot ierakstām atpakaļ visu sarakstu failā ar jaunajiem datiem.
    with open(PLAYER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(new_p_data.keys()))
        writer.writeheader()
        writer.writerows(p_rows)

# funkcija load_game_csv pieņem str tipa vērtību name, str tipa vērtību char_type, Player tipa vērtību p un SkillTree tipa vērtību s_tree un atgriež None tipa vērtību None
def load_game_csv(name, char_type, p, s_tree):
    if os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["name"] == name and row["char_type"] == char_type:
                    # Iekšējās palīgfunkcijas drošai datu konvertēšanai no teksta uz cipariem.
                    # Ja šūna ir tukša vai nederīga, tiek atgriezta noklusējuma vērtība 'd'.
                    def s_i(k, d): return int(row[k]) if k in row and row[k].strip() else d
                    def s_f(k, d): return float(row[k]) if k in row and row[k].strip() else d

                    p.money = s_i("money", 0)
                    p.max_health = s_f("max_health", 100.0)
                    p.attack_radius = s_f("radius", 100.0)
                    p.speed = s_f("speed", 1.3)
                    p.damage = s_f("damage", 1.0)
                    p.projectile_count = s_i("multi", 1)
                    p.base_cooldown = s_i("aspeed", 25)
                    p.max_energy = s_f("max_energy", 10.0)
                    p.skill_points = s_i("sp", 0)
                    p.magnet_range = s_i("magnet", 60)
                    p.dash_unlocked = bool(s_i("dash", 0))
                    p.armor = s_f("armor", 0)
                    p.lifesteal = s_f("lifesteal", 0)
                    p.crit_chance = s_i("crit_chance", 0)
                    p.thorns = s_i("thorns", 0)
                    p.regen = s_f("regen", 0.0)
                    p.gold_modifier = s_f("gold_modifier", 1.0)
                    p.energy = p.max_energy
                    p.highscore = s_i("highscore", 1)

                    for s in s_tree.skills:
                        key = f"skill_{s['id']}"
                        s["level"] = s_i(key, 0)

                    s_tree.sync_with_player(p)

# funkcija get_leaderboard pieņem int tipa vērtību limit un atgriež sarakstu ar augstākajiem rezultātiem
def get_leaderboard(limit=5):
    entries = []
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        score = int(row.get("highscore", "0") or 0)
                    except ValueError:
                        score = 0
                    entries.append((row.get("name", ""), row.get("char_type", ""), score))
        except:
            return []
    entries.sort(key=lambda e: e[2], reverse=True)
    return entries[:limit]

# funkcija get_dist_to_rect pieņem tuple tipa vērtību point un pygame.Rect tipa vērtību rect un atgriež float tipa vērtību distance
def get_dist_to_rect(point, rect):
    px = max(rect.left, min(point[0], rect.right))
    py = max(rect.top, min(point[1], rect.bottom))
    return math.hypot(point[0] - px, point[1] - py)

game_state, user_name = "menu", ""
player = Player()
skills = SkillTree(screen_w, screen_h)
bosses, enemies, projectiles, coins, chests, active_swings, special_coins, hp_drops = [], [], [], [], [], [], [], []
boss_energy, boss_goal, max_enemies = 0, 100, 4
time_freeze_timer = 0
nuke_flash_timer = 0

# funkcija spawn_enemy pieņem float tipa vērtību hp_m, float tipa vērtību spd_m un int tipa vērtību wave un atgriež None tipa vērtību None
def spawn_enemy(hp_m=1.0, spd_m=1.0, wave=1):
    e = Enemy(random.randint(0, screen_w), random.randint(0, screen_h))
    e.max_health = int(e.max_health * hp_m)
    e.health = e.max_health
    e.speed = min(4.5, e.speed * spd_m)
    e.armor = wave // 5
    enemies.append(e)

# funkcija spawn_coin nepieņem argumentus un atgriež None tipa vērtību None
def spawn_coin():
    c = Coin()
    c.rect.x, c.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    coins.append(c)

flicker_val = 0

# --- GALVENAIS CIKLS ---
while True:
    m_pos = pygame.mouse.get_pos()
    m_click = pygame.mouse.get_pressed()
    flicker_val += 0.08

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC tikai iziet no spēles, ja NAV playing stāvoklī (pause menu tiek apstrādāts atsevišķi)
                if game_state != "playing":
                    if user_name and player.char_type: save_game_csv(user_name, player.char_type, player, skills, user_password)
                    pygame.quit(); sys.exit()

            if game_state == "menu":
                if event.key == pygame.K_RETURN and user_name.strip():
                    # Pārbauda, vai spēlētājs jau eksistē. Ja jā, lūdz paroli; ja nē, jaunas konta izveidošana
                    if player_exists_in_csv(user_name.strip()):
                        is_new_account = False
                    else:
                        is_new_account = True
                    game_state = "password_input"
                    user_password = ""
                    password_error_msg = ""
                elif event.key == pygame.K_BACKSPACE: user_name = user_name[:-1]
                else: 
                    # [SAREŽĢĪTA LOĢIKA]: Ierobežot vārda garumu
                    # Pārbaudām, vai garums ir mazāks par 24 rakstzīmēm UN 
                    # vai nospiestais taustiņš ir izmantojams burts/cipars (len(event.unicode) > 0),
                    # lai novērstu "Shift" vai "Tab" taustiņu kā tukšu simbolu pievienošanu.
                    if len(user_name) < 24 and len(event.unicode) > 0:
                        user_name += event.unicode

            elif game_state == "password_input":
                if event.key == pygame.K_RETURN and user_password.strip():
                    if not is_new_account:
                        # Pārbauda paroli esošajam kontam
                        if check_password(user_name.strip(), user_password.strip()):
                            game_state = "char_select"
                            password_error_msg = ""
                        else:
                            password_error_msg = "Wrong password!"
                            password_error_timer = 120
                            user_password = ""
                    else:
                        # Jauns konts - pārbauda paroles garumu
                        if len(user_password.strip()) < 4:
                            password_error_msg = "Password too short (min 4)!"
                            password_error_timer = 120
                            user_password = ""
                        else:
                            game_state = "char_select"
                            password_error_msg = ""
                elif event.key == pygame.K_BACKSPACE: user_password = user_password[:-1]
                elif event.key == pygame.K_ESCAPE:
                    game_state = "menu"
                    user_name = ""
                    user_password = ""
                    password_error_msg = ""
                else:
                    if len(user_password) < 32 and len(event.unicode) > 0:
                        user_password += event.unicode

            elif game_state == "playing" and event.key == pygame.K_SPACE:
                if getattr(player, 'dash_unlocked', False) and player.dash_cooldown <= 0:
                    k = pygame.key.get_pressed()
                    dx, dy = 0, 0
                    dist = 140
                    if k[pygame.K_w]: dy = -dist
                    if k[pygame.K_s]: dy = dist
                    if k[pygame.K_a]: dx = -dist
                    if k[pygame.K_d]: dx = dist
                    if dx == 0 and dy == 0:
                        dx = dist if player.direction == "right" else -dist
                    player.rect.x += dx
                    player.rect.y += dy
                    player.rect.clamp_ip(screen.get_rect())
                    player.dash_cooldown = 60

            elif game_state == "playing" and event.key == pygame.K_p:
                start_transition("dissolve")
                game_state = "paused"

            elif game_state == "paused" and event.key == pygame.K_ESCAPE:
                start_transition("fade")
                game_state = "playing"

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "paused":
                if pause_save_btn.collidepoint(event.pos):
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    trigger_save_anim("GAME SAVED!")
                elif pause_resume_btn.collidepoint(event.pos):
                    start_transition("fade")
                    game_state = "playing"
                elif pause_quit_btn.collidepoint(event.pos):
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    start_transition("fade")
                    game_state = "menu"
                    user_name = ""
                    user_password = ""
                    player = Player()
            elif game_state == "char_select":
                for i in range(3):
                    rect = pygame.Rect(screen_w // 2 - 450 + (i * 310), 200, 280, 400)
                    if rect.collidepoint(event.pos):
                        sel = ["wizard", "shadow", "dwarf"][i]
                        player.setup_class(sel)
                        # Ja jauns konts, saglabā paroli ar spēlētāja datiem
                        if is_new_account:
                            save_game_csv(user_name, sel, player, skills, user_password)
                        load_game_csv(user_name, sel, player, skills)
                        enemies.clear(); bosses.clear(); projectiles.clear(); coins.clear(); chests.clear(); active_swings.clear()
                        current_wave, max_enemies, time_freeze_timer = 1, 4, 0
                        for _ in range(max_enemies): spawn_enemy()
                        game_state = "playing"

            elif game_state == "skill_tree":
                result = skills.handle_click(event.pos, player)
                if result == "respawn":
                    enemies.clear(); bosses.clear(); projectiles.clear(); active_swings.clear()
                    player.health = player.max_health
                    player.energy = player.max_energy
                    current_wave, max_enemies = 1, 4
                    for _ in range(max_enemies): spawn_enemy()
                    start_transition("wipe")
                    game_state = "playing"
                elif result == "saved":
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    trigger_save_anim("UZLABOTS!")

    # --- IZVĒLNE ---
    if game_state == "menu":
        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        else:
            screen.fill((5, 5, 15))

        if menu_logo:
            # 1. Iegūstam logo pozīciju
            logo_rect = menu_logo.get_rect(center=(screen_w // 2, screen_h // 2 - 80))
            
            # 2. Izveidojam masku no logo (iegūstam formas kontūru)
            mask = pygame.mask.from_surface(menu_logo)
            
            # 3. Pārvēršam masku par tumšu virsmu (setcolor = ēnas krāsa un caurspīdīgums)
            shadow_surf = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            
            # 4. Uzzīmējam ēnu, nobīdot to par 5 pikseļiem pa labi (+5) un uz leju (+5)
            screen.blit(shadow_surf, (logo_rect.x + 10, logo_rect.y + 5))
            
            # 5. Uzzīmējam oriģinālo logo pa virsu
            screen.blit(menu_logo, logo_rect)
        else:
            # Ja logo attēls neielādējas, izveidojam ēnu arī rezerves tekstam!
            title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 255, 150))
            shadow_title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 0, 0))
            title_rect = title.get_rect(center=(screen_w // 2, screen_h // 2 - 80))
            
            screen.blit(shadow_title, (title_rect.x + 5, title_rect.y + 5))
            screen.blit(title, title_rect)



        box_w, box_h = 400, 50
        box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2 + 40, box_w, box_h)
        pygame.draw.rect(screen, (20, 20, 35), box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), box_rect, 2, border_radius=10)
        u_txt = pygame.font.SysFont("Arial", 28).render(f"{user_name}|", True, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=box_rect.center))
        hint = pygame.font.SysFont("Arial", 20).render("Input the user and press ENTER", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 110)))

        leaderboard = get_leaderboard(6)
        lb_x = screen_w - 420
        lb_y = screen_h // 4 - 40
        lb_w, lb_h = 400, 370
        lb_rect = pygame.Rect(lb_x, lb_y, lb_w, lb_h)
        pygame.draw.rect(screen, (15, 15, 30), lb_rect, border_radius=12)
        pygame.draw.rect(screen, (0, 255, 150), lb_rect, 2, border_radius=12)

        title_font = pygame.font.SysFont("Impact", 28)
        entry_font = pygame.font.SysFont("Arial", 20)
        screen.blit(title_font.render("LEADERBOARD", True, (255, 255, 255)), (lb_x + 20, lb_y + 18))

        if leaderboard:
            for idx, (name, char_type, score) in enumerate(leaderboard):
                rank_text = f"{idx + 1}. {name or '---'} ({char_type or 'N/A'})"
                score_text = f"{score}"
                entry_surface = entry_font.render(rank_text, True, (200, 200, 255))
                score_surface = entry_font.render(score_text, True, (0, 255, 150))
                screen.blit(entry_surface, (lb_x + 20, lb_y + 60 + idx * 45))
                screen.blit(score_surface, (lb_x + lb_w - 70, lb_y + 60 + idx * 45))
        else:
            screen.blit(entry_font.render("No leaderboard data yet", True, (150, 150, 150)), (lb_x + 20, lb_y + 60))

    # --- PAROLES IEVADS ---
    elif game_state == "password_input":
        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        else:
            screen.fill((5, 5, 15))

        # Parāda virsrakstu (jauns konts vai esošs konts)
        if is_new_account:
            title = pygame.font.SysFont("Impact", 60).render("CREATE PASSWORD", True, (0, 255, 150))
        else:
            title = pygame.font.SysFont("Impact", 60).render("ENTER PASSWORD", True, (0, 255, 150))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, screen_h // 2 - 150))

        # Paroles ievada logs
        box_w, box_h = 400, 50
        box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2, box_w, box_h)
        pygame.draw.rect(screen, (20, 20, 35), box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), box_rect, 2, border_radius=10)
        
        # Rāda paroli ar aizklātiem rakstzīmēm (*)
        masked_password = "*" * len(user_password) + "|"
        p_txt = pygame.font.SysFont("Arial", 28).render(masked_password, True, (255, 255, 255))
        screen.blit(p_txt, p_txt.get_rect(center=box_rect.center))
        
        # Instrukcijas
        if is_new_account:
            hint = pygame.font.SysFont("Arial", 20).render("Set a password (min 4 characters) and press ENTER", True, (150, 150, 150))
        else:
            hint = pygame.font.SysFont("Arial", 20).render("Enter your password and press ENTER", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 90)))
        
        # Kļūdas ziņojums
        if password_error_timer > 0:
            error_txt = pygame.font.SysFont("Arial", 24, bold=True).render(password_error_msg, True, (255, 0, 0))
            screen.blit(error_txt, error_txt.get_rect(center=(screen_w // 2, screen_h // 2 + 150)))
            password_error_timer -= 1

    # --- VAROŅA IZVĒLE ---
    elif game_state == "char_select":
        if char_select_bg:
            screen.blit(char_select_bg, (0, 0))
        else:
            screen.fill((10, 10, 20))

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title = pygame.font.SysFont("Impact", 60).render("CHOOSE YOUR CHARACTER", True, (255, 255, 255))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 80))

        classes = [("WIZARD", (0, 200, 255), wizard_ui), ("SHADOW", (150, 0, 255), shadow_ui), ("DWARF", (255, 150, 0), dwarf_ui)]
        for i, (name, col, img) in enumerate(classes):      
            rect = pygame.Rect(screen_w // 2 - 450 + (i * 310), 200, 280, 400)
            is_hovered = rect.collidepoint(m_pos)
            border_col = (255, 255, 255) if is_hovered else col
            pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=15)
            pygame.draw.rect(screen, border_col, rect, 3 if is_hovered else 2, border_radius=15)
            screen.blit(img, img.get_rect(center=(rect.centerx, rect.centery - 20)))
            name_t = pygame.font.SysFont("Impact", 32).render(name, True, border_col)
            screen.blit(name_t, name_t.get_rect(center=(rect.centerx, rect.bottom - 45)))

    # --- SPĒLĒŠANA ---
    elif game_state == "playing":
        if game_bg: screen.blit(game_bg, (0, 0))
        else: screen.fill((5, 5, 15))

        if time_freeze_timer <= 0: player.energy -= 1/60
        if player.dash_cooldown > 0: player.dash_cooldown -= 1
        if time_freeze_timer > 0: time_freeze_timer -= 1
        if nuke_flash_timer > 0: nuke_flash_timer -= 1
        if player.attack_cooldown > 0: player.attack_cooldown -= 1

        player.energy = max(0, min(player.energy, player.max_energy))
        if player.energy <= 0 or player.health <= 0:
            player.health = 0
            save_game_csv(user_name, player.char_type, player, skills, user_password)
            game_state, death_timer = "dead", 120
            continue

        if player.health < player.max_health:
            player.health += getattr(player, 'regen', 0)

        if not enemies and not bosses:
            current_wave += 1
            max_enemies += 2
            hp_scale = 1.0 + (current_wave * 0.2)
            spd_scale = 1.0 + (current_wave * 0.05)
            for _ in range(max_enemies): spawn_enemy(hp_scale, spd_scale, current_wave)
            if current_wave % 2 == 0:
                chests.append(Chest(random.randint(100, screen_w-100), random.randint(100, screen_h-100)))
            trigger_save_anim(f"WAVE: {current_wave}")

        player.move(pygame.key.get_pressed())
        player.rect.clamp_ip(screen.get_rect())

        while len(coins) < 5: spawn_coin()
        for c in coins[:]:
            dist = math.hypot(player.rect.centerx - c.rect.centerx, player.rect.centery - c.rect.centery)
            if dist < player.magnet_range:
                c.rect.x += (player.rect.centerx - c.rect.centerx) * 0.1
                c.rect.y += (player.rect.centery - c.rect.centery) * 0.1
            c.draw(screen)
            if player.rect.colliderect(c.rect):
                player.money += int(1 * getattr(player, 'gold_modifier', 1.0))
                player.energy = min(player.max_energy, player.energy + 1.5)
                coins.remove(c)

        if len(special_coins) < 1:
            sc = SpecialCoin()
            sc.rect.x, sc.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
            special_coins.append(sc)
        for s in special_coins[:]:
            dist = math.hypot(player.rect.centerx - s.rect.centerx, player.rect.centery - s.rect.centery)
            if dist < player.magnet_range:
                s.rect.x += (player.rect.centerx - s.rect.centerx) * 0.1
                s.rect.y += (player.rect.centery - s.rect.centery) * 0.1
            s.draw(screen)
            if player.rect.colliderect(s.rect):
                player.money += int(5 * getattr(player, 'gold_modifier', 1.0))
                player.energy = min(player.max_energy, player.energy + 3)
                special_coins.remove(s)

        if len(hp_drops) < 1:
            hc = HpCoin()
            hc.rect.x, hc.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
            hp_drops.append(hc)
        for h in hp_drops[:]:
            dist = math.hypot(player.rect.centerx - h.rect.centerx, player.rect.centery - h.rect.centery)
            if dist < player.magnet_range:
                h.rect.x += (player.rect.centerx - h.rect.centerx) * 0.1
                h.rect.y += (player.rect.centery - h.rect.centery) * 0.1
            h.draw(screen)
            if player.rect.colliderect(h.rect):
                player.health = min(player.max_health, player.health + 20)
                hp_drops.remove(h)

        for ch in chests[:]:
            ch.draw(screen)
            if player.rect.colliderect(ch.rect):
                effect = random.choice(["energy", "freeze", "nuke"])
                if effect == "energy": player.energy = player.max_energy; trigger_save_anim("MAX ENERGY!")
                elif effect == "freeze": time_freeze_timer = 300; trigger_save_anim("FREEZE TIME!")
                elif effect == "nuke":
                    nuke_flash_timer = 15; trigger_save_anim("NUKE!")
                    # 1. Iznīcināt visus parastos ienaidniekus
                    for e in enemies[:]: 
                        e.health = 0
                    # 2. Nodarīt 150 bojājumus VISIEM bosses, kas šobrīd ir ekrānā!
                    for b in bosses[:]:
                        b.health -= 150  
                        
                chests.remove(ch)

        # [SAREŽĢĪTA LOĢIKA]: Automātiskā šaušana un mērķēšana
        if player.attack_cooldown <= 0:
            if player.char_type == "dwarf":
                # Rūķis veic apļveida sitienu visiem, kas ir apkārt
                active_swings.append(MeleeSwing(player, enemies + bosses, player.damage))
                player.attack_cooldown = player.base_cooldown
            else:
                # Burvis un Ēna izmanto tēmēšanu:
                # 1. Atrod visus ienaidniekus un priekšniekus, kas atrodas spēlētāja rādiusā
                targets = [e for e in (enemies + bosses) if get_dist_to_rect(player.rect.center, e.rect) <= player.attack_radius]
                if targets:
                    # 2. Sakārto mērķus, sākot no tuvākā (izmantojot lambda funkciju attāluma iegūšanai)
                    targets.sort(key=lambda t: get_dist_to_rect(player.rect.center, t.rect))
                    
                    # 3. Izšauj lādiņus. Cikls iet līdz 'projectile_count' skaitam, vai kamēr nebeidzas mērķi
                    for i in range(min(len(targets), player.projectile_count)):
                        projectiles.append(Projectile(player.rect.centerx, player.rect.centery, targets[i], player.color, player.attack_radius * 1.5))
                    player.attack_cooldown = player.base_cooldown

        for s in active_swings[:]:
            s.update(); s.draw(screen)
            if s.lifetime <= 0: active_swings.remove(s)

        for p_obj in projectiles[:]:
            if p_obj.update(enemies + bosses):
                p_obj.draw(screen)
                if p_obj.rect.colliderect(p_obj.target.rect):
                    dmg = max(1, player.damage - getattr(p_obj.target, 'armor', 0))
                    if random.randint(1, 100) <= getattr(player, 'crit_chance', 0): dmg *= 2
                    p_obj.target.health -= dmg
                    if getattr(player, 'lifesteal', 0) > 0:
                        player.health = min(player.max_health, player.health + player.lifesteal)
                    if p_obj in projectiles: projectiles.remove(p_obj)
            else:
                if p_obj in projectiles: projectiles.remove(p_obj)

        dilation = getattr(player, 'time_dilation', 1.0)
        for e in enemies[:]:
            if time_freeze_timer <= 0:
                e.update(player.rect, dilation)
                if player.rect.colliderect(e.rect):
                    player.health -= max(0.05, 0.3 - (getattr(player, 'armor', 0) * 0.03))
                    if getattr(player, 'thorns', 0) > 0: e.health -= player.thorns
            e.draw(screen)
            if e.health <= 0:
                enemies.remove(e); player.money += 2; boss_energy += 10

        for b in bosses[:]:
            if time_freeze_timer <= 0:
                # Saglabājam izšauto ugunsbumbu damage mainīgajā 'boss_projectile_dmg'
                boss_projectile_dmg = b.update(player.rect, dilation)
                
                # Ja mēs saņēmam saapi no ugunsbumbas, atņemam dzīvību (ņemot vērā bruņas)
                if boss_projectile_dmg and boss_projectile_dmg > 0:
                    player.health -= max(1, boss_projectile_dmg - getattr(player, 'armor', 0))
                    
                # Pieskaršanās bojājumi joprojām strādā!
                if player.rect.colliderect(b.rect):
                    player.health -= max(0.1, 0.8 - (getattr(player, 'armor', 0) * 0.05))
            b.draw(screen)
            if b.health <= 0:
                apply_boss_drop(player, current_wave)
                bosses.remove(b); player.money += 50; player.skill_points += 1; trigger_save_anim("+1 SP!")

        if boss_energy >= boss_goal:
            # beigās 'current_wave', lai boss zinātu, cik stipram viņam jābūt!
            bosses.append(Boss(screen_w, screen_h, current_wave))
            boss_energy = 0

        player.draw(screen)

        # [SAREŽĢĪTA LOĢIKA]: TUMSAS SISTĒMA (Apgaismojuma renderēšana)
        # Šis kods pārklāj ekrānu ar tumšu slāni, bet ap spēlētāju izgriež "caurumu", lai radītu gaismas efektu.
        shroud.fill((5, 5, 15, 180))
        pulse = int(6 * math.sin(flicker_val))
        light_radius = max(10, int(player.attack_radius * 1.4) + pulse)
        
        # [SAREŽĢĪTA LOĢIKA]: Gaismas kešatmiņa (Glow Cache)
        # Ja mēs katru kadru zīmējam 200+ lielus apļus, spēle sāk ļoti bremzēt, kad uzbrukuma rādiuss ir liels.
        # Tāpēc mēs izmantojam vārdnīcu 'glow_cache', lai saglabātu uzzīmētos gaismas apļus.
        if not hasattr(player, 'glow_cache'):
            player.glow_cache = {}
            
        # Pārbaudām, vai šāda izmēra gaisma jau ir uzzīmēta iepriekš
        if light_radius not in player.glow_cache:
            t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
            core_radius = max(1, light_radius // 2)
            pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), core_radius)
            
            # Solis -3 nozīmē, ka mēs zīmējam 3x mazāk apļu (ietaupot resursus), saglabājot to pašu izskatu!
            for r in range(light_radius, core_radius, -3):
                alpha = max(0, min(255, int(255 * (1 - (r - core_radius) / max(1, light_radius - core_radius)))))
                pygame.draw.circle(t_surf, (0, 0, 0, alpha), (light_radius, light_radius), r)
                
            # Saglabājam gatavo bildi atmiņā
            player.glow_cache[light_radius] = t_surf
            
        # Paņemam gatavo gaismu no atmiņas (Tas neprasa nekādu skaitļošanas jaudu!)
        t_surf = player.glow_cache[light_radius]
        
        shroud.blit(t_surf, t_surf.get_rect(center=player.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(shroud, (0, 0))
        # --- LIETOTĀJA SASKARNE (UI) ---
        if nuke_flash_timer > 0:
            flash = pygame.Surface((screen_w, screen_h)); flash.fill((255, 255, 255))
            flash.set_alpha(int((nuke_flash_timer / 15) * 255)); screen.blit(flash, (0, 0))
        if time_freeze_timer > 0:
            screen.blit(freeze_surf, (0, 0))

        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"Money: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        screen.blit(ui_f.render(f"Wave: {current_wave} [Best: {player.highscore}]", True, (200, 200, 255)), (20, 50))
        screen.blit(ui_f.render(f"ID: {user_name}", True, (200, 200, 255)), (20, 80))
        bar_x, bar_y = screen_w // 2 - 100, screen_h - 55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10))
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, (player.energy / player.max_energy) * 200), 10))
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health / player.max_health) * 200), 15))

        # --- STATS PANEL (Right side) ---
        stats_font = pygame.font.SysFont("Consolas", 16)
        stats_x = screen_w - 220
        stats_y = 20
        stats_bg = pygame.Surface((200, 160), pygame.SRCALPHA)
        stats_bg.fill((20, 20, 40, 200))
        pygame.draw.rect(stats_bg, (0, 150, 200), (0, 0, 200, 160), 2)
        screen.blit(stats_bg, (stats_x, stats_y))
        
        stats_list = [
            f"DMG: {int(player.damage)}",
            f"SPD: {player.speed:.1f}",
            f"RNG: {int(player.attack_radius)}",
            f"ARM: {getattr(player, 'armor', 0):.1f}",
            f"LIFE: {getattr(player, 'lifesteal', 0):.1f}",
            f"CRIT: {getattr(player, 'crit_chance', 0)}%",
            f"MAG: {int(player.magnet_range)}"
        ]
        
        for i, stat in enumerate(stats_list):
            stat_text = stats_font.render(stat, True, (100, 255, 200))
            screen.blit(stat_text, (stats_x + 10, stats_y + 10 + i * 20))

        if save_notification_timer > 0:
            t = pygame.font.SysFont("Arial", 28, bold=True).render(save_notification_msg, True, (0, 255, 150))
            screen.blit(t, t.get_rect(center=(screen_w // 2, 100)))
            save_notification_timer -= 1

        if boss_drop_timer > 0:
            # Big glowing boss drop notification
            alpha = int(255 * (boss_drop_timer / 180))
            big_font = pygame.font.SysFont("Arial", 52, bold=True)
            drop_text = big_font.render(boss_drop_msg, True, (255, 215, 0))
            
            # Add background box for visibility
            pad = 20
            box_rect = pygame.Rect(screen_w // 2 - drop_text.get_width() // 2 - pad, 
                                   screen_h // 2 - 80 - pad,
                                   drop_text.get_width() + pad * 2,
                                   drop_text.get_height() + pad * 2)
            # Semi-transparent gold/red glow background
            box_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
            box_surf.fill((139, 35, 35, 180))
            pygame.draw.rect(box_surf, (255, 215, 0), (0, 0, box_rect.width, box_rect.height), 3)
            screen.blit(box_surf, box_rect.topleft)
            
            # Draw the text centered in the box
            screen.blit(drop_text, drop_text.get_rect(center=box_rect.center))
            boss_drop_timer -= 1

    elif game_state == "paused":
        # Pūš semi-transparent overlay pār spēles ekrānu
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Pause menu title
        title = pygame.font.SysFont("Impact", 80).render("PAUSED", True, (0, 255, 150))
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, screen_h // 2 - 150))
        
        # Pause menu buttons
        btn_w, btn_h = 200, 50
        btn_x = screen_w // 2 - btn_w // 2
        
        # Save button
        pause_save_btn = pygame.Rect(btn_x, screen_h // 2 - 20, btn_w, btn_h)
        pygame.draw.rect(screen, (50, 150, 255), pause_save_btn, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), pause_save_btn, 2, border_radius=10)
        save_btn_text = pygame.font.SysFont("Arial", 28, bold=True).render("SAVE", True, (0, 0, 0))
        screen.blit(save_btn_text, save_btn_text.get_rect(center=pause_save_btn.center))
        
        # Resume button
        pause_resume_btn = pygame.Rect(btn_x, screen_h // 2 + 50, btn_w, btn_h)
        pygame.draw.rect(screen, (50, 200, 100), pause_resume_btn, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), pause_resume_btn, 2, border_radius=10)
        resume_btn_text = pygame.font.SysFont("Arial", 28, bold=True).render("RESUME", True, (0, 0, 0))
        screen.blit(resume_btn_text, resume_btn_text.get_rect(center=pause_resume_btn.center))
        
        # Quit button
        pause_quit_btn = pygame.Rect(btn_x, screen_h // 2 + 120, btn_w, btn_h)
        pygame.draw.rect(screen, (200, 50, 50), pause_quit_btn, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), pause_quit_btn, 2, border_radius=10)
        quit_btn_text = pygame.font.SysFont("Arial", 28, bold=True).render("QUIT", True, (0, 0, 0))
        screen.blit(quit_btn_text, quit_btn_text.get_rect(center=pause_quit_btn.center))
        
        # Hint text
        hint = pygame.font.SysFont("Arial", 18).render("Press ESC to Resume", True, (150, 150, 150))
        screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, screen_h - 50))

    elif game_state == "dead":
        # Death cinematic: Fade to black, then show GAME OVER
        progress = 1.0 - (death_timer / 120.0)  # 0 at start, 1 at end
        
        # Phase 1 (0-0.5): Fade the game to black
        if progress < 0.5:
            fade_alpha = int(255 * (progress * 2))  # 0 -> 255 over first half
            fade_surf = pygame.Surface((screen_w, screen_h))
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(fade_alpha)
            screen.blit(fade_surf, (0, 0))
            
            # Optional: Red vignette effect during fade
            vignette = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            vignette.fill((139, 0, 0, int(100 * (progress * 2))))
            screen.blit(vignette, (0, 0))
        else:
            # Phase 2 (0.5-1.0): Show GAME OVER text fading in
            screen.fill((5, 5, 15))
            text_alpha = int(255 * ((progress - 0.5) * 2))  # 0 -> 255 over second half
            msg = pygame.font.SysFont("Impact", 100).render("GAME OVER", True, (255, 0, 0))
            msg_with_alpha = msg.copy()
            msg_with_alpha.set_alpha(text_alpha)
            screen.blit(msg_with_alpha, msg_with_alpha.get_rect(center=(screen_w // 2, screen_h // 2)))
        
        death_timer -= 1
        if death_timer <= 0:
            # Atiestatīt spēlētāja stats, lai noņemtu visus bosu dropu bonusus
            skills.sync_with_player(player)
            game_state = "skill_tree"

    elif game_state == "skill_tree":
        skills.draw(screen, player.money, player.skill_points, player.char_type)
        if save_notification_timer > 0:
            t = pygame.font.SysFont("Arial", 22, bold=True).render(save_notification_msg, True, (0, 255, 150))
            screen.blit(t, t.get_rect(center=(screen_w // 2, 40)))
            save_notification_timer -= 1

    # Render cinematic transition effects
    render_transition(screen)

    pygame.display.flip()
    clock.tick(60)