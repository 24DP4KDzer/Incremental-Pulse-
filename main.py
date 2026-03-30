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

# --- UPDATED CLASS: SPINNING MELEE SWING ---
class MeleeSwing:
    def __init__(self, owner, color):
        self.owner = owner
        self.color = color
        self.angle = 0
        # Use the player's rotation_speed if it exists, otherwise default to 15
        self.spin_speed = getattr(owner, 'rotation_speed', 15) 
        self.radius = owner.attack_radius
        self.lifetime = 360 // self.spin_speed 
        self.hit_enemies = [] 
        # ... rest of __init__ remains the same

        # Axe Image Placeholder
        self.surface = pygame.Surface((70, 35), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, (100, 50, 0), (0, 12, 50, 10)) # Handle
        pygame.draw.rect(self.surface, (200, 200, 200), (45, 0, 25, 35)) # Blade head

    def update(self, enemies, damage):
        self.angle += self.spin_speed
        self.lifetime -= 1
        
        # Calculate current position of the axe head for collision
        rad = math.radians(self.angle)
        axe_x = self.owner.rect.centerx + math.cos(rad) * self.radius
        axe_y = self.owner.rect.centery + math.sin(rad) * self.radius
        axe_rect = pygame.Rect(axe_x - 25, axe_y - 25, 50, 50)

        # Collision with ALL enemies (CLEAVE logic)
        for e in enemies:
            if e not in self.hit_enemies and axe_rect.colliderect(e.rect):
                e.health -= damage
                self.hit_enemies.append(e)

    def draw(self, surface):
        rotated_axe = pygame.transform.rotate(self.surface, -self.angle)
        rad = math.radians(self.angle)
        pos_x = self.owner.rect.centerx + math.cos(rad) * self.radius
        pos_y = self.owner.rect.centery + math.sin(rad) * self.radius
        rect = rotated_axe.get_rect(center=(pos_x, pos_y))
        surface.blit(rotated_axe, rect)

def trigger_save_anim(msg):
    global save_notification_timer, save_notification_msg
    save_notification_timer = 90
    save_notification_msg = msg

def save_game_csv(name, char_type, p, s_tree):
    p_rows = []
    if os.path.exists(PLAYER_FILE):
        with open(PLAYER_FILE, 'r', newline='') as f:
            p_rows = list(csv.DictReader(f))
    
    if globals().get('current_wave', 1) > getattr(p, 'highscore', 1):
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

def get_dist_to_rect(point, rect):
    px = max(rect.left, min(point[0], rect.right))
    py = max(rect.top, min(point[1], rect.bottom))
    return math.hypot(point[0] - px, point[1] - py)

# 3. SPRITES & OBJECTS
def load_sprite(path, size=(280, 280)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255)) 
        return surf

wizard_ui = load_sprite("photos/pixil-frame-going-right.png") 
shadow_ui = load_sprite("photos/wizard_left.png") 
dwarf_ui = load_sprite("photos/pixil-frame-going-up.png")

class Chest:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(100, screen_w-100), random.randint(100, screen_h-100), 40, 40)
        self.color = (255, 215, 0)
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

game_state, user_name = "menu", ""
player = Player()
skills = SkillTree(screen_w, screen_h)
bosses, enemies, projectiles, coins, chests, active_swings = [], [], [], [], [], []
boss_energy, boss_goal, max_enemies = 0, 100, 4
time_freeze_timer = 0
nuke_flash_timer = 0

darkness_surf = pygame.Surface((screen_w, screen_h))
darkness_surf.fill((0, 0, 0))
freeze_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
freeze_surf.fill((0, 150, 255, 40))

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
flicker_val = 0
while True:
    screen.fill((5, 5, 10))
    m_pos = pygame.mouse.get_pos()
    m_click = pygame.mouse.get_pressed()
    flicker_val += 0.08 

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
            if game_state == "char_select":
                for i in range(3):
                    rect = pygame.Rect(screen_w // 2 - 450 + (i * 310), 200, 280, 400)
                    if rect.collidepoint(event.pos):
                        sel = ["wizard", "shadow", "dwarf"][i]
                        player.setup_class(sel)
                        load_game_csv(user_name, sel, player, skills)
                        enemies.clear(); bosses.clear(); projectiles.clear(); coins.clear(); chests.clear(); active_swings.clear()
                        current_wave, max_enemies, time_freeze_timer = 1, 4, 0
                        for _ in range(max_enemies): spawn_enemy()
                        game_state = "playing"
            
            # FIXED: Added click detection for the skill tree
            elif game_state == "skill_tree":
                result = skills.handle_click(event.pos, player)
                if result == "respawn":
                    enemies.clear(); bosses.clear(); projectiles.clear(); active_swings.clear()
                    player.health = player.max_health
                    player.energy = player.max_energy
                    current_wave = 1
                    max_enemies = 4
                    for _ in range(max_enemies): spawn_enemy()
                    game_state = "playing"
                elif result == "saved":
                    trigger_save_anim("UPGRADED!")

    if game_state == "menu":
        title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 255, 150))
        screen.blit(title, title.get_rect(center=(screen_w//2, screen_h//2 - 50)))
        u_txt = pygame.font.SysFont("Arial", 30).render(f"User: {user_name}|", True, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=(screen_w//2, screen_h//2 + 50)))

    elif game_state == "char_select":
        title = pygame.font.SysFont("Impact", 60).render("SELECT CHARACTER", True, (255, 255, 255))
        screen.blit(title, (screen_w//2 - title.get_width()//2, 80))
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

    elif game_state == "playing":
        if time_freeze_timer <= 0:
            player.energy -= 1/60 
        
        if player.energy <= 0: player.health = 0
        if player.dash_cooldown > 0: player.dash_cooldown -= 1
        if time_freeze_timer > 0: time_freeze_timer -= 1
        if nuke_flash_timer > 0: nuke_flash_timer -= 1

        if not enemies and not bosses:
            current_wave += 1
            max_enemies += 2
            for _ in range(max_enemies): spawn_enemy(1.0 + (current_wave*0.1), 1.0 + (current_wave*0.02))
            if current_wave % 2 == 0: chests.append(Chest())
            trigger_save_anim(f"WAVE {current_wave}")

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
                player.money += 1; player.energy = min(player.max_energy, player.energy + 1.2)
                coins.remove(c)

        for ch in chests[:]:
            ch.draw(screen)
            if player.rect.colliderect(ch.rect):
                effect = random.choice(["energy", "freeze", "nuke"])
                if effect == "energy": player.energy = player.max_energy; trigger_save_anim("MAX ENERGY!")
                elif effect == "freeze": time_freeze_timer = 300; trigger_save_anim("TIME FREEZE!")
                elif effect == "nuke": 
                    nuke_flash_timer = 15; trigger_save_anim("SCREEN WIPE!")
                    for e in enemies[:]: e.health = 0
                chests.remove(ch)

        # --- UPDATED ATTACK LOGIC ---
        if m_click[0] and player.attack_cooldown <= 0:
            if player.char_type == "dwarf":
                active_swings.append(MeleeSwing(player, player.color))
                player.attack_cooldown = player.base_cooldown
            else:
                targets = [e for e in (enemies + bosses) if get_dist_to_rect(player.rect.center, e.rect) <= player.attack_radius]
                if targets:
                    targets.sort(key=lambda t: get_dist_to_rect(player.rect.center, t.rect))
                    for i in range(min(len(targets), player.projectiles_count)):
                        projectiles.append(Projectile(player.rect.centerx, player.rect.centery, targets[i], player.color, player.attack_radius * 1.5))
                    player.attack_cooldown = player.base_cooldown

        for s in active_swings[:]:
            s.update(enemies + bosses, player.damage)
            s.draw(screen)
            if s.lifetime <= 0: active_swings.remove(s)

        for p_obj in projectiles[:]:
            if p_obj.update(enemies + bosses):
                p_obj.draw(screen)
                if p_obj.rect.colliderect(p_obj.target.rect):
                    p_obj.target.health -= player.damage
                    if p_obj in projectiles: projectiles.remove(p_obj)
            else: 
                if p_obj in projectiles: projectiles.remove(p_obj)

        for e in enemies[:]:
            if time_freeze_timer <= 0:
                e.update(player.rect)
                if player.rect.colliderect(e.rect): player.health -= 0.3
            e.draw(screen)
            if e.health <= 0: enemies.remove(e); player.money += 2; boss_energy += 10
            
        for b in bosses[:]:
            if time_freeze_timer <= 0:
                b.update(player.rect)
                if player.rect.colliderect(b.rect): player.health -= 0.8
            b.draw(screen)
            if b.health <= 0: bosses.remove(b); player.money += 50; player.skill_points += 1; trigger_save_anim("+1 SP!")

        if boss_energy >= boss_goal: bosses.append(Boss(screen_w, screen_h)); boss_energy = 0

        player.draw(screen) 
        # Draw Pulse Aura
        aura_diameter = int(player.attack_radius * 2)
        pulse = int(5 * math.sin(flicker_val)) 
        aura_size = aura_diameter + pulse
        temp_aura = pygame.Surface((aura_size, aura_size), pygame.SRCALPHA)
        for r in range(aura_size // 2, 0, -4):
            alpha = int(160 * (r / (aura_size // 2)))
            pygame.draw.circle(temp_aura, (0, 0, 0, alpha), (aura_size // 2, aura_size // 2), r)
        screen.blit(temp_aura, temp_aura.get_rect(center=player.rect.center))
        
        if nuke_flash_timer > 0:
            flash = pygame.Surface((screen_w, screen_h)); flash.fill((255,255,255))
            flash.set_alpha(int((nuke_flash_timer/15)*255)); screen.blit(flash, (0,0))
        if time_freeze_timer > 0:
            screen.blit(freeze_surf, (0, 0))
            ui_freeze = pygame.font.SysFont("Impact", 40).render("TIME FROZEN!", True, (0, 200, 255))
            screen.blit(ui_freeze, ui_freeze.get_rect(center=(screen_w//2, 100)))

        # HUD
        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        screen.blit(ui_f.render(f"WAVE: {current_wave} (BEST: {player.highscore})", True, (200, 200, 255)), (20, 50))
        bar_x, bar_y = screen_w//2-100, screen_h-55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10))
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, (player.energy/player.max_energy)*200), 10))
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health/player.max_health)*200), 15))

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
        skills.draw(screen, player.money, player.skill_points, player.char_type)
        if save_notification_timer > 0:
            t = pygame.font.SysFont("Arial", 22, bold=True).render(save_notification_msg, True, (0, 255, 150))
            screen.blit(t, t.get_rect(center=(screen_w // 2, 40)))
            save_notification_timer -= 1

    pygame.display.flip()
    clock.tick(60)