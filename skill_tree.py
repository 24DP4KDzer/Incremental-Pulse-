import pygame

class SkillTree:
    def __init__(self, screen_w, screen_h):
        self.font = pygame.font.SysFont("Arial", 28, bold=True)
        # Define clickable areas (Rects) for our buttons
        self.buttons = {
            "health": {"rect": pygame.Rect(screen_w//2 - 200, 200, 400, 60), "cost": 15, "name": "Base Max HP +20", "level": 0},
            "speed":  {"rect": pygame.Rect(screen_w//2 - 200, 280, 400, 60), "cost": 20, "name": "Base Speed +1", "level": 0},
            "range":  {"rect": pygame.Rect(screen_w//2 - 200, 360, 400, 60), "cost": 25, "name": "Base Range +10", "level": 0}
        }
        self.respawn_btn = pygame.Rect(screen_w//2 - 100, 500, 200, 60)

    def draw(self, screen, player_money):
        # Draw Upgrades
        for key, btn in self.buttons.items():
            # Green if affordable, Gray if too expensive
            color = (50, 200, 50) if player_money >= btn["cost"] else (100, 100, 100)
            pygame.draw.rect(screen, color, btn["rect"], border_radius=10)
            
            txt = self.font.render(f"{btn['name']} (Lvl {btn['level']}) - ${btn['cost']}", True, (255, 255, 255))
            screen.blit(txt, (btn["rect"].x + 20, btn["rect"].y + 15))

        # Draw Respawn Button
        pygame.draw.rect(screen, (200, 50, 50), self.respawn_btn, border_radius=10)
        respawn_txt = self.font.render("RESPAWN", True, (255, 255, 255))
        screen.blit(respawn_txt, (self.respawn_btn.x + 40, self.respawn_btn.y + 15))

    def handle_click(self, mouse_pos, player):
        # Check if an upgrade was clicked
        for key, btn in self.buttons.items():
            if btn["rect"].collidepoint(mouse_pos):
                if player.money >= btn["cost"]:
                    player.money -= btn["cost"]
                    btn["level"] += 1
                    btn["cost"] = int(btn["cost"] * 1.5) # Price goes up each time
                    
                    # Apply permanent stats
                    if key == "health": player.max_health += 20
                    elif key == "speed": player.speed += 1
                    elif key == "range": player.attack_radius += 10

        # Check if Respawn was clicked
        if self.respawn_btn.collidepoint(mouse_pos):
            return True # Signal to respawn
        return False