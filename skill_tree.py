import pygame
import math

class SkillTree:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        
        self.title_font = pygame.font.SysFont("Impact", 16)
        self.stat_font = pygame.font.SysFont("Arial", 13, bold=True)
        self.price_font = pygame.font.SysFont("Consolas", 13, bold=True)
        
        self.circle_radius = 38 
        self.animation_timer = 0
        
        cx, cy = screen_w // 2, screen_h // 2
        col1, col2, col3, col4, col5 = cx - 550, cx - 275, cx, cx + 275, cx + 550
        row1, row2, row3, row4 = cy - 250, cy - 80, cy + 90, cy + 260

        self.skills = [
           # --- COLUMN 1: DEFENSE ---
            {"id": "health", "name": "MAX HEALTH", "pos": (col1, row1), "cost": 48, "level": 0, "max": 10, "color": (255, 60, 60), "req": None, "currency": "gold"},
            {"id": "armor", "name": "ARMOR", "pos": (col1, row2), "cost": 55, "level": 0, "max": 10, "color": (120, 120, 120), "req": "health", "currency": "gold"},
            {"id": "thorns", "name": "THORN DAMAGE", "pos": (col1, row3), "cost": 3, "level": 0, "max": 5, "color": (34, 139, 34), "req": "armor", "currency": "sp"},
            {"id": "regen", "name": "HP REGEN", "pos": (col1, row4), "cost": 4, "level": 0, "max": 5, "color": (255, 105, 180), "req": "health", "currency": "sp"},

            # --- COLUMN 2: UTILITY ---
            {"id": "magnet", "name": "COIN MAGNET", "pos": (col2, row1), "cost": 35, "level": 0, "max": 10, "color": (100, 100, 255), "req": None, "currency": "gold"},
            {"id": "greed", "name": "EXTRA GOLD", "pos": (col2, row2), "cost": 3, "level": 0, "max": 5, "color": (255, 215, 0), "req": "magnet", "currency": "sp"},
            {"id": "knockback", "name": "KNOCKBACK", "pos": (col2, row3), "cost": 45, "level": 0, "max": 8, "color": (200, 200, 200), "req": "greed", "currency": "gold"},
            {"id": "lifesteal", "name": "LIFE STEAL", "pos": (col2, row4), "cost": 4, "level": 0, "max": 5, "color": (150, 0, 0), "req": "knockback", "currency": "sp"},

            # --- COLUMN 3: CORE ---
            {"id": "stamina", "name": "MAX ENERGY", "pos": (col3, row1), "cost": 60, "level": 0, "max": 15, "color": (0, 255, 255), "req": None, "currency": "gold"},
            

            # --- COLUMN 4: MOVEMENT ---
            {"id": "speed", "name": "MOVE SPEED", "pos": (col4, row1), "cost": 40, "level": 0, "max": 10, "color": (50, 255, 150), "req": None, "currency": "gold"},
            {"id": "dash", "name": "UNLOCK DASH", "pos": (col4, row2), "cost": 2, "level": 0, "max": 1, "color": (255, 0, 150), "req": "speed", "currency": "sp"},
            {"id": "dash_cd", "name": "DASH COOLDOWN", "pos": (col4, row3), "cost": 2, "level": 0, "max": 5, "color": (255, 100, 200), "req": "dash", "currency": "sp"},

            # --- COLUMN 5: OFFENSE ---
            {"id": "damage", "name": "ATTACK POWER", "pos": (col5, row1), "cost": 54, "level": 0, "max": 10, "color": (255, 150, 50), "req": None, "currency": "gold"},
            {"id": "range", "name": "ATTACK RANGE", "pos": (col5, row2), "cost": 40, "level": 0, "max": 10, "color": (255, 220, 50), "req": "damage", "currency": "gold"},
            {"id": "multi", "name": "MULTI-PROJECTILE", "pos": (col5, row3), "cost": 3, "level": 0, "max": 3, "color": (255, 255, 100), "req": "damage", "currency": "sp"},
            {"id": "crit", "name": "CRIT CHANCE", "pos": (col5, row4), "cost": 50, "level": 0, "max": 10, "color": (255, 0, 0), "req": "multi", "currency": "gold"},
        ]
        
        # PRE-LINK FOR PERFORMANCE
        for s in self.skills:
            s["req_node"] = next((n for n in self.skills if n["id"] == s["req"]), None) if s["req"] else None

        self.respawn_btn = pygame.Rect(screen_w//2 - 90, screen_h - 75, 180, 45)
        self.vignette = self._create_vignette()

    def _create_vignette(self):
        surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        for r in range(0, 600, 40):
            alpha = int(min(255, (r / 600) * 220))
            pygame.draw.rect(surf, (0, 0, 0, alpha), surf.get_rect(), 600-r)
        return surf.convert_alpha()

    def sync_with_player(self, player):
        """Standardizes stats. Range and Multi have HARD CAPS to stop lag."""
        for s in self.skills:
            lvl = s["level"]
            if lvl <= 0: continue
            
            if s["id"] == "health": player.max_health += 20 * lvl
            elif s["id"] == "range": 
                # 250px is the stability limit for Pygame targeting
                player.attack_radius = min(300, player.attack_radius + (15 * lvl))
            elif s["id"] == "multi": 
                # 5 projectiles is the limit for physics stability
                player.projectiles_count = min(5, 1 + lvl)
            elif s["id"] == "speed": 
                player.speed = min(6.5, player.speed + (0.4 * lvl))
            elif s["id"] == "damage": 
                player.damage += 0.5 * lvl
            elif s["id"] == "magnet": 
                player.magnet_range = min(300, player.magnet_range + (15 * lvl))

            if s["currency"] == "gold":
                s["cost"] = int(s["cost"] * (1.5 ** lvl))

        player.health, player.energy = player.max_health, player.max_energy

    def draw_connection(self, surface, start, end, active):
        col = (180, 180, 255, 150) if active else (40, 40, 50, 80)
        pygame.draw.line(surface, col, start, end, 2)

    def draw(self, screen, money, sp, char_type):
        self.animation_timer += 1
        screen.blit(self.vignette, (0,0))
        
        screen.blit(self.stat_font.render(f"GOLD: ${money}", True, (255, 215, 0)), (40, 40))
        screen.blit(self.stat_font.render(f"SKILL POINTS: {sp}", True, (0, 255, 150)), (40, 65))

        m_pos = pygame.mouse.get_pos()
        
        for s in self.skills:
            if s["req_node"]:
                self.draw_connection(screen, s["req_node"]["pos"], s["pos"], s["level"] > 0)

        for s in self.skills:
            x, y = s["pos"]
            dist_sq = (m_pos[0]-x)**2 + (m_pos[1]-y)**2
            is_hovered = dist_sq < self.circle_radius**2
            radius = self.circle_radius + (3 if is_hovered else 0)

            pygame.draw.circle(screen, (30, 30, 45) if not is_hovered else (55, 55, 80), (x, y), radius)
            pygame.draw.circle(screen, s["color"], (x, y), radius, 2)

            # Optimization: Pre-calculate Pi
            for i in range(s["max"]):
                dot_col = s["color"] if i < s["level"] else (60, 60, 60)
                angle = (i / s["max"]) * 6.283 - 1.57
                px, py = x + math.cos(angle)*(radius+8), y + math.sin(angle)*(radius+8)
                pygame.draw.circle(screen, dot_col, (int(px), int(py)), 2)

            name_s = self.title_font.render(s["name"], True, (255, 255, 255))
            lvl_s = self.stat_font.render(f"{s['level']}/{s['max']}", True, s["color"])
            screen.blit(name_s, name_s.get_rect(center=(x, y - 8)))
            screen.blit(lvl_s, lvl_s.get_rect(center=(x, y + 10)))

            if s["level"] < s["max"]:
                c_text = f"${s['cost']}" if s["currency"] == "gold" else f"{s['cost']} SP"
                c_col = (255, 215, 0) if s["currency"] == "gold" else (0, 255, 200)
                cost_s = self.price_font.render(c_text, True, c_col)
                screen.blit(cost_s, cost_s.get_rect(center=(x, y + radius + 25)))

        pygame.draw.rect(screen, (0, 255, 150), self.respawn_btn, border_radius=12)
        btn_txt = self.title_font.render("RESUME", True, (0,0,0))
        screen.blit(btn_txt, btn_txt.get_rect(center=self.respawn_btn.center))

    def handle_click(self, pos, player):
        if self.respawn_btn.collidepoint(pos): return "respawn"
        for s in self.skills:
            if math.hypot(pos[0]-s["pos"][0], pos[1]-s["pos"][1]) < self.circle_radius:
                if s["level"] >= s["max"]: continue
                if s["req_node"] and s["req_node"]["level"] < 1: continue

                if s["currency"] == "gold" and player.money >= s["cost"]: player.money -= s["cost"]
                elif s["currency"] == "sp" and player.skill_points >= s["cost"]: player.skill_points -= s["cost"]
                else: continue

                s["level"] += 1

                # IMPACT STATS WITH SAFETY CAPS
                if s["id"] == "range":
                    player.attack_radius = min(250, player.attack_radius + 15)
                elif s["id"] == "multi":
                    player.projectiles_count = min(5, getattr(player, 'projectiles_count', 1) + 1)
                elif s["id"] == "damage":
                    player.damage += 0.5
                elif s["id"] == "speed":
                    player.speed = min(6.5, player.speed + 0.3)
                
                if s["currency"] == "gold":
                    s["cost"] = int(s["cost"] * 1.5)
                return "saved"
        return None