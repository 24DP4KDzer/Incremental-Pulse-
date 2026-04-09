import pygame
import math

class SkillTree:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        self.title_font = pygame.font.SysFont("Impact", 16)
        self.stat_font  = pygame.font.SysFont("Arial", 18, bold=True)
        self.price_font = pygame.font.SysFont("Consolas", 13, bold=True)

        self.circle_radius = 38
        self.animation_timer = 0

        cx = screen_w  // 2
        cy = screen_h  // 2

        self.skills = [
            # CORE
            {"id": "stamina",      "name": "MAX ENERGY",     "pos": (cx,       cy),
             "cost": 60, "level": 0, "max": 15, "color": (0, 255, 255),   "req": None,           "currency": "gold"},

            # OFFENSE (up)
            {"id": "damage",       "name": "ATTACK POWER",   "pos": (cx,       cy - 130),
             "cost": 54, "level": 0, "max": 10, "color": (255, 150, 50),  "req": None,           "currency": "gold"},
            {"id": "lifesteal",    "name": "LIFE STEAL",     "pos": (cx,       cy - 260),
             "cost": 4,  "level": 0, "max": 5,  "color": (150, 0, 0),     "req": "damage",       "currency": "sp"},
            {"id": "explosion",    "name": "KILL EXPLOSION", "pos": (cx,       cy - 390),
             "cost": 5,  "level": 0, "max": 5,  "color": (255, 80, 0),    "req": "lifesteal",    "currency": "sp"},

            {"id": "range",        "name": "ATTACK RANGE",   "pos": (cx - 130, cy - 220),
             "cost": 40, "level": 0, "max": 10, "color": (255, 220, 50),  "req": "damage",       "currency": "gold"},
            {"id": "knockback",    "name": "KNOCKBACK",      "pos": (cx - 130, cy - 340),
             "cost": 45, "level": 0, "max": 8,  "color": (200, 200, 200), "req": "range",        "currency": "gold"},
            {"id": "poison",       "name": "POISON",         "pos": (cx - 260, cy - 340),
             "cost": 3,  "level": 0, "max": 5,  "color": (100, 255, 80),  "req": "knockback",    "currency": "sp"},

            {"id": "multi",        "name": "MULTI-PROJ",     "pos": (cx + 130, cy - 220),
             "cost": 3,  "level": 0, "max": 3,  "color": (255, 255, 100), "req": "damage",       "currency": "sp"},
            {"id": "crit",         "name": "CRIT CHANCE",    "pos": (cx + 130, cy - 340),
             "cost": 50, "level": 0, "max": 10, "color": (255, 0, 0),     "req": "multi",        "currency": "gold"},
            {"id": "firerate",     "name": "ATTACK SPEED",   "pos": (cx + 260, cy - 340),
             "cost": 45, "level": 0, "max": 10, "color": (255, 100, 100), "req": "crit",         "currency": "gold"},

            # DEFENSE (down)
            {"id": "health",       "name": "MAX HEALTH",     "pos": (cx,       cy + 130),
             "cost": 20, "level": 0, "max": 10, "color": (255, 60, 60),   "req": None,           "currency": "gold"},
            {"id": "armor",        "name": "ARMOR",          "pos": (cx + 130, cy + 250),
             "cost": 55, "level": 0, "max": 10, "color": (120, 120, 120), "req": "health",       "currency": "gold"},
            {"id": "regen",        "name": "HP REGEN",       "pos": (cx - 130, cy + 250),
             "cost": 4,  "level": 0, "max": 5,  "color": (255, 105, 180), "req": "health",       "currency": "sp"},
            {"id": "thorns",       "name": "THORN DMG",      "pos": (cx + 130, cy + 370),
             "cost": 3,  "level": 0, "max": 5,  "color": (34, 139, 34),   "req": "armor",        "currency": "sp"},
            {"id": "shield",       "name": "SHIELD BURST",   "pos": (cx - 130, cy + 370),
             "cost": 4,  "level": 0, "max": 3,  "color": (0, 200, 255),   "req": "regen",        "currency": "sp"},

            # UTILITY (left)
            {"id": "magnet",       "name": "COIN MAGNET",    "pos": (cx - 170, cy),
             "cost": 35, "level": 0, "max": 10, "color": (100, 100, 255), "req": None,           "currency": "gold"},
            {"id": "greed",        "name": "EXTRA GOLD",     "pos": (cx - 300, cy),
             "cost": 3,  "level": 0, "max": 5,  "color": (255, 215, 0),   "req": "magnet",       "currency": "sp"},
            {"id": "gold_rush",    "name": "GOLD RUSH",      "pos": (cx - 430, cy),
             "cost": 60, "level": 0, "max": 5,  "color": (255, 200, 0),   "req": "greed",        "currency": "gold"},
            {"id": "energy_saver", "name": "ENERGY SAVER",   "pos": (cx - 300, cy - 110),
             "cost": 4,  "level": 0, "max": 5,  "color": (0, 255, 200),   "req": "greed",        "currency": "sp"},

            # MOVEMENT (right)
            {"id": "speed",        "name": "MOVE SPEED",     "pos": (cx + 170, cy),
             "cost": 40, "level": 0, "max": 10, "color": (50, 255, 150),  "req": None,           "currency": "gold"},
            {"id": "dash",         "name": "UNLOCK DASH",    "pos": (cx + 300, cy),
             "cost": 2,  "level": 0, "max": 1,  "color": (255, 0, 150),   "req": "speed",        "currency": "sp"},
            {"id": "dash_cd",      "name": "DASH COOLDOWN",  "pos": (cx + 430, cy),
             "cost": 2,  "level": 0, "max": 5,  "color": (255, 100, 200), "req": "dash",         "currency": "sp"},
            {"id": "blink",        "name": "BLINK DIST",     "pos": (cx + 430, cy - 110),
             "cost": 3,  "level": 0, "max": 5,  "color": (180, 0, 255),   "req": "dash_cd",      "currency": "sp"},
        ]

        for node in self.skills:
            node["req_node"]  = next((n for n in self.skills if n["id"] == node["req"]), None) if node["req"] else None
            node["base_cost"] = node["cost"]

        self.respawn_btn = pygame.Rect(screen_w // 2 - 90, screen_h - 75, 180, 45)
        self.vignette    = self._create_vignette()

    def _create_vignette(self):
        v = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
        for r in range(0, 600, 40):
            alpha = int(min(255, (r / 600) * 220))
            pygame.draw.rect(v, (0, 0, 0, alpha), v.get_rect(), 600 - r)
        return v.convert_alpha()

    def sync_with_player(self, player):
        """Apply all purchased skill levels to player (call AFTER setup_class resets stats)."""
        for node in self.skills:
            lvl = node["level"]
            if lvl <= 0:
                continue
            sid = node["id"]

            if   sid == "health":        player.max_health        = min(500, player.max_health + (player.max_health * 0.1) * lvl)
            elif sid == "armor":         player.armor             = getattr(player, "armor",          0)   + lvl
            elif sid == "thorns":        player.thorns            = getattr(player, "thorns",         0)   + lvl
            elif sid == "regen":         player.regen             = getattr(player, "regen",          0)   + 0.01 * lvl
            elif sid == "range":         player.attack_radius     = min(250, player.attack_radius     + 15 * lvl)
            elif sid == "multi":         player.projectile_count  = min(5,   1 + lvl)
            elif sid == "speed":         player.speed             = min(22,  player.speed             + 0.4 * lvl)
            elif sid == "damage":        player.damage           += 0.5 * lvl
            elif sid == "magnet":        player.magnet_range      = min(300, player.magnet_range      + 15 * lvl)
            elif sid == "dash":          player.dash_unlocked     = True
            elif sid == "dash_cd":       player.dash_cd_bonus     = getattr(player, "dash_cd_bonus",  0)   + lvl
            elif sid == "blink":         player.blink_dist        = getattr(player, "blink_dist",    140)  + 30 * lvl
            elif sid == "stamina":       player.max_energy       += 5 * lvl
            elif sid == "crit":          player.crit_chance       = getattr(player, "crit_chance",    0)   + 5 * lvl
            elif sid == "lifesteal":     player.lifesteal         = min(30, player.lifesteal + lvl)
            elif sid == "firerate":
                player.base_cooldown  = max(5, player.base_cooldown - 2 * lvl)
                player.firerate_level = lvl
            elif sid == "explosion":     player.explosion_lvl     = getattr(player, "explosion_lvl",  0)   + lvl
            elif sid == "poison":        player.poison_lvl        = getattr(player, "poison_lvl",     0)   + lvl
            elif sid == "shield":        player.shield_lvl        = getattr(player, "shield_lvl",     0)   + lvl
            elif sid == "greed":         player.gold_modifier     = getattr(player, "gold_modifier",  1.0) + 0.25 * lvl
            elif sid == "energy_saver":  player.energy_drain_mult = max(0.3, 1.0 - 0.14 * lvl)
            elif sid == "gold_rush":     player.gold_rush_lvl     = getattr(player, "gold_rush_lvl",  0)   + lvl
            elif sid == "knockback":     player.knockback_lvl     = getattr(player, "knockback_lvl",  0)   + lvl

            if node["currency"] == "gold":
                node["cost"] = int(node["base_cost"] * (1.5 ** lvl))

        player.health = player.max_health
        player.energy = player.max_energy

    def handle_click(self, pos, player):
        if self.respawn_btn.collidepoint(pos):
            return "respawn"

        for node in self.skills:
            if math.hypot(pos[0] - node["pos"][0], pos[1] - node["pos"][1]) >= self.circle_radius:
                continue
            if node["level"] >= node["max"]:
                continue
            if node["req_node"] and node["req_node"]["level"] < 1:
                continue

            if node["currency"] == "gold":
                if player.money < node["cost"]: continue
                player.money -= node["cost"]
            else:
                if player.skill_points < node["cost"]: continue
                player.skill_points -= node["cost"]

            node["level"] += 1
            sid = node["id"]

            if   sid == "health":
                if player.max_health >= 500: node["level"] -= 1; return None
                player.max_health += player.max_health * 0.1
                player.health     += player.max_health * 0.1
            elif sid == "armor":         player.armor             = getattr(player, "armor",          0)   + 1
            elif sid == "regen":         player.regen             = getattr(player, "regen",          0)   + 0.01
            elif sid == "thorns":        player.thorns            = getattr(player, "thorns",         0)   + 1
            elif sid == "range":         player.attack_radius     = min(250, player.attack_radius     + 15)
            elif sid == "multi":         player.projectile_count  = min(5, getattr(player, "projectile_count", 1) + 1)
            elif sid == "damage":        player.damage           += 0.5
            elif sid == "speed":
                if player.speed >= 22: node["level"] -= 1; return None
                player.speed = min(22, player.speed + 0.4)
            elif sid == "lifesteal":
                if getattr(player, "lifesteal", 0) >= 30: node["level"] -= 1; return None
                player.lifesteal = min(30, getattr(player, "lifesteal", 0) + 1)
            elif sid == "magnet":        player.magnet_range      = min(300, player.magnet_range      + 15)
            elif sid == "dash":          player.dash_unlocked     = True
            elif sid == "dash_cd":       player.dash_cd_bonus     = getattr(player, "dash_cd_bonus",  0)   + 1
            elif sid == "blink":         player.blink_dist        = getattr(player, "blink_dist",    140)  + 30
            elif sid == "stamina":       player.max_energy       += 5
            elif sid == "crit":          player.crit_chance       = getattr(player, "crit_chance",    0)   + 5
            elif sid == "firerate":
                player.base_cooldown  = max(5, player.base_cooldown - 2)
                player.firerate_level = getattr(player, "firerate_level", 0) + 1
            elif sid == "explosion":     player.explosion_lvl     = getattr(player, "explosion_lvl",  0)   + 1
            elif sid == "poison":        player.poison_lvl        = getattr(player, "poison_lvl",     0)   + 1
            elif sid == "shield":        player.shield_lvl        = getattr(player, "shield_lvl",     0)   + 1
            elif sid == "greed":         player.gold_modifier     = getattr(player, "gold_modifier",  1.0) + 0.25
            elif sid == "energy_saver":  player.energy_drain_mult = max(0.3, getattr(player, "energy_drain_mult", 1.0) - 0.14)
            elif sid == "gold_rush":     player.gold_rush_lvl     = getattr(player, "gold_rush_lvl",  0)   + 1
            elif sid == "knockback":     player.knockback_lvl     = getattr(player, "knockback_lvl",  0)   + 1

            if node["currency"] == "gold":
                node["cost"] = int(node["cost"] * 1.5)

            return "saved"

        return None

    def draw_connection(self, surface, start, end, active):
        color = (180, 180, 255, 150) if active else (40, 40, 50, 80)
        pygame.draw.line(surface, color, start, end, 2)

    def draw(self, screen, money, sp, char_type):
        self.animation_timer += 1
        screen.blit(self.vignette, (0, 0))

        screen.blit(self.stat_font.render(f"GOLD: ${money}",     True, (255, 215, 0)),  (40, 40))
        screen.blit(self.stat_font.render(f"SKILL POINTS: {sp}", True, (0, 255, 150)), (40, 65))

        mouse_pos  = pygame.mouse.get_pos()
        stamina_nd = next(n for n in self.skills if n["id"] == "stamina")

        for node in self.skills:
            if node["req_node"]:
                self.draw_connection(screen, node["req_node"]["pos"], node["pos"], node["level"] > 0)
            elif node["id"] != "stamina":
                self.draw_connection(screen, stamina_nd["pos"], node["pos"], True)

        for node in self.skills:
            nx, ny  = node["pos"]
            hovered = (mouse_pos[0] - nx)**2 + (mouse_pos[1] - ny)**2 < self.circle_radius**2
            radius  = self.circle_radius + (3 if hovered else 0)

            pygame.draw.circle(screen, (55, 55, 80) if hovered else (30, 30, 45), (nx, ny), radius)
            pygame.draw.circle(screen, node["color"], (nx, ny), radius, 2)

            for i in range(node["max"]):
                dot_color = node["color"] if i < node["level"] else (60, 60, 60)
                a  = (i / node["max"]) * 6.283 - 1.57
                px = nx + math.cos(a) * (radius + 8)
                py = ny + math.sin(a) * (radius + 8)
                pygame.draw.circle(screen, dot_color, (int(px), int(py)), 2)

            name_txt  = self.title_font.render(node["name"], True, (255, 255, 255))
            level_txt = self.stat_font.render(f"{node['level']}/{node['max']}", True, node["color"])
            screen.blit(name_txt,  name_txt.get_rect(center=(nx, ny - 8)))
            screen.blit(level_txt, level_txt.get_rect(center=(nx, ny + 10)))

            if node["level"] < node["max"]:
                cost_str   = f"${node['cost']}" if node["currency"] == "gold" else f"{node['cost']} SP"
                cost_color = (255, 215, 0) if node["currency"] == "gold" else (0, 255, 200)
                cost_surf  = self.price_font.render(cost_str, True, cost_color)
                screen.blit(cost_surf, cost_surf.get_rect(center=(nx, ny + radius + 25)))

        pygame.draw.rect(screen, (0, 255, 150), self.respawn_btn, border_radius=12)
        btn_txt = self.title_font.render("RESUME", True, (0, 0, 0))
        screen.blit(btn_txt, btn_txt.get_rect(center=self.respawn_btn.center))