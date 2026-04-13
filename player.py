import pygame
import math
from fonts import render_pixel_text

# --- PALĪGFUNKCIJA SPREITU LOKSNĒM ---
# funkcija get_image_from_sheet pieņem pygame.Surface tipa vērtību sheet un atgriež pygame.Surface tipa vērtību image
def get_image_from_sheet(sheet, column, row, width, height, start_x=0, start_y=0, padding_x=0, padding_y=0, scale_size=(100, 100)):
    """Izvelk kadru, ņemot vērā sākuma pozīcijas un atstarpes starp kadriem."""
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    
    exact_x = start_x + (column * width) + (column * padding_x)
    exact_y = start_y + (row * height) + (row * padding_y)
    
    crop_rect = pygame.Rect(exact_x, exact_y, width, height)
    image.blit(sheet, (0, 0), crop_rect)
    
    return pygame.transform.scale(image, scale_size)

class Player:
    # funkcija __init__ pieņem Player tipa vērtību self un atgriež None tipa vērtību None
    def __init__(self):
        # 1. IESTATĪT RECT UN BĀZES AKTĪVUS
        self.rect = pygame.Rect(100, 100, 60, 80) # Sadursmes zonas (hitbox) izmērs
        self.color = (0, 255, 0)
        
        # --- ANIMĀCIJAS MAINĪGIE ---
        self.animations = {"up": [], "down": [], "left": [], "right": []}
        self.direction = "down"   
        self.frame_index = 0      
        self.anim_timer = 0       
        self.anim_speed = 0.15    
        self.image = None

        # Ēna zem spēlētāja
        self.shadow_surf = pygame.Surface((self.rect.width, 100), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_surf, (0, 0, 0, 80), [0, 0, self.rect.width, 20])

        # --- TUMSAS SISTĒMAS IESTATĪŠANA ---
        display_info = pygame.display.Info()
        sw, sh = display_info.current_w, display_info.current_h
        
        self.darkness_surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        self.darkness_intensity = 235

        # --- SARKANAS MALAS (DAMAGE VIGNETTE) ---
        self.damage_flash_timer = 0          # frames remaining for red flash
        self.damage_flash_duration = 18      # very short flash — just a quick hint
        self._damage_vignette = self._build_damage_vignette(sw, sh)
        
        # 2. PASTĀVĪGIE STATI (PARAMETRI)
        self.money = 0
        self.skill_points = 0
        self.highscore = 1
        
        # 3. ATRIBŪTI
        self.speed = 1.3
        self.max_health = 100
        self.health = 100
        self.damage = 1.0 
        self.projectile_count = 1
        self.base_cooldown = 25
        self.max_energy = 10.0
        self.energy = 10.0
        
        self.dash_unlocked = False
        self.dash_cooldown = 0
        self.magnet_range = 60 

        self.thorns = 0
        self.regen = 0.0
        self.armor = 0
        self.gold_modifier = 1.0
        self.crit_chance = 0
        self.lifesteal = 0
        self.firerate_level = 0

        # 4. CĪŅAS STĀVOKLIS
        self.char_type = "none"
        self.attack_style = "none"
        self.attacking = False
        self.attack_timer = 0
        self.attack_radius = 100
        self.attack_cooldown = 0

    # funkcija setup_class pieņem str tipa vērtību char_type un atgriež None tipa vērtību None
    def setup_class(self, char_type):
        self.damage = 1.0
        self.speed = 1.3
        self.max_health = 100
        self.attack_radius = 100
        self.projectile_count = 1
        self.max_energy = 10.0
        self.magnet_range = 60
        self.armor = 0
        self.regen = 0.0
        self.thorns = 0
        self.crit_chance = 0
        self.lifesteal = 0
        self.dash_unlocked     = False
        self.base_cooldown     = 25
        self.gold_modifier     = 1.0
        # New skill attributes
        self.firerate_level    = 0
        self.explosion_lvl     = 0
        self.poison_lvl        = 0
        self.shield_lvl        = 0
        self.gold_rush_lvl     = 0
        self.knockback_lvl     = 0
        self.dash_cd_bonus     = 0
        self.blink_dist        = 140
        self.energy_drain_mult = 1.0
        self.soul_drain_lvl    = 0

        self.char_type = char_type
        
        if char_type == "wizard":
            self.speed, self.max_health, self.color = 5, 80, (100, 200, 255)
            self.attack_radius, self.attack_style = 250, "homing"
        elif char_type == "shadow":
            self.speed, self.max_health, self.color = 8, 60, (150, 100, 255)
            self.attack_radius, self.attack_style, self.crit_chance = 150, "homing", 10
        elif char_type == "dwarf":
            self.speed, self.max_health, self.color = 3, 150, (255, 250, 100)
            self.attack_radius, self.attack_style = 120, "melee"
            self.damage = 2 
            
        # 1. IELĀDĒT SPREITU LOKSNI
        try:
            if char_type == "shadow":
                sheet = pygame.image.load("photos/allOfShadow.png").convert_alpha()
                frame_w = 100 
                frame_h = 143 
                start_x = 258 
                start_y = 252 
                padding_x = 47 
                padding_y = 55 
                num_frames = 2 

            elif char_type == "wizard":
                sheet = pygame.image.load("photos/allOfWizard.png").convert_alpha()
                frame_w = 200    
                frame_h = 230    
                start_x = 1     
                start_y = 0     
                padding_x = 20     
                padding_y = 5     
                num_frames = 2 
            
            elif char_type == "dwarf":
                sheet = pygame.image.load("photos/allOfDwarf.png").convert_alpha()
                frame_w = 200    # Width of the box
                frame_h = 276       # Height of the box
                start_x = 0     # Distance from left edge to the first box
                start_y = 0   # Distance from top edge to the first box
                padding_x = 300     # Empty space between columns
                padding_y = 50    # Empty space between rows
                num_frames = 2     # Number of columns
                
            else:
                sheet = pygame.image.load(f"photos/{char_type}_sheet.png").convert_alpha()
        except:
            sheet = pygame.Surface((200, 200), pygame.SRCALPHA)
            sheet.fill((255, 0, 255))
            frame_w, frame_h, start_x, start_y = 50, 50, 0, 0
            padding_x, padding_y, num_frames = 0, 0, 1

        # 2. NOTĪRĪT IEPRIEKŠĒJĀS ANIMĀCIJAS
        self.animations = {"up": [], "down": [], "left": [], "right": []}

        # 3. IESTATĪT GRIEŠANAS DIMENSIJAS (Pielāgojiet šos, lai perfekti atbilstu jūsu attēlam)
        # 4 kadri katrai animācijai
        
        # 4. SAGRIEZT LOKSNI SARAKSTOS
        for i in range(num_frames):
            # Parasti UZ AUGŠU un UZ LEJU (Rinda 0 un Rinda 1)
            self.animations["up"].append(get_image_from_sheet(sheet, i, 0, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
            self.animations["down"].append(get_image_from_sheet(sheet, i, 1, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
            
            # Paņemt attēlu, kas skatās PA LABI (Rinda 3)
            img_right = get_image_from_sheet(sheet, i, 3, frame_w, frame_h, start_x, start_y, padding_x, padding_y)
            self.animations["right"].append(img_right)
            
            # Apgriezt PA LABI vērsto attēlu horizontāli, lai tas skatītos PA KREISI!
            # pygame.transform.flip(image, flip_x, flip_y)
            img_left = pygame.transform.flip(img_right, True, False)
            self.animations["left"].append(img_left)

        # Iestatīt sākotnējo attēlu
        self.direction = "down"
        self.frame_index = 0
        self.image = self.animations["down"][0]
        self.health = self.max_health

    # funkcija move pieņem list tipa vērtību keys un atgriež None tipa vērtību None
    def move(self, keys):
        dx, dy = 0, 0
        is_moving = False
        
        # Pārbaudīt Uz Augšu un Uz Leju
        if keys[pygame.K_w]: 
            dy -= 1
            self.direction = "up"
            is_moving = True
        if keys[pygame.K_s]:
            dy += 1
            self.direction = "down"
            is_moving = True
            
        # Pārbaudīt Pa Kreisi un Pa Labi (Izmantojot 'if' nevis 'elif'!)
        if keys[pygame.K_a]:
            dx -= 1
            self.direction = "left"
            is_moving = True
        if keys[pygame.K_d]:
            dx += 1
            self.direction = "right"
            is_moving = True

        # Normalizēt diagonālo kustību, lai tas nebūtu ātrāks
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2 ≈ 0.707
            dy *= 0.707

        # Pielietot ātrumu un pārvietojumu
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Apstrādāt animācijas loģiku
        if is_moving:
            self.anim_timer += self.anim_speed
            if self.anim_timer >= len(self.animations[self.direction]):
                self.anim_timer = 0
            self.frame_index = int(self.anim_timer)
        else:
            self.frame_index = 0 
            self.anim_timer = 0
            
        # Atjaunināt pašreizējo attēlu!
        if len(self.animations[self.direction]) > 0:
            self.image = self.animations[self.direction][self.frame_index]

    # funkcija _build_damage_vignette izveido sarkanu vinjetes virsmu ekrāna malām
    @staticmethod
    def _build_damage_vignette(w, h):
        """Pre-render a tiny soft red shadow only around screen edges — barely noticeable."""
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        # Only paint a very thin rim: 8 layers, each just a few pixels wide
        rim = 50          # total rim thickness in pixels
        steps = 10
        corner_r = max(0, min(w, h) // 10)   # large corner radius so it feels round/organic
        for i in range(steps, 0, -1):
            t = i / steps                     # 1 at outermost, ~0 at innermost
            alpha = int(t ** 2.5 * 72)        # peaks at ~72 at outermost ring, drops fast → very subtle
            shrink = int((1 - t) * rim)
            rect = pygame.Rect(shrink, shrink, w - shrink * 2, h - shrink * 2)
            border_w = max(2, rim // steps + 1)
            pygame.draw.rect(surf, (210, 0, 0, alpha), rect, border_w,
                             border_radius=max(corner_r - shrink, 8))
        return surf.convert_alpha()

    def trigger_damage_flash(self):
        """Call this whenever the player takes damage to start the red edge flash."""
        self.damage_flash_timer = self.damage_flash_duration

    def draw_damage_flash(self, screen):
        """Render a red vignette around screen edges, fading out over time."""
        if self.damage_flash_timer <= 0:
            return
        # Ease-out fade: strongest right after hit, fades quickly
        t = self.damage_flash_timer / self.damage_flash_duration   # 1.0 → 0.0
        alpha = int(t ** 0.6 * 255) 
        self._damage_vignette.set_alpha(alpha) 
        screen.blit(self._damage_vignette, (0, 0))
        self.damage_flash_timer = max(0, self.damage_flash_timer - 1)

    # funkcija draw_darkness pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw_darkness(self, screen, flicker_val):
        self.darkness_surf.fill((5, 5, 15, self.darkness_intensity))
        pulse = int(6 * math.sin(flicker_val))
        light_radius = int(self.attack_radius * 1.4) + pulse
        t_surf = pygame.Surface((light_radius * 2, light_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(t_surf, (0, 0, 0, 255), (light_radius, light_radius), light_radius // 2)
        for r in range(light_radius, light_radius // 2, -1):
            alpha_to_remove = int(255 * (1 - (r - light_radius // 2) / (light_radius // 2)))
            pygame.draw.circle(t_surf, (0, 0, 0, alpha_to_remove), (light_radius, light_radius), r)
        self.darkness_surf.blit(t_surf, t_surf.get_rect(center=self.rect.center), special_flags=pygame.BLEND_RGBA_SUB)
        screen.blit(self.darkness_surf, (0, 0))

    # funkcija draw pieņem pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # Uzzīmēt Ēnu
        shadow_pos = (self.rect.x, self.rect.bottom - 10) 
        screen.blit(self.shadow_surf, shadow_pos)

        # DROŠI Uzzīmēt Spēlētāja Spreitu
        if self.image:
            # Apstrādāt Dash (izrāviena) caurspīdīgumu
            if self.dash_cooldown > 0:
                self.image.set_alpha(150) 
            else:
                self.image.set_alpha(255)

            draw_pos = self.image.get_rect(center=self.rect.center)
            screen.blit(self.image, draw_pos)

        # Draw speech bubble if in kill mode
        if getattr(self, 'kill_mode', False):
            self._draw_speech_bubble(screen)

    # funkcija _draw_speech_bubble pieņem Player tipa vērtību self un pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def _draw_speech_bubble(self, screen): # Šī funkcija tiek izsaukta tikai tad, kad spēlētājs ir "kill mode" stāvoklī
        
        kill_timer = getattr(self, 'kill_timer', 0)
        kill_duration = getattr(self, 'kill_duration', 180)
        
        if kill_timer >= kill_duration:
            bubble_text = "Goodbye, cruel world..."
        elif kill_timer > kill_duration * 0.66:
            bubble_text = "Is This Really The End?"
        elif kill_timer > kill_duration * 0.33:
            bubble_text = "Is This The End?"
        else:
            bubble_text = "Hold K to end it all..."
            
        text_surface = render_pixel_text(bubble_text, 14, (0, 0, 0), bold=True)
        
        # Bubble dimensions
        text_width = text_surface.get_width()
        text_height = text_surface.get_height()
        padding = 10
        bubble_width = text_width + padding * 2
        bubble_height = text_height + padding * 2
        
        # Bubble position (above player's head)
        bubble_x = self.rect.centerx - bubble_width // 2
        bubble_y = self.rect.top - bubble_height - 20
        
        # Draw bubble background (white with black border)
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        pygame.draw.rect(screen, (255, 255, 255), bubble_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2, border_radius=8)
        
        # Draw pointer/tail pointing down to player
        pointer_x = self.rect.centerx
        pointer_y = self.rect.top - 20
        pointer_points = [
            (pointer_x, pointer_y),
            (pointer_x - 8, pointer_y - 10),
            (pointer_x + 8, pointer_y - 10)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), pointer_points)
        pygame.draw.polygon(screen, (0, 0, 0), pointer_points, 2)
        
        # Draw text centered in bubble
        text_x = bubble_x + (bubble_width - text_width) // 2
        text_y = bubble_y + (bubble_height - text_height) // 2
        screen.blit(text_surface, (text_x, text_y))
        
        # Draw progress bar for kill timer
        if kill_timer > 0 and kill_timer < kill_duration:
            progress_width = int((kill_timer / kill_duration) * (bubble_width - 20))
            progress_rect = pygame.Rect(bubble_x + 10, bubble_y + bubble_height - 8, progress_width, 4)
            pygame.draw.rect(screen, (255, 0, 0), progress_rect)  # Red progress bar