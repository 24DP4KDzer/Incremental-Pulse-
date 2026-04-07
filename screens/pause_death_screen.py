import pygame
from fonts import render_pixel_text, UI_MEDIUM

# funkcija draw_death_screen pieņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w, int tipa vērtību screen_h un int tipa vērtību death_timer un atgriež None tipa vērtību None
def draw_death_screen(screen, screen_w, screen_h, death_timer):
    """Draw cinematic death scene"""
    progress = 1.0 - (death_timer / 120.0)
    
    # Phase 1 (0-0.5): Fade the game to black
    if progress < 0.5:
        fade_alpha = int(255 * (progress * 2))
        fade_surf = pygame.Surface((screen_w, screen_h))
        fade_surf.fill((0, 0, 0))
        fade_surf.set_alpha(fade_alpha)
        screen.blit(fade_surf, (0, 0))
        
        # Red vignette effect during fade
        vignette = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
        vignette.fill((139, 0, 0, int(100 * (progress * 2))))
        screen.blit(vignette, (0, 0))
    else:
        # Phase 2 (0.5-1.0): Show GAME OVER text fading in
        screen.fill((5, 5, 15))
        text_alpha = int(255 * ((progress - 0.5) * 2))
        msg = render_pixel_text("GAME OVER", 72, (255, 0, 0), bold=True)
        msg_with_alpha = msg.copy()
        msg_with_alpha.set_alpha(text_alpha)
        screen.blit(msg_with_alpha, msg_with_alpha.get_rect(center=(screen_w // 2, screen_h // 2)))


# funkcija draw_pause_menu pieņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w un int tipa vērtību screen_h un atgriež tuple tipa vērtību button_rects
def draw_pause_menu(screen, screen_w, screen_h):
    """Draw pause menu overlay"""
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    title = render_pixel_text("PAUSED", 56, (0, 255, 150), bold=True)
    screen.blit(title, (screen_w // 2 - title.get_width() // 2, screen_h // 2 - 150))
    
    btn_w, btn_h = 200, 50
    btn_x = screen_w // 2 - btn_w // 2
    
    # Save button
    pause_save_btn = pygame.Rect(btn_x, screen_h // 2 - 20, btn_w, btn_h)
    pygame.draw.rect(screen, (50, 150, 255), pause_save_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), pause_save_btn, 2, border_radius=10)
    save_btn_text = render_pixel_text("SAVE", UI_MEDIUM, (0, 0, 0), bold=True)
    screen.blit(save_btn_text, save_btn_text.get_rect(center=pause_save_btn.center))
    
    # Resume button
    pause_resume_btn = pygame.Rect(btn_x, screen_h // 2 + 50, btn_w, btn_h)
    pygame.draw.rect(screen, (50, 200, 100), pause_resume_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), pause_resume_btn, 2, border_radius=10)
    resume_btn_text = render_pixel_text("RESUME", UI_MEDIUM, (0, 0, 0), bold=True)
    screen.blit(resume_btn_text, resume_btn_text.get_rect(center=pause_resume_btn.center))
    
    # Quit button
    pause_quit_btn = pygame.Rect(btn_x, screen_h // 2 + 120, btn_w, btn_h)
    pygame.draw.rect(screen, (200, 50, 50), pause_quit_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), pause_quit_btn, 2, border_radius=10)
    quit_btn_text = render_pixel_text("QUIT", UI_MEDIUM, (0, 0, 0), bold=True)
    screen.blit(quit_btn_text, quit_btn_text.get_rect(center=pause_quit_btn.center))
    
    # Hint text
    hint = render_pixel_text("Press ESC to Resume", 14, (150, 150, 150))
    screen.blit(hint, (screen_w // 2 - hint.get_width() // 2, screen_h - 50))
    
    return pause_save_btn, pause_resume_btn, pause_quit_btn
