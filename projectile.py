import pygame

class Projectile:
    # funkcija __init__ pieņem Projectile tipa vērtību self, int tipa vērtību x, int tipa vērtību y, object tipa vērtību target, tuple tipa vērtību color un int tipa vērtību max_range un atgriež None tipa vērtību None
    def __init__(self, x, y, target, color, max_range):
        self.start_pos = pygame.math.Vector2(x, y)
        self.pos = pygame.math.Vector2(x, y)
        self.target = target
        self.speed = 10
        self.radius = 8
        self.color = color
        self.max_range = max_range # Range limit (Maksimālais lidojuma attālums)
        self.rect = pygame.Rect(x, y, self.radius*2, self.radius*2)

    # funkcija update pieņem Projectile tipa vērtību self un list tipa vērtību enemies_list un atgriež bool tipa vērtību is_active
    def update(self, enemies_list):
        # 1. Distances pārbaude: Iznīcināt lādiņu (atgriezt False), ja tas aizlido pārāk tālu no sava sākuma punkta
        if self.pos.distance_to(self.start_pos) > self.max_range:
            return False

        # [SAREŽĢĪTA LOĢIKA]: Pašmērķēšanas (Homing) sistēma
        # Vispirms pārbauda, vai mērķis (target) joprojām ir dzīvs un atrodas ienaidnieku sarakstā.
        if self.target in enemies_list:
            # Izveido virziena vektoru, atņemot lādiņa pozīciju no mērķa pozīcijas
            direction = pygame.math.Vector2(self.target.rect.center) - self.pos
            
            # Normalizē vektoru (padara tā garumu precīzi 1). 
            # Tas ir svarīgi, lai lādiņš vienmēr lidotu ar nemainīgu ātrumu (self.speed), neatkarīgi no tā, cik tālu ir mērķis.
            if direction.length() > 0:
                direction.normalize_ip()
            
            # Pievieno normalizēto virzienu (reizinātu ar ātrumu) lādiņa pašreizējai pozīcijai
            self.pos += direction * self.speed
            
            # Atjaunina sadursmes kastes (rect) centru, lai tas sakristu ar jauno pozīciju
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            return True # Lādiņš veiksmīgi kustas un joprojām ir aktīvs
            
        return False # Ja mērķis vairs neeksistē, lādiņš tiek iznīcināts

    # funkcija draw pieņem Projectile tipa vērtību self un pygame.Surface tipa vērtību screen un atgriež None tipa vērtību None
    def draw(self, screen):
        # Uzzīmē lādiņu kā apli
        pygame.draw.circle(screen, self.color, self.rect.center, self.radius)