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
    play_btn = pygame.Rect(screen_w // 2 - 100, screen_h // 2 + 50, 300, 80)  # Palielināts platums, lai atbilstu jaunajam attēla izmēram
    if play_img:
        screen.blit(play_img, play_btn.topleft)
    else:
        # ja netiek ielaadets attels, uzzimejam rezerves pogu
        pygame.draw.rect(screen, (50, 200, 100), play_btn, border_radius=10) 
        play_text = render_pixel_text("PLAY", UI_MEDIUM, (0, 0, 0), bold=True)
        screen.blit(play_text, play_text.get_rect(center=play_btn.center))

    # iestatījumu poga
    settings_btn = pygame.Rect(screen_w // 2 - 115, screen_h // 2 + 150, 300, 80) 
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
                      input_field_active, password_error_msg, password_error_timer, menu_logo, login_img, back_img=None):

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

    # --- USERNAME INPUT SADAĻA ---
    if login_img:
        # Izveidojam Rect, pamatojoties uz bildes izmēru, un nocentrējam to
        user_box_rect = login_img.get_rect(center=(screen_w // 2, screen_h // 2 + 30))
        user_input_rect = user_box_rect.copy()

        # Zīmējam kauliņu bildi
        screen.blit(login_img, user_box_rect.topleft)

        # Aktīvā lauka rāmis (Dzeltens, kad izvēlēts)
        if input_field_active == "username":
            # border_radius=15 palīdz rāmim labāk piegult kauliņu stūriem
            pygame.draw.rect(screen, (0, 0, 5, 200), user_box_rect, 5, border_radius=8)

        # Username teksta renderēšana
        u_display = f"{user_name}|" if input_field_active == "username" else user_name
        u_txt = render_pixel_text(u_display if user_name else "Username", 18, (255, 255, 255) if user_name else (255, 255, 255))
        
        # Nocentrējam tekstu tieši bildes vidū
        screen.blit(u_txt, u_txt.get_rect(center=user_box_rect.center))
    else:
        # Rezerves variants, ja bilde neielādējas
        user_box_rect = pygame.Rect(screen_w // 2 - 175, screen_h // 2 + 10, 350, 50)
        user_input_rect = user_box_rect.copy()
        pygame.draw.rect(screen, (30, 30, 50), user_box_rect, border_radius=10)

    # --- PASSWORD INPUT SADAĻA ---
    if login_img:
        # Novietojam paroles lauku zemāk par 80 pikseļiem
        pass_box_rect = login_img.get_rect(center=(screen_w // 2, screen_h // 2 + 110))
        pass_input_rect = pass_box_rect.copy()

        # Zīmējam bildi
        screen.blit(login_img, pass_box_rect.topleft)

        # Aktīvā lauka rāmis
        if input_field_active == "password":
            pygame.draw.rect(screen, (0, 0, 5, 200), pass_box_rect, 5, border_radius= 8)

        # Paroles teksta loģika - parādām zvaigznītes, nevis īsto paroli
        hidden_pass = "*" * len(user_password)
        p_display = f"{hidden_pass}|" if input_field_active == "password" else hidden_pass
        p_txt = render_pixel_text(p_display if user_password else "Password", 18, (255, 255, 255) if user_password else (255, 255, 255))
        
        # Nocentrējam tekstu tieši bildes vidū
        screen.blit(p_txt, p_txt.get_rect(center=pass_box_rect.center))
    else:
        pass_box_rect = pygame.Rect(screen_w // 2 - 175, screen_h // 2 + 80, 350, 50)
        pass_input_rect = pass_box_rect.copy()
        pygame.draw.rect(screen, (30, 30, 50), pass_box_rect, border_radius=10)

    # 3. Papildu informācija un kļūdu paziņojumi
    hint_text = "Click fields or press TAB to switch • ENTER to login"
    hint = render_pixel_text(hint_text, 12, (180, 180, 180))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 180)))

    if password_error_timer > 0:
        err_txt = render_pixel_text(password_error_msg, 14, (255, 80, 80))
        screen.blit(err_txt, err_txt.get_rect(center=(screen_w // 2, screen_h // 2 + 220)))

    # Back Button
    back_btn = pygame.Rect(20, screen_h - 80, 150, 50)
    if back_img:
        screen.blit(back_img, back_btn.topleft)
    else:
        pygame.draw.rect(screen, (100, 100, 150), back_btn, border_radius=10)
        back_text = render_pixel_text("BACK", 16, (255, 255, 255), bold=True)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    # Atgriežam taisnstūrus, lai main.py zinātu, kur lietotājs klikšķina
    return user_input_rect, pass_input_rect, back_btn, None

# funkcija draw_settings_overlay pieņem pygame.Surface tipa vērtību screen, int tipa vērtību screen_w, int tipa vērtību screen_h, int tipa vērtību master_volume, int tipa vērtību music_volume un int tipa vērtību sfx_volume un atgriež pygame.Rect tipa vērtību back_button_rect
def draw_settings_overlay(screen, screen_w, screen_h, master_volume, music_volume, sfx_volume, back_img):

    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    title = render_pixel_text("SETTINGS", 44, (0, 255, 150), bold=True)
    screen.blit(title, (screen_w // 2 - title.get_width() // 2, 100))
    
    vol_font_large = 20
    button_rects = {}
    
    # Master Volume
    screen.blit(render_pixel_text(f"Master Volume: {master_volume}%", vol_font_large, (255, 255, 255)), (200, 250))
    master_minus = pygame.Rect(200, 290, 50, 40)
    master_plus = pygame.Rect(260, 290, 50, 40)
    pygame.draw.rect(screen, (100, 100, 150), master_minus, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 150), master_plus, border_radius=5)
    minus_text = render_pixel_text("-", 24, (255, 255, 255))
    plus_text = render_pixel_text("+", 24, (255, 255, 255))
    screen.blit(minus_text, minus_text.get_rect(center=master_minus.center))
    screen.blit(plus_text, plus_text.get_rect(center=master_plus.center))
    button_rects['master_minus'] = master_minus
    button_rects['master_plus'] = master_plus
    
    # Music Volume
    screen.blit(render_pixel_text(f"Music Volume: {music_volume}%", vol_font_large, (255, 255, 255)), (200, 350))
    music_minus = pygame.Rect(200, 390, 50, 40)
    music_plus = pygame.Rect(260, 390, 50, 40)
    pygame.draw.rect(screen, (100, 100, 150), music_minus, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 150), music_plus, border_radius=5)
    screen.blit(minus_text, minus_text.get_rect(center=music_minus.center))
    screen.blit(plus_text, plus_text.get_rect(center=music_plus.center))
    button_rects['music_minus'] = music_minus
    button_rects['music_plus'] = music_plus
    
    # SFX Volume
    screen.blit(render_pixel_text(f"SFX Volume: {sfx_volume}%", vol_font_large, (255, 255, 255)), (200, 450))
    sfx_minus = pygame.Rect(200, 490, 50, 40)
    sfx_plus = pygame.Rect(260, 490, 50, 40)
    pygame.draw.rect(screen, (100, 100, 150), sfx_minus, border_radius=5)
    pygame.draw.rect(screen, (100, 100, 150), sfx_plus, border_radius=5)
    screen.blit(minus_text, minus_text.get_rect(center=sfx_minus.center))
    screen.blit(plus_text, plus_text.get_rect(center=sfx_plus.center))
    button_rects['sfx_minus'] = sfx_minus
    button_rects['sfx_plus'] = sfx_plus
    
    # Back Button
    back_btn = pygame.Rect(screen_w // 2 - 75, screen_h - 150, 150, 50)
    
    if back_img:
        # Zīmējam attēlu pogas vietā
        screen.blit(back_img, back_btn.topleft)
    else:
        # Rezerves variants, ja attēls nav ielādēts
        pygame.draw.rect(screen, (50, 150, 255), back_btn, border_radius=10)
        back_text = render_pixel_text("BACK", UI_MEDIUM, (0, 0, 0), bold=True)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))
    
    button_rects['back'] = back_btn
    return button_rects
