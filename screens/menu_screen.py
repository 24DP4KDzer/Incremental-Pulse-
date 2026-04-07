import pygame
from fonts import render_pixel_text, UI_MEDIUM

# funkcija draw_main_menu pieņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w, int tipa vērtību screen_h, pygame.Surface tipa vērtību menu_bg un pygame.Surface tipa vērtību menu_logo un atgriež tuple tipa vērtību button_rects
def draw_main_menu(screen, screen_w, screen_h, menu_bg, menu_logo, play_img, settings_img):
    if menu_bg:
        screen.blit(menu_bg, (0, 0))
    else:
        screen.fill((5, 5, 15))
    
    if menu_logo:
        logo_rect = menu_logo.get_rect(center=(screen_w // 2, screen_h // 2 - 200))
        mask = pygame.mask.from_surface(menu_logo)
        shadow_surf = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        screen.blit(shadow_surf, (logo_rect.x + 10, logo_rect.y + 5))
        screen.blit(menu_logo, logo_rect)
    
    # play poga
    play_btn = pygame.Rect(screen_w // 2 - 100, screen_h // 2 + 50, 2000, 900)  # Palielināts platums, lai atbilstu jaunajam attēla izmēram
    if play_img:
        screen.blit(play_img, play_btn.topleft)
    else:
        # ja netiek ielaadets attels, uzzimejam rezerves pogu
        pygame.draw.rect(screen, (50, 200, 100), play_btn, border_radius=10) 
        play_text = render_pixel_text("PLAY", UI_MEDIUM, (0, 0, 0), bold=True)
        screen.blit(play_text, play_text.get_rect(center=play_btn.center))

    # iestatījumu poga
    settings_btn = pygame.Rect(screen_w // 2 - 100, screen_h // 2 + 140, 2000, 900) 
    if settings_img:
        screen.blit(settings_img, settings_btn.topleft)
    else:
        # ja netiek ielaadets attels, uzzimejam rezerves pogu
        pygame.draw.rect(screen, (150, 100, 255), settings_btn, border_radius=10)
        settings_text = render_pixel_text("SETTINGS", UI_MEDIUM, (0, 0, 0), bold=True)
        screen.blit(settings_text, settings_text.get_rect(center=settings_btn.center))

    return play_btn, settings_btn


# funkcija draw_login_screen paņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w, int tipa vērtību screen_h, pygame.Surface tipa vērtību menu_bg, str tipa vērtību user_name, str tipa vērtību user_password, str tipa vērtību input_field_active, str tipa vērtību password_error_msg, int tipa vērtību password_error_timer un pygame.Surface tipa vērtību menu_logo un atgriež tuple tipa vērtību input_rects
def draw_login_screen(screen, screen_w, screen_h, menu_bg, user_name, user_password, 
                      input_field_active, password_error_msg, password_error_timer, menu_logo):

    if menu_bg:
        screen.blit(menu_bg, (0, 0))
    else:
        screen.fill((5, 5, 15))

    if menu_logo:
        logo_rect = menu_logo.get_rect(center=(screen_w // 2, screen_h // 2 - 150))
        mask = pygame.mask.from_surface(menu_logo)
        shadow_surf = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        screen.blit(shadow_surf, (logo_rect.x + 10, logo_rect.y + 5))
        screen.blit(menu_logo, logo_rect)
    else:
        title = render_pixel_text("PULSE", 60, (0, 255, 150), bold=True)
        shadow_title = render_pixel_text("PULSE", 60, (0, 0, 0), bold=True)
        title_rect = title.get_rect(center=(screen_w // 2, screen_h // 2 - 150))
        screen.blit(shadow_title, (title_rect.x + 5, title_rect.y + 5))
        screen.blit(title, title_rect)

    # --- USERNAME INPUT ---
    box_w, box_h = 350, 50
    user_box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2 + 20, box_w, box_h)
    user_input_rect = user_box_rect.copy()
    
    # Highlight if focused
    border_col = (255, 255, 0) if input_field_active == "username" else (0, 255, 150)
    pygame.draw.rect(screen, (20, 20, 35), user_box_rect, border_radius=10)
    pygame.draw.rect(screen, border_col, user_box_rect, 2, border_radius=10)
    
    # Render username text (no placeholder, shown text is gray if empty)
    if user_name:
        u_txt = render_pixel_text(f"User: {user_name}|" if input_field_active == "username" else f"User: {user_name}", 18, (255, 255, 255))
    else:
        # Gray placeholder when empty
        u_txt = render_pixel_text("User: ", 18, (100, 100, 100))
    screen.blit(u_txt, u_txt.get_rect(center=user_box_rect.center))
    
    # --- PASSWORD INPUT ---
    pass_box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2 + 90, box_w, box_h)
    pass_input_rect = pass_box_rect.copy()
    
    border_col = (255, 255, 0) if input_field_active == "password" else (0, 255, 150)
    pygame.draw.rect(screen, (20, 20, 35), pass_box_rect, border_radius=10)
    pygame.draw.rect(screen, border_col, pass_box_rect, 2, border_radius=10)
    
    # Render password text (no placeholder, shown as dots)
    if user_password:
        pass_display = "*" * len(user_password)
        p_txt = render_pixel_text(f"Pass: {pass_display}|" if input_field_active == "password" else f"Pass: {pass_display}", 18, (255, 255, 255))
    else:
        # Gray placeholder when empty
        p_txt = render_pixel_text("Pass: ", 18, (100, 100, 100))
    screen.blit(p_txt, p_txt.get_rect(center=pass_box_rect.center))
    
    hint = render_pixel_text("Click fields or press TAB to switch • ENTER to login", 12, (150, 150, 150))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 170)))
    
    if password_error_timer > 0:
        err_txt = render_pixel_text(password_error_msg, 14, (255, 100, 100), bold=True)
        screen.blit(err_txt, err_txt.get_rect(center=(screen_w // 2, screen_h // 2 + 210)))

    # Leaderboard (from main.py)
    leaderboard = []  # This will be passed in from main.py if needed
    
    return user_input_rect, pass_input_rect, None, None


# funkcija draw_settings_overlay pieņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w, int tipa vērtību screen_h, int tipa vērtību master_volume, int tipa vērtību music_volume un int tipa vērtību sfx_volume un atgriež pygame.Rect tipa vērtību back_button_rect
def draw_settings_overlay(screen, screen_w, screen_h, master_volume, music_volume, sfx_volume):
    """Draw the settings overlay"""
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title = render_pixel_text("SETTINGS", 44, (0, 255, 150), bold=True)
    screen.blit(title, (screen_w // 2 - title.get_width() // 2, 100))
    
    # Master Volume
    vol_font_large = 20
    screen.blit(render_pixel_text(f"Master Volume: {master_volume}%", vol_font_large, (255, 255, 255)), (200, 250))
    
    # Music Volume
    screen.blit(render_pixel_text(f"Music Volume: {music_volume}%", vol_font_large, (255, 255, 255)), (200, 350))
    
    # SFX Volume
    screen.blit(render_pixel_text(f"SFX Volume: {sfx_volume}%", vol_font_large, (255, 255, 255)), (200, 450))
    
    # Back Button
    back_btn = pygame.Rect(screen_w // 2 - 75, screen_h - 150, 150, 50)
    pygame.draw.rect(screen, (50, 150, 255), back_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 255, 150), back_btn, 2, border_radius=10)
    back_text = render_pixel_text("BACK", UI_MEDIUM, (0, 0, 0), bold=True)
    screen.blit(back_text, back_text.get_rect(center=back_btn.center))
    
    return back_btn
