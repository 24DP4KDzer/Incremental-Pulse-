import pygame
from player import Player
from action import Coin

# Setup
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 30)

player = Player()
coin = Coin()

running = True
while running:
    screen.fill((30, 30, 30)) # Background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # --- ADD THIS PART ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: # Pressing Esc will close the game
                running = False
        # ---------------------

    # Movement & Logic
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Check for "Collection" (The Incremental part!)
    if player.rect.colliderect(coin.rect):
        player.money += 1
        coin.respawn()

    # Draw everything
    coin.draw(screen)
    player.draw(screen)
    
    # UI
    score_text = font.render(f"Money: ${player.money}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()