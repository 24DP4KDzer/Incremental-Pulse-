import pygame
import math

class SkillTree:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.title_font = pygame.font.SysFont("Impact", 60)
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.hud_font = pygame.font.SysFont("Consolas", 35, bold=True)
        
        center_x, center_y = screen_w // 2, screen_h // 2
        self.circle_radius = 70 

        # Skills configuration
        self.skills = [
            {"id": "health", "name": "VITALITY", "pos": (center_x - 350, center_y - 150), "cost": 15, "level": 0, "max": 10, "color": (230, 50, 50), "req": None, "req_lvl": 0, "currency": "gold"},
            {"id": "speed", "name": "AGILITY", "pos": (center_x + 350, center_y - 150), "cost": 20, "level": 0, "max": 10, "color": (50, 230, 150), "req": None, "req_lvl": 0, "currency": "gold"},
            {"id": "range", "name": "REACH", "pos": (center_x - 350, center_y + 100), "cost": 25, "level": 0, "max": 10, "color": (100, 150, 255), "req": None, "req_lvl": 0, "currency": "gold"},
            {"id": "damage", "name": "POWER", "pos": (center_x + 350, center_y + 100), "cost": 30, "level": 0, "max": 10, "color": (255, 180, 50), "req": None, "req_lvl": 0, "currency": "gold"},
            
            # ENERGY UPGRADE
            {"id": "energy", "name": "STAMINA", "pos": (center_x, center_y - 200), "cost": 40, "level": 0, "max": 20, "color": (255, 255, 255), "req": None, "req_lvl": 0, "currency": "gold"},

            # SP EXCHANGE (Buy 1 SP for Gold)
            {"id": "buy_sp", "name": "BUY SP", "pos": (center_x, center_y), "cost": 200, "level": 0, "max": 99, "color": (0, 255, 150), "req": None, "req_lvl": 0, "currency": "gold"},

            # NEW SKILLS (Require Skill Points 'SP')
            {"id": "magnet", "name": "MAGNET", "pos": (center_x - 150, center_y - 50), "cost": 1, "level": 0, "max": 5, "color": (0, 200, 200), "req": "energy", "req_lvl": 1, "currency": "sp"},
            {"id": "dash", "name": "DASH", "pos": (center_x + 150, center_y - 50), "cost": 2, "level": 0, "max": 1, "color": (255, 0, 100), "req": "speed", "req_lvl": 2, "currency": "sp"},

            # SPECIAL SKILLS
            {"id": "multishot", "name": "MULTI-SHOT", "pos": (center_x - 150, center_y + 200), "cost": 100, "level": 0, "max": 3, "color": (200, 50, 255), "req": "range", "req_lvl": 2, "currency": "gold"},
            {"id": "rapidfire", "name": "RAPID FIRE", "pos": (center_x + 150, center_y + 200), "cost": 100, "level": 0, "max": 5, "color": (255, 255, 100), "req": "damage", "req_lvl": 2, "currency": "gold"}
        ]
        
        self.respawn_btn = pygame.Rect(screen_w//2 - 100, screen_h - 80, 200, 50)

    def sync_with_player(self, player):
        """Updates UI levels based on player's saved CSV stats."""
        for s in self.skills:
            if s["id"] == "health": s["level"] = int((player.max_health - 100) / 20)
            elif s["id"] == "speed": s["level"] = int((player.speed - 1.3) / 0.5)
            elif s["id"] == "range": s["level"] = int((player.attack_radius - 100) / 15)
            elif s["id"] == "damage": s["level"] = int((player.damage - 1.0) / 0.5)
            elif s["id"] == "energy": s["level"] = int((player.max_energy - 10.0) / 5)
            elif s["id"] == "multishot": s["level"] = player.projectiles_count - 1
            elif s["id"] == "rapidfire": s["level"] = int((25 - player.base_cooldown) / 3)
            elif s["id"] == "magnet": s["level"] = int((player.magnet_range - 60) / 40)
            elif s["id"] == "dash": s["level"] = 1 if player.dash_unlocked else 0
            
            s["level"] = max(0, min(s["level"], s["max"]))

            # Recalculate cost for gold skills
            if s["currency"] == "gold" and s["level"] > 0:
                base_costs = {"health": 15, "speed": 20, "range": 25, "damage": 30, "energy": 40, "multishot": 100, "rapidfire": 100, "buy_sp": 200}
                new_cost = base_costs.get(s["id"], s["cost"])
                for _ in range(s["level"]):
                    new_cost = int(new_cost * 1.8)
                s["cost"] = new_cost

    def draw(self, screen, player_money, player_sp):
        overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        overlay.fill((10, 10, 25, 245)) 
        screen.blit(overlay, (0,0))

        # HUD
        gold_txt = self.hud_font.render(f"GOLD: ${player_money}", True, (255, 215, 0))
        sp_txt = self.hud_font.render(f"SP: {player_sp}", True, (0, 255, 150))
        screen.blit(gold_txt, (40, 40))
        screen.blit(sp_txt, (40, 85))

        def get_lvl(skill_id):
            return next((s["level"] for s in self.skills if s["id"] == skill_id), 0)

        # 1. DRAW CONNECTING LINES FIRST (So they appear behind circles)
        for s in self.skills:
            if s["req"]:
                parent = next((p for p in self.skills if p["id"] == s["req"]), None)
                if parent:
                    # Line color based on if parent requirement is met
                    line_color = (100, 100, 100)
                    if get_lvl(parent["id"]) >= s["req_lvl"]:
                        line_color = s["color"]
                    
                    pygame.draw.line(screen, line_color, parent["pos"], s["pos"], 3)

        # 2. DRAW CIRCLES
        for s in self.skills:
            unlocked = s["req"] is None or get_lvl(s["req"]) >= s["req_lvl"]
            x, y = s["pos"]
            is_max = s["level"] >= s["max"]

            if not unlocked:
                pygame.draw.circle(screen, (30, 30, 30), (x, y), self.circle_radius)
                pygame.draw.circle(screen, (50, 50, 50), (x, y), self.circle_radius, 2)
                lock_t = self.font.render("LOCKED", True, (80, 80, 80))
                screen.blit(lock_t, lock_t.get_rect(center=(x, y)))
                continue

            # Affordability
            if s["currency"] == "gold":
                can_afford = player_money >= s["cost"] and not is_max
                price_tag = f"${s['cost']}"
            else:
                can_afford = player_sp >= s["cost"] and not is_max
                price_tag = f"{s['cost']} SP"

            color = s["color"] if can_afford else (60, 60, 60)
            if is_max: color = (255, 215, 0)

            pygame.draw.circle(screen, (20, 20, 30), (x, y), self.circle_radius)
            pygame.draw.circle(screen, color, (x, y), self.circle_radius, 5)

            name_t = self.font.render(s["name"], True, (255, 255, 255))
            screen.blit(name_t, name_t.get_rect(center=(x, y - 15)))
            
            lvl_t = self.font.render(f"{s['level']}/{s['max']}", True, color)
            screen.blit(lvl_t, lvl_t.get_rect(center=(x, y + 15)))

            if not is_max:
                p_color = (0, 255, 100) if can_afford else (200, 50, 50)
                p_t = self.font.render(price_tag, True, p_color)
                screen.blit(p_t, p_t.get_rect(center=(x, y + self.circle_radius + 20)))

        pygame.draw.rect(screen, (255, 255, 255), self.respawn_btn, border_radius=25)
        res_t = self.font.render("BATTLE", True, (0, 0, 0))
        screen.blit(res_t, res_t.get_rect(center=self.respawn_btn.center))

    def handle_click(self, mouse_pos, player):
        def get_lvl(skill_id):
            return next((s["level"] for s in self.skills if s["id"] == skill_id), 0)

        for s in self.skills:
            unlocked = s["req"] is None or get_lvl(s["req"]) >= s["req_lvl"]
            if not unlocked: continue

            dist = math.hypot(mouse_pos[0] - s["pos"][0], mouse_pos[1] - s["pos"][1])
            if dist < self.circle_radius:
                if s["currency"] == "gold":
                    if player.money >= s["cost"] and s["level"] < s["max"]:
                        player.money -= s["cost"]
                    else: return False
                else:
                    if getattr(player, 'skill_points', 0) >= s["cost"] and s["level"] < s["max"]:
                        player.skill_points -= s["cost"]
                    else: return False

                s["level"] += 1
                
                if s["id"] == "health": 
                    player.max_health += 20
                    player.health = player.max_health
                elif s["id"] == "speed": player.speed += 0.5
                elif s["id"] == "range": player.attack_radius += 15
                elif s["id"] == "damage": player.damage += 0.5
                elif s["id"] == "multishot": player.projectiles_count += 1
                elif s["id"] == "rapidfire": player.base_cooldown = max(5, player.base_cooldown - 3)
                elif s["id"] == "energy": player.max_energy += 5
                elif s["id"] == "buy_sp": player.skill_points += 1
                elif s["id"] == "magnet": player.magnet_range += 40
                elif s["id"] == "dash": player.dash_unlocked = True
                
                if s["currency"] == "gold":
                    s["cost"] = int(s["cost"] * 1.8)
                
                return "saved"

        if self.respawn_btn.collidepoint(mouse_pos): 
            return "respawn"
        return False