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

# PERSISTENT SHROUD SURFACE
shroud = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

# --- IMAGE LOADERS ---
def load_bg(path):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (screen_w, screen_h))
    except:
        return None

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

def load_logo(path, max_w, max_h):
    try:
        img = pygame.image.load(path).convert_alpha()
        orig_w, orig_h = img.get_size()
        scale = min(max_w / orig_w, max_h / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        return pygame.transform.scale(img, (new_w, new_h))
    except:
        return None

# --- LOAD ALL ASSETS ---
# Backgrounds — put these PNGs in your photos/ folder:
#   photos/menu_bg.png        -> menu screen background
#   photos/char_select_bg.png -> character select background
#   photos/bg.png             -> in-game background
#   photos/logo.png           -> game title logo (replaces "PULSE" text)
menu_bg        = load_bg("photos/menu_bg.png")
char_select_bg = load_bg("photos/char_select_bg.png")
game_bg        = load_bg("photos/bg.png")
if game_bg:
    game_bg.set_alpha(180)

menu_logo = load_logo("photos/logo.png", screen_w * 0.6, screen_h * 0.3)

# Character sprites
wizard_ui = load_sprite("photos/wizard_right.png")
shadow_ui = load_sprite("photos/Shadow_right.png")
dwarf_ui  = load_sprite("photos/dwarf_forward.png")

freeze_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
freeze_surf.fill((0, 150, 255, 40))

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

class Chest:
    def __init__(self, x, y):
        try:
            self.image = pygame.image.load("photos/chest.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (45, 45))
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill((255, 215, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

game_state, user_name = "menu", ""
player = Player()
skills = SkillTree(screen_w, screen_h)
bosses, enemies, projectiles, coins, chests, active_swings, special_coins, hp_drops = [], [], [], [], [], [], [], []
boss_energy, boss_goal, max_enemies = 0, 100, 4
time_freeze_timer = 0
nuke_flash_timer = 0

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

# --- MAIN LOOP ---
while True:
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

    # --- MENU ---
    if game_state == "menu":
        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        else:
            screen.fill((5, 5, 15))

        if menu_logo:
            screen.blit(menu_logo, menu_logo.get_rect(center=(screen_w // 2, screen_h // 2 - 80)))
        else:
            title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 255, 150))
            screen.blit(title, title.get_rect(center=(screen_w // 2, screen_h // 2 - 80)))

        box_w, box_h = 400, 50
        box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2 + 40, box_w, box_h)
        pygame.draw.rect(screen, (20, 20, 35), box_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 255, 150), box_rect, 2, border_radius=10)
        u_txt = pygame.font.SysFont("Arial", 28).render(f"{user_name}|", True, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=box_rect.center))
        hint = pygame.font.SysFont("Arial", 20).render("Enter your name and press ENTER", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 110)))

    # --- CHAR SELECT ---
    elif game_state == "char_select":
        if char_select_bg:
            screen.blit(char_select_bg, (0, 0))
        else:
            screen.fill((10, 10, 20))

        overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        screen.blit(overlay, (0, 0))

        title = pygame.font.SysFont("Impact", 60).render("SELECT CHARACTER", True, (255, 255, 255))
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

    # --- PLAYING ---
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
            save_game_csv(user_name, player.char_type, player, skills)
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
            trigger_save_anim(f"WAVE {current_wave}: EVOLVED")

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
                player.health = min(player.max_health, player.health + 5)
                hp_drops.remove(h)

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
                b.update(player.rect, dilation)
                if player.rect.colliderect(b.rect):
                    player.health -= max(0.1, 0.8 - (getattr(player, 'armor', 0) * 0.05))
            b.draw(screen)
            if b.health <= 0:
                bosses.remove(b); player.money += 50; player.skill_points += 1; trigger_save_anim("+1 SP!")

        if boss_energy >= boss_goal:
            bosses.append(Boss(screen_w, screen_h))
            boss_energy = 0

        player.draw(screen)

        # --- DARKNESS SYSTEM ---
        shroud.fill((5, 5, 15, 200))
        pulse = int(6 * math.sin(flicker_val))
        light_radius = max(10, int(player.attack_radius * 1.4) + pulse)
        t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        core_radius = max(1, light_radius // 2)
        pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), core_radius)
        for r in range(light_radius, core_radius, -1):
            alpha = max(0, min(255, int(255 * (1 - (r - core_radius) / max(1, light_radius - core_radius)))))
            pygame.draw.circle(t_surf, (0, 0, 0, alpha), (light_radius, light_radius), r)
        shroud.blit(t_surf, t_surf.get_rect(center=player.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(shroud, (0, 0))

        # --- UI ---
        if nuke_flash_timer > 0:
            flash = pygame.Surface((screen_w, screen_h)); flash.fill((255, 255, 255))
            flash.set_alpha(int((nuke_flash_timer / 15) * 255)); screen.blit(flash, (0, 0))
        if time_freeze_timer > 0:
            screen.blit(freeze_surf, (0, 0))

        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        screen.blit(ui_f.render(f"WAVE: {current_wave} (BEST: {player.highscore})", True, (200, 200, 255)), (20, 50))
        bar_x, bar_y = screen_w // 2 - 100, screen_h - 55
        pygame.draw.rect(screen, (20, 20, 40), (bar_x, bar_y, 200, 10))
        pygame.draw.rect(screen, (0, 150, 255), (bar_x, bar_y, max(0, (player.energy / player.max_energy) * 200), 10))
        pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y + 15, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (bar_x, bar_y + 15, max(0, (player.health / player.max_health) * 200), 15))

    elif game_state == "dead":
        screen.fill((5, 5, 15))
        msg = pygame.font.SysFont("Impact", 100).render("OUT OF TIME", True, (255, 0, 0))
        screen.blit(msg, msg.get_rect(center=(screen_w // 2, screen_h // 2)))
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