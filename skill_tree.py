import pygame
import math

class SkillTree:
    # funkcija __init__ pieņem SkillTree tipa vērtību self, int tipa vērtību screen_w un int tipa vērtību screen_h un atgriež None tipa vērtību None
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        self.title_font = pygame.font.SysFont("Impact", 16)
        self.stat_font = pygame.font.SysFont("Arial", 13, bold=True)
        self.price_font = pygame.font.SysFont("Consolas", 13, bold=True)
        
        self.circle_radius = 38 
        self.animation_timer = 0
        
        # [SAREŽĢĪTA LOĢIKA]: Koka centrālo koordinātu aprēķins
        # Mēs iegūstam ekrāna centru un izmantojam to kā izejas punktu.
        # Visas spējas tiks izvietotas, saskaitot vai atņemot pikseļus no šī centra,
        # veidojot zvaigznes jeb sazarota koka vizuālo izskatu.
        center_x = screen_w // 2
        center_y = screen_h // 2

        # --- SKILL DEFINITIONS (Kategorizēts un sakārtots) ---
        self.skills = [
            # CENTRS: CORE (Enerģija centrā)
            {"id": "stamina", "name": "MAX ENERGY", "pos": (center_x, center_y), "cost": 60, "level": 0, "max": 15, "color": (0, 255, 255), "req": None, "currency": "gold"},

            # ZARS UZ AUGŠU: OFFENSE (Bojājumi, uzbrukums un atsišana)
            {"id": "damage", "name": "ATTACK POWER", "pos": (center_x, center_y - 130), "cost": 54, "level": 0, "max": 10, "color": (255, 150, 50), "req": None, "currency": "gold"},
            
            {"id": "lifesteal", "name": "LIFE STEAL", "pos": (center_x, center_y - 260), "cost": 4, "level": 0, "max": 5, "color": (150, 0, 0), "req": "damage", "currency": "sp"},
            
            {"id": "range", "name": "ATTACK RANGE", "pos": (center_x - 120, center_y - 220), "cost": 40, "level": 0, "max": 10, "color": (255, 220, 50), "req": "damage", "currency": "gold"},
            {"id": "knockback", "name": "KNOCKBACK", "pos": (center_x - 120, center_y - 330), "cost": 45, "level": 0, "max": 8, "color": (200, 200, 200), "req": "range", "currency": "gold"},
            
            {"id": "multi", "name": "MULTI-PROJECTILE", "pos": (center_x + 120, center_y - 220), "cost": 3, "level": 0, "max": 3, "color": (255, 255, 100), "req": "damage", "currency": "sp"},
            {"id": "crit", "name": "CRIT CHANCE", "pos": (center_x + 120, center_y - 330), "cost": 50, "level": 0, "max": 10, "color": (255, 0, 0), "req": "multi", "currency": "gold"},

            # ZARS UZ LEJU: DEFENSE (Dzīvība un aizsardzība)
            {"id": "health", "name": "MAX HEALTH", "pos": (center_x, center_y + 130), "cost": 20, "level": 0, "max": 10, "color": (255, 60, 60), "req": None, "currency": "gold"},
            {"id": "armor", "name": "ARMOR", "pos": (center_x + 120, center_y + 240), "cost": 55, "level": 0, "max": 10, "color": (120, 120, 120), "req": "health", "currency": "gold"},
            {"id": "regen", "name": "HP REGEN", "pos": (center_x - 120, center_y + 240), "cost": 4, "level": 0, "max": 5, "color": (255, 105, 180), "req": "health", "currency": "sp"},
            {"id": "thorns", "name": "THORN DAMAGE", "pos": (center_x + 120, center_y + 350), "cost": 3, "level": 0, "max": 5, "color": (34, 139, 34), "req": "armor", "currency": "sp"},

            # ZARS PA KREISI: UTILITY (Nauda un magnēts)
            {"id": "magnet", "name": "COIN MAGNET", "pos": (center_x - 160, center_y), "cost": 35, "level": 0, "max": 10, "color": (100, 100, 255), "req": None, "currency": "gold"},
            {"id": "greed", "name": "EXTRA GOLD", "pos": (center_x - 290, center_y), "cost": 3, "level": 0, "max": 5, "color": (255, 215, 0), "req": "magnet", "currency": "sp"},

            # ZARS PA LABI: MOVEMENT (Kustība)
            {"id": "speed", "name": "MOVE SPEED", "pos": (center_x + 160, center_y), "cost": 40, "level": 0, "max": 10, "color": (50, 255, 150), "req": None, "currency": "gold"},
            {"id": "dash", "name": "UNLOCK DASH", "pos": (center_x + 290, center_y), "cost": 2, "level": 0, "max": 1, "color": (255, 0, 150), "req": "speed", "currency": "sp"},
            {"id": "dash_cd", "name": "DASH COOLDOWN", "pos": (center_x + 420, center_y), "cost": 2, "level": 0, "max": 5, "color": (255, 100, 200), "req": "dash", "currency": "sp"},
        ]
        
        for skill_node in self.skills:
            skill_node["req_node"] = next((n for n in self.skills if n["id"] == skill_node["req"]), None) if skill_node["req"] else None
            skill_node["base_cost"] = skill_node["cost"] 

        self.respawn_btn = pygame.Rect(screen_w // 2 - 90, screen_h - 75, 180, 45)
        self.vignette = self._create_vignette()

    # funkcija _create_vignette pieņem SkillTree tipa vērtību self un atgriež pygame.Surface tipa vērtību vignette_surface
    def _create_vignette(self):
        vignette_surface = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        for r in range(0, 600, 40):
            alpha = int(min(255, (r / 600) * 220))
            pygame.draw.rect(vignette_surface, (0, 0, 0, alpha), vignette_surface.get_rect(), 600-r)
        return vignette_surface.convert_alpha()

    # funkcija sync_with_player pieņem SkillTree tipa vērtību self un Player tipa vērtību player un atgriež None tipa vērtību None
    def sync_with_player(self, player):
        for skill_node in self.skills:
            lvl = skill_node["level"]
            if lvl <= 0: continue
            
            if skill_node["id"] == "health": player.max_health += (player.max_health * 0.1) * lvl
            elif skill_node["id"] == "armor": player.armor = getattr(player, 'armor', 0) + lvl
            elif skill_node["id"] == "thorns": player.thorns = getattr(player, 'thorns', 0) + lvl
            elif skill_node["id"] == "regen": player.regen = getattr(player, 'regen', 0) + (0.01 * lvl)
            elif skill_node["id"] == "range": player.attack_radius = min(50, player.attack_radius + (15 * lvl))
            elif skill_node["id"] == "multi": player.projectile_count = min(5, 1 + lvl)
            elif skill_node["id"] == "speed": player.speed += (0.4 * lvl) # Izlabots ātruma limits
            elif skill_node["id"] == "damage": player.damage += 0.5 * lvl
            elif skill_node["id"] == "magnet": player.magnet_range = min(300, player.magnet_range + (15 * lvl))
            elif skill_node["id"] == "dash": player.dash_unlocked = True
            elif skill_node["id"] == "stamina": player.max_energy += 5 * lvl
            elif skill_node["id"] == "crit": player.crit_chance = getattr(player, 'crit_chance', 0) + (5 * lvl)
            elif skill_node["id"] == "lifesteal": player.lifesteal = getattr(player, 'lifesteal', 0) + lvl

            if skill_node["currency"] == "gold":
                skill_node["cost"] = int(skill_node["base_cost"] * (1.5 ** lvl))

        player.health = player.max_health
        player.energy = player.max_energy

    # funkcija handle_click pieņem SkillTree tipa vērtību self, tuple tipa vērtību pos un Player tipa vērtību player un atgriež str tipa vērtību result
    def handle_click(self, pos, player):
        if self.respawn_btn.collidepoint(pos): return "respawn"
        
        for skill_node in self.skills:
            if math.hypot(pos[0] - skill_node["pos"][0], pos[1] - skill_node["pos"][1]) < self.circle_radius:
                if skill_node["level"] >= skill_node["max"]: continue
                if skill_node["req_node"] and skill_node["req_node"]["level"] < 1: continue

                if skill_node["currency"] == "gold":
                    if player.money >= skill_node["cost"]: player.money -= skill_node["cost"]
                    else: continue
                elif skill_node["currency"] == "sp":
                    if player.skill_points >= skill_node["cost"]: player.skill_points -= skill_node["cost"]
                    else: continue

                skill_node["level"] += 1

                # --- IMMEDIATE PLAYER UPDATES ---
                if skill_node["id"] == "health":
                    player.max_health += player.max_health * 0.1
                    player.health += player.max_health * 0.1
                elif skill_node["id"] == "armor":
                    player.armor = getattr(player, 'armor', 0) + 1
                elif skill_node["id"] == "regen":
                    player.regen = getattr(player, 'regen', 0) + 0.01
                elif skill_node["id"] == "range":
                    player.attack_radius = min(500, player.attack_radius + 15)
                elif skill_node["id"] == "multi":
                    player.projectile_count = min(5, getattr(player, 'projectile_count', 1) + 1)
                elif skill_node["id"] == "damage":
                    player.damage += 0.5
                elif skill_node["id"] == "speed":
                    player.speed += 0.3 # Izlabots ātruma limits
                elif skill_node["id"] == "magnet":
                    player.magnet_range = min(300, player.magnet_range + 15)
                elif skill_node["id"] == "dash":
                    player.dash_unlocked = True
                elif skill_node["id"] == "stamina":
                    player.max_energy += 5
                elif skill_node["id"] == "crit":
                    player.crit_chance = getattr(player, 'crit_chance', 0) + 5
                
                if skill_node["currency"] == "gold":
                    skill_node["cost"] = int(skill_node["cost"] * 1.5)
                
                return "saved"
        return None

    # funkcija draw_connection pieņem SkillTree tipa vērtību self, pygame.Surface tipa vērtību surface, tuple tipa vērtību start, tuple tipa vērtību end un bool tipa vērtību active un atgriež None tipa vērtību None
    def draw_connection(self, surface, start, end, active):
        line_color = (180, 180, 255, 150) if active else (40, 40, 50, 80)
        pygame.draw.line(surface, line_color, start, end, 2)

    # funkcija draw pieņem SkillTree tipa vērtību self, pygame.Surface tipa vērtību screen, int tipa vērtību money, int tipa vērtību sp un str tipa vērtību char_type un atgriež None tipa vērtību None
    def draw(self, screen, money, sp, char_type):
        self.animation_timer += 1
        screen.blit(self.vignette, (0, 0))
        
        screen.blit(self.stat_font.render(f"GOLD: ${money}", True, (255, 215, 0)), (40, 40))
        screen.blit(self.stat_font.render(f"SKILL POINTS: {sp}", True, (0, 255, 150)), (40, 65))

        mouse_pos = pygame.mouse.get_pos()
        
        # Atrod centrālo "stamina" mezglu vizuālajiem savienojumiem
        stamina_node = next(n for n in self.skills if n["id"] == "stamina")
        
        # [SAREŽĢĪTA LOĢIKA]: Vizuālo savienojumu (līniju) zīmēšana koka formā
        # Ja spējai ir tieša prasība (req_node), mēs zīmējam līniju uz to.
        # Ja prasības nav (piemēram, "damage", "health", "speed", "magnet"), 
        # mēs mākslīgi uzzīmējam līniju uz centrālo "stamina" mezglu, 
        # lai vizuāli radītu vienota, centrēta koka efektu!
        for skill_node in self.skills:
            if skill_node["req_node"]:
                self.draw_connection(screen, skill_node["req_node"]["pos"], skill_node["pos"], skill_node["level"] > 0)
            elif skill_node["id"] != "stamina":
                self.draw_connection(screen, stamina_node["pos"], skill_node["pos"], True)

        for skill_node in self.skills:
            node_x, node_y = skill_node["pos"]
            dist_sq = (mouse_pos[0] - node_x)**2 + (mouse_pos[1] - node_y)**2
            is_hovered = dist_sq < self.circle_radius**2
            radius = self.circle_radius + (3 if is_hovered else 0)

            pygame.draw.circle(screen, (30, 30, 45) if not is_hovered else (55, 55, 80), (node_x, node_y), radius)
            pygame.draw.circle(screen, skill_node["color"], (node_x, node_y), radius, 2)

            for i in range(skill_node["max"]):
                dot_color = skill_node["color"] if i < skill_node["level"] else (60, 60, 60)
                angle = (i / skill_node["max"]) * 6.283 - 1.57
                px, py = node_x + math.cos(angle) * (radius + 8), node_y + math.sin(angle) * (radius + 8)
                pygame.draw.circle(screen, dot_color, (int(px), int(py)), 2)

            name_text = self.title_font.render(skill_node["name"], True, (255, 255, 255))
            level_text = self.stat_font.render(f"{skill_node['level']}/{skill_node['max']}", True, skill_node["color"])
            screen.blit(name_text, name_text.get_rect(center=(node_x, node_y - 8)))
            screen.blit(level_text, level_text.get_rect(center=(node_x, node_y + 10)))

            if skill_node["level"] < skill_node["max"]:
                cost_text = f"${skill_node['cost']}" if skill_node["currency"] == "gold" else f"{skill_node['cost']} SP"
                cost_color = (255, 215, 0) if skill_node["currency"] == "gold" else (0, 255, 200)
                cost_surface = self.price_font.render(cost_text, True, cost_color)
                screen.blit(cost_surface, cost_surface.get_rect(center=(node_x, node_y + radius + 25)))

        pygame.draw.rect(screen, (0, 255, 150), self.respawn_btn, border_radius=12)
        btn_text = self.title_font.render("RESUME", True, (0, 0, 0))
        screen.blit(btn_text, btn_text.get_rect(center=self.respawn_btn.center))