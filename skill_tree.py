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

            # --- COLUMN 2: UTILITY (Cleaned up duplicates) ---
            {"id": "magnet", "name": "COIN MAGNET", "pos": (col2, row1), "cost": 35, "level": 0, "max": 10, "color": (100, 100, 255), "req": None, "currency": "gold"},
            {"id": "greed", "name": "EXTRA GOLD", "pos": (col2, row2), "cost": 3, "level": 0, "max": 5, "color": (255, 215, 0), "req": "magnet", "currency": "sp"},
            {"id": "knockback", "name": "KNOCKBACK", "pos": (col2, row3), "cost": 45, "level": 0, "max": 8, "color": (200, 200, 200), "req": "greed", "currency": "gold"},
            {"id": "lifesteal", "name": "LIFE STEAL", "pos": (col2, row4), "cost": 4, "level": 0, "max": 5, "color": (150, 0, 0), "req": "knockback", "currency": "sp"},

            # --- COLUMN 3: CORE ---
            {"id": "stamina", "name": "MAX ENERGY", "pos": (col3, row1), "cost": 60, "level": 0, "max": 15, "color": (0, 255, 255), "req": None, "currency": "gold"},
            {"id": "buy_sp", "name": "BUY SKILL PT", "pos": (col3, row2 + 40), "cost": 250, "level": 0, "max": 99, "color": (0, 255, 150), "req": None, "currency": "gold"},
            

            # --- COLUMN 4: MOVEMENT ---
            {"id": "speed", "name": "MOVE SPEED", "pos": (col4, row1), "cost": 40, "level": 0, "max": 10, "color": (50, 255, 150), "req": None, "currency": "gold"},
            {"id": "dash", "name": "UNLOCK DASH", "pos": (col4, row2), "cost": 2, "level": 0, "max": 1, "color": (255, 0, 150), "req": "speed", "currency": "sp"},
            {"id": "dash_cd", "name": "DASH COOLDOWN", "pos": (col4, row3), "cost": 2, "level": 0, "max": 5, "color": (255, 100, 200), "req": "dash", "currency": "sp"},

            # --- COLUMN 5: OFFENSE ---
            {"id": "damage", "name": "ATTACK POWER", "pos": (col5, row1), "cost": 54, "level": 0, "max": 10, "color": (255, 150, 50), "req": None, "currency": "gold"},
            {"id": "range", "name": "ATTACK RANGE", "pos": (col5, row2), "cost": 40, "level": 0, "max": 10, "color": (255, 220, 50), "req": "damage", "currency": "gold", "hidden_for": ["dwarf"]},
            {"id": "multi", "name": "MULTI-PROJECTILE", "pos": (col5, row3), "cost": 3, "level": 0, "max": 3, "color": (255, 255, 100), "req": "damage", "currency": "sp"},
            {"id": "crit", "name": "CRIT CHANCE", "pos": (col5, row4), "cost": 50, "level": 0, "max": 10, "color": (255, 0, 0), "req": "multi", "currency": "gold"},
        ]
        
        self.respawn_btn = pygame.Rect(screen_w//2 - 90, screen_h - 75, 180, 45)
        self.vignette = self._create_vignette()

    def _create_vignette(self):
        surf = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        for r in range(0, 500, 15):
            alpha = int(r / 500 * 240)
            pygame.draw.rect(surf, (0, 0, 0, alpha), surf.get_rect(), 500-r)
        return surf

    def sync_with_player(self, player):
        for s in self.skills:
            lvl = s["level"]
            if lvl == 0:
                continue  # Don't apply anything for unpurchased skills
            if s["id"] == "health":
                player.max_health += 20 * lvl
            elif s["id"] == "armor":
                player.armor = getattr(player, 'armor', 0) + (1 * lvl)
            elif s["id"] == "thorns":
                player.thorns = getattr(player, 'thorns', 0) + (5 * lvl)
            elif s["id"] == "regen":
                player.regen = getattr(player, 'regen', 0) + (0.1 * lvl)
            elif s["id"] == "magnet":
                player.magnet_range += 15 * lvl
            elif s["id"] == "greed":
                player.gold_modifier = getattr(player, 'gold_modifier', 1.0) + (0.2 * lvl)
            elif s["id"] == "knockback":
                player.knockback_force = getattr(player, 'knockback_force', 5) + (2 * lvl)
            elif s["id"] == "lifesteal":
                player.lifesteal = getattr(player, 'lifesteal', 0) + (1 * lvl)
            elif s["id"] == "stamina":
                player.max_energy += 2.0 * lvl
            elif s["id"] == "buy_sp":
                pass  # Don't re-grant SP on load
            elif s["id"] == "speed":
                player.speed += 0.4 * lvl
            elif s["id"] == "dash":
                player.dash_unlocked = True
            elif s["id"] == "dash_cd":
                player.dash_cd_reduction = getattr(player, 'dash_cd_reduction', 0) + (10 * lvl)
            elif s["id"] == "damage":
                player.damage += 0.5 * lvl
            elif s["id"] == "range":
                if player.char_type == "dwarf":
                    player.rotation_speed = getattr(player, 'rotation_speed', 15) + (3 * lvl)
                else:
                    player.attack_radius += 20 * lvl
            elif s["id"] == "multi":
                player.projectile_count = getattr(player, 'projectile_count', 1) + (1 * lvl)
            elif s["id"] == "crit":
                player.crit_chance = getattr(player, 'crit_chance', 0) + (5 * lvl)

            s["level"] = max(0, min(s["level"], s["max"]))
            if s["currency"] == "gold" and s["id"] != "buy_sp":
                s["cost"] = int(s["cost"] * (1.5 ** lvl))

        player.health = player.max_health
        player.energy = player.max_energy


    def draw_connection(self, surface, start, end, active):
        col = (200, 200, 200, 150) if active else (50, 50, 60, 80)
        pygame.draw.line(surface, col, start, end, 2)
        if active:
            t = (self.animation_timer * 0.015) % 1.0
            px = start[0] + (end[0] - start[0]) * t
            py = start[1] + (end[1] - start[1]) * t
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 2)



    def draw(self, screen, money, sp, char_type):
        self.animation_timer += 1
        screen.blit(self.vignette, (0,0))
        
        screen.blit(self.stat_font.render(f"GOLD: ${money}", True, (255, 215, 0)), (40, 40))
        screen.blit(self.stat_font.render(f"SKILL POINTS: {sp}", True, (0, 255, 150)), (40, 65))




        # Connections (filtered)
        for s in self.skills:
            if "hidden_for" in s and char_type in s["hidden_for"]: continue
            if s["req"]:
                req_node = next((n for n in self.skills if n["id"] == s["req"]), None)
                if req_node: self.draw_connection(screen, req_node["pos"], s["pos"], s["level"] > 0)

        m_pos = pygame.mouse.get_pos()
        for s in self.skills:
            # Skip hidden skills
            if "hidden_for" in s and char_type in s["hidden_for"]: continue

            x, y = s["pos"]
            is_hovered = math.hypot(m_pos[0]-x, m_pos[1]-y) < self.circle_radius
            radius = self.circle_radius + (2 if is_hovered else 0)

            bg_col = (30, 30, 40) if not is_hovered else (50, 50, 70)
            pygame.draw.circle(screen, bg_col, (x, y), radius)
            pygame.draw.circle(screen, s["color"], (x, y), radius, 2)

            for i in range(s["max"]):
                dot_col = s["color"] if i < s["level"] else (60, 60, 60)
                angle = (i / s["max"]) * 2 * math.pi - math.pi/2
                dx = x + math.cos(angle) * (radius + 6)
                dy = y + math.sin(angle) * (radius + 6)
                pygame.draw.circle(screen, dot_col, (int(dx), int(dy)), 2)

            name_surf = self.title_font.render(s["name"], True, (255, 255, 255))
            lvl_surf = self.stat_font.render(f"{s['level']}/{s['max']}", True, s["color"])
            screen.blit(name_surf, name_surf.get_rect(center=(x, y - 8)))
            screen.blit(lvl_surf, lvl_surf.get_rect(center=(x, y + 10)))

            

            # --- Updated Cost Label Section ---
            if s["level"] < s["max"]:
                if s["currency"] == "gold":
                    c_text = f"${s['cost']}"
                    c_col = (255, 215, 0)  # Gold Color
                else:
                    c_text = f"{s['cost']} SP"
                    c_col = (0, 255, 200)  # Teal/SP Color
                
                cost_surf = self.price_font.render(c_text, True, c_col)
                # Increase the +22 to a larger number if you want more gap from the circle
                cost_rect = cost_surf.get_rect(center=(x, y + radius + 25))
                screen.blit(cost_surf, cost_rect)

        pygame.draw.rect(screen, (0, 255, 150), self.respawn_btn, border_radius=12)
        btn_txt = self.title_font.render("RESUME JOURNEY", True, (0,0,0))
        screen.blit(btn_txt, btn_txt.get_rect(center=self.respawn_btn.center))

    def handle_click(self, pos, player):
        if self.respawn_btn.collidepoint(pos): return "respawn"
        for s in self.skills:
            # Prevent clicking hidden skills
            if "hidden_for" in s and player.char_type in s["hidden_for"]: continue

            if math.hypot(pos[0]-s["pos"][0], pos[1]-s["pos"][1]) < self.circle_radius:
                if s["level"] >= s["max"]: continue
                if s["req"]:
                    req_node = next((n for n in self.skills if n["id"] == s["req"]), None)
                    if req_node and req_node["level"] < 1: continue

                if s["currency"] == "gold" and player.money >= s["cost"]: player.money -= s["cost"]
                elif s["currency"] == "sp" and player.skill_points >= s["cost"]: player.skill_points -= s["cost"]
                else: continue

                s["level"] += 1
                
                # Add Stats To Player
                if s["id"] == "health": 
                    player.max_health += 20
                    player.health = player.max_health
                elif s["id"] == "armor": 
                    player.armor = getattr(player, 'armor', 0) + 1
                elif s["id"] == "thorns": 
                    player.thorns = getattr(player, 'thorns', 0) + 5
                elif s["id"] == "regen": 
                    player.regen = getattr(player, 'regen', 0) + 0.05
                elif s["id"] == "speed": 
                    player.speed += 0.4
                elif s["id"] == "damage": 
                    player.damage += 0.5
                elif s["id"] == "stamina": 
                    player.max_energy += 2.0
                    player.energy = player.max_energy
                elif s["id"] == "magnet": 
                    player.magnet_range += 15
                elif s["id"] == "greed":
                    player.gold_modifier = getattr(player, 'gold_modifier', 1.0) + 0.2
                elif s["id"] == "knockback":
                    player.knockback_force = getattr(player, 'knockback_force', 5) + 2
                elif s["id"] == "lifesteal":
                    player.lifesteal = getattr(player, 'lifesteal', 0) + 1
                elif s["id"] == "crit":
                    player.crit_chance = getattr(player, 'crit_chance', 0) + 5
                elif s["id"] == "chrono":
                    player.time_dilation = getattr(player, 'time_dilation', 1.0) - 0.05
                elif s["id"] == "buy_sp": 
                    player.skill_points += 1
                elif s["id"] == "dash": 
                    player.dash_unlocked = True
                elif s["id"] == "range":
                    player.attack_radius += 20
                
                if s["currency"] == "gold" and s["id"] != "buy_sp": 
                    s["cost"] = int(s["cost"] * 1.5)
                return "saved"
        return None