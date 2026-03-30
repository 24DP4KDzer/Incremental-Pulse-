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
    
    # Check if current wave is higher than the stored highscore
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
        "highscore": getattr(p, 'highscore', 1) # NEW FIELD
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
                    def s_i(k, d): return int(row[k]) if row.get(k) and row[k].strip() else d
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
                    # SYNC THE SKILL TREE UI WITH THE LOADED STATS
                    s_tree.sync_with_player(p)

# 3. SPRITES
def load_sprite(path, size=(60, 60)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255))
        return surf

wizard_img = load_sprite("image_5d21e5.png") 
shadow_img = load_sprite("image_5d25a6.png")
dwarf_img = load_sprite("image_5d25fd.png")

# 4. GAME OBJECTS
game_state, user_name = "menu", ""
player = Player()
skills = SkillTree(screen_w, screen_h)
bosses, enemies, projectiles, coins, special_coins, hp_coins = [], [], [], [], [], []
boss_energy, boss_goal, max_enemies = 0, 100, 4

darkness_surf = pygame.Surface((screen_w, screen_h))
darkness_surf.fill((0, 0, 0))

def spawn_enemy(hp_mult=1.0, speed_mult=1.0):
    e = Enemy(random.randint(0, screen_w), random.randint(0, screen_h))
    e.max_health = int(e.max_health * hp_mult)
    e.health = e.max_health
    e.speed = min(3.5, e.speed * speed_mult)
    enemies.append(e)

def spawn_coin():
    c = Coin()
    c.rect.x, c.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    coins.append(c)

def spawn_special():
    sc = SpecialCoin()
    sc.rect.x, sc.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    special_coins.append(sc)

def spawn_hp():
    hc = HpCoin()
    hc.rect.x, hc.rect.y = random.randint(100, screen_w-100), random.randint(100, screen_h-100)
    hp_coins.append(hc)

for _ in range(5): spawn_coin()

for l in range(3): spawn_hp()

# --- MAIN LOOP ---
while True:
    screen.fill((5, 5, 10))
    m_pos, m_click = pygame.mouse.get_pos(), pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            pygame.quit(); sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Save the game before closing if a user is logged in
                if user_name and player.char_type:
                    save_game_csv(user_name, player.char_type, player, skills)
                    print(f"Progress for {user_name} saved. Goodbye!")
                
                pygame.quit()
                sys.exit()
            
            if game_state == "menu":
                if event.key == pygame.K_RETURN and user_name.strip(): 
                    game_state = "char_select"
                elif event.key == pygame.K_BACKSPACE: 
                    user_name = user_name[:-1]
                else: 
                    user_name += event.unicode
            
            elif game_state == "char_select":
                sel = None
                if event.key == pygame.K_1: sel = "wizard"
                elif event.key == pygame.K_2: sel = "shadow"
                elif event.key == pygame.K_3: sel = "dwarf"
                if sel:
                    player.setup_class(sel)
                    load_game_csv(user_name, sel, player, skills)
                    enemies.clear(); bosses.clear(); projectiles.clear()
                    current_wave = 1
                    max_enemies = 4
                    for _ in range(max_enemies): spawn_enemy()
                    game_state = "playing"
            
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                if getattr(player, 'dash_unlocked', False) and getattr(player, 'dash_cooldown', 0) <= 0:
                    keys = pygame.key.get_pressed()
                    dx, dy = 0, 0
                    if keys[pygame.K_w]: dy = -120
                    if keys[pygame.K_s]: dy = 120
                    if keys[pygame.K_a]: dx = -120
                    if keys[pygame.K_d]: dx = 120
                    player.rect.x += dx
                    player.rect.y += dy
                    player.dash_cooldown = 120 

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "skill_tree":
                result = skills.handle_click(event.pos, player)
                if result:
                    save_game_csv(user_name, player.char_type, player, skills)
                    if result == "respawn":
                        player.health, player.energy = player.max_health, player.max_energy
                        enemies.clear(); bosses.clear(); projectiles.clear(); coins.clear(); special_coins.clear()
                        current_wave, max_enemies = 1, 4
                        for _ in range(max_enemies): spawn_enemy()
                        for _ in range(5): spawn_coin()
                        game_state = "playing"

    if game_state == "menu":
        title = pygame.font.SysFont("Impact", 100).render("PULSE", True, (0, 255, 150))
        screen.blit(title, title.get_rect(center=(screen_w//2, screen_h//2 - 50)))
        u_txt = pygame.font.SysFont("Arial", 30).render(f"User: {user_name}|", True, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=(screen_w//2, screen_h//2 + 50)))

    elif game_state == "char_select":
        title = pygame.font.SysFont("Impact", 60).render("SELECT CHARACTER", True, (255, 255, 255))
        screen.blit(title, (screen_w//2 - title.get_width()//2, 100))
        classes = [("1. WIZARD", (0, 200, 255), wizard_img), ("2. SHADOW", (150, 0, 255), shadow_img), ("3. DWARF", (255, 150, 0), dwarf_img)]
        for i, (name, col, img) in enumerate(classes):
            rect = pygame.Rect(screen_w//2 - 450 + (i * 320), 250, 250, 350)
            pygame.draw.rect(screen, (20, 20, 30), rect, border_radius=15)
            pygame.draw.rect(screen, col, rect, 3, border_radius=15)
            screen.blit(img, (rect.centerx - 30, rect.y + 50)) 
            name_t = pygame.font.SysFont("Arial", 28, bold=True).render(name, True, col)
            screen.blit(name_t, name_t.get_rect(center=(rect.centerx, rect.y + 300)))

    elif game_state == "playing":
        player.energy -= 1/60 
        if player.energy <= 0: player.health = 0
        if getattr(player, 'dash_cooldown', 0) > 0: player.dash_cooldown -= 1

        if not enemies and not bosses:
            current_wave += 1
            max_enemies += 2 + (current_wave // 5)
            hp_m = 1.0 + (current_wave * 0.1)
            speed_m = 1.0 + (current_wave * 0.05)
            for _ in range(max_enemies): spawn_enemy(hp_m, speed_m)
            boss_goal = 100 + (current_wave * 15)
            trigger_save_anim(f"WAVE {current_wave} START")

        player.move(pygame.key.get_pressed())
        player.rect.clamp_ip(screen.get_rect())

        while len(coins) < 5: spawn_coin()
        
        m_range = getattr(player, 'magnet_range', 60)
        for c in coins + special_coins:
            dist = math.hypot(player.rect.centerx - c.rect.centerx, player.rect.centery - c.rect.centery)
            if dist < m_range:
                c.rect.x += (player.rect.centerx - c.rect.centerx) * 0.1
                c.rect.y += (player.rect.centery - c.rect.centery) * 0.1

        for c in coins[:]:
            c.draw(screen)
            if player.rect.colliderect(c.rect):
                player.money += 1; player.energy = min(player.max_energy, player.energy + 1.5)
                coins.remove(c)

        for sc in special_coins[:]:
            sc.draw(screen)
            if player.rect.colliderect(sc.rect):
                player.money += 10; player.energy = min(player.max_energy, player.energy + 5.0)
                special_coins.remove(sc)

        current_dmg = getattr(player, 'damage', 1.0)
        current_cooldown = max(5, getattr(player, 'base_cooldown', 25))
        if m_click[0] and player.attack_cooldown <= 0:
            all_t = [e for e in (bosses + enemies)]
            all_t.sort(key=lambda t: pygame.math.Vector2(player.rect.center).distance_to(t.rect.center))
            in_range = [t for t in all_t if pygame.math.Vector2(player.rect.center).distance_to(t.rect.center) < player.attack_radius]
            shots = min(len(in_range), getattr(player, 'projectiles_count', 1))
            for i in range(shots):
                projectiles.append(Projectile(player.rect.centerx, player.rect.centery, in_range[i], player.color, player.attack_radius * 1.5))
            if shots > 0: player.attack_cooldown = current_cooldown

        for p in projectiles[:]:
            if p.update(enemies + bosses):
                p.draw(screen)
                if p.rect.colliderect(p.target.rect):
                    p.target.health -= current_dmg 
                    if p in projectiles: projectiles.remove(p)
            else: 
                if p in projectiles: projectiles.remove(p)

        for e in enemies[:]:
            e.update(player.rect); e.draw(screen)
            if e.health <= 0: 
                enemies.remove(e); player.money += 2; boss_energy += 10
                if random.random() < 0.1: spawn_special()
            elif player.rect.colliderect(e.rect): 
                player.health -= (0.2 * (1.0 + current_wave * 0.05))
            
        for b in bosses[:]:
            b.update(player.rect); b.draw(screen)
            if b.health <= 0: 
                bosses.remove(b)
                player.money += 100
                player.skill_points += 1
                player.energy = player.max_energy
                trigger_save_anim("+1 SKILL POINT!")
            elif player.rect.colliderect(b.rect): player.health -= 1.0

        if boss_energy >= boss_goal:
            nb = Boss(screen_w, screen_h)
            nb.max_health *= (1.0 + (current_wave * 0.2))
            nb.health = nb.max_health
            bosses.append(nb); boss_energy = 0

        if player.char_type == "wizard": screen.blit(wizard_img, player.rect)
        elif player.char_type == "shadow": screen.blit(shadow_img, player.rect)
        elif player.char_type == "dwarf": screen.blit(dwarf_img, player.rect)

        energy_ratio = player.energy / player.max_energy
        if energy_ratio < 0.5:
            darkness_alpha = int((1 - (energy_ratio * 2)) * 200)
            darkness_surf.set_alpha(max(0, darkness_alpha))
            screen.blit(darkness_surf, (0,0))

        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points} | WAVE: {current_wave}", True, (255, 215, 0)), (20, 20))
        # UI rendering in the "playing" loop
        ui_f = pygame.font.SysFont("Consolas", 22, bold=True)
        screen.blit(ui_f.render(f"GOLD: ${player.money} | SP: {player.skill_points}", True, (255, 215, 0)), (20, 20))
        
        # Wave and Highscore display
        wave_txt = f"WAVE: {current_wave} (BEST: {getattr(player, 'highscore', 1)})"
        screen.blit(ui_f.render(wave_txt, True, (200, 200, 255)), (20, 50))
        
        pygame.draw.rect(screen, (20, 20, 20), (screen_w//2-100, screen_h-70, 200, 8))
        pygame.draw.rect(screen, (0, 180, 255), (screen_w//2-100, screen_h-70, max(0, (player.energy/player.max_energy)*200), 8))
        pygame.draw.rect(screen, (60, 0, 0), (screen_w//2-100, screen_h-55, 200, 15))
        pygame.draw.rect(screen, (0, 255, 120), (screen_w//2-100, screen_h-55, max(0, (player.health/player.max_health)*200), 15))

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