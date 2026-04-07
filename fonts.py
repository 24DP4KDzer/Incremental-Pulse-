"""
Pixelated font utility for Pulse: Evolution
Provides retro 8-bit/12-bit style text rendering
"""
import pygame

# Font cache for better performance
_font_cache = {}

# funkcija get_pixel_font pieņem int tipa vērtību size un bool tipa vērtību bold un atgriež pygame.font.Font tipa vērtību font
def get_pixel_font(size, bold=False):
    """Get a pixelated font using monospace fonts for retro appearance"""
    key = (size, bold)
    
    if key in _font_cache:
        return _font_cache[key]
    
    # Try to use monospace fonts for pixelated look
    # These fonts are available on most systems
    font_names = ["Courier New", "Courier", "Consolas", "Monospace"]
    
    font = None
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size, bold=bold)
            break
        except:
            continue
    
    # Fallback to default if none found
    if font is None:
        font = pygame.font.Font(None, size)
    
    _font_cache[key] = font
    return font


# funkcija render_pixel_text pieņem str tipa vērtību text, int tipa vērtību size, tuple tipa vērtību color, bool tipa vērtību bold un bool tipa vērtību antialias un atgriež pygame.Surface tipa vērtību text_surface
def render_pixel_text(text, size, color, bold=False, antialias=False):
    """Render text with pixelated appearance"""
    font = get_pixel_font(size, bold)
    return font.render(text, antialias, color)


# Predefined font sizes for different UI elements
UI_LARGE = 60      # Main titles, large headings
UI_MEDIUM = 36     # Buttons, important text
UI_NORMAL = 28     # Regular UI text
UI_SMALL = 20      # Secondary text, hints
UI_TINY = 16       # Very small text, stats
GAME_STATS = 22    # In-game stats display
GAME_SCORE = 52    # Large score/notification text
