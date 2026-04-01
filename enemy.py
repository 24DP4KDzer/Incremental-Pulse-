import pygame
import math

# --- GUDRO SPREITU GRIEŠANAS FUNKCIJA (Tāda pati kā spēlētājam!) ---
def get_image_from_sheet(sheet, column, row, width, height, start_x=0, start_y=0, padding_x=0, padding_y=0, scale_size=(50, 50)):
    image = pygame.Surface((width, height), pygame.SRCALPHA)
    exact_x = start_x + (column * width) + (column * padding_x)
    exact_y = start_y + (row * height) + (row * padding_y)
    
    crop_rect = pygame.Rect(exact_x, exact_y, width, height)
    image.blit(sheet, (0, 0), crop_rect)
    return pygame.transform.scale(image, scale_size)

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.max_health = 10
        self.health = 10
        self.speed = 2.0
        self.armor = 0

        # --- ANIMĀCIJAS MAINĪGIE ---
        self.animations = {"up": [], "down": [], "left": [], "right": []}
        self.direction = "down"
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.2

        # 1. IELĀDĒT SPREITU LOKSNI
        try:
            sheet = pygame.image.load("photos/allOfEnemies.png").convert_alpha()
            


            # šos skaitļus ieguvu no sava griešanas rīks (Google Gemini izveidoja riiku):

            frame_w = 190     # Rāmja platums
            frame_h = 225     # Rāmja augstums
            start_x = 62       # Sākuma X pozīcija
            start_y = 310       # Sākuma Y pozīcija
            padding_x = 42     # Atstarpe starp rāmjiem horizontāli
            padding_y = 43     # Atstarpe starp rāmjiem vertikāli
            num_frames = 2    # Kadru skaits vienā rindā
            # ==========================================
            
            # Izgriežam kadrus no loksnes katram virzienam
            for i in range(num_frames):
                # Rinda 0: Uz augšu (skatās prom)
                self.animations["up"].append(get_image_from_sheet(sheet, i, 0, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
                # Rinda 1: Uz leju (skatās uz mums)
                self.animations["down"].append(get_image_from_sheet(sheet, i, 1, frame_w, frame_h, start_x, start_y, padding_x, padding_y))
                
                # Rinda 2: Skatās pa labi
                img_right = get_image_from_sheet(sheet, i, 2, frame_w, frame_h, start_x, start_y, padding_x, padding_y)
                self.animations["right"].append(img_right)
                
                # Apgriežam "pa labi" bildi, lai iegūtu "pa kreisi"
                img_left = pygame.transform.flip(img_right, True, False)
                self.animations["left"].append(img_left)

        except:
            # Ja bildi neatrod, rāda sarkanu kvadrātu
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 50, 50), (0, 0, 40, 40))
            self.animations = {"up": [surf], "down": [surf], "left": [surf], "right": [surf]}

        self.image = self.animations["down"][0]

    def update(self, player_rect, dilation):
        # 1. Aprēķina distanci
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        is_moving = False
        
        # 2. Kustības loģika un virziena noteikšana
        if dist > 0:
            move_x = (dx / dist) * self.speed * dilation
            move_y = (dy / dist) * self.speed * dilation
            
            self.rect.x += move_x
            self.rect.y += move_y
            is_moving = True

            # Nosakām, kurā virzienā ienaidnieks kustas visvairāk (lai izvēlētos pareizo animāciju)
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

    def draw(self, screen):
        draw_rect = self.image.get_rect(center=self.rect.center)
        screen.blit(self.image, draw_rect)
        
        if self.health < self.max_health:
            health_ratio = max(0, self.health / self.max_health)
            pygame.draw.rect(screen, (255, 0, 0), (self.rect.x, self.rect.y - 8, self.rect.width, 4))
            pygame.draw.rect(screen, (0, 255, 0), (self.rect.x, self.rect.y - 8, self.rect.width * health_ratio, 4))