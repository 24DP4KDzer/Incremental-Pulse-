import pygame
import sys
import os

pygame.init()

# --- KONFIGURĀCIJA ---
IMAGE_PATH = "photos/allOfBoss.png"
SCALE = 0.15  # Samazinām, lai ietilpst ekrānā, ja bilde ir milzīga

# 1. VISPIRMS IZVEIDOJAM LOGU
screen = pygame.display.set_mode((1100, 800))
pygame.display.set_caption("Boss Sprite Slicer (2x2 Mode)")

# 2. TAD IELĀDĒJAM BILDI
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, IMAGE_PATH)
    original_sheet = pygame.image.load(full_path).convert_alpha()
    w, h = original_sheet.get_size()
    sheet = pygame.transform.scale(original_sheet, (int(w * SCALE), int(h * SCALE)))
except Exception as e:
    print(f"Kļūda: {e}")
    pygame.quit()
    sys.exit()

# --- MAINĪGIE (Sākuma vērtības) ---
# Tā kā tev ir 4 kadri (2 rindiņas, 2 kolonnas), šie skaitļi palīdzēs atrast centru
f_w = sheet.get_width() // 2
f_h = sheet.get_height() // 2
s_x, s_y = 0, 0  # Nobīde no malas
p_x, p_y = 0, 0  # Atstarpe starp kadriem (padding)

font = pygame.font.SysFont("Arial", 18)
clock = pygame.time.Clock()

def draw_text(text, pos, color=(255, 255, 255)):
    screen.blit(font.render(text, True, color), pos)

while True:
    screen.fill((30, 30, 30))
    screen.blit(sheet, (0, 0))

    keys = pygame.key.get_pressed()
    step = 5 if keys[pygame.K_LSHIFT] else 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            # Platums/Augstums
            if event.key == pygame.K_w: f_w += step
            if event.key == pygame.K_s: f_w -= step
            if event.key == pygame.K_e: f_h += step
            if event.key == pygame.K_d: f_h -= step
            # Atstarpes
            if event.key == pygame.K_r: p_x += step
            if event.key == pygame.K_f: p_x -= step
            if event.key == pygame.K_t: p_y += step
            if event.key == pygame.K_g: p_y -= step
            # Pozīcija
            if event.key == pygame.K_UP:    s_y -= step
            if event.key == pygame.K_DOWN:  s_y += step
            if event.key == pygame.K_LEFT:  s_x -= step
            if event.key == pygame.K_RIGHT: s_x += step

    # Definējam tavas 4 pozīcijas (Top Left, Top Right, Bottom Left, Bottom Right)
    # Atbilstoši tavam aprakstam:
    positions = [
        (0, 0, "LEFT (Top-L)"),      # Col 0, Row 0
        (1, 0, "DOWN (Top-R)"),      # Col 1, Row 0
        (0, 1, "RIGHT (Bot-L)"),     # Col 0, Row 1
        (1, 1, "UP (Bot-R)")         # Col 1, Row 1
    ]

    for col, row, label in positions:
        x = s_x + (col * f_w) + (col * p_x)
        y = s_y + (row * f_h) + (row * p_y)
        
        rect = pygame.Rect(x, y, f_w, f_h)
        pygame.draw.rect(screen, (255, 0, 0), rect, 2)
        draw_text(label, (x + 5, y + 5), (255, 255, 0))

    # INFO PANELIS
    panel_x = sheet.get_width() + 20
    draw_text("VADĪBA:", (panel_x, 20), (0, 255, 255))
    draw_text(f"Bultiņas: Pozīcija ({s_x}, {s_y})", (panel_x, 50))
    draw_text(f"W/S: Platums ({f_w})", (panel_x, 5))
    draw_text(f"E/D: Augstums ({f_h})", (panel_x, 100))
    draw_text(f"R/F: Atstarpe X ({p_x})", (panel_x, 125))
    draw_text(f"T/G: Atstarpe Y ({p_y})", (panel_x, 150))
    
    draw_text("KODAM (reizini ar 2, ja SCALE=0.5):", (panel_x, 250), (0, 255, 0))
    # Ja tu izmanto SCALE 0.5, tad īstajā kodā skaitļi jādubulto
    mult = 1 / SCALE
    draw_text(f"frame_w = {int(f_w * mult)}", (panel_x, 280))
    draw_text(f"frame_h = {int(f_h * mult)}", (panel_x, 305))
    draw_text(f"pad_x = {int(p_x * mult)}", (panel_x, 330))
    draw_text(f"pad_y = {int(p_y * mult)}", (panel_x, 355))

    pygame.display.flip()
    clock.tick(60)