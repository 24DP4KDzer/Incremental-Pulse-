import pygame
import sys

pygame.init()

# 1. Load the image
# Make sure this matches your exact file path!
image_path = "photos/allOfBoss.png"
try:
    sheet = pygame.image.load(image_path)
except:
    print(f"Could not load {image_path}! Check your spelling.")
    sys.exit()

# Get image size and create a window
img_w, img_h = sheet.get_size()
screen = pygame.display.set_mode((max(800, img_w), max(800, img_h)))
pygame.display.set_caption("Sprite Slicer Tool")

# ==========================================
# 2. TWEAK THESE NUMBERS UNTIL THE RED BOXES FIT!
# ==========================================
frame_w = 125    # Width of the box
frame_h = 157       # Height of the box
start_x = 10   # Distance from left edge to the first box
start_y = 80    # Distance from top edge to the first box
padding_x = 26     # Empty space between columns
padding_y = 3    # Empty space between rows
num_frames = 2     # Number of columns
# ==========================================

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Draw background and image
    screen.fill((30, 30, 30))
    screen.blit(sheet, (0, 0))

    # Draw the red bounding boxes
    for row in range(4): # 4 rows (Up, Down, Left, Right)
        for col in range(num_frames):
            exact_x = start_x + (col * frame_w) + (col * padding_x)
            exact_y = start_y + (row * frame_h) + (row * padding_y)
            
            rect = pygame.Rect(exact_x, exact_y, frame_w, frame_h)
            # Draw a 2-pixel thick red box
            pygame.draw.rect(screen, (255, 0, 0), rect, 2) 

    pygame.display.flip()