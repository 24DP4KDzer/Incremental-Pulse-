import pygame
import sys
import random
import csv
import os
import math
from player import Player
from enemy import Enemy
from action import Coin, SpecialCoin, HpCoin
from projectile import Projectile
from skill_tree import SkillTree
from boss import Boss

# 1. INITIALIZATION
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_w, screen_h = screen.get_size()
pygame.display.set_caption("Pulse: Evolution")
clock = pygame.time.Clock()

# 2. SAVE/LOAD SYSTEM
PLAYER_FILE = "data/players.csv"
if not os.path.exists("data"): 
    os.makedirs("data")

save_notification_timer = 0
save_notification_msg = ""
current_wave = 1

def trigger_save_anim(msg):
    global save_notification_timer, save_notification_msg
    save_notification_timer = 90
    save_notification_msg = msg

def save_game_csv(name, char_type, p, s_tree):
    p_rows = []
    if os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE, 'r', newline='') as f:
            p_rows = list(csv.DictReader(f))
    
    current_record = getattr(p, 'highscore', 1)
    if globals().get('current_wave', 1) > current_record:
        p.highscore = globals().get('current_wave', 1)

    new_p_data = {
        "name": name, "char_type": char_type, "money": p.money, 
        "max_health": p.max_health, "radius": p.attack_radius, 
        "speed": p.speed, "damage": getattr(p, 'damage', 1.0),
        "multi": getattr(p, 'projectiles_count', 1),
        "aspeed": getattr(p, 'base_cooldown', 25),
        "max_energy": getattr(p, 'max_energy', 10.0),
        "sp": getattr(p, 'skill_points', 0),
        "magnet": getattr(p, 'magnet_range', 60),
        "dash": int(getattr(p, 'dash_unlocked', False)),
        "highscore": getattr(p, 'highscore', 1)
    }
    
    found_p = False
    for i, row in enumerate(p_rows):
        if row["name"] == name and row["char_type"] == char_type:
            p_rows[i] = new_p_data
            found_p = True
            break
    if not found_p: p_rows.append(new_p_data)
    
    with open(PLAYER_FILE, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(new_p_data.keys()))
        writer.writeheader()
        writer.writerows(p_rows)

def load_game_csv(name, char_type, p, s_tree):
    if os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["name"] == name and row["char_type"] == char_type:
                    def s_i(k, d): return int(row[k]) if row.get(k) and row[k].strip() else d
                    def s_f(k, d): return float(row[k]) if row.get(k) and row[k].strip() else d
                    p.money = s_i("money", 0)
                    p.max_health = s_f("max_health", 100.0)
                    p.attack_radius = s_f("radius", 100.0)
                    p.speed = s_f("speed", 1.3)
                    p.damage = s_f("damage", 1.0)
                    p.projectiles_count = s_i("multi", 1)
                    p.base_cooldown = s_i("aspeed", 25)
                    p.max_energy = s_f("max_energy", 10.0)
                    p.skill_points = s_i("sp", 0)
                    p.magnet_range = s_i("magnet", 60)
                    p.dash_unlocked = bool(s_i("dash", 0))
                    p.energy = p.max_energy
                    p.highscore = s_i("highscore", 1)
                    s_tree.sync_with_player(p)

# 3. SPRITES (Main Menu / Selection only)
def load_sprite(path, size=(320, 320)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255)) 
        return surf

# Pre-loading for the Character Select screen
wizard_ui = load_sprite("photos/pixil-frame-going-right.png") 
shadow_ui = load_sprite("photos/wizard_left.png") 
dwarf_ui = load_sprite("photos/pixil-frame-going-up.png")

class Chest:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(200, screen_w-200), random.randint(200, screen_h-200), 40, 40)
    def draw(self, surf):
        pygame.draw.rect(surf, (255, 215, 0), self.rect, border_radius=8)
        pygame.draw.rect(surf, (255, 255, 255), self.rect, 2, border_radius=8)

# 4. GAME OBJECTS
game_state, user_name = "menu", ""
player = Player()
skills = SkillTree(screen_w, screen_h)
bosses, enemies, projectiles, coins, chests = [], [], [], [], []
boss_energy, boss_goal, max_enemies = 0, 100, 4

darkness_surf = pygame.Surface((screen_w, screen_h))
darkness_surf.fill((0, 0, 0))

def spawn_enemy(hp_m=1.0, spd_m=1.0):
    e = Enemy(random.randint(0, screen_w), random.randint(0, screen_h))
    e.max_health = int(e.max_health * hp_m)
    e.health = e.max_health
    e.speed = min(3.5, e.speed * spd_m)
    enemies.append(e)

def spawn_coin():
    c = Coin()
    c.rect.x, c.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    coins.append(c)

# --- MAIN LOOP ---
while True:
    screen.fill((5, 5, 10))
    m_pos, m_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit(); sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if user_name and player.char_type: save_game_csv(user_name, player.char_type, player, skills)
                pygame.quit(); sys.exit()
            
            if game_state == "menu":
                if event.key == pygame.K_RETURN and user_name.strip(): game_state = "char_select"
                elif event.key == pygame.K_BACKSPACE: user_name = user_name[:-1]
                else: user_name += event.unicode
            
            elif game_state == "char_select":
                sel = None
                if event.key == pygame.K_1: sel = "wizard"
                elif event.key == pygame.K_2: sel = "shadow"
                elif event.key == pygame.K_3: sel = "dwarf"
                if sel:
                    player.setup_class(sel)
                    load_game_csv(user_name, sel, player, skills)
                    enemies.clear(); bosses.clear(); projectiles.clear(); coins.clear(); chests.clear()
                    current_wave, max_enemies = 1, 4
                    for _ in range(max_enemies): spawn_enemy()
                    game_state = "playing"
            
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                if player.dash_unlocked and player.dash_cooldown <= 0:
                    k = pygame.key.get_pressed()
                    dx, dy = 0, 0
                    if k[pygame.K_w]: dy = -130
                    if k[pygame.K_s]: dy = 130
                    if k[pygame.K_a]: dx = -130
                    if k[pygame.K_d]: dx = 130
                    if dx != 0 or dy != 0:
                        player.rect.x += dx
                        player.rect.y += dy
                        player.dash_cooldown = 100 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "skill_tree":
                res = skills.handle_click(event.pos, player)
                if res:
                    save_game_csv(user_name, player.char_type, player, skills)
                    if res == "respawn":
                        player.health, player.energy = player.max_health, player.max_energy
                        enemies.clear(); bosses.clear(); projectiles.clear(); coins.clear(); chests.clear()
                        current_wave, max_enemies = 1, 4
                        for _ in range(max_enemies): spawn_enemy()
                        game_state = "playing"

    if game_state == "menu":
        title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 255, 150))
        screen.blit(title, title.get_rect(center=(screen_w//2, screen_h//2 - 50)))
        u_txt = pygame.font.SysFont("Arial", 30).render(f"User: {user_name}|", True, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=(screen_w//2, screen_h//2 + 50)))

    elif game_state == "char_select":
        title = pygame.font.SysFont("Impact", 60).render("SELECT CHARACTER", True, (255, 255, 255))
        screen.blit(title, (screen_w//2 - title.get_width()//2, 100))
        classes = [("1. WIZARD", (0, 200, 255), wizard_ui), ("2. SHADOW", (150, 0, 255), shadow_ui), ("3. DWARF", (255, 150, 0), dwarf_ui)]
        for i, (name, col, img) in enumerate(classes):
            rect = pygame.Rect(screen_w//2 - 450 + (i * 320), 250, 250, 350)
            pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=15)
            pygame.draw.rect(screen, col, rect, 3, border_radius=15)
            screen.blit(img, (rect.centerx - 40, rect.y + 50)) 
            name_t = pygame.font.SysFont("Arial", 28, bold=True).render(name, True, col)
            screen.blit(name_t, name_t.get_rect(center=(rect.centerx, rect.y + 300)))

    elif game_state == "playing":
        # --- LOGIC ---
        player.energy -= 1/60 
        if player.energy <= 0: player.health = 0
        if player.dash_cooldown > 0: player.dash_cooldown -= 1

        if not enemies and not bosses:
            current_wave += 1
            max_enemies += 2
            for _ in range(max_enemies): spawn_enemy(1.0 + (current_wave*0.1), 1.0 + (current_wave*0.02))
            if current_wave % 2 == 0: chests.append(Chest())
            trigger_save_anim(f"WAVE {current_wave}")

        player.move(pygame.key.get_pressed())
        player.rect.clamp_ip(screen.get_rect())

        while len(coins) < 5: spawn_coin()
        
        # Magnet Logic
        for c in coins:
            dist = math.hypot(player.rect.centerx - c.rect.centerx, player.rect.centery - c.rect.centery)
            if dist < player.magnet_range:
                c.rect.x += (player.rect.centerx - c.rect.centerx) * 0.1
                c.rect.y += (player.rect.centery - c.rect.centery) * 0.1

        for c in coins[:]:
            c.draw(screen)
            if player.rect.colliderect(c.rect):
                player.money += 1; player.energy = min(player.max_energy, player.energy + 1.2)
                coins.remove(c)

        for ch in chests[:]:
            ch.draw(screen)
            if player.rect.colliderect(ch.rect):
                player.energy = player.max_energy
                trigger_save_anim("MAX ENERGY!")
                chests.remove(ch)

        # Combat Logic
        if m_click[0] and player.attack_cooldown <= 0:
            targets = [e for e in (enemies + bosses) if pygame.math.Vector2(player.rect.center).distance_to(e.rect.center) < player.attack_radius]
            targets.sort(key=lambda t: pygame.math.Vector2(player.rect.center).distance_to(t.rect.center))
            if targets:
                for i in range(min(len(targets), player.projectiles_count)):
                    projectiles.append(Projectile(player.rect.centerx, player.rect.centery, targets[i], player.color, player.attack_radius * 1.5))
                player.attack_cooldown = player.base_cooldown

        for p in projectiles[:]:
            if p.update(enemies + bosses):
                p.draw(screen)
                if p.rect.colliderect(p.target.rect):
                    p.target.health -= player.damage
                    if p in projectiles: projectiles.remove(p)
            else: 
                if p in projectiles: projectiles.remove(p)

        for e in enemies[:]:
            e.update(player.rect); e.draw(screen)
            if e.health <= 0: 
                enemies.remove(e); player.money += 2; boss_energy += 10
            elif player.rect.colliderect(e.rect): player.health -= 0.3
            
        for b in bosses[:]:
            b.update(player.rect); b.draw(screen)
            if b.health <= 0: 
                bosses.remove(b); player.money += 50; player.skill_points += 1; trigger_save_anim("+1 SP!")
            elif player.rect.colliderect(b.rect): player.health -= 0.8

        if boss_energy >= boss_goal:
            bosses.append(Boss(screen_w, screen_h))
            boss_energy = 0

        # --- DRAWING ---
        player.draw(screen)

        # Dash Bar
        if player.dash_cooldown > 0:
            pygame.draw.rect(screen, (40, 40, 40), (player.rect.x, player.rect.bottom + 5, 60, 4))
            w = 60 * (1 - (player.dash_cooldown / 100))
            pygame.draw.rect(screen, (0, 200, 255), (player.rect.x, player.rect.bottom + 5, w, 4))

        # Darkness Effect
        energy_ratio = player.energy / player.max_energy
        if energy_ratio < 0.4:
            darkness_surf.set_alpha(int((1 - energy_ratio) * 160))
            screen.blit(darkness_surf, (0,0))

        # UI
        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        screen.blit(ui_f.render(f"WAVE: {current_wave} (BEST: {player.highscore})", True, (200, 200, 255)), (20, 50))
        
        # Bottom Center Bars
        bar_x, bar_y = screen_w//2-100, screen_h-55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10)) # Energy BG
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, energy_ratio * 200), 10)) # Energy FG
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15)) # Health BG
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health/player.max_health)*200), 15)) # Health FG

        if player.health <= 0:
            save_game_csv(user_name, player.char_type, player, skills)
            game_state, death_timer = "dead", 120
        if player.attack_cooldown > 0: player.attack_cooldown -= 1

    elif game_state == "dead":
        msg = pygame.font.SysFont("Impact", 100).render("OUT OF TIME", True, (255, 0, 0))
        screen.blit(msg, msg.get_rect(center=(screen_w//2, screen_h//2)))
        death_timer -= 1
        if death_timer <= 0: game_state = "skill_tree"

    elif game_state == "skill_tree":
        skills.draw(screen, player.money, player.skill_points)
        if save_notification_timer > 0:
            t = pygame.font.SysFont("Arial", 22, bold=True).render(save_notification_msg, True, (0, 255, 150))
            screen.blit(t, t.get_rect(center=(screen_w // 2, 40)))
            save_notification_timer -= 1

    pygame.display.flip()
    clock.tick(60)