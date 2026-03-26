import pygame
import sys
import random
from player import Player
from enemy import Enemy
from action import Coin, SpecialCoin
from projectile import Projectile
from skill_tree import SkillTree
from boss import Boss

# 1. INITIALIZE
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_w, screen_h = screen.get_size()
pygame.display.set_caption("Pulse Game")
clock = pygame.time.Clock()

# 2. SPRITE LOADING (Using your uploaded files)
def load_sprite(path, size=(50, 50)):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except:
        # Fallback to a surface if file not found
        surf = pygame.Surface(size)
        surf.fill((255, 0, 255))
        return surf

# Change these filenames to match your exact saved filenames
wizard_img = load_sprite("image_5d21e5.png") 
dwarf_img = load_sprite("image_5d25fd.png")

# 3. FONTS
font = pygame.font.SysFont("Arial", 32)
menu_font = pygame.font.SysFont("Impact", 80)
score_font = pygame.font.SysFont("Consolas", 28, bold=True)

# 4. OBJECTS
game_state = "menu"
user_name = ""
player = Player()
coin = Coin()
specialcoin = SpecialCoin()
coin.respawn(screen_w, screen_h)
specialcoin.respawn(screen_w, screen_h)
skills = SkillTree(screen_w, screen_h)
death_timer = -1 
bosses = []
coins_collected = 0

enemies = [Enemy(random.randint(0, screen_w), random.randint(0, screen_h)) for _ in range(3)]
projectiles = []
death = 0
running = True

while running:
    screen.fill((30, 30, 30))
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    # --- PHASE 1: EVENTS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        # MOUSE CLICKS
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "skill_tree":
                if skills.handle_click(event.pos, player):
                    # Respawn Logic
                    player.health = player.max_health
                    player.rect.center = (screen_w // 2, screen_h // 2)
                    enemies.clear()
                    for _ in range(3): enemies.append(Enemy(random.randint(0, screen_w), random.randint(0, screen_h)))
                    game_state = "playing"
                    death_timer = -1

        # KEYBOARD
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            
            if game_state == "menu":
                if event.key == pygame.K_RETURN and user_name.strip() != "":
                    game_state = "char_select"
                elif event.key == pygame.K_BACKSPACE: user_name = user_name[:-1]
                elif event.unicode.isprintable(): user_name += event.unicode

            elif game_state == "char_select":
                if event.key == pygame.K_1: player.setup_class("wizard"); game_state = "playing"
                if event.key == pygame.K_2: player.setup_class("shadow"); game_state = "playing"
                if event.key == pygame.K_3: player.setup_class("dwarf"); game_state = "playing"

    # --- PHASE 2: LOGIC & DRAW ---
    if game_state == "menu":
        title = menu_font.render("PULSE", True, (0, 255, 0))
        screen.blit(title, title.get_rect(center=(screen_w // 2, screen_h // 2 - 100)))
        prompt = font.render(f"Enter Name: {user_name}|", True, (255, 255, 255))
        screen.blit(prompt, prompt.get_rect(center=(screen_w // 2, screen_h // 2)))

    elif game_state == "char_select":
        header = menu_font.render("CHOOSE YOUR HERO", True, (255, 255, 255))
        screen.blit(header, header.get_rect(center=(screen_w // 2, 100)))
        classes = [("1. WIZARD", (100, 200, 255)), ("2. SHADOW", (150, 100, 255)), ("3. DWARF", (255, 100, 100))]
        for i, (name, col) in enumerate(classes):
            txt = font.render(name, True, col)
            screen.blit(txt, (screen_w // 2 - 150, 300 + (i * 80)))

    elif game_state == "playing":
        player.move(pygame.key.get_pressed())
        player.rect.clamp_ip(screen.get_rect())

        # Attack
        if coins_collected >= 50:
            bosses.append(Boss(screen_w, screen_h))
            coins_collected = 0 # Reset counter

        # 2. UPDATED ATTACK (Now with Range Limit)
        if mouse_click[0] and player.attack_cooldown <= 0:
            if player.attack_style == "homing":
                closest, min_dist = None, player.attack_radius
                # Combine enemies and bosses for targeting
                all_targets = enemies + bosses
                for t in all_targets:
                    dist = pygame.math.Vector2(mouse_pos).distance_to(t.rect.center)
                    if dist < min_dist: closest, min_dist = t, dist
                
                if closest:
                    # Weapon Range is now passed here (e.g., player.attack_radius * 2)
                    projectiles.append(Projectile(player.rect.centerx, player.rect.centery, 
                                                 closest, player.color, player.attack_radius * 1.5))
                    player.attack_cooldown = 20
            else:
                player.attacking, player.attack_timer, player.attack_cooldown = True, 10, 30
                for e in enemies[:]:
                    if pygame.math.Vector2(player.rect.center).distance_to(e.rect.center) < player.attack_radius:
                        enemies.remove(e); player.money += 2
                        enemies.append(Enemy(random.randint(0, screen_w), random.randint(0, screen_h)))

        if player.attack_cooldown > 0: player.attack_cooldown -= 1
        if player.attack_timer > 0: player.attack_timer -= 1
        else: player.attacking = False

        # Projectiles
        for p in projectiles[:]:
            if p.update(enemies):
                p.draw(screen)
                if p.rect.colliderect(p.target.rect):
                    enemies.remove(p.target); player.money += 2
                    enemies.append(Enemy(random.randint(0, screen_w), random.randint(0, screen_h)))
                    projectiles.remove(p)
            else: projectiles.remove(p)

        # Collision & Enemies
        if player.rect.colliderect(coin.rect): player.money += 1; coin.respawn(screen_w, screen_h)
        if player.rect.colliderect(specialcoin.rect): player.money += 5; specialcoin.respawn(screen_w, screen_h)

        for e in enemies:
            e.update(player.rect); e.draw(screen)
            if player.rect.colliderect(e.rect):
                player.health -= 0.5
                if player.health <= 0:
                    death += 1; player.money = max(0, player.money - (death + 5))
                    game_state = "dead"; projectiles.clear(); death_timer = 180

        coin.draw(screen); specialcoin.draw(screen); player.draw(screen)
        
        # Simple Sprite Overlay (Optional: remove player.draw and use this)
        # if player.char_type == "wizard": screen.blit(wizard_img, player.rect)
        # elif player.char_type == "dwarf": screen.blit(dwarf_img, player.rect)

        # UI
        screen.blit(score_font.render(f"ID: {user_name}  Money: ${player.money}", True, (255, 215, 0)), (20, 20))
        hp_ratio = max(0, player.health / player.max_health)
        pygame.draw.rect(screen, (100, 0, 0), (screen_w//2-100, screen_h-50, 200, 20))
        pygame.draw.rect(screen, (0, 200, 0), (screen_w//2-100, screen_h-50, 200*hp_ratio, 20))

    elif game_state == "dead":
        msg = menu_font.render("WASTED", True, (255, 50, 50))
        screen.blit(msg, msg.get_rect(center=(screen_w // 2, screen_h // 2)))
        death_timer -= 1
        timer_txt = font.render(f"Entering Skill Tree in: {max(0, death_timer // 60)}", True, (255, 255, 255))
        screen.blit(timer_txt, timer_txt.get_rect(center=(screen_w // 2, screen_h // 2 + 80)))
        if death_timer <= 0: game_state = "skill_tree"

    elif game_state == "skill_tree":
        header = menu_font.render("SOUL UPGRADES", True, (150, 100, 255))
        screen.blit(header, header.get_rect(center=(screen_w // 2, 80)))
        money_txt = font.render(f"Remaining Money: ${player.money}", True, (255, 215, 0))
        screen.blit(money_txt, money_txt.get_rect(center=(screen_w // 2, 140)))
        skills.draw(screen, player.money)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()