import pygame
import math

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
        self.dash_unlocked = False

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
        else:
            # Atkāpšanās variants, ja attēls pilnībā neielādējas
            pygame.draw.rect(screen, self.color, self.rect)
        
        # Vizuālais efekts tuvcīņas (Melee) uzbrukumiem
        if self.attacking and self.attack_style == "melee":
            alpha_radius = int(self.attack_radius * (self.attack_timer / 15))
            pygame.draw.circle(screen, (255, 255, 255), self.rect.center, alpha_radius, 3)