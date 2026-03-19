import pygame
import time
import math
import random
import sys

# --- 1. INITIALIZATION ---
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 1000, 600
FPS = 60
SONG_BPM = 120
BEAT_INTERVAL = 60 / SONG_BPM
LEVEL_DISTANCE = 55428
BASE_GROUND_HEIGHT = 100

BG_COLOR = (26, 26, 46)
ACCENT_COLOR = (255, 255, 0)
PLAYER_COLOR = (0, 255, 210)
OBSTACLE_COLOR = (255, 255, 0)
GROUND_COLOR = (22, 33, 62)
TEXT_COLOR = (255, 255, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat Dash")
clock = pygame.time.Clock()

# --- 2. ASSETS ---
try:
    pygame.mixer.music.load('sfx/soundtracklv1(ver2).mp3')
    death_sfx = pygame.mixer.Sound('sfx/deathsfx(ver2).mp3')
    start_sfx = pygame.mixer.Sound('sfx/start.mp3')
    end_sfx = pygame.mixer.Sound('sfx/lvlcomplete.mp3')

except:
    death_sfx = None
try:
    bg_image = pygame.image.load('images/Background/aibg2.png').convert()
    bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
except:
    bg_image = None

font_title = pygame.font.SysFont("Arial", 80, bold=True)
font_ui = pygame.font.SysFont("Arial", 22, bold=True)
font_btn = pygame.font.SysFont("Arial", 30, bold=True)


# --- 3. CLASSES ---
def get_ground_height(world_x, locked_height=None):
    if locked_height is not None:
        return locked_height
    chunk_idx = int(world_x // 800)
    levels = [0, 0, 1, 1, 2, 1, 0, -1, -1, 0, 1, 2, 2, 3, 2, 1, 0]
    return BASE_GROUND_HEIGHT + levels[chunk_idx % len(levels)] * 40


class Player:
    def __init__(self):
        self.height = 40
        self.width = 60

        self.size = 40
        self.x = 50
        self.y = HEIGHT - BASE_GROUND_HEIGHT - self.height

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # --- PHYSICS SETTINGS ---
        self.vel_y = 0
        self.gravity = 0.8
        self.jump_force = -14
        self.rotation = 0
        self.is_jumping = False

        # --- ANIMATION SETTINGS ---
        self.run_frames = []
        for i in range(1, 8):
            try:
                img = pygame.image.load(f'Images/cat/run/Run_{i}.png').convert_alpha()
                self.run_frames.append(pygame.transform.scale(img, (self.width, self.height)))
            except Exception as e:
                print(f"Error loading Run_{i}.png: {e}")
                self.run_frames.append(None)

        self.jump_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(f'Images/cat/Jump/Jump_{i}.png').convert_alpha()
                self.jump_frames.append(pygame.transform.scale(img, (self.width, self.height)))
            except Exception as e:
                print(f"Error loading Jump_{i}.png: {e}")
                self.jump_frames.append(None)

        self.anim_index = 0
        self.anim_speed = 0.2

    def jump(self):
        if not self.is_jumping:
            self.vel_y = self.jump_force
            self.is_jumping = True

    def update(self, ground_rects):
        self.vel_y += self.gravity
        self.y += self.vel_y
        self.rect.y = self.y

        died = False
        for r in ground_rects:
            if self.rect.colliderect(r):
                if self.vel_y >= 0 and (self.rect.bottom - self.vel_y) <= r.top + 10:
                    self.rect.bottom = r.top
                    self.y = self.rect.y
                    self.vel_y = 0
                    self.is_jumping = False

                else:
                    died = True

        if self.is_jumping:
            # self.rotation -= 7
            pass

        return "DIE" if died else "OK"

    def draw(self, screen):
        current_sprite = None

        if self.is_jumping:
            # --- JUMP ANIMATION LOGIC ---
            # 1. Start of jump
            if self.vel_y < -5:
                current_sprite = self.jump_frames[0]
            # 2. Airborne
            elif -5 <= self.vel_y <= 5:
                current_sprite = self.jump_frames[1]
            # 3. Landing
            else:
                current_sprite = self.jump_frames[2]
        else:
            # --- RUN ANIMATION LOGIC ---
            self.anim_index += self.anim_speed
            if self.anim_index >= len(self.run_frames):
                self.anim_index = 0
            idx = int(self.anim_index)
            if idx < len(self.run_frames):
                current_sprite = self.run_frames[idx]

        if current_sprite:
            screen.blit(current_sprite, (self.x, self.y))


class Obstacle:
    def __init__(self, x, type, current_dist):
        self.type = type
        self.x = x
        self.size = 40
        self.y = HEIGHT - get_ground_height(current_dist + x) - self.size
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        self.start_dist = WIDTH

    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x

    def draw(self, surface, p_x, p_y):
        # 1. The Line and Circle
        hit_x = p_x + 30
        current_dist = self.x - hit_x
        dist_ratio = self.start_dist if self.start_dist != 0 else WIDTH
        ratio = max(1.0, (current_dist / dist_ratio) * 3 + 1)

        if self.x > p_x - 50 and ratio < 4:
            fx_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            line_alpha = int(100 / ratio)
            pygame.draw.line(fx_surf, (255, 255, 255, line_alpha),
                             (p_x + 20, p_y + 20), (self.x + 20, self.y + 20), 2)
            pygame.draw.circle(fx_surf, (255, 255, 255, 120),
                               (int(p_x + 20), int(p_y + 20)), int(35 * (ratio - 0.25)), 2)
            surface.blit(fx_surf, (0, 0))

        # 2. DRAW THE PNG IMAGE
        if self.type == 'spike' and game.spike_img:
            surface.blit(game.spike_img, (self.x, self.y - 10))
        elif self.type == 'block' and game.block_img:
            surface.blit(game.block_img, (self.x, self.y - 10))
        else:
            color = (233, 69, 96)
            if self.type == 'spike':
                pygame.draw.polygon(surface, color, [
                    (self.x, self.y + self.size),
                    (self.x + self.size // 2, self.y),
                    (self.x + self.size, self.y + self.size)
                ])
            else:
                pygame.draw.rect(surface, color, self.rect)


class Portal:
    def __init__(self, x, current_dist):
        self.width = 60
        self.height = 120
        self.x = x
        world_x = current_dist + self.x
        gh = get_ground_height(world_x)
        self.y = HEIGHT - gh - self.height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.angle = 0

    def update(self, speed):
        self.x -= speed
        self.rect.x = self.x
        self.angle += 5

    def draw(self, surface):
        portal_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for i in range(5):
            alpha = 150 - (i * 30)
            size_adj = i * 4
            pygame.draw.ellipse(portal_surf, (0, 255, 210, alpha),
                                (size_adj, size_adj, self.width - size_adj * 2, self.height - size_adj * 2), 3)
        pygame.draw.circle(portal_surf, (255, 255, 255), (self.width // 2, self.height // 2), 5)
        surface.blit(portal_surf, (self.x, self.y))


# --- 4. GAME ENGINE STATE ---
class Game:
    def __init__(self):
        self.state = "MENU"
        self.is_endless = False
        self.autoplay = True
        self.attempts = 1
        self.high_score = 0

        self.master_volume = 0.14
        self.cue_volume = 0.19
        self.settings_idx = 0
        self.level_idx = 0

        self.click_sfx = None
        self.cue_sfx = None
        self.start_sfx = None
        self.end_sfx = None
        self.death_sfx = None

        self.SP_START_EVENT = pygame.USEREVENT + 1
        self.SP_JUMP_EVENT = pygame.USEREVENT + 2
        self.sp_start = None
        self.sp_jump = None
        self.level_tracks = []
        self.target_start_dist = 0

        if 'start_sfx' in globals(): self.start_sfx = start_sfx
        if 'end_sfx' in globals(): self.end_sfx = end_sfx
        if 'death_sfx' in globals(): self.death_sfx = death_sfx

        try:
            self.click_sfx = pygame.mixer.Sound('sfx/click.mp3')
            self.cue_sfx = pygame.mixer.Sound('sfx/jumpcue.mp3')
        except Exception as e:
            print(f"Note: Optional sounds (click/cue) not found: {e}")

        try:
            self.sp_start = pygame.mixer.Sound('sfx/Spstart.wav')
            self.sp_jump = pygame.mixer.Sound('sfx/SpJump.wav')
        except Exception as e:
            print(f"Error loading Sp files: {e}")

        import os
        for i in range(1, 16):
            path_mp3 = os.path.join('lvl', f'lvl{i}.mp3')
            path_wav = os.path.join('lvl', f'lvl{i}.wav')
            try:
                if os.path.exists(path_mp3):
                    track = pygame.mixer.Sound(path_mp3)
                elif os.path.exists(path_wav):
                    track = pygame.mixer.Sound(path_wav)
                else:
                    track = None

                if track: track.set_volume(self.master_volume * 10)
                self.level_tracks.append(track)
            except:
                self.level_tracks.append(None)

            for sfx in [self.start_sfx, self.end_sfx, self.death_sfx, self.click_sfx]:
                if sfx:
                    sfx.set_volume(self.master_volume)

            if self.sp_start:
                self.sp_start.set_volume(self.master_volume * 0)
            if self.sp_jump:
                self.sp_jump.set_volume(self.master_volume * 100)

        if self.cue_sfx:
            self.cue_sfx.set_volume(self.cue_volume)

        pygame.time.set_timer(self.SP_START_EVENT, 1000)
        # --- LOAD TERRAIN PNGS ---
        try:
            self.tile_size = 80
            r1 = pygame.image.load('images/terrain/Rooftop/roof1.png').convert_alpha()
            r2 = pygame.image.load('images/terrain/Rooftop/roof2.png').convert_alpha()

            wall = pygame.image.load('images/terrain/Walls/wall.png').convert_alpha()

            self.roof_variants = [
                pygame.transform.scale(r1, (self.tile_size, self.tile_size)),
                pygame.transform.scale(r1, (self.tile_size, self.tile_size)),
                pygame.transform.scale(r1, (self.tile_size, self.tile_size)),
                pygame.transform.scale(r1, (self.tile_size, self.tile_size)),
                pygame.transform.scale(r2, (self.tile_size, self.tile_size))
            ]
            self.filler_img = pygame.transform.scale(wall, (self.tile_size, self.tile_size))

        except Exception as e:
            print(f"Error loading terrain PNGs: {e}")
            self.roof_variants = []
            self.filler_img = None
        # --- LOAD OBSTACLE PNG IMAGES ---
        try:
            self.spike_img = pygame.image.load('images/Obstacles/chimney.png').convert_alpha()
            self.block_img = pygame.image.load('images/Obstacles/antenna.png').convert_alpha()
            self.spike_img = pygame.transform.scale(self.spike_img, (50, 50))
            self.block_img = pygame.transform.scale(self.block_img, (50, 50))
        except Exception as e:
            print(f"Error loading obstacle PNGs: {e}")
            self.spike_img = None
            self.block_img = None

        self.death_frames = []
        for i in range(1, 10):
            try:
                img = pygame.image.load(f'Images/cat/Death/Explosion_{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (120, 120))
                self.death_frames.append(img)
            except:
                print(f"Could not load Explosion_{i}.png")
        self.death_index = -1
        self.reset_game()
        self.last_progress = 0
        pygame.mixer.music.set_volume(self.master_volume)



    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.game_speed = 6
        self.current_dist = 0
        self.start_time = 0
        self.next_spawn_time = 2.0
        self.time_offset = 0
        self.portal = None
        self.smooth_spike = 1.0
        self.beat_index = 0
        self.final_h = None
        self.flatten_start_x = 9999999
        self.cue_played_for_this_obs = False
        self.cue_flash_alpha = 0

    def draw_text(self, text, font, color, x, y, center=True):
        img = font.render(text, True, color)
        rect = img.get_rect()
        if center:
            rect.center = (x, y)
        else:
            rect.topleft = (x, y)
        screen.blit(img, rect)

    def draw_soundwaves(self):
        num_bars = 80
        bar_w = WIDTH / num_bars
        target_spike = 1.0
        obs_spike = 1.0
        wall_spike = 1.0

        for obs in self.obstacles:
            dist = obs.x - self.player.x
            if 0 < dist < 500:
                proximity = 1.0 - (dist / 500)
                obs_spike = 1.0 + (math.sin(proximity * math.pi / 2) * 2.8)
                break

        p_wx = self.current_dist + self.player.x
        curr_h = get_ground_height(p_wx)
        for scan in range(50, 500, 50):
            if get_ground_height(p_wx + scan) > curr_h:
                proximity = 1.0 - (scan / 500)
                wall_spike = 1.0 + (math.sin(proximity * math.pi / 2) * 2.8)
                break

        target_spike = max(obs_spike, wall_spike)

        if target_spike > self.smooth_spike:
            self.smooth_spike += (target_spike - self.smooth_spike) * 0.12
        else:
            self.smooth_spike += (target_spike - self.smooth_spike) * 0.25

        for i in range(num_bars):
            x_pos = i * bar_w
            wave = math.sin(self.time_offset * 0.8 + i * 0.1) * 0.4
            wave += math.sin(self.time_offset * 0.4 + i * 0.05) * 0.3
            h = int(((wave + 1) / 2) * (110 * self.smooth_spike)) + 250

            wave_surf = pygame.Surface((int(bar_w) + 1, h), pygame.SRCALPHA)
            alpha = min(200, int(35 * self.smooth_spike))
            wave_surf.fill((233, 69, 96, alpha))
            screen.blit(wave_surf, (x_pos, (BASE_GROUND_HEIGHT + 600) - h))

            top_h = (h - 200) // 2.5
            top_surf = pygame.Surface((int(bar_w) + 1, top_h), pygame.SRCALPHA)
            top_surf.fill((233, 69, 96, alpha // 2))
            screen.blit(top_surf, (x_pos, 0))

    def run(self):
        while True:
            if self.state == "MENU":
                self.menu_screen()
            elif self.state == "SETTINGS":
                self.settings_screen()
            elif self.state == "LEVEL_SELECT":
                self.level_menu()
            elif self.state == "PLAYING":
                self.play_screen()
            elif self.state == "PAUSED":
                self.pause_screen()
            elif self.state == "CLEAR":
                self.clear_screen()
            elif self.state == "GAMEOVER":
                self.game_over_screen()

    def menu_screen(self):
        while self.state == "MENU":
            screen.fill(BG_COLOR)
            self.draw_text("CAT DASH", font_title, ACCENT_COLOR, WIDTH // 2, 120)
            self.draw_text("PROOF OF CONCEPT", font_btn, PLAYER_COLOR, WIDTH // 2, 190)

            mode_text = "Endless Mode: ON" if self.is_endless else "Level Mode: ON"
            self.draw_text(f"1. {mode_text}", font_ui, TEXT_COLOR, WIDTH // 2, 280)
            self.draw_text(f"2. Autopilot: {'ON' if self.autoplay else 'OFF'}", font_ui, TEXT_COLOR, WIDTH // 2, 310)

            self.draw_text("PRESS [SPACE] TO PLAY", font_btn, (255, 255, 255), WIDTH // 2, 420)
            self.draw_text("PRESS [S] FOR SETTINGS", font_btn, PLAYER_COLOR, WIDTH // 2, 480)

            if self.is_endless:
                self.draw_text(f"High Score: {int(self.high_score)}", font_ui, TEXT_COLOR, WIDTH // 2, 540)
            else:
                self.draw_text(f"Attempts: {self.attempts}", font_ui, TEXT_COLOR, WIDTH // 2, 540)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: self.is_endless = not self.is_endless
                    if event.key == pygame.K_2: self.autoplay = not self.autoplay
                    if event.key == pygame.K_s: self.state = "SETTINGS"
                    if event.key == pygame.K_SPACE:
                        if event.key == pygame.K_SPACE:
                            if self.is_endless:
                                self.reset_game()
                                pygame.time.set_timer(self.SP_JUMP_EVENT, 1000)
                                if self.start_sfx: self.start_sfx.play()
                                pygame.mixer.music.play(-1)
                                self.state = "PLAYING"
                            else:
                                if self.sp_start:
                                    self.sp_start.stop()
                                if len(self.level_tracks) > 0 and self.level_tracks[0]:
                                    self.level_tracks[0].play(0)

                                self.state = "LEVEL_SELECT"
            pygame.display.flip()
            clock.tick(FPS)

    def settings_screen(self):
        while self.state == "SETTINGS":
            screen.fill(BG_COLOR)
            self.draw_text("SETTINGS", font_title, PLAYER_COLOR, WIDTH // 2, 100)

            color_m = ACCENT_COLOR if self.settings_idx == 0 else TEXT_COLOR
            self.draw_text(f"MASTER VOLUME: {int(self.master_volume * 100)}%", font_btn, color_m, WIDTH // 2, 250)
            pygame.draw.rect(screen, GROUND_COLOR, (WIDTH // 2 - 100, 280, 200, 10))
            pygame.draw.circle(screen, color_m, (WIDTH // 2 - 100 + int(self.master_volume * 200), 285), 10)

            color_c = ACCENT_COLOR if self.settings_idx == 1 else TEXT_COLOR
            self.draw_text(f"JUMP CUE VOLUME: {int(self.cue_volume * 100)}%", font_btn, color_c, WIDTH // 2, 350)
            pygame.draw.rect(screen, GROUND_COLOR, (WIDTH // 2 - 100, 380, 200, 10))
            pygame.draw.circle(screen, color_c, (WIDTH // 2 - 100 + int(self.cue_volume * 200), 385), 10)

            self.draw_text("UP/DOWN: Select | LEFT/RIGHT: Adjust | ENTER: Save", font_ui, TEXT_COLOR, WIDTH // 2, 500)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        self.settings_idx = 1 - self.settings_idx

                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        change = 0.05 if event.key == pygame.K_RIGHT else -0.05

                        if self.settings_idx == 0:
                            self.master_volume = max(0, min(1, self.master_volume + change))
                            pygame.mixer.music.set_volume(self.master_volume)

                            if self.start_sfx: self.start_sfx.set_volume(self.master_volume)
                            if self.end_sfx: self.end_sfx.set_volume(self.master_volume)
                            if self.death_sfx: self.death_sfx.set_volume(self.master_volume)
                            if self.click_sfx:
                                self.click_sfx.set_volume(self.master_volume)
                                self.click_sfx.play()
                        else:
                            self.cue_volume = max(0, min(1, self.cue_volume + change))
                            if self.cue_sfx:
                                self.cue_sfx.set_volume(self.cue_volume)
                                self.cue_sfx.play()

                    if event.key == pygame.K_RETURN:
                        self.state = "MENU"

            pygame.display.flip()
            clock.tick(FPS)

    def level_menu(self):
        while self.state == "LEVEL_SELECT":
            screen.fill(BG_COLOR)
            self.draw_text("SELECT LEVEL", font_title, PLAYER_COLOR, WIDTH // 2, 80)

            for i in range(15):
                row = i // 5
                col = i % 5
                x = 200 + col * 150
                y = 200 + row * 100

                color = ACCENT_COLOR if self.level_idx == i else GROUND_COLOR
                txt_color = TEXT_COLOR if i == 0 else (100, 100, 100)

                pygame.draw.rect(screen, color, (x - 60, y - 35, 120, 70), border_radius=10)
                self.draw_text(str(i + 1), font_btn, txt_color, x, y)

            self.draw_text("Arrows to Move | SPACE to Start | Q for Menu", font_ui, TEXT_COLOR, WIDTH // 2, 520)

            for event in pygame.event.get():
                if event.type == self.SP_START_EVENT:
                    if self.sp_start: self.sp_start.play()
                    pygame.time.set_timer(self.SP_START_EVENT, 0)

                if event.type == self.SP_JUMP_EVENT:
                    if self.sp_jump: self.sp_jump.play()
                    pygame.time.set_timer(self.SP_JUMP_EVENT, 0)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN]:
                        if self.click_sfx:
                            self.click_sfx.play()
                    old_idx = self.level_idx

                    if event.key == pygame.K_RIGHT: self.level_idx = (self.level_idx + 1) % 15
                    if event.key == pygame.K_LEFT: self.level_idx = (self.level_idx - 1) % 15
                    if event.key == pygame.K_DOWN: self.level_idx = (self.level_idx + 5) % 15
                    if event.key == pygame.K_UP: self.level_idx = (self.level_idx - 5) % 15

                    if old_idx != self.level_idx:
                        if self.click_sfx:
                            self.click_sfx.play()

                        for track in self.level_tracks:
                            if track: track.stop()

                        if self.level_idx < len(self.level_tracks):
                            track = self.level_tracks[self.level_idx]
                            if track:
                                track.play(0)

                    if event.key == pygame.K_q:
                        self.state = "MENU"

                    if event.key == pygame.K_SPACE:
                        if self.level_idx == 0:
                            self.reset_game()
                            pygame.time.set_timer(self.SP_JUMP_EVENT, 1000)
                            if self.start_sfx: self.start_sfx.play()
                            pygame.mixer.music.play(0)
                            self.state = "PLAYING"


            pygame.display.flip()
            clock.tick(FPS)

    def game_over_screen(self):
        while self.state == "GAMEOVER":
            screen.fill(BG_COLOR)
            self.draw_soundwaves()
            self.draw_text("GAME OVER", font_title, OBSTACLE_COLOR, WIDTH // 2, 180)

            pygame.draw.rect(screen, GROUND_COLOR, (WIDTH // 2 - 200, 250, 400, 150), border_radius=15)

            if self.is_endless:
                self.draw_text(f"SCORE: {int(self.current_dist)}", font_btn, TEXT_COLOR, WIDTH // 2, 290)
                self.draw_text(f"HIGH SCORE: {int(self.high_score)}", font_btn, PLAYER_COLOR, WIDTH // 2, 340)
            else:
                self.draw_text(f"PROGRESS: {self.last_progress}%", font_btn, TEXT_COLOR, WIDTH // 2, 290)

                bar_x = WIDTH // 2 - 150
                bar_y = 330
                bar_w = 300
                bar_h = 20

                pygame.draw.rect(screen, (40, 40, 70), (bar_x, bar_y, bar_w, bar_h), border_radius=10)

                fill_w = int(bar_w * (self.last_progress / 100))

                if fill_w > 5:
                    pygame.draw.rect(screen, PLAYER_COLOR, (bar_x, bar_y, fill_w, bar_h), border_radius=10)

                pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_w, bar_h), 2, border_radius=10)

                self.draw_text(f"ATTEMPT {self.attempts}", font_ui, TEXT_COLOR, WIDTH // 2, 375)

            self.draw_text("PRESS SPACE TO RESTART | Q FOR MENU", font_ui, TEXT_COLOR, WIDTH // 2, 480)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                        pygame.mixer.music.play(-1 if self.is_endless else 0)
                        self.state = "PLAYING"
                    if event.key == pygame.K_q:
                        self.state = "MENU"

            pygame.display.flip()
            clock.tick(FPS)

    def pause_screen(self):
        pygame.mixer.music.pause()
        while self.state == "PAUSED":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            self.draw_text("PAUSED", font_title, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 - 50)
            self.draw_text("ESC to Resume | Q for Main Menu", font_btn, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.mixer.music.unpause()
                        self.state = "PLAYING"
                    if event.key == pygame.K_q:
                        pygame.mixer.music.stop()
                        self.state = "MENU"
            pygame.display.flip()
            clock.tick(FPS)

    def play_screen(self):
        STRICT_MIN = 0.7
        RANDOM_EXTRA = 1.2

        while self.state == "PLAYING":
            if 'bg_image' in globals() and bg_image:
                screen.blit(bg_image, (0, 0))
            else:
                screen.fill(BG_COLOR)

            raw_pos = pygame.mixer.music.get_pos()
            song_time = raw_pos / 1000.0 if raw_pos != -1 else 0
            self.time_offset += 0.05
            lock_h = None

            for event in pygame.event.get():
                if event.type == self.SP_START_EVENT:
                    if self.sp_start: self.sp_start.play()
                    pygame.time.set_timer(self.SP_START_EVENT, 0)
                if event.type == self.SP_JUMP_EVENT:
                    if self.sp_jump: self.sp_jump.play()
                    pygame.time.set_timer(self.SP_JUMP_EVENT, 0)
                if event.type == pygame.QUIT:
                    pygame.quit();
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"
                    if event.key == pygame.K_b:
                        self.autoplay = not self.autoplay

            if self.death_index == -1 and self.portal is None:
                if song_time >= self.next_spawn_time:
                    world_spawn_x = self.current_dist + WIDTH
                    dist_to_prev = world_spawn_x % 800
                    dist_to_next = 800 - dist_to_prev
                    gh_prev = get_ground_height(world_spawn_x - dist_to_prev - 1)
                    gh_my = get_ground_height(world_spawn_x)
                    gh_next = get_ground_height(world_spawn_x + dist_to_next + 1)

                    valid_spawn = True
                    if dist_to_prev < 200 and gh_prev != gh_my: valid_spawn = False
                    if dist_to_next < 250 and gh_next != gh_my: valid_spawn = False

                    if valid_spawn:
                        obs_type = random.choice(['spike', 'block'])
                        self.obstacles.append(Obstacle(WIDTH, obs_type, self.current_dist))
                        self.next_spawn_time = song_time + STRICT_MIN + random.uniform(0, RANDOM_EXTRA)
                    else:
                        self.next_spawn_time = song_time + 0.1

            if self.death_index == -1 and raw_pos != -1:
                self.current_dist += self.game_speed

                if self.portal is not None and self.final_h is None:
                    self.flatten_start_x = self.current_dist + self.player.x

                    self.final_h = get_ground_height(self.flatten_start_x)


                    portal_height_size = 100
                    self.portal.y = HEIGHT - self.final_h - portal_height_size
                    self.portal.rect.y = self.portal.y

            ground_rects = []
            start_chunk = int(self.current_dist // 800)
            end_chunk = int((self.current_dist + WIDTH) // 800) + 1

            for chunk_idx in range(start_chunk, end_chunk + 1):
                world_x = chunk_idx * 800

                if self.final_h is not None and world_x >= (self.flatten_start_x - 800):
                    gh = self.final_h
                else:
                    gh = get_ground_height(world_x)

                screen_x = world_x - self.current_dist
                ground_rects.append(pygame.Rect(screen_x, HEIGHT - gh, 800, gh))

            self.draw_soundwaves()
            for r in ground_rects:
                tiles_x = r.width // self.tile_size

                start_world_x = r.left + self.current_dist

                for tx in range(tiles_x):
                    world_tx = int((start_world_x // self.tile_size) + tx)

                    tile_x = r.left + (tx * self.tile_size)

                    if -self.tile_size < tile_x < WIDTH:
                        if self.roof_variants:
                            variant_idx = world_tx % len(self.roof_variants)
                            screen.blit(self.roof_variants[variant_idx], (tile_x, r.top))

                        current_y = r.top + self.tile_size
                        while current_y < HEIGHT:
                            if self.filler_img:
                                screen.blit(self.filler_img, (tile_x, current_y))
                            else:
                                pygame.draw.rect(screen, GROUND_COLOR,
                                                 (tile_x, current_y, self.tile_size, self.tile_size))
                            current_y += self.tile_size

            fx_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

            p_x = self.player.x
            p_y = self.player.y
            p_wx = self.current_dist + p_x
            curr_h = get_ground_height(p_wx)

            found_wall = False
            for scan in range(50, 1000, 10):
                ahead_h = get_ground_height(p_wx + scan)

                if ahead_h > curr_h:
                    found_wall = True
                    target_x = (p_wx + scan) - self.current_dist
                    target_y = HEIGHT - ahead_h

                    current_dist = scan

                    if self.target_start_dist == 0:
                        self.target_start_dist = current_dist

                    dist_ratio = self.target_start_dist if self.target_start_dist != 0 else 1000
                    ratio = max(1.0, (current_dist / dist_ratio) * 3 + 1)

                    if target_x > p_x - 50 and ratio < 4:
                        line_alpha = int(100 / ratio)

                        pygame.draw.line(fx_surf, (255, 255, 0, line_alpha),
                                         (p_x + 20, p_y + 20),
                                         (target_x + 20, target_y + 20), 2)

                        pygame.draw.circle(fx_surf, (255, 255, 0, 120),
                                           (int(p_x + 20), int(p_y + 20)),
                                           int(35 * (ratio - 0.25)), 2)
                    break

            if not found_wall:
                self.target_start_dist = 0

            screen.blit(fx_surf, (0, 0))

            status = self.player.update(ground_rects)
            collision = any(self.player.rect.colliderect(obs.rect) for obs in self.obstacles)

            if self.autoplay and self.death_index == -1:
                curr_p_h = get_ground_height(self.current_dist + self.player.x, lock_h)
                ahead_p_h = get_ground_height(self.current_dist + self.player.x + self.game_speed * 15, lock_h)
                if ahead_p_h > curr_p_h and not self.player.is_jumping:
                    self.player.jump()
                for obs in self.obstacles:
                    if 0 < (obs.x - self.player.x) < (self.game_speed * 15) and not self.player.is_jumping:
                        self.player.jump()

            p_wx = self.current_dist + self.player.x
            cue_range = self.game_speed * 27
            near_obs = any(0 < (obs.x - self.player.x) < cue_range for obs in self.obstacles)
            if get_ground_height(p_wx + cue_range) > get_ground_height(p_wx): near_obs = True

            if near_obs and not self.cue_played_for_this_obs and self.death_index == -1:
                if self.cue_sfx:
                    self.cue_sfx.set_volume(self.cue_volume)
                    self.cue_sfx.play()
                self.cue_flash_alpha = 150
                self.cue_played_for_this_obs = True
            elif not near_obs:
                self.cue_played_for_this_obs = False

            if self.cue_flash_alpha > 0:
                flash_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                pygame.draw.rect(flash_surf, (255, 255, 0, int(self.cue_flash_alpha)), (0, 0, WIDTH, HEIGHT), 20)
                screen.blit(flash_surf, (0, 0))
                self.cue_flash_alpha -= 4

            for obs in self.obstacles[:]:
                if self.death_index == -1:
                    obs.update(self.game_speed)
                obs.draw(screen, self.player.x, self.player.y)
                if obs.x < -100: self.obstacles.remove(obs)

            if (status == "DIE" or collision) and self.death_index == -1:
                if not (self.portal is not None and status == "DIE"):
                    self.death_index = 0
                    if self.death_sfx: self.death_sfx.play()
                    pygame.mixer.music.stop()
                    self.last_progress = int((song_time / 149.0) * 100)

            if self.death_index >= 0:
                idx = int(self.death_index)
                if idx < len(self.death_frames):
                    screen.blit(self.death_frames[idx], (self.player.x, self.player.y - 80))
                    self.death_index += 0.25

                if self.death_index >= len(self.death_frames):
                    if self.is_endless:
                        self.high_score = max(self.high_score, self.current_dist)
                    else:
                        self.attempts += 1
                    self.death_index = -1
                    self.state = "GAMEOVER"
                    return
            else:
                self.player.draw(screen)

            if self.is_endless:
                self.draw_text(f"DISTANCE: {int(self.current_dist)}", font_ui, TEXT_COLOR, 20, 25, center=False)
            else:
                progress = min(1.0, song_time / 149.0)
                pygame.draw.rect(screen, PLAYER_COLOR, (0, 0, WIDTH * progress, 6))
                self.draw_text(f"PROGRESS: {int(progress * 100)}% | ATTEMPT {self.attempts}", font_ui, TEXT_COLOR, 20,
                               25, center=False)
                if song_time > 147 and self.portal is None:
                    self.portal = Portal(WIDTH + 200, self.current_dist)

            if self.portal:
                self.portal.update(self.game_speed)
                self.portal.draw(screen)
                if self.player.rect.colliderect(self.portal.rect):
                    pygame.mixer.music.stop()
                    if self.end_sfx: self.end_sfx.play()
                    self.state = "CLEAR"

            pygame.display.flip()
            clock.tick(FPS)

    def clear_screen(self):
        while self.state == "CLEAR":
            screen.fill(BG_COLOR)
            self.draw_soundwaves()
            y_offset = math.sin(time.time() * 5) * 10
            self.draw_text("LEVEL COMPLETE!", font_title, PLAYER_COLOR, WIDTH // 2, 180 + y_offset)
            pygame.draw.rect(screen, GROUND_COLOR, (WIDTH // 2 - 200, 250, 400, 150), border_radius=15)
            self.draw_text(f"Attempts: {self.attempts}", font_btn, TEXT_COLOR, WIDTH // 2, 290)
            self.draw_text(f"Total Distance: {int(self.current_dist)}", font_btn, TEXT_COLOR, WIDTH // 2, 340)
            self.draw_text("PRESS SPACE FOR MAIN MENU", font_ui, TEXT_COLOR, WIDTH // 2, 480)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.attempts = 1
                        self.state = "MENU"
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()