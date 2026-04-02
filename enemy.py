import pygame
import math

# funkcija get_image_from_sheet pieņem pygame.Surface tipa vērtību sheet, int tipa vērtību column, int tipa vērtību row, int tipa vērtību width un int tipa vērtību height un atgriež pygame.Surface tipa vērtību image
def get_image_from_sheet(sheet, column, row, width, height, start_x=0, start_y=0, padding_x=0, padding_y=0, scale_size=(50, 50)):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    exact_x = start_x + (column * width) + (column * padding_x)
    exact_y = start_y + (row * height) + (row * padding_y)
    
    crop_rect = pygame.Rect(exact_x, exact_y, width, height)
    image.blit(sheet, (0, 0), crop_rect)
    return pygame.transform.scale(image, scale_size)

# Globālā kešatmiņa (Cache), lai saglabātu sagrieztos kadrus un novērstu aizķeršanos (lag) viļņu beigās.
_ENEMY_ANIMATIONS_CACHE = None

class Enemy:
    # funkcija __init__ pieņem Enemy tipa vērtību self, int tipa vērtību x un int tipa vērtību y un atgriež None tipa vērtību None
    def __init__(self, x, y):
        global _ENEMY_ANIMATIONS_CACHE
        
        self.rect = pygame.Rect(x, y, 40, 40)
        self.max_health = 3
        self.health = 3
        self.speed = 2.0
        self.armor = 0

        # --- ANIMĀCIJAS MAINĪGIE ---
        self.direction = "down"
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2

        # [SAREŽĢĪTA LOĢIKA]: Attēlu ielāde ar kešatmiņu (Cache)
        # Lai novērstu spēles apstāšanos (lag spikes), kad parādās daudz jaunu ienaidnieku,
        # bilde tiek ielādēta un sagriezta tikai VIENU REIZI pašā sākumā.
        # Pārējie ienaidnieki vienkārši izmanto jau sagatavotos kadrus no atmiņas (_ENEMY_ANIMATIONS_CACHE).
        if _ENEMY_ANIMATIONS_CACHE is None:
            _ENEMY_ANIMATIONS_CACHE = {"up": [], "down": [], "left": [], "right": []}
            try:
                sheet = pygame.image.load("photos/allOfEnemies.png").convert_alpha()
                
                # Šos skaitļus ieguvu no sava griešanas rīks (Google Gemini izveidoja riiku):
                frame_w = 190     # Rāmja platums
                frame_h = 225     # Rāmja augstums
                start_x = 62       # Sākuma X pozīcija
                start_y = 310      # Sākuma Y pozīcija
                padding_x = 42     # Atstarpe starp rāmjiem horizontāli
                padding_y = 43     # Atstarpe starp rāmjiem vertikāli
                num_frames = 2     # Kadru skaits vienā rindā
                
                # Izgriežam kadrus no loksnes katram virzienam un saglabājam kešatmiņā
                for i in range(num_frames):
                    # Rinda 0: Uz augšu (skatās prom)
                    _ENEMY_ANIMATIONS_CACHE["up"].append(get_image_from_sheet(sheet, i, 0, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
                    # Rinda 1: Uz leju (skatās uz mums)
                    _ENEMY_ANIMATIONS_CACHE["down"].append(get_image_from_sheet(sheet, i, 1, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
                    
                    # Rinda 2: Skatās pa labi
                    img_right = get_image_from_sheet(sheet, i, 2, frame_w, frame_h, start_x, start_y, padding_x, padding_y)
                    _ENEMY_ANIMATIONS_CACHE["right"].append(img_right)
                    
                    # Apgriežam "pa labi" bildi, lai iegūtu "pa kreisi"
                    img_left = pygame.transform.flip(img_right, True, False)
                    _ENEMY_ANIMATIONS_CACHE["left"].append(img_left)

            except:
                # Ja bildi neatrod, rāda sarkanu kvadrātu
                surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 50, 50), (0, 0, 40, 40))
                _ENEMY_ANIMATIONS_CACHE = {"up": [surf], "down": [surf], "left": [surf], "right": [surf]}

        # Piešķiram ienaidniekam jau ielādēto animāciju vārdnīcu no globālās atmiņas
        self.animations = _ENEMY_ANIMATIONS_CACHE
        self.image = self.animations["down"][0]

    # funkcija update pieņem Enemy tipa vērtību self, pygame.Rect tipa vērtību player_rect un float tipa vērtību dilation un atgriež None tipa vērtību None
    def update(self, player_rect, dilation):
        # 1. Aprēķina distanci
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        is_moving = False
        
        # [SAREŽĢĪTA LOĢIKA]: Kustības loģika un virziena noteikšana
        # Ienaidnieks pārvietojas pretī spēlētājam, ņemot vērā ātrumu un laika palēninājumu (dilation).
        if dist > 0:
            move_x = (dx / dist) * self.speed * dilation
            move_y = (dy / dist) * self.speed * dilation
            
            self.rect.x += move_x
            self.rect.y += move_y
            is_moving = True

            # Nosakām, kurā virzienā ienaidnieks kustas visvairāk (lai izvēlētos pareizo animāciju).
            # Ja X ass kustība ir lielāka nekā Y ass, tātad ienaidnieks pārvietojas horizontāli.
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"

        # 3. Animācijas atjaunināšana
        if is_moving and len(self.animations[self.direction]) > 0:
            self.anim_timer += self.anim_speed * dilation
            if self.anim_timer >= len(self.animations[self.direction]):
                self.anim_timer = 0
            
            self.frame_index = int(self.anim_timer)
            self.image = self.animations[self.direction][self.frame_index]

    # funkcija draw pieņem Enemy tipa vērtību self un pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)
        
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 8, self.rect.width, 4))
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 8, self.rect.width * health_ratio, 4))