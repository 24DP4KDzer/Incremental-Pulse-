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

# PERSISTENT SHROUD SURFACE (Prevents lag)
shroud = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

class MeleeSwing:
    def __init__(self, owner, enemies, damage):
        self.owner = owner
        self.angle = 0
        self.spin_speed = getattr(owner, 'rotation_speed', 20) 
        self.radius = owner.attack_radius
        self.lifetime = 360 // self.spin_speed 
        
        for e in enemies:
            dist = math.hypot(owner.rect.centerx - e.rect.centerx, owner.rect.centery - e.rect.centery)
            if dist <= self.radius + 25: 
                enemy_armor = getattr(e, 'armor', 0)
                base_dmg = max(1, damage - enemy_armor)
                final_dmg = base_dmg
                if random.randint(1, 100) <= getattr(owner, 'crit_chance', 0):
                    final_dmg *= 2
                e.health -= final_dmg
                if getattr(owner, 'lifesteal', 0) > 0:
                    owner.health = min(owner.max_health, owner.health + owner.lifesteal)
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

    def update(self):
        self.angle += self.spin_speed
        self.lifetime -= 1

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
        try:
            with open(PLAYER_FILE, 'r', newline='') as f:
                p_rows = list(csv.DictReader(f))
        except: p_rows = []
    
    if globals().get('current_wave', 1) > getattr(p, 'highscore', 1):
        p.highscore = globals().get('current_wave', 1)

    new_p_data = {
        "name": name, "char_type": char_type, "money": p.money, 
        "max_health": p.max_health, "radius": p.attack_radius, 
        "speed": p.speed, "damage": getattr(p, 'damage', 1.0),
        "multi": getattr(p, 'projectile_count', 1),
        "aspeed": getattr(p, 'base_cooldown', 25),
        "max_energy": getattr(p, 'max_energy', 10.0),
        "sp": getattr(p, 'skill_points', 0),
        "magnet": getattr(p, 'magnet_range', 60),
        "dash": int(getattr(p, 'dash_unlocked', False)),
        "highscore": getattr(p, 'highscore', 1)
    }
    
    for s in s_tree.skills:
        new_p_data[f"skill_{s['id']}"] = s["level"]
    
    found_p = False
    for i, row in enumerate(p_rows):
        if row.get("name") == name and row.get("char_type") == char_type:
            p_rows[i] = new_p_data
            found_p = True
            break
    if not found_p: 
        p_rows.append(new_p_data)
    
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
                    p.energy = p.max_energy
                    p.highscore = s_i("highscore", 1)
                    
                    for s in s_tree.skills:
                        key = f"skill_{s['id']}"
                        s["level"] = s_i(key, 0) 
                    
                    s_tree.sync_with_player(p)

def get_dist_to_rect(point, rect):
    px = max(rect.left, min(point[0], rect.right))
    py = max(rect.top, min(point[1], rect.bottom))
    return math.hypot(point[0] - px, point[1] - py)

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

freeze_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
freeze_surf.fill((0, 150, 255, 40))

def spawn_enemy(hp_m=1.0, spd_m=1.0, wave=1):
    e = Enemy(random.randint(0, screen_w), random.randint(0, screen_h))
    e.max_health = int(e.max_health * hp_m)
    e.health = e.max_health
    e.speed = min(4.5, e.speed * spd_m)
    e.armor = wave // 5 
    enemies.append(e)

def spawn_coin():
    c = Coin()
    c.rect.x, c.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    coins.append(c)

flicker_val = 0
while True:
    screen.fill((5, 5, 15)) 
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
                if getattr(player, 'dash_unlocked', False) and player.dash_cooldown <= 0:
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
            
            elif game_state == "skill_tree":
                result = skills.handle_click(event.pos, player)
                if result == "respawn":
                    enemies.clear(); bosses.clear(); projectiles.clear(); active_swings.clear()
                    player.health = player.max_health
                    player.energy = player.max_energy
                    current_wave, max_enemies = 1, 4
                    for _ in range(max_enemies): spawn_enemy()
                    game_state = "playing"
                elif result == "saved":
                    save_game_csv(user_name, player.char_type, player, skills)
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
        
        player.energy = max(0, min(player.energy, player.max_energy))
        
        if player.energy <= 0 or player.health <= 0: 
            player.health = 0
            save_game_csv(user_name, player.char_type, player, skills)
            game_state, death_timer = "dead", 120
            continue 

        if player.health < player.max_health:
            player.health += getattr(player, 'regen', 0)
        
        if player.dash_cooldown > 0: player.dash_cooldown -= 1
        if time_freeze_timer > 0: time_freeze_timer -= 1
        if nuke_flash_timer > 0: nuke_flash_timer -= 1
        if player.attack_cooldown > 0: player.attack_cooldown -= 1

        if not enemies and not bosses:
            current_wave += 1
            max_enemies += 2
            hp_scale = 1.0 + (current_wave * 0.2)
            spd_scale = 1.0 + (current_wave * 0.05)
            for _ in range(max_enemies): spawn_enemy(hp_scale, spd_scale, current_wave)
            if current_wave % 2 == 0: chests.append(Chest())
            trigger_save_anim(f"WAVE {current_wave}: ENEMIES EVOLVED")

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
                player.energy = min(player.max_energy, player.energy + 1.2)
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

        if m_click[0] and player.attack_cooldown <= 0:
            if player.char_type == "dwarf":
                active_swings.append(MeleeSwing(player, enemies + bosses, player.damage))
                player.attack_cooldown = player.base_cooldown
            else:
                targets = [e for e in (enemies + bosses) if get_dist_to_rect(player.rect.center, e.rect) <= player.attack_radius]
                if targets:
                    targets.sort(key=lambda t: get_dist_to_rect(player.rect.center, t.rect))
                    count = getattr(player, 'projectile_count', 1)
                    for i in range(min(len(targets), count)):
                        projectiles.append(Projectile(player.rect.centerx, player.rect.centery, targets[i], player.color, player.attack_radius * 1.5))
                    player.attack_cooldown = player.base_cooldown

        for s in active_swings[:]:
            s.update(); s.draw(screen)
            if s.lifetime <= 0: active_swings.remove(s)

        for p_obj in projectiles[:]:
            if p_obj.update(enemies + bosses):
                p_obj.draw(screen)
                if p_obj.rect.colliderect(p_obj.target.rect):
                    enemy_armor = getattr(p_obj.target, 'armor', 0)
                    dmg = max(1, player.damage - enemy_armor) 
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
                    armor = getattr(player, 'armor', 0)
                    dmg_in = max(0.15, 0.3 - (armor * 0.01))  # FIX: softer reduction, higher floor
                    player.health -= dmg_in
                    thorns = getattr(player, 'thorns', 0)
                    if thorns > 0: e.health -= thorns
            e.draw(screen)
            if e.health <= 0: 
                enemies.remove(e); player.money += 2; boss_energy += 10
            
        for b in bosses[:]:
            if time_freeze_timer <= 0:
                b.update(player.rect, dilation)
                if player.rect.colliderect(b.rect):
                    armor = getattr(player, 'armor', 0)
                    dmg_in = max(0.1, 0.8 - (armor * 0.05))
                    player.health -= dmg_in
            b.draw(screen)
            if b.health <= 0: 
                bosses.remove(b); player.money += 50; player.skill_points += 1; trigger_save_anim("+1 SP!")

        if boss_energy >= boss_goal: 
            bosses.append(Boss(screen_w, screen_h))
            boss_energy = 0

        player.draw(screen) 
        
        # --- BULLETPROOF SMOOTH DARKNESS SYSTEM ---
        # 1. Clear shroud and set darkness (235 is very dark)
        shroud.fill((5, 5, 15, 235)) 
        
        # 2. Dynamic Radius with flicker
        pulse = int(6 * math.sin(flicker_val))
        light_radius = max(10, int(player.attack_radius * 1.4) + pulse)
        
        # 3. Create the smooth gradient hole
        t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        
        # Solid center core (prevents black lines)
        core_radius = max(1, light_radius // 2)
        pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), core_radius)
        
        # Fade out (step of 1 for perfect smoothness)
        for r in range(light_radius, core_radius, -1):
            # Calculate alpha and force it to be an integer between 0 and 255
            raw_alpha = 255 * (1 - (r - core_radius) / max(1, light_radius - core_radius))
            alpha = max(0, min(255, int(raw_alpha)))
            pygame.draw.circle(t_surf, (0, 0, 0, alpha), (light_radius, light_radius), r)
        
        # 4. Subtract light from shroud and draw
        shroud.blit(t_surf, t_surf.get_rect(center=player.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(shroud, (0, 0))
        
        # --- UI ELEMENTS (Drawn on top of darkness) ---
        if nuke_flash_timer > 0:
            flash = pygame.Surface((screen_w, screen_h)); flash.fill((255,255,255))
            flash.set_alpha(int((nuke_flash_timer/15)*255)); screen.blit(flash, (0,0))
        if time_freeze_timer > 0:
            screen.blit(freeze_surf, (0, 0))
            ui_freeze = pygame.font.SysFont("Impact", 40).render("TIME FROZEN!", True, (0, 200, 255))
            screen.blit(ui_freeze, ui_freeze.get_rect(center=(screen_w//2, 100)))

        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        screen.blit(ui_f.render(f"WAVE: {current_wave} (BEST: {player.highscore})", True, (200, 200, 255)), (20, 50))
        bar_x, bar_y = screen_w//2-100, screen_h-55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10))
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, (player.energy/player.max_energy)*200), 10))
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health/player.max_health)*200), 15))

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