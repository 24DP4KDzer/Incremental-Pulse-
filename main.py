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
from screens.menu_screen import (draw_main_menu, draw_login_screen, draw_settings_overlay,
                                  draw_leaderboard, draw_delete_confirm)
from screens.pause_death_screen import draw_death_screen, draw_pause_menu
from fonts import (render_pixel_text, UI_LARGE, UI_MEDIUM, UI_NORMAL, 
                   UI_SMALL, UI_TINY, GAME_STATS, GAME_SCORE)
import db as DB

# Iegūst skripta direktoriju, lai izkrautos failus no pareizuma ceļa neatkarīgi no darba direktorijas
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)  # Mainīt darba direktoriju uz skripta vietu

# funkcija get_path pieņem str tipa vērtību relative_path un atgriež str tipa vērtību full_path
def get_path(relative_path):
    """ 
    LIETOŠANA: Attēliem, skaņām, sākuma datiem.
    Atrod failus, kas ir iepakoti .exe failā (lasīšanai).
    """
    if getattr(sys, 'frozen', False):
        # Ja palaists kā .exe, skatās pagaidu mapē (_MEIPASS)
        base_path = sys._MEIPASS
    else:
        # Ja palaists kā skripts, skatās tur, kur ir main.py
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

def get_save_path(relative_path):
    """ 
    LIETOŠANA: Progresa saglabāšanai, CSV failu rakstīšanai.
    Atrod ceļu blakus tavam .exe failam, lai dati nepazustu.
    """
    if getattr(sys, 'frozen', False):
        # Atrod mapi, kurā fiziski atrodas .exe fails
        base_path = os.path.dirname(sys.executable)
    else:
        # Atrod mapi, kurā ir tavs main.py
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    # Izveido mapi, ja tā neeksistē (piemēram, "data" mapi)
    full_path = os.path.join(base_path, relative_path)
    directory = os.path.dirname(full_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    return full_path

# 1. INICIALIZĀCIJA
pygame.init()

MUSIC_END_EVENT = pygame.USEREVENT + 1
bg_music_files = []
current_music_index = 0
music_volume = 10
sfx_volume = 100

_dragging_slider = None
settings_mouse_down = False
settings_mouse_up = False

def get_background_music_files():
    audio_dir = get_path("audio")
    if not os.path.isdir(audio_dir):
        return []
    return sorted([
        os.path.join(audio_dir, f)
        for f in os.listdir(audio_dir)
        if f.lower().endswith((".mp3", ".wav", ".ogg", ".flac", ".mid", ".midi"))
    ])


def play_current_bg_music():
    if not bg_music_files:
        return
    pygame.mixer.music.load(bg_music_files[current_music_index])
    pygame.mixer.music.set_volume(music_volume / 100)
    pygame.mixer.music.play(0)

try:
    pygame.mixer.init()
    bg_music_files = get_background_music_files()
    if bg_music_files:
        pygame.mixer.music.set_endevent(MUSIC_END_EVENT)
        play_current_bg_music()
except Exception:
    pass

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_w, screen_h = screen.get_size()

clock = pygame.time.Clock()
try:
    icon_path = get_path("photos/icon.png") # Pārliecinies, ka fails eksistē šajā mapē
    game_icon = pygame.image.load(icon_path)
    pygame.display.set_icon(game_icon)
    pygame.display.set_caption("Pulse: Evolution") # Spēles nosaukums
except Exception as e:
    print(f"Ikonu neizdevās ielādēt: {e}")

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
game_state, user_name = "main_menu", ""  # Start at main menu instead of login
account_in_use = False        # True when another session holds this account
heartbeat_timer = 0           # counts frames, fires every 5 s
user_password = ""
input_field_active = None  # Track which field is being edited ("username", "password", or None)
password_error_msg = ""
password_error_timer = 0
is_new_account = False
# --- INPUT FIELD RECTS FOR CLICKING ---
user_input_rect = pygame.Rect(0, 0, 400, 50)
pass_input_rect = pygame.Rect(0, 0, 400, 50)
user_clear_btn = pygame.Rect(0, 0, 40, 40)
pass_clear_btn = pygame.Rect(0, 0, 40, 40)
# --- MENU BUTTONS ---


play_btn = pygame.Rect(0, 0, 200, 60) 
settings_btn = pygame.Rect(0, 0, 200, 60)
back_btn = pygame.Rect(0, 0, 0, 0)
show_settings = False


# --- SETTINGS ---
show_settings = False
music_volume = 10
sfx_volume = 100
settings_buttons = {}
settings_mouse_down = False   # track slider drag start

# --- LEADERBOARD SEARCH ---
lb_search_text = ""
lb_search_active = False
lb_search_result = ""

# --- DELETE ACCOUNT CONFIRM ---
show_delete_confirm = False
delete_confirm_password = ""      # password typed inside the delete modal
delete_confirm_pw_active = False  # is that input field focused?
delete_confirm_error_msg = ""
delete_confirm_error_timer = 0

# --- KILL TIMER ---
kill_hold_timer = 0
KILL_HOLD_DURATION = 180  # 3 seconds at 60 FPS

pause_save_btn = pygame.Rect(0, 0, 0, 0)
pause_resume_btn = pygame.Rect(0, 0, 0, 0)
pause_quit_btn = pygame.Rect(0, 0, 0, 0)
quit_btn = pygame.Rect(0, 0, 0, 0)          # main-menu quit button
lb_search_rect = pygame.Rect(0, 0, 0, 0)    # leaderboard search bar rect
delete_account_btn = pygame.Rect(0, 0, 0, 0)
_delete_confirm_rects = (pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0))


# ── DATABASE INIT ─────────────────────────────────────────────────────────
DB.connect()   # non-blocking; falls back to CSV if offline

def player_exists_in_csv(name):
    if DB.is_connected():
        return DB.account_exists(name)
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, "r", newline="") as f:
                for row in csv.DictReader(f):
                    if row.get("name") == name:
                        return True
        except: pass
    return False

def check_password(name, password):
    if DB.is_connected():
        return DB.check_password(name, password)
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, "r", newline="") as f:
                for row in csv.DictReader(f):
                    if row.get("name") == name:
                        return row.get("password", "") == password
        except: pass
    return False

# funkcija apply_boss_drop pieņem Player tipa vērtību player un int tipa vērtību wave un atgriež None tipa vērtību None
def apply_boss_drop(player, wave):
    # Dod spēlētājam izlases spēka uzpūšanu, kad tas nogalina bosu
    # [SAREŽĢĪTA LOĢIKA]: Izlases buff izvēle no vairākām iespējām
    drop_type = random.choice(["damage", "speed", "health", "armor", "lifesteal"])
    
    if drop_type == "damage":
        if player.damage >= 100:
            player.money += 100 # Iedodam moneeey bonusu, ja damage jau ir maxed out
            trigger_boss_drop_anim("DAMAGE MAXED! +$100")
            return "money"
        else:
            bonus = int(1 + (wave * 0.2))
            old_dmg = player.damage
            player.damage = min(100, player.damage + bonus)
            actual_gain = player.damage - old_dmg
 
            trigger_boss_drop_anim(f"DAMAGE BOOST! +{actual_gain}")





    elif drop_type == "speed":
        if player.speed >= 22:
            player.money += 100 # Iedodam moneeey bonusu, ja ātrums jau ir maxed out
            trigger_boss_drop_anim("SPEED MAXED! +$100")
            return "money"
        else:
            bonus = round(0.2 + (wave * 0.2), 1)
            
            # Pieskaitām bonusu, bet neļaujam tam pārsniegt 22
            old_speed = player.speed
            player.speed = min(22, player.speed + bonus)
            
            # Aprēķinām, cik reāli tika pieskaitīts (vizuālam efektam)
            actual_gain = round(player.speed - old_speed, 1)
            
            if actual_gain > 0: # Ja spēlētājs tiešām saņēma ātruma bonusu, rādam animāciju
                trigger_boss_drop_anim(f"SPEED BOOST! +{actual_gain}")


    elif drop_type == "health":
        if player.max_health >= 500:
            player.money += 100
            trigger_boss_drop_anim("HEALTH MAXED! +$100")
            return "money"
        bonus = round(wave * 0.1, 1)
        old_mh = player.max_health
        player.max_health = round(min(500, player.max_health + bonus), 1)
        player.health = round(min(500, player.health + bonus), 1)
        actual_gain = round(player.health - old_mh, 1)
        if actual_gain > 0:
                trigger_boss_drop_anim(f"HEALTH BOOST! +{actual_gain}")



    elif drop_type == "armor":
        armor_boost = 1 + (wave // 8)
        new_armor = getattr(player, 'armor', 0) + armor_boost
        if new_armor > 30:
            player.money += 100
            trigger_boss_drop_anim("ARMOR MAXED! +$100")
            return "money"
        player.armor = new_armor
        trigger_boss_drop_anim(f"ARMOR BOOST! +{armor_boost}")

    elif drop_type == "lifesteal":
        if player.lifesteal >= 15:
            player.money += 100 # Iedodam moneeey bonusu, ja lifesteal jau ir maxed out
            trigger_boss_drop_anim("LIFESTEAL MAXED! +$100")
            return "money"
        else:
            # Aprēķinām bonusu
            bonus = round(wave * 0.2, 1)
            
            # Saglabājam veco vērtību, lai zinātu, cik reāli pieskaitījām
            old_ls = player.lifesteal
            
            # Pieskaitām, bet ierobežojam uz 15 un noapaļojam
            player.lifesteal = round(min(15, player.lifesteal + bonus), 1)
            
            # Aprēķinām faktisko ieguvumu vizuālajai animācijai
            actual_gain = round(player.lifesteal - old_ls, 1)
            
            if actual_gain > 0:
                trigger_boss_drop_anim(f"LIFESTEAL BOOST! +{actual_gain}")


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


# funkcija load_logo pieņem str tipa vērtību path, int tipa vērtību max_w un int tipa vērtību max_h un atgriež pygame.Surface tipa vērtību logo_image
def load_logo(path, max_w, max_h):
    try:
        img = pygame.image.load(path).convert_alpha()
        orig_w, orig_h = img.get_size()
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        return pygame.transform.scale(img, (new_w, new_h))
    except:
        return None

# --- IELĀDĒT VISU ---
menu_bg        = load_bg(get_path("photos/menu_bg.png"))
char_select_bg = load_bg(get_path("photos/char_select_bg.png"))
game_bg        = load_bg(get_path("photos/bg.png"))
if game_bg:
    game_bg.set_alpha(180)

menu_logo = load_logo(get_path("photos/logo.png"), screen_w * 0.6, screen_h * 0.3)
play_img = load_sprite(get_path("photos/play_button.png"), size=(300, 80))
settings_img = load_sprite(get_path("photos/settings_button.png"), size=(300, 80))
back_img = load_sprite(get_path("photos/back_button.png"), size=(150, 50))
quit_img = load_sprite(get_path("photos/quit_button.png"), size=(220, 70))  # optional; falls back gracefully
pause_bg = load_bg(get_path("photos/pause_bg.png"))  # optional background for pause menu

original_login_img = pygame.image.load(get_path("photos/login.png")).convert_alpha()
login_img = pygame.transform.scale(original_login_img, (350, 80))


char_card_img = pygame.image.load(get_path("photos/char_select.png")).convert_alpha()
char_card_img = pygame.transform.scale(char_card_img, (280, 400))



# Varoņu sprites
wizard_ui = load_sprite(get_path("photos/wizard_right.png"))
shadow_ui = load_sprite(get_path("photos/Shadow_up.png"))
dwarf_ui  = load_sprite(get_path("photos/dwarf_forward.png"))

# Load chain image for dwarf damage lines (fallback to red line if not found)
_chain_img_path = get_path("photos/chain.png")
if os.path.exists(_chain_img_path):
    chain_img_original = pygame.image.load(_chain_img_path).convert_alpha()
    chain_img_original= pygame.transform.scale(chain_img_original,(90, 10))
else:
    chain_img_original = None

# Load axe image for dwarf axes (fallback to drawn rectangles if not found)
_axe_img_path = get_path("photos/axe.png")
if os.path.exists(_axe_img_path):
    axe_img_original = pygame.image.load(_axe_img_path).convert_alpha()
    axe_img_original = pygame.transform.scale(axe_img_original, (70, 35))
else:
    axe_img_original = None


freeze_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
freeze_surf.fill((0, 150, 255, 40))

skills = SkillTree(screen_w, screen_h)

class MeleeSwing:
    # funkcija __init__ pieņem MeleeSwing tipa vērtību self, Player tipa vērtību owner, list tipa vērtību enemies un int tipa vērtību damage un atgriež None tipa vērtību None
    def __init__(self, owner, enemies, damage):
        self.owner = owner
        self.angle = 0
        self.spin_speed = getattr(owner, 'rotation_speed', 20)
        self.radius = owner.attack_radius
        self.lifetime = 360 // self.spin_speed
        self.is_dwarf = owner.char_type == "dwarf"
        self.damage = damage
        self.enemies = enemies  # Store enemies for continuous damage
        
        if self.is_dwarf:
            # Dwarf has spinning axes - get number of axes from multi skill
            self.num_axes = getattr(owner, 'projectile_count', 1)
            # Base spin speed with gentle scaling: 5% increase per firerate level (max 50% at lvl 10)
            base_spin_speed = 5
            firerate_level = getattr(owner, 'firerate_level', 0)
            speed_multiplier = 1.0 + (firerate_level * 0.05)  # 5% per level
            self.spin_speed = base_spin_speed * speed_multiplier
            # Dwarf axes spin continuously, so longer lifetime
            self.lifetime = 600  # Much longer lifetime for continuous spinning
        else:
            # Regular melee swing for other characters - do damage immediately
            self.num_axes = 1
            self.do_damage()

        # Create axe surface only for non-dwarf characters
        if not self.is_dwarf:
            self.surface = pygame.Surface((70, 35), pygame.SRCALPHA)
            pygame.draw.rect(self.surface, (100, 50, 0), (0, 12, 50, 10))
            pygame.draw.rect(self.surface, (200, 200, 200), (45, 0, 25, 35))

    # funkcija do_damage pieņem MeleeSwing tipa vērtību self un atgriež None tipa vērtību None
    def do_damage(self):
        if self.is_dwarf:
            # Damage via lines from player to each axe
            for i in range(self.num_axes):
                axe_angle = self.angle + (360 / self.num_axes) * i
                rad = math.radians(axe_angle)
                
                # Calculate axe position
                axe_x = self.owner.rect.centerx + math.cos(rad) * self.radius
                axe_y = self.owner.rect.centery + math.sin(rad) * self.radius
                
                # End the line at the axe tip instead of at the axe center
                axe_tip_offset = 35
                line_start = (self.owner.rect.centerx, self.owner.rect.centery)
                line_end = (axe_x + math.cos(rad) * axe_tip_offset,
                            axe_y + math.sin(rad) * axe_tip_offset)
                
                # Check each enemy for collision with this damage line
                for e in self.enemies:
                    if not hasattr(e, 'rect') or e.health <= 0:
                        continue
                    
                    # Calculate distance from enemy center to line
                    dist_to_line = self._point_to_line_distance(e.rect.center, line_start, line_end)
                    
                    # If enemy is close enough to the line (enemy radius + line thickness)
                    enemy_radius = 15  # Approximate enemy hitbox radius
                    line_thickness = 8  # Damage line thickness
                    
                    if dist_to_line <= enemy_radius + line_thickness:
                        enemy_armor = getattr(e, 'armor', 0)
                        base_dmg = max(1, self.damage - enemy_armor)
                        final_dmg = base_dmg
                        
                        # Critical hit chance
                        if random.randint(1, 100) <= getattr(self.owner, 'crit_chance', 0):
                            final_dmg *= 2
                        
                        e.health -= final_dmg
                        
                        # Lifesteal
                        if getattr(self.owner, 'lifesteal', 0) > 0:
                            self.owner.health = min(self.owner.max_health, self.owner.health + self.owner.lifesteal)
                        
                        # Knockback
                        if hasattr(e, 'rect'):
                            dx = e.rect.centerx - self.owner.rect.centerx
                            dy = e.rect.centery - self.owner.rect.centery
                            dist_kb = math.hypot(dx, dy)
                            if dist_kb != 0:
                                e.rect.x += (dx / dist_kb) * 10
                                e.rect.y += (dy / dist_kb) * 10
        else:
            # Original circular damage for non-dwarf characters
            for e in self.enemies:
                if not hasattr(e, 'rect') or e.health <= 0:
                    continue
                    
                dist = math.hypot(self.owner.rect.centerx - e.rect.centerx, self.owner.rect.centery - e.rect.centery)
                
                if dist <= self.radius + 25:
                    enemy_armor = getattr(e, 'armor', 0)
                    base_dmg = max(1, self.damage - enemy_armor)
                    final_dmg = base_dmg
                    
                    if random.randint(1, 100) <= getattr(self.owner, 'crit_chance', 0):
                        final_dmg *= 2
                    
                    e.health -= final_dmg
                    
                    if getattr(self.owner, 'lifesteal', 0) > 0:
                        self.owner.health = min(self.owner.max_health, self.owner.health + self.owner.lifesteal)
                    
                    if hasattr(e, 'rect'):
                        dx = e.rect.centerx - self.owner.rect.centerx
                        dy = e.rect.centery - self.owner.rect.centery
                        dist_kb = math.hypot(dx, dy)
                        if dist_kb != 0:
                            e.rect.x += (dx / dist_kb) * 10
                            e.rect.y += (dy / dist_kb) * 10

    # funkcija _point_to_line_distance pieņem MeleeSwing tipa vērtību self, tuple tipa vērtību point, tuple tipa vērtību line_start un tuple tipa vērtību line_end un atgriež float tipa vērtību distance
    def _point_to_line_distance(self, point, line_start, line_end):
        """Calculate distance from point to line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line_start to line_end
        dx = x2 - x1
        dy = y2 - y1
        
        # If line has zero length, return distance to start point
        if dx == 0 and dy == 0:
            return math.hypot(px - x1, py - y1)
        
        # Parameter t represents position along line segment
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        # Closest point on line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Distance from point to closest point on line
        return math.hypot(px - closest_x, py - closest_y)

    # funkcija update pieņem MeleeSwing tipa vērtību self un atgriež None tipa vērtību None
    def update(self):
        self.angle += self.spin_speed
        self.lifetime -= 1
        
        # For dwarf, do damage continuously as axes spin
        if self.is_dwarf:
            self.do_damage()

    # funkcija draw pieņem MeleeSwing tipa vērtību self un pygame.Surface tipa vērtību surface un atgriež None tipa vērtību None
    def draw(self, surface):
        if self.is_dwarf:
            # Draw chain/line and spinning axes for dwarf
            for i in range(self.num_axes):
                # Calculate angle for each axe (evenly distributed)
                axe_angle = self.angle + (360 / self.num_axes) * i
                rad = math.radians(axe_angle)
                
                # Calculate axe position
                axe_x = self.owner.rect.centerx + math.cos(rad) * self.radius
                axe_y = self.owner.rect.centery + math.sin(rad) * self.radius
                
                axe_tip_offset = 35
                tip_x = axe_x + math.cos(rad) * axe_tip_offset
                tip_y = axe_y + math.sin(rad) * axe_tip_offset
                
                # Draw chain PNG or fallback red line (NO full-screen surface!)
                if chain_img_original is not None:
                    # Scale and rotate chain image to connect player center to axe tip
                    cx, cy = self.owner.rect.centerx, self.owner.rect.centery
                    chain_len = math.hypot(tip_x - cx, tip_y - cy)
                    if chain_len > 0:
                        chain_angle_deg = -math.degrees(math.atan2(tip_y - cy, tip_x - cx))
                        scaled_chain = pygame.transform.scale(chain_img_original, (int(chain_len), max(1, chain_img_original.get_height())))
                        rotated_chain = pygame.transform.rotate(scaled_chain, chain_angle_deg)
                        mid_x = (cx + tip_x) / 2
                        mid_y = (cy + tip_y) / 2
                        chain_rect = rotated_chain.get_rect(center=(mid_x, mid_y))
                        surface.blit(rotated_chain, chain_rect)
                else:
                    # Fallback: draw line directly on the surface (no alpha surface needed)
                    pygame.draw.line(surface, (255, 100, 100), 
                                   (self.owner.rect.centerx, self.owner.rect.centery), 
                                   (int(tip_x), int(tip_y)), 3)
                
                # Draw axe using PNG or fallback to drawn rectangles
                if axe_img_original is not None:
                    rotated_axe = pygame.transform.rotate(axe_img_original, -axe_angle)
                    rect = rotated_axe.get_rect(center=(axe_x, axe_y))
                    surface.blit(rotated_axe, rect)
                else:
                    axe_surface = pygame.Surface((70, 35), pygame.SRCALPHA)
                    pygame.draw.rect(axe_surface, (100, 50, 0), (0, 12, 50, 10))
                    pygame.draw.rect(axe_surface, (200, 200, 200), (45, 0, 25, 35))
                    rotated_axe = pygame.transform.rotate(axe_surface, -axe_angle)
                    rect = rotated_axe.get_rect(center=(axe_x, axe_y))
                    surface.blit(rotated_axe, rect)
        else:
            # Regular melee swing for other characters
            rotated_axe = pygame.transform.rotate(self.surface, -self.angle)
            rad = math.radians(self.angle)
            pos_x = self.owner.rect.centerx + math.cos(rad) * self.radius
            pos_y = self.owner.rect.centery + math.sin(rad) * self.radius
            rect = rotated_axe.get_rect(center=(pos_x, pos_y))
            surface.blit(rotated_axe, rect)

# funkcija trigger_save_anim pieņem str tipa vērtību msg un atgriež None tipa vērtību None
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
    """Save to MongoDB Atlas (primary) and CSV (fallback)."""
    if globals().get('current_wave', 1) > getattr(p, 'highscore', 1):
        p.highscore = globals().get('current_wave', 1)

    # ── MongoDB save (async, non-blocking) ──────────────────────────────
    if DB.is_connected():
        DB.save_character(name, char_type, p, s_tree)

    # ── CSV fallback save ────────────────────────────────────────────────
    p_rows = []
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                p_rows = list(csv.DictReader(f))
        except: p_rows = []

    new_p_data = {
        "name": name, "password": password, "char_type": char_type,
        "money": p.money, "max_health": p.max_health, "radius": p.attack_radius,
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

    found_p = False
    for i, row in enumerate(p_rows):
        if row.get("name") == name and row.get("char_type") == char_type:
            if not password:
                password = row.get("password", "")
            new_p_data["password"] = password
            p_rows[i] = new_p_data
            found_p = True
            break
    if not found_p:
        p_rows.append(new_p_data)

    try:
        with open(PLAYER_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(new_p_data.keys()), extrasaction='ignore')
            writer.writeheader()
            writer.writerows(p_rows)
    except Exception as e:
        print(f"[CSV] save error: {e}")

def load_game_csv(name, char_type, p, s_tree):
    """Load from MongoDB Atlas first, fall back to CSV."""
    if DB.is_connected():
        if DB.load_character(name, char_type, p, s_tree):
            return   # loaded from Atlas

    # CSV fallback
    if not os.path.exists(PLAYER_FILE):
        return
    try:
        with open(PLAYER_FILE, 'r', newline='') as f:
            for row in csv.DictReader(f):
                if row.get("name") == name and row.get("char_type") == char_type:
                    def s_i(k, d):
                        try: return int(float(row[k])) if k in row and row[k].strip() else d
                        except: return d
                    def s_f(k, d):
                        try: return float(row[k]) if k in row and row[k].strip() else d
                        except: return d

                    p.money            = s_i("money", 0)
                    p.max_health       = s_f("max_health", 100.0)
                    p.attack_radius    = s_f("radius", 100.0)
                    p.speed            = s_f("speed", 1.3)
                    p.damage           = s_f("damage", 1.0)
                    p.projectile_count = s_i("multi", 1)
                    p.base_cooldown    = s_i("aspeed", 25)
                    p.max_energy       = s_f("max_energy", 10.0)
                    p.skill_points     = s_i("sp", 0)
                    p.magnet_range     = s_i("magnet", 60)
                    p.dash_unlocked    = bool(s_i("dash", 0))
                    p.armor            = s_f("armor", 0)
                    p.lifesteal        = s_f("lifesteal", 0)
                    p.crit_chance      = s_i("crit_chance", 0)
                    p.thorns           = s_i("thorns", 0)
                    p.regen            = s_f("regen", 0.0)
                    p.gold_modifier    = s_f("gold_modifier", 1.0)
                    p.energy           = p.max_energy
                    p.highscore        = s_i("highscore", 1)
                    for s in s_tree.skills:
                        s["level"] = s_i(f"skill_{s['id']}", 0)
                    s_tree.sync_with_player(p)
                    return
    except Exception as e:
        print(f"[CSV] load error: {e}")

def get_leaderboard(limit=6):
    """Fetch from MongoDB Atlas, fall back to CSV."""
    if DB.is_connected():
        result = DB.get_leaderboard(limit)
        if result:
            return result
    # CSV fallback
    entries = []
    if os.path.exists(PLAYER_FILE):
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                for row in csv.DictReader(f):
                    try: score = int(row.get("highscore", 0) or 0)
                    except: score = 0
                    entries.append((row.get("name", ""), row.get("char_type", ""), score))
        except: return []
    entries.sort(key=lambda e: e[2], reverse=True)
    return entries[:limit]

# funkcija get_dist_to_rect pieņem tuple tipa vērtību point un pygame.Rect tipa vērtību rect un atgriež float tipa vērtību distance
def get_dist_to_rect(point, rect):
    px = max(rect.left, min(point[0], rect.right))
    py = max(rect.top, min(point[1], rect.bottom))
    return math.hypot(point[0] - px, point[1] - py)


player = Player()

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

    # ── Heartbeat & session check (every ~5 s = 300 frames) ─────────────
    heartbeat_timer += 1
    if heartbeat_timer >= 300:
        heartbeat_timer = 0
        if user_name and DB.is_connected():
            DB.heartbeat_session(user_name)
            account_in_use = DB.is_session_active(user_name)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_delete_confirm:
                    show_delete_confirm = False
                    delete_confirm_password = ""
                    delete_confirm_pw_active = False
                    delete_confirm_error_msg = ""
                elif game_state == "playing":
                    # ESC during gameplay → pause (same as P key)
                    start_transition("dissolve")
                    game_state = "paused"
                elif game_state == "paused":
                    # ESC while paused → resume
                    start_transition("fade")
                    game_state = "playing"
                elif game_state == "skill_tree":
                    # ESC in skill tree → do nothing (player is in skill tree after death, can't resume)
                    pass
                elif game_state == "menu":
                    # ESC on login screen → go back to main menu
                    game_state = "main_menu"
                    user_name = ""
                    user_password = ""
                    input_field_active = None
                elif game_state == "char_select":
                    # ESC on char select → go back to login
                    game_state = "menu"
                elif game_state == "main_menu":
                    # ESC on main menu → quit cleanly
                    if user_name and player.char_type:
                        save_game_csv(user_name, player.char_type, player, skills, user_password)
                    DB.release_session(user_name)
                    pygame.quit(); sys.exit()
                # In all other states (dead, etc.) ESC is ignored to prevent crashes

            # ── Delete-confirm modal keyboard handling ────────────────────────
            if show_delete_confirm and delete_confirm_pw_active:
                if event.key == pygame.K_BACKSPACE:
                    delete_confirm_password = delete_confirm_password[:-1]
                    delete_confirm_error_msg = ""
                elif event.key == pygame.K_RETURN:
                    if check_password(user_name, delete_confirm_password):
                        if DB.is_connected():
                            DB.release_session(user_name)
                            DB.delete_account(user_name)
                        if os.path.exists(PLAYER_FILE):
                            try:
                                with open(PLAYER_FILE, 'r', newline='') as f:
                                    rows = [r for r in csv.DictReader(f)
                                            if r.get("name") != user_name]
                                if rows:
                                    with open(PLAYER_FILE, 'w', newline='') as f:
                                        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                                        writer.writeheader()
                                        writer.writerows(rows)
                                else:
                                    open(PLAYER_FILE, 'w').close()
                            except Exception as _del_e:
                                print(f"[CSV] delete_account error: {_del_e}")
                        user_name = ""; user_password = ""
                        delete_confirm_password = ""; delete_confirm_pw_active = False
                        delete_confirm_error_msg = ""
                        input_field_active = None
                        show_delete_confirm = False
                        game_state = "main_menu"
                    else:
                        delete_confirm_error_msg = "Wrong password!"
                        delete_confirm_error_timer = 120
                        delete_confirm_password = ""
                elif len(event.unicode) > 0 and len(delete_confirm_password) < 32:
                    delete_confirm_password += event.unicode
                    delete_confirm_error_msg = ""

            if game_state == "menu":
                if event.key == pygame.K_TAB:
                    # izveleties starp username un password laukiem ar TAB
                    if input_field_active == "username":
                        input_field_active = "password"
                    else:
                        input_field_active = "username"
                elif event.key == pygame.K_RETURN:
                    if user_name.strip() and user_password.strip():
                        uname = user_name.strip()
                        upass = user_password.strip()
                        if not player_exists_in_csv(uname):
                            if len(upass) < 4:
                                password_error_msg = "Password too short (min 4)!"
                                password_error_timer = 120
                            else:
                                # Create account in DB + CSV
                                if DB.is_connected():
                                    DB.create_account(uname, upass)
                                save_game_csv(uname, "wizard", player, skills, upass)
                                is_new_account = True
                                # Acquire session
                                if not DB.acquire_session(uname):
                                    password_error_msg = "Account in use on another PC!"
                                    password_error_timer = 180
                                else:
                                    account_in_use = False
                                    game_state = "char_select"
                                    password_error_msg = ""
                        else:
                            if check_password(uname, upass):
                                if not DB.acquire_session(uname):
                                    password_error_msg = "Account in use on another PC!"
                                    password_error_timer = 180
                                else:
                                    is_new_account = False
                                    account_in_use = False
                                    game_state = "char_select"
                                    password_error_msg = ""
                            else:
                                password_error_msg = "Wrong password!"
                                password_error_timer = 120
                                user_password = ""
                    else:
                        password_error_msg = "Please fill both fields!"
                        password_error_timer = 120
                elif event.key == pygame.K_BACKSPACE:
                    if input_field_active == "username":
                        user_name = user_name[:-1]
                    elif input_field_active == "password":
                        user_password = user_password[:-1]
                    elif lb_search_active:
                        lb_search_text = lb_search_text[:-1]
                        lb_search_result = ""
                elif event.key == pygame.K_RETURN:
                    if lb_search_active and lb_search_text.strip():
                        query = lb_search_text.strip()
                        found = False
                        # ── Try DB first (searches ALL entries, no limit) ──────
                        if DB.is_connected():
                            hit = DB.search_leaderboard(query)
                            if hit:
                                rank, nm, ct, sc = hit
                                lb_search_result = f"#{rank}  {nm} ({ct})  Wave {sc}"
                                found = True
                        # ── CSV fallback: scan entire file ───────────────────
                        if not found and os.path.exists(PLAYER_FILE):
                            try:
                                csv_entries = []
                                with open(PLAYER_FILE, 'r', newline='') as f:
                                    for row in csv.DictReader(f):
                                        try: sc = int(row.get("highscore", 0) or 0)
                                        except: sc = 0
                                        csv_entries.append((row.get("name",""), row.get("char_type",""), sc))
                                csv_entries.sort(key=lambda e: e[2], reverse=True)
                                for rank, (nm, ct, sc) in enumerate(csv_entries, 1):
                                    if nm.lower() == query.lower():
                                        lb_search_result = f"#{rank}  {nm} ({ct})  Wave {sc}"
                                        found = True
                                        break
                            except Exception:
                                pass
                        if not found:
                            lb_search_result = f'"{query}" not found'
                else:
                    if len(event.unicode) > 0:
                        if lb_search_active:
                            if len(lb_search_text) < 24:
                                lb_search_text += event.unicode
                                lb_search_result = ""
                        else:
                            if not input_field_active:
                                input_field_active = "username"
                            if input_field_active == "username" and len(user_name) < 24:
                                user_name += event.unicode
                            elif input_field_active == "password" and len(user_password) < 24:
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

        elif MUSIC_END_EVENT is not None and event.type == MUSIC_END_EVENT:
            if bg_music_files:
                current_music_index = (current_music_index + 1) % len(bg_music_files)
                play_current_bg_music()

        if event.type == pygame.MOUSEBUTTONDOWN:
            # 1. Prioritāte: Delete Confirm (Bloķē visu)
            if show_delete_confirm:
                confirm_btn_r, cancel_btn_r, del_pw_rect = _delete_confirm_rects
                if confirm_btn_r.collidepoint(event.pos):
                    # ── Validate password before deleting ────────────────────
                    if not check_password(user_name, delete_confirm_password):
                        delete_confirm_error_msg = "Wrong password!"
                        delete_confirm_error_timer = 120
                        delete_confirm_password = ""
                    else:
                        # ── Actually delete the account ───────────────────────
                        if DB.is_connected():
                            DB.release_session(user_name)
                            DB.delete_account(user_name)
                        if os.path.exists(PLAYER_FILE):
                            try:
                                with open(PLAYER_FILE, 'r', newline='') as f:
                                    rows = [r for r in csv.DictReader(f)
                                            if r.get("name") != user_name]
                                if rows:
                                    with open(PLAYER_FILE, 'w', newline='') as f:
                                        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                                        writer.writeheader()
                                        writer.writerows(rows)
                                else:
                                    open(PLAYER_FILE, 'w').close()
                            except Exception as _del_e:
                                print(f"[CSV] delete_account error: {_del_e}")
                        user_name = ""
                        user_password = ""
                        delete_confirm_password = ""
                        delete_confirm_pw_active = False
                        delete_confirm_error_msg = ""
                        input_field_active = None
                        show_delete_confirm = False
                        game_state = "main_menu"
                elif cancel_btn_r.collidepoint(event.pos):
                    show_delete_confirm = False
                    delete_confirm_password = ""
                    delete_confirm_pw_active = False
                    delete_confirm_error_msg = ""
                elif del_pw_rect.collidepoint(event.pos):
                    delete_confirm_pw_active = True
                else:
                    delete_confirm_pw_active = False
                continue  # block all other clicks while modal is open

            # 2. Prioritāte: Settings BACK poga
            if show_settings:
                if settings_buttons and settings_buttons.get('back').collidepoint(event.pos):
                    show_settings = False
                continue  # All other clicks handled inside draw_settings_overlay via mouse state

            # ── Per-state click handling ──────────────────────────────────────
            if game_state == "main_menu":
                if play_btn.collidepoint(event.pos):
                    game_state = "menu"
                    user_name = ""; user_password = ""; input_field_active = None
                elif settings_btn.collidepoint(event.pos):
                    show_settings = True
                elif quit_btn.collidepoint(event.pos):
                    pygame.quit(); sys.exit()

            elif game_state == "menu":
                if user_input_rect.collidepoint(event.pos):
                    input_field_active = "username"
                    lb_search_active = False
                elif pass_input_rect.collidepoint(event.pos):
                    input_field_active = "password"
                    lb_search_active = False
                elif lb_search_rect.collidepoint(event.pos):
                    lb_search_active = True
                    input_field_active = None
                elif user_clear_btn and user_clear_btn.collidepoint(event.pos):
                    game_state = "main_menu"
                    user_name = ""; user_password = ""; input_field_active = None
                else:
                    lb_search_active = False
                    input_field_active = None
                    # Check delete account button
                    if delete_account_btn.collidepoint(event.pos):
                        show_delete_confirm = True

            elif game_state == "paused":
                if pause_save_btn.collidepoint(event.pos):
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    trigger_save_anim("GAME SAVED!")
                elif pause_resume_btn.collidepoint(event.pos):
                    start_transition("fade")
                    game_state = "playing"
                elif pause_quit_btn.collidepoint(event.pos):
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    DB.release_session(user_name)
                    game_state = "menu"
                    user_name = ""; user_password = ""
                    player = Player()
                    for skill_node in skills.skills:
                        skill_node["level"] = 0; skill_node["cost"] = skill_node["base_cost"]

            elif game_state == "char_select":
                for i in range(3):
                    rect = pygame.Rect(screen_w // 2 - 450 + (i * 310), 200, 280, 400)
                    if rect.collidepoint(event.pos):
                        sel = ["wizard", "shadow", "dwarf"][i]
                        player.setup_class(sel)
                        if is_new_account:
                            save_game_csv(user_name, sel, player, skills, user_password)
                        load_game_csv(user_name, sel, player, skills)
                        enemies.clear(); bosses.clear(); projectiles.clear()
                        coins.clear(); chests.clear(); active_swings.clear()
                        current_wave, max_enemies, time_freeze_timer = 1, 4, 0
                        for _ in range(max_enemies): spawn_enemy()
                        game_state = "playing"

            elif game_state == "skill_tree":
                result = skills.handle_click(event.pos, player)
                if result == "respawn":
                    saved_money = player.money
                    saved_char = player.char_type
                    player.setup_class(saved_char)
                    player.health = player.max_health
                    player.energy = player.max_energy
                    player.money = saved_money
                    player.boss_drops = []
                    skills.sync_with_player(player)
                    enemies.clear(); bosses.clear(); projectiles.clear()
                    current_wave, max_enemies = 1, 4
                    game_state = "playing"
                elif result == "saved":
                    save_game_csv(user_name, player.char_type, player, skills, user_password)
                    trigger_save_anim("UPGRADED!")


    # --- MAIN MENU ---
    if game_state == "main_menu":
        play_btn, settings_btn, quit_btn = draw_main_menu(
            screen, screen_w, screen_h, menu_bg, menu_logo, play_img, settings_img, quit_img)

    # --- SETTINGS OVERLAY (drawn on top of current screen) ---
    if show_settings and game_state != "playing":
        _mouse_btn = pygame.mouse.get_pressed()[0]   # True while left button held
        res = draw_settings_overlay(
            screen, screen_w, screen_h, music_volume, sfx_volume, back_img,
            mouse_pos=m_pos,
            mouse_down=_mouse_btn,
            mouse_up=False,   # menu_screen.py handles release via _dragging_slider check
        )
        music_volume    = res['music_volume']
        sfx_volume      = res['sfx_volume']
        settings_buttons = res
        pygame.mixer.music.set_volume(music_volume / 100.0)
    # --- MENU + LOGIN/REGISTER (MERGED) ---
    elif game_state == "menu":
        user_input_rect, pass_input_rect, user_clear_btn, pass_clear_btn = draw_login_screen(
            screen, screen_w, screen_h, menu_bg, user_name, user_password,
            input_field_active, password_error_msg, password_error_timer,
            menu_logo, login_img, back_img)

        # ── Delete account button ───────────────────────────────────────────
        if user_name:
            delete_account_btn = pygame.Rect(screen_w // 2 - 100, screen_h // 2 + 255, 200, 36)
            pygame.draw.rect(screen, (80, 20, 20), delete_account_btn, border_radius=8)
            pygame.draw.rect(screen, (200, 50, 50), delete_account_btn, 2, border_radius=8)
            del_txt = render_pixel_text("DELETE ACCOUNT", 13, (255, 120, 120), bold=True)
            screen.blit(del_txt, del_txt.get_rect(center=delete_account_btn.center))
        else:
            delete_account_btn = pygame.Rect(0, 0, 0, 0)

        # ── Leaderboard ─────────────────────────────────────────────────────
        leaderboard = get_leaderboard(6)
        lb_x = screen_w - 420
        lb_y = screen_h // 4 - 40
        lb_w, lb_h = 400, 390
        lb_search_rect = draw_leaderboard(
            screen, leaderboard, lb_x, lb_y, lb_w, lb_h,
            search_text=lb_search_text,
            search_active=lb_search_active,
            search_result=lb_search_result)

        # Draw delete confirm modal if active
        if show_delete_confirm:
            if delete_confirm_error_timer > 0:
                delete_confirm_error_timer -= 1
            _delete_confirm_rects = draw_delete_confirm(
                screen, screen_w, screen_h,
                delete_password=delete_confirm_password,
                delete_pw_active=delete_confirm_pw_active,
                delete_error_msg=delete_confirm_error_msg,
                delete_error_timer=delete_confirm_error_timer)
        else:
            _delete_confirm_rects = (pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0))

    # --- VAROŅA IZVĒLE ---
    elif game_state == "char_select":
        if char_select_bg:
            screen.blit(char_select_bg, (0, 0))
        else:
            screen.fill((10, 10, 20))

        # Tumšais pārklājums fonam
        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title = render_pixel_text("CHOOSE YOUR CHARACTER", 44, (255, 255, 255), bold=True)
        screen.blit(title, (screen_w // 2 - title.get_width() // 2, 80))

        # Definējam klases (img šeit ir tēla sprites, nevis rāmis)
        classes = [("WIZARD", (0, 200, 255), wizard_ui), 
                   ("SHADOW", (150, 0, 255), shadow_ui), 
                   ("DWARF", (255, 150, 0), dwarf_ui)]

        for i, (name, col, img) in enumerate(classes):      
            # Kartītes novietojums
            rect = pygame.Rect(screen_w // 2 - 450 + (i * 310), 200, 280, 400)
            is_hovered = rect.collidepoint(m_pos)
            
            # 1. Zīmējam "char_select.png" kā kartītes fonu
            if char_card_img:
                screen.blit(char_card_img, rect.topleft)
            else:
                # Rezerves variants, ja bilde pazūd
                pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=15)

            # 2. Zīmējam izgaismojumu (hover), ja pele ir virsū


            # 3. Zīmējam pašu tēlu (virsū fonam)
            # Ja is_hovered, tēls nedaudz "peld" uz augšu
            offset_y = -10 if is_hovered else 0
            char_rect = img.get_rect(center=(rect.centerx, rect.centery - 20 + offset_y))
            screen.blit(img, char_rect)

            # 4. Tēla vārds
            name_col = (255, 255, 255) if is_hovered else col
            name_t = render_pixel_text(name, 24, name_col, bold=True)
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
            # Auto-save mid-game on wave clear
            save_game_csv(user_name, player.char_type, player, skills, user_password)

        player.move(pygame.key.get_pressed())
        player.rect.clamp_ip(screen.get_rect())

        # Check for kill key (hold K for 3 seconds to kill player)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_k]:
            kill_hold_timer += 1
            if kill_hold_timer >= KILL_HOLD_DURATION:
                player.health = 0
                kill_hold_timer = 0  # Reset timer after death
        else:
            kill_hold_timer = 0
        
        player.kill_mode = kill_hold_timer > 0
        player.kill_timer = kill_hold_timer
        player.kill_duration = KILL_HOLD_DURATION

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
            # Ģenerējam pozīciju pirms objekta izveides
            drop_x = random.randint(100, screen_w - 100)
            drop_y = random.randint(100, screen_h - 100)
            
            # Izveidojam monētu (pārliecinies, ka tavā klasē __init__(self, x, y) pieņem šos mainīgos)
            hc = HpCoin(drop_x, drop_y) 
            hp_drops.append(hc)

        for h in hp_drops[:]:
            # 1. Aprēķinām attālumu
            dist = math.hypot(player.rect.centerx - h.rect.centerx, player.rect.centery - h.rect.centery)
            
            # 2. Magnēta loģika (pārvietojam, ja ir rādiusā)
            if dist < player.magnet_range:
                # Reizinātājs 0.1 ir labs, tas liek monētai "pievilkties" plūstoši
                h.posx += (player.rect.centerx - h.rect.centerx) * 0.1
                h.posy += (player.rect.centery - h.rect.centery) * 0.1
                h.rect.x = int(h.posx)
                h.rect.y = int(h.posy)
            
            # 3. Zīmējam (izmantojam 'screen' vai 'surface', kā tev definēts)
            h.draw(screen)
            
            # 4. Sadursme
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
                # Dwarf maintains continuous spinning axes
                # Check if dwarf already has a swing active
                dwarf_swing_exists = any(s.is_dwarf for s in active_swings)
                if not dwarf_swing_exists:
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
            # Update dwarf swings with current enemies
            if s.is_dwarf:
                s.enemies = enemies + bosses
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
                    player.trigger_damage_flash()
                    if getattr(player, 'thorns', 0) > 0: e.health -= player.thorns
            e.draw(screen)
            if e.health <= 0:
                enemies.remove(e); player.money += 2; boss_energy += 10
                # Soul Drain: wizard gains a tiny amount of energy per kill
                soul_lvl = getattr(player, 'soul_drain_lvl', 0)
                if soul_lvl > 0 and player.char_type == "wizard":
                    player.energy = min(player.max_energy, player.energy + 0.15 * soul_lvl)

        for b in bosses[:]:
            if time_freeze_timer <= 0:
                # Saglabājam izšauto ugunsbumbu damage mainīgajā 'boss_projectile_dmg'
                boss_projectile_dmg = b.update(player.rect, dilation)
                
                # Ja mēs saņēmam saapi no ugunsbumbas, atņemam dzīvību (ņemot vērā bruņas)
                if boss_projectile_dmg and boss_projectile_dmg > 0:
                    player.health -= max(1, boss_projectile_dmg - getattr(player, 'armor', 0))
                    player.trigger_damage_flash()
                    
                # Pieskaršanās bojājumi joprojām strādā!
                if player.rect.colliderect(b.rect):
                    player.health -= max(0.1, 0.8 - (getattr(player, 'armor', 0) * 0.05))
                    player.trigger_damage_flash()
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
        # Snap to nearest 10px so cache stays tiny (avoids new surface every frame from pulse)
        light_radius = max(10, round(int(player.attack_radius * 1.4) / 10) * 10)
        
        if not hasattr(player, 'glow_cache'):
            player.glow_cache = {}
            
        if light_radius not in player.glow_cache:
            t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
            core_radius = max(1, light_radius // 2)
            pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), core_radius)
            for r in range(light_radius, core_radius, -3):
                alpha = max(0, min(255, int(255 * (1 - (r - core_radius) / max(1, light_radius - core_radius)))))
                pygame.draw.circle(t_surf, (0, 0, 0, alpha), (light_radius, light_radius), r)
            player.glow_cache[light_radius] = t_surf
            
        t_surf = player.glow_cache[light_radius]
        
        shroud.blit(t_surf, t_surf.get_rect(center=player.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(shroud, (0, 0))
        # --- LIETOTĀJA SASKARNE (UI) ---
        if nuke_flash_timer > 0:
            flash = pygame.Surface((screen_w, screen_h)); flash.fill((255, 255, 255))
            flash.set_alpha(int((nuke_flash_timer / 15) * 255)); screen.blit(flash, (0, 0))
        player.draw_damage_flash(screen)
        # ── Red vignette damage indicator ─────────────────────────────────
        _dmg_flash = getattr(player, 'damage_flash_timer', 0)
        if _dmg_flash > 0:
            _vign_alpha = int(180 * (_dmg_flash / max(1, getattr(player, 'damage_flash_duration', 20))))
            _vign_depth = 50   # how many px the shadow bleeds inward from each edge
            _vign_surf  = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            # Four gradient strips: top, bottom, left, right
            for _step in range(_vign_depth):
                _edge_alpha = int(_vign_alpha * (1.0 - _step / _vign_depth) ** 1.8)
                _col = (200, 0, 0, _edge_alpha)
                # top strip
                pygame.draw.line(_vign_surf, _col, (0, _step), (screen_w, _step))
                # bottom strip
                pygame.draw.line(_vign_surf, _col, (0, screen_h - 1 - _step), (screen_w, screen_h - 1 - _step))
                # left strip
                pygame.draw.line(_vign_surf, _col, (_step, 0), (_step, screen_h))
                # right strip
                pygame.draw.line(_vign_surf, _col, (screen_w - 1 - _step, 0), (screen_w - 1 - _step, screen_h))
            screen.blit(_vign_surf, (0, 0))
        if time_freeze_timer > 0:
            screen.blit(freeze_surf, (0, 0))

        ui_f = 22  # Font size for pixelated UI
        screen.blit(render_pixel_text(f"Money: ${player.money} | SP: {player.skill_points}", ui_f, (255, 215, 0), bold=True), (20, 20))
        screen.blit(render_pixel_text(f"Wave: {current_wave} [Best: {player.highscore}]", ui_f, (200, 200, 255), bold=True), (20, 50))
        screen.blit(render_pixel_text(f"ID: {user_name}", ui_f, (200, 200, 255), bold=True), (20, 80))
        bar_x, bar_y = screen_w // 2 - 100, screen_h - 55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10))
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, (player.energy / player.max_energy) * 200), 10))
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health / player.max_health) * 200), 15))

        # --- STATS PANEL (Right side) ---
        stats_font_size = 14
        stats_x = screen_w - 220
        stats_y = 20
        stats_bg = pygame.Surface((200, 190), pygame.SRCALPHA)
        stats_bg.fill((20, 20, 40, 200))
        pygame.draw.rect(stats_bg, (0, 150, 200), (0, 0, 200, 190), 2) 
        screen.blit(stats_bg, (stats_x, stats_y))
        
        stats_list = [
            f"DMG: {int(player.damage)}",
            f"SPD: {player.speed:.1f}",
            f"RANGE: {int(player.attack_radius)}",
            f"ARMOR: {getattr(player, 'armor', 0):.1f}",
            f"LIFESTEAL: {getattr(player, 'lifesteal', 0):.1f}",
            f"CRIT CHANCE: {getattr(player, 'crit_chance', 0)}%",
            f"MAGNET RANGE: {int(player.magnet_range)}",
            f"DASH: {'YES' if getattr(player, 'dash_unlocked', False) else 'NO'}",
            f"HEALTH: {int(player.health)}/{int(player.max_health)}"
        ]
        
        for i, stat in enumerate(stats_list):
            stat_text = render_pixel_text(stat, stats_font_size, (100, 255, 200))
            screen.blit(stat_text, (stats_x + 10, stats_y + 10 + i * 20))

        if save_notification_timer > 0:
            t = render_pixel_text(save_notification_msg, UI_NORMAL, (0, 255, 150), bold=True)
            screen.blit(t, t.get_rect(center=(screen_w // 2, 100)))
            save_notification_timer -= 1

        if boss_drop_timer > 0:
            # Big glowing boss drop notification
            alpha = int(255 * (boss_drop_timer / 180))
            drop_text = render_pixel_text(boss_drop_msg, GAME_SCORE, (255, 215, 0), bold=True)
            
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
        pause_save_btn, pause_resume_btn, pause_quit_btn = draw_pause_menu(screen, screen_w, screen_h, pause_bg)

    elif game_state == "dead":
        draw_death_screen(screen, screen_w, screen_h, death_timer)
        death_timer -= 1
        if death_timer <= 0:
            player.setup_class(player.char_type)
            skills.sync_with_player(player)
            player.boss_drops = []
            # Auto-save to Atlas when entering skill tree
            save_game_csv(user_name, player.char_type, player, skills, user_password)
            game_state = "skill_tree"

    elif game_state == "skill_tree":
        skills.draw(screen, player.money, player.skill_points, player.char_type)
        if save_notification_timer > 0:
            t = render_pixel_text(save_notification_msg, UI_NORMAL, (0, 255, 150), bold=True)
            screen.blit(t, t.get_rect(center=(screen_w // 2, 40)))
            save_notification_timer -= 1

    # Render cinematic transition effects
    render_transition(screen)

    # ── Account-in-use warning banner ───────────────────────────────────
    if account_in_use:
        warn_txt = render_pixel_text("ACCOUNT IN USE ON ANOTHER PC", 18, (255, 60, 60), bold=True)
        warn_bg  = pygame.Surface((warn_txt.get_width() + 20, warn_txt.get_height() + 8), pygame.SRCALPHA)
        warn_bg.fill((20, 0, 0, 200))
        screen.blit(warn_bg, (screen_w // 2 - warn_bg.get_width() // 2, screen_h - 30))
        screen.blit(warn_txt, warn_txt.get_rect(center=(screen_w // 2, screen_h - 22)))

    pygame.display.flip()
    clock.tick(60)