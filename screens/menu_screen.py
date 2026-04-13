import pygame
from fonts import render_pixel_text, UI_MEDIUM

# ─── SLIDER HELPER ────────────────────────────────────────────────────────────
def _draw_slider(screen, label, value, rect, color=(0, 200, 255)):
    """Draw a labelled horizontal slider. Returns the track Rect for hit-testing."""
    font_surf = render_pixel_text(f"{label}: {value}%", 18, (255, 255, 255))
    screen.blit(font_surf, (rect.x, rect.y - 24))
    # Track
    pygame.draw.rect(screen, (50, 50, 80), rect, border_radius=6)
    # Fill
    fill_w = int(rect.width * value / 100)
    if fill_w > 0:
        fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
        pygame.draw.rect(screen, color, fill_rect, border_radius=6)
    # Knob
    knob_x = rect.x + fill_w
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, rect.centery), 10)
    pygame.draw.rect(screen, (100, 100, 160), rect, 2, border_radius=6)
    return rect


# ─── MAIN MENU ────────────────────────────────────────────────────────────────
def draw_main_menu(screen, screen_w, screen_h, menu_bg, menu_logo, play_img, settings_img, quit_img=None):
    if menu_bg:
        screen.blit(menu_bg, (0, 0))
    else:
        screen.fill((5, 5, 15))

    if menu_logo:
        logo_rect = menu_logo.get_rect(center=(screen_w // 2, screen_h // 2 - 220))
        mask = pygame.mask.from_surface(menu_logo)
        shadow_surf = mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
        screen.blit(shadow_surf, (logo_rect.x + 10, logo_rect.y + 5))
        screen.blit(menu_logo, logo_rect)

    # PLAY button
    play_btn = pygame.Rect(screen_w // 2 - 100, screen_h // 2 + 30, 300, 80)
    if play_img:
        screen.blit(play_img, play_btn.topleft)
    else:
        pygame.draw.rect(screen, (50, 200, 100), play_btn, border_radius=10)
        screen.blit(render_pixel_text("PLAY", UI_MEDIUM, (0, 0, 0), bold=True),
                    render_pixel_text("PLAY", UI_MEDIUM, (0, 0, 0), bold=True).get_rect(center=play_btn.center))

    # SETTINGS button
    settings_btn = pygame.Rect(screen_w // 2 - 115, screen_h // 2 + 130, 300, 80)
    if settings_img:
        screen.blit(settings_img, settings_btn.topleft)
    else:
        pygame.draw.rect(screen, (150, 100, 255), settings_btn, border_radius=10)
        screen.blit(render_pixel_text("SETTINGS", UI_MEDIUM, (0, 0, 0), bold=True),
                    render_pixel_text("SETTINGS", UI_MEDIUM, (0, 0, 0), bold=True).get_rect(center=settings_btn.center))

    # QUIT button (below settings)
    quit_btn = pygame.Rect(screen_w // 2 - 75, screen_h // 2 + 230, 220, 70)
    if quit_img:
        screen.blit(quit_img, quit_btn.topleft)
    else:
        pygame.draw.rect(screen, (180, 40, 40), quit_btn, border_radius=10)
        pygame.draw.rect(screen, (255, 80, 80), quit_btn, 2, border_radius=10)
        q_txt = render_pixel_text("QUIT", UI_MEDIUM, (255, 255, 255), bold=True)
        screen.blit(q_txt, q_txt.get_rect(center=quit_btn.center))

    return play_btn, settings_btn, quit_btn


# ─── LOGIN SCREEN ─────────────────────────────────────────────────────────────
def draw_login_screen(screen, screen_w, screen_h, menu_bg, user_name, user_password,
                      input_field_active, password_error_msg, password_error_timer,
                      menu_logo, login_img, back_img=None):

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

    # USERNAME
    if login_img:
        user_box_rect = login_img.get_rect(center=(screen_w // 2, screen_h // 2 + 30))
        user_input_rect = user_box_rect.copy()
        screen.blit(login_img, user_box_rect.topleft)
        if input_field_active == "username":
            pygame.draw.rect(screen, (0, 0, 5, 200), user_box_rect, 5, border_radius=8)
        u_display = f"{user_name}|" if input_field_active == "username" else user_name
        u_txt = render_pixel_text(u_display if user_name else "Username", 18, (255, 255, 255))
        screen.blit(u_txt, u_txt.get_rect(center=user_box_rect.center))
    else:
        user_box_rect = pygame.Rect(screen_w // 2 - 175, screen_h // 2 + 10, 350, 50)
        user_input_rect = user_box_rect.copy()
        pygame.draw.rect(screen, (30, 30, 50), user_box_rect, border_radius=10)

    # PASSWORD
    if login_img:
        pass_box_rect = login_img.get_rect(center=(screen_w // 2, screen_h // 2 + 110))
        pass_input_rect = pass_box_rect.copy()
        screen.blit(login_img, pass_box_rect.topleft)
        if input_field_active == "password":
            pygame.draw.rect(screen, (0, 0, 5, 200), pass_box_rect, 5, border_radius=8)
        hidden_pass = "*" * len(user_password)
        p_display = f"{hidden_pass}|" if input_field_active == "password" else hidden_pass
        p_txt = render_pixel_text(p_display if user_password else "Password", 18, (255, 255, 255))
        screen.blit(p_txt, p_txt.get_rect(center=pass_box_rect.center))
    else:
        pass_box_rect = pygame.Rect(screen_w // 2 - 175, screen_h // 2 + 80, 350, 50)
        pass_input_rect = pass_box_rect.copy()
        pygame.draw.rect(screen, (30, 30, 50), pass_box_rect, border_radius=10)

    hint = render_pixel_text("Click fields or press TAB to switch • ENTER to login", 12, (180, 180, 180))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, screen_h // 2 + 180)))

    if password_error_timer > 0:
        err_txt = render_pixel_text(password_error_msg, 14, (255, 80, 80))
        screen.blit(err_txt, err_txt.get_rect(center=(screen_w // 2, screen_h // 2 + 220)))

    # BACK button
    back_btn = pygame.Rect(20, screen_h - 80, 150, 50)
    if back_img:
        screen.blit(back_img, back_btn.topleft)
    else:
        pygame.draw.rect(screen, (100, 100, 150), back_btn, border_radius=10)
        back_text = render_pixel_text("BACK", 16, (255, 255, 255), bold=True)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    return user_input_rect, pass_input_rect, back_btn, None


# ─── SETTINGS OVERLAY (sliders, no master volume) ────────────────────────────
# Slider state — track which slider the user is dragging
_dragging_slider = None   # "music" | "sfx" | None



def draw_settings_overlay(screen, screen_w, screen_h, music_volume, sfx_volume, back_img,
                          mouse_pos=None, mouse_down=False, mouse_up=False):
    global _dragging_slider

    # 1. Zīmējam fonu
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 210))
    screen.blit(overlay, (0, 0))

    title = render_pixel_text("SETTINGS", 44, (0, 255, 150), bold=True)
    screen.blit(title, (screen_w // 2 - title.get_width() // 2, 100))

    # Definējam slīdņu rāmjus
    slider_w = 400
    slider_x = screen_w // 2 - slider_w // 2
    music_rect = pygame.Rect(slider_x, 290, slider_w, 14)
    sfx_rect   = pygame.Rect(slider_x, 390, slider_w, 14)

    # Palīgfunkcija vērtības aprēķināšanai
    def _get_val(rect, mx):
        return max(0, min(100, int((mx - rect.x) / rect.width * 100)))

    # ── VILKŠANAS LOĢIKA ───────────────────────────────────────────────────
    if mouse_pos:
        # If mouse button is held down, try to claim or continue dragging
        if mouse_down:
            if _dragging_slider is None:
                # Initiate drag — check if mouse is near either knob/track
                if music_rect.inflate(0, 30).collidepoint(mouse_pos):
                    _dragging_slider = "music"
                elif sfx_rect.inflate(0, 30).collidepoint(mouse_pos):
                    _dragging_slider = "sfx"

            # Apply drag movement to whichever slider is grabbed
            if _dragging_slider == "music":
                music_volume = _get_val(music_rect, mouse_pos[0])
            elif _dragging_slider == "sfx":
                sfx_volume = _get_val(sfx_rect, mouse_pos[0])
        else:
            # Mouse button released — drop the slider
            _dragging_slider = None

    # ── ZĪMĒŠANA ──────────────────────────────────────────────────────────
    _draw_slider(screen, "Music Volume", music_volume, music_rect, (0, 200, 255))
    _draw_slider(screen, "SFX Volume",   sfx_volume,   sfx_rect,   (200, 100, 255))

    hint = render_pixel_text("Drag sliders to adjust volume", 14, (150, 150, 180))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, 450)))

    # BACK poga
    back_btn = pygame.Rect(screen_w // 2 - 75, screen_h - 150, 150, 50)
    if back_img:
        screen.blit(back_img, back_btn.topleft)
    else:
        pygame.draw.rect(screen, (50, 150, 255), back_btn, border_radius=10)
        back_text = render_pixel_text("BACK", UI_MEDIUM, (0, 0, 0), bold=True)
        screen.blit(back_text, back_text.get_rect(center=back_btn.center))

    return {
        'back': back_btn,
        'music_volume': music_volume,
        'sfx_volume': sfx_volume,
        'dragging': _dragging_slider 
    }


# ─── LEADERBOARD with search bar ─────────────────────────────────────────────
def draw_leaderboard(screen, leaderboard, lb_x, lb_y, lb_w, lb_h,
                     search_text="", search_active=False, search_result=""):
    """
    Draw the leaderboard panel with a search bar at the bottom.
    leaderboard: list of (username, char_type, highscore)
    Returns: search_input_rect
    """
    lb_rect = pygame.Rect(lb_x, lb_y, lb_w, lb_h)
    pygame.draw.rect(screen, (15, 15, 30), lb_rect, border_radius=12)
    pygame.draw.rect(screen, (0, 255, 150), lb_rect, 2, border_radius=12)

    screen.blit(render_pixel_text("LEADERBOARD", 20, (255, 255, 255), bold=True),
                (lb_x + 20, lb_y + 18))

    if leaderboard:
        for idx, (name, char_type, score) in enumerate(leaderboard):
            y = lb_y + 55 + idx * 38
            rank_color = [(255, 215, 0), (192, 192, 192), (205, 127, 50)][idx] if idx < 3 else (200, 200, 255)
            rank_surf  = render_pixel_text(f"#{idx+1}", 15, rank_color, bold=True)
            name_surf  = render_pixel_text(f"{name or '---'} ({char_type or 'N/A'})", 14, (200, 200, 255))
            score_surf = render_pixel_text(str(score), 14, (0, 255, 150))
            screen.blit(rank_surf,  (lb_x + 12,          y))
            screen.blit(name_surf,  (lb_x + 48,          y))
            screen.blit(score_surf, (lb_x + lb_w - 60,   y))
    else:
        screen.blit(render_pixel_text("No data yet", 14, (150, 150, 150)), (lb_x + 20, lb_y + 55))

    # ── Search bar ──────────────────────────────────────────────────────────
    search_bar_rect = pygame.Rect(lb_x + 10, lb_y + lb_h - 70, lb_w - 20, 34)
    bar_color = (40, 40, 80) if not search_active else (60, 60, 120)
    border_color = (0, 255, 150) if search_active else (80, 80, 120)
    pygame.draw.rect(screen, bar_color, search_bar_rect, border_radius=8)
    pygame.draw.rect(screen, border_color, search_bar_rect, 2, border_radius=8)

    placeholder = "Search username…"
    display_text = (search_text + "|") if search_active else (search_text if search_text else placeholder)
    text_color   = (255, 255, 255) if search_text else (120, 120, 160)
    search_surf  = render_pixel_text(display_text, 14, text_color)
    screen.blit(search_surf, (search_bar_rect.x + 8, search_bar_rect.y + 8))

    # ── Result line ─────────────────────────────────────────────────────────
    if search_result:
        res_surf = render_pixel_text(search_result, 13, (255, 215, 0), bold=True)
        screen.blit(res_surf, res_surf.get_rect(center=(lb_x + lb_w // 2, lb_y + lb_h - 20)))

    return search_bar_rect


# ─── DELETE ACCOUNT CONFIRMATION OVERLAY ─────────────────────────────────────
def draw_delete_confirm(screen, screen_w, screen_h,
                        delete_password="", delete_pw_active=False,
                        delete_error_msg="", delete_error_timer=0):
    """
    Draw a modal confirmation dialog for account deletion.
    Requires the player to re-enter their password before deletion is allowed.

    Returns: (confirm_btn_rect, cancel_btn_rect, password_input_rect)
    """
    # Dim background
    dim = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 190))
    screen.blit(dim, (0, 0))

    # Dialog box — taller to fit the password field
    box_w, box_h = 500, 310
    box_rect = pygame.Rect(screen_w // 2 - box_w // 2, screen_h // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(screen, (25, 8, 8), box_rect, border_radius=14)
    pygame.draw.rect(screen, (200, 50, 50), box_rect, 3, border_radius=14)

    # Title
    title_surf = render_pixel_text("DELETE ACCOUNT?", 26, (255, 60, 60), bold=True)
    screen.blit(title_surf, title_surf.get_rect(center=(screen_w // 2, box_rect.y + 38)))

    # Warning line
    warn_surf = render_pixel_text("This will permanently delete ALL your data!", 14, (255, 180, 180))
    screen.blit(warn_surf, warn_surf.get_rect(center=(screen_w // 2, box_rect.y + 78)))

    # ── Password label ────────────────────────────────────────────────────
    pw_label = render_pixel_text("Enter your password to confirm:", 13, (200, 160, 160))
    screen.blit(pw_label, pw_label.get_rect(center=(screen_w // 2, box_rect.y + 118)))

    # Password input box
    pw_input_rect = pygame.Rect(screen_w // 2 - 170, box_rect.y + 136, 340, 44)
    border_col = (255, 80, 80) if delete_pw_active else (140, 50, 50)
    pygame.draw.rect(screen, (40, 12, 12), pw_input_rect, border_radius=8)
    pygame.draw.rect(screen, border_col, pw_input_rect, 2, border_radius=8)

    hidden = "*" * len(delete_password)
    display_pw = (hidden + "|") if delete_pw_active else (hidden if delete_password else "Password")
    pw_color   = (255, 255, 255) if delete_password else (130, 90, 90)
    pw_surf    = render_pixel_text(display_pw, 16, pw_color)
    screen.blit(pw_surf, pw_surf.get_rect(center=pw_input_rect.center))

    # Error message
    if delete_error_timer > 0 and delete_error_msg:
        err_surf = render_pixel_text(delete_error_msg, 13, (255, 80, 80))
        screen.blit(err_surf, err_surf.get_rect(center=(screen_w // 2, box_rect.y + 198)))

    # ── Buttons ───────────────────────────────────────────────────────────
    confirm_btn = pygame.Rect(screen_w // 2 - 200, box_rect.y + 226, 180, 50)
    pygame.draw.rect(screen, (180, 30, 30), confirm_btn, border_radius=10)
    pygame.draw.rect(screen, (255, 80, 80), confirm_btn, 2, border_radius=10)
    c_txt = render_pixel_text("YES, DELETE", 16, (255, 255, 255), bold=True)
    screen.blit(c_txt, c_txt.get_rect(center=confirm_btn.center))

    cancel_btn = pygame.Rect(screen_w // 2 + 20, box_rect.y + 226, 180, 50)
    pygame.draw.rect(screen, (40, 100, 40), cancel_btn, border_radius=10)
    pygame.draw.rect(screen, (0, 200, 100), cancel_btn, 2, border_radius=10)
    x_txt = render_pixel_text("CANCEL", 16, (255, 255, 255), bold=True)
    screen.blit(x_txt, x_txt.get_rect(center=cancel_btn.center))

    return confirm_btn, cancel_btn, pw_input_rect