import pygame
import sys
import random
import math
from collections import deque

# 1. 게임 기본 설정 및 상수
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- DJMAX 감성의 모던 & 차분한 색상 팔레트 (네온 배제) ---
BG_DARK = (10, 10, 14)          # 전체 배경 (매우 어두운 차콜)
PANEL_DARK = (20, 20, 26)       # 좌측 패널 및 기어 배경
PANEL_LIGHT = (45, 45, 55)      # 일반 버튼 및 라인 테두리
TEXT_WHITE = (240, 240, 245)    # 메인 텍스트
TEXT_MUTED = (130, 132, 145)    # 서브 텍스트
COLOR_GOLD = (215, 165, 55)     # 포인트 컬러 (BPM, 활성화 키 등)
COLOR_SELECTED = (235, 85, 45)  # 선택 바 하이라이트 (코랄 오렌지)

# 판정 및 노트 색상
COLOR_PERFECT = (220, 180, 60)
COLOR_GOOD = (70, 150, 220)
COLOR_MISS = (170, 55, 55)
COLOR_NOTE_BODY = (230, 235, 245) 
COLOR_NOTE_HIGHLIGHT = (180, 190, 210) 

# 폰트 설정
FONT_DEF = ["malgun gothic", "applesdgothicneo", "notosanskorean", "arial", "sans-serif"]

# --- 리듬게임 핵심 설정 (화면 중앙에 4개 라인 320px 정렬) ---
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_X = [240, 320, 400, 480]  # 각 라인의 시작 X 좌표
LANE_WIDTH = 80                 # 총 가로폭 320px (240 ~ 560)
GEAR_START_X = 240
GEAR_WIDTH = 320
JUDGE_LINE_Y = 500
NOTE_SPEED = 0.5

# --- 그라데이션 둥근 사각형 그리기 함수 ---
def draw_graded_rounded_rect(surface, rect, color1, color2, corner_radius, border_width=0, is_vertical=True):
    if corner_radius > min(rect.width, rect.height) // 2:
        corner_radius = min(rect.width, rect.height) // 2

    if border_width == 0:
        temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        c1_a = color1[3] if len(color1) > 3 else 255
        c2_a = color2[3] if len(color2) > 3 else 255
        
        for i in range(rect.height if is_vertical else rect.width):
            ratio = i / (rect.height if is_vertical else rect.width or 1)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            a = int(c1_a * (1 - ratio) + c2_a * ratio)
            
            if is_vertical:
                pygame.draw.line(temp_surf, (r, g, b, a), (0, i), (rect.width, i))
            else:
                pygame.draw.line(temp_surf, (r, g, b, a), (i, 0), (i, rect.height))
        
        mask_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(mask_surf, (255, 255, 255, 255), (0, 0, rect.width, rect.height), border_radius=corner_radius)
        temp_surf.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surface.blit(temp_surf, rect.topleft)
    else:
        pygame.draw.rect(surface, color1, rect, width=border_width, border_radius=corner_radius)

# 버튼 클래스
class Button:
    def __init__(self, x, y, width, height, text, color1, color2):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color1 = color1 
        self.color2 = color2 
        self.is_hovered = False
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface, font):
        c1 = tuple(min(255, c + 30) for c in self.color1[:3]) if self.is_hovered else self.color1[:3]
        c2 = tuple(min(255, c + 30) for c in self.color2[:3]) if self.is_hovered else self.color2[:3]
        
        draw_graded_rounded_rect(surface, self.rect, c1, c2, corner_radius=10)
        pygame.draw.rect(surface, COLOR_GOLD if self.is_hovered else PANEL_LIGHT, self.rect, width=2, border_radius=10)
        
        text_surf = font.render(self.text, True, TEXT_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

# 파티클 클래스
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.radius = random.randint(2, 5)
        self.color = color
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15 
        self.alpha -= 10
        if self.radius > 0.5:
            self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0:
            int_radius = max(1, int(self.radius))
            p_surf = pygame.Surface((int_radius * 2, int_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, max(0, int(self.alpha))), (int_radius, int_radius), int_radius)
            surface.blit(p_surf, (int(self.x) - int_radius, int(self.y) - int_radius))

# Note 클래스
class Note:
    def __init__(self, target_time, lane):
        self.target_time = target_time  
        self.lane = lane
        self.x = LANE_X[lane]
        self.y = 0
        self.width = LANE_WIDTH
        self.height = 24 

    def update(self, current_time):
        time_diff = self.target_time - current_time
        self.y = JUDGE_LINE_Y - (time_diff * NOTE_SPEED)

    def draw(self, surface):
        note_rect = pygame.Rect(self.x + 4, self.y - self.height//2, self.width - 8, self.height)
        draw_graded_rounded_rect(surface, note_rect, COLOR_NOTE_BODY, COLOR_NOTE_HIGHLIGHT, corner_radius=6)
        pygame.draw.rect(surface, TEXT_WHITE, note_rect, width=1, border_radius=6)

# NoteQueueManager 클래스
class NoteQueueManager:
    def __init__(self):
        self.noteQueue = deque()  
        self.comboCount = 0
        self.playerScore = 0
        self.playerLife = 100
        
        self.last_judgement = ""
        self.judge_text_color = TEXT_WHITE
        self.judge_timer = 0
        self.particles = []

    def spawnNote(self, newNote):
        self.noteQueue.append(newNote)

    def judgeInput(self, inputKey, current_time):
        if inputKey not in LANE_KEYS:
            return
        
        target_lane = LANE_KEYS.index(inputKey)
        target_note = None
        for note in self.noteQueue:
            if note.lane == target_lane:
                target_note = note
                break
        
        if target_note:
            time_error = abs(current_time - target_note.target_time)
            
            if time_error <= 45:      
                self.playerScore += 1000
                self.comboCount += 1
                self.last_judgement = "PERFECT"
                self.judge_text_color = COLOR_PERFECT
                self.create_particles(target_note.x + LANE_WIDTH//2, JUDGE_LINE_Y, COLOR_PERFECT)
                self.noteQueue.remove(target_note)
            elif time_error <= 95:    
                self.playerScore += 500
                self.comboCount += 1
                self.last_judgement = "GOOD"
                self.judge_text_color = COLOR_GOOD
                self.create_particles(target_note.x + LANE_WIDTH//2, JUDGE_LINE_Y, COLOR_GOOD)
                self.noteQueue.remove(target_note)
            elif time_error <= 160:   
                self.playerLife -= 8
                self.comboCount = 0
                self.last_judgement = "MISS"
                self.judge_text_color = COLOR_MISS
                self.noteQueue.remove(target_note)
            
            self.judge_timer = pygame.time.get_ticks()

    def checkMiss(self, current_time):
        if self.noteQueue:
            front_note = self.noteQueue[0]
            if current_time - front_note.target_time > 160:
                self.noteQueue.popleft()  
                self.playerLife -= 10
                self.comboCount = 0
                self.last_judgement = "MISS"
                self.judge_text_color = COLOR_MISS
                self.judge_timer = pygame.time.get_ticks()

    def create_particles(self, x, y, color):
        for _ in range(15): 
            self.particles.append(Particle(x, y, color))

    def update_particles(self):
        for p in self.particles[:]:
            p.update()
            if p.alpha <= 0:
                self.particles.remove(p)

# 메인 게임 루프 관리 클래스
class RhythmGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("DJMAX Style UI Edition")
        self.fps_clock = pygame.time.Clock()
        
        matched_font_path = None
        for f in FONT_DEF:
            path = pygame.font.match_font(f)
            if path:
                matched_font_path = path
                break

        if matched_font_path:
            self.font_large = pygame.font.Font(matched_font_path, 44)
            self.font_medium = pygame.font.Font(matched_font_path, 26)
            self.font_small = pygame.font.Font(matched_font_path, 16)
            self.font_mini = pygame.font.Font(matched_font_path, 13)
            self.font_button = pygame.font.Font(matched_font_path, 20)
        else:
            self.font_large = pygame.font.SysFont(None, 44, bold=True)
            self.font_medium = pygame.font.SysFont(None, 26, bold=True)
            self.font_small = pygame.font.SysFont(None, 16, bold=False)
            self.font_mini = pygame.font.SysFont(None, 13, bold=False)
            self.font_button = pygame.font.SysFont(None, 20, bold=True)
        
        self.state = "MENU"
        
        # --- 11곡의 데이터 베이스 구성 ---
        self.tracks = [
            {"title": "POP/STARS", "composer": "K/DA", "bpm": 170, "difficulty": "MAXIMUM", "level": 12, "notes": 140, "intervals": [250, 350]},
            {"title": "Out Law", "composer": "Croove", "bpm": 130, "difficulty": "HARD", "level": 8, "notes": 80, "intervals": [400, 600]},
            {"title": "Over Your Dream", "composer": "xxdbxx", "bpm": 140, "difficulty": "NORMAL", "level": 5, "notes": 70, "intervals": [500, 700]},
            {"title": "Para-Q", "composer": "Forte Escape", "bpm": 160, "difficulty": "HARD", "level": 9, "notes": 100, "intervals": [300, 500]},
            {"title": "Phantom Of Sky", "composer": "M2U", "bpm": 155, "difficulty": "MAXIMUM", "level": 11, "notes": 120, "intervals": [280, 400]},
            {"title": "plastic method", "composer": "zts", "bpm": 125, "difficulty": "NORMAL", "level": 6, "notes": 75, "intervals": [450, 650]},
            {"title": "quixotic", "composer": "Bermei.inazawa", "bpm": 135, "difficulty": "HARD", "level": 7, "notes": 90, "intervals": [350, 550]},
            {"title": "Ray of Illuminati", "composer": "ESTi", "bpm": 150, "difficulty": "MAXIMUM", "level": 13, "notes": 150, "intervals": [200, 350]},
            {"title": "RED", "composer": "Croove", "bpm": 142, "difficulty": "HARD", "level": 9, "notes": 110, "intervals": [320, 480]},
            {"title": "Remains Of Doom", "composer": "NieN", "bpm": 165, "difficulty": "MAXIMUM", "level": 14, "notes": 160, "intervals": [220, 300]},
            {"title": "REVENGE", "composer": "ND Lee", "bpm": 140, "difficulty": "NORMAL", "level": 6, "notes": 80, "intervals": [400, 600]}
        ]
        self.selected_track_idx = 0
        self.bg_timer = 0
        
        self.replay_button = None
        self.menu_button = None

    def init_game(self):
        self.manager = NoteQueueManager()
        self.song_data = []
        
        current_track = self.tracks[self.selected_track_idx]
        start_delay = 2000 
        for _ in range(current_track["notes"]):
            start_delay += random.choice(current_track["intervals"])
            lane = random.randint(0, 3)
            self.song_data.append((start_delay, lane))
        
        self.start_time = pygame.time.get_ticks()
        self.active_keys = [False, False, False, False]
        
        self.replay_button = Button(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 70, 140, 50, "다시 하기", PANEL_LIGHT, PANEL_DARK)
        self.menu_button = Button(SCREEN_WIDTH//2 + 10, SCREEN_HEIGHT//2 + 70, 140, 50, "곡 선택", PANEL_LIGHT, PANEL_DARK)

    def run(self):
        running = True
        game_over = False

        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.bg_timer += 1 
            
            if self.state == "MENU":
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if event.type == pygame.KEYDOWN:
                        if event.key in [pygame.K_DOWN, pygame.K_d]:  
                            self.selected_track_idx = (self.selected_track_idx + 1) % len(self.tracks)
                        elif event.key in [pygame.K_UP, pygame.K_k]:  
                            self.selected_track_idx = (self.selected_track_idx - 1) % len(self.tracks)
                        elif event.key == pygame.K_SPACE:  
                            self.state = "GAME"
                            game_over = False
                            self.init_game()
                
                self.draw_menu()

            elif self.state == "GAME":
                current_time = pygame.time.get_ticks() - self.start_time

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    
                    if not game_over and event.type == pygame.KEYDOWN:
                        if event.key in LANE_KEYS:
                            idx = LANE_KEYS.index(event.key)
                            self.active_keys[idx] = True
                            self.manager.judgeInput(event.key, current_time)
                    
                    if event.type == pygame.KEYUP:
                        if event.key in LANE_KEYS:
                            idx = LANE_KEYS.index(event.key)
                            self.active_keys[idx] = False
                    
                    if game_over and event.type == pygame.MOUSEBUTTONDOWN:
                        if self.replay_button.is_clicked(mouse_pos):
                            game_over = False
                            self.init_game()
                        elif self.menu_button.is_clicked(mouse_pos):
                            game_over = False
                            self.state = "MENU"  

                if not game_over:
                    while self.song_data and self.song_data[0][0] - current_time < 1200:
                        note_time, lane = self.song_data.pop(0)
                        self.manager.spawnNote(Note(note_time, lane))

                    for note in list(self.manager.noteQueue):
                        note.update(current_time)
                    
                    self.manager.checkMiss(current_time)
                    self.manager.update_particles()

                    if self.manager.playerLife <= 0 or (not self.song_data and not self.manager.noteQueue):
                        game_over = True

                self.draw_game_elements(current_time, game_over, mouse_pos)

            pygame.display.flip()
            self.fps_clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

    def draw_menu(self):
        self.screen.fill(BG_DARK)
        pygame.draw.line(self.screen, PANEL_DARK, (260, 0), (260, SCREEN_HEIGHT), 2)
        
        # --- LEFT PANEL ---
        current_track = self.tracks[self.selected_track_idx]
        mode_txt = self.font_medium.render("4 BUTTON", True, COLOR_GOLD)
        self.screen.blit(mode_txt, (25, 25))
        tunes_txt = self.font_mini.render("TUNES", True, TEXT_MUTED)
        self.screen.blit(tunes_txt, (25 + mode_txt.get_width() + 5, 35))
        
        jacket_rect = pygame.Rect(25, 80, 210, 160)
        pygame.draw.rect(self.screen, PANEL_DARK, jacket_rect, border_radius=6)
        pygame.draw.rect(self.screen, PANEL_LIGHT, jacket_rect, width=1, border_radius=6)
        pygame.draw.line(self.screen, COLOR_GOLD, (25, 200), (235, 220), 2)
        
        title_surf = self.font_medium.render(current_track["title"], True, TEXT_WHITE)
        self.screen.blit(title_surf, (25, 260))
        
        composer_surf = self.font_small.render(current_track["composer"], True, TEXT_MUTED)
        self.screen.blit(composer_surf, (25, 295))
        
        bpm_surf = self.font_small.render(f"BPM {current_track['bpm']}", True, COLOR_GOLD)
        self.screen.blit(bpm_surf, (25, 320))
        
        diff_labels = ["NORMAL", "HARD", "MAXIMUM"]
        for idx, diff in enumerate(diff_labels):
            diff_rect = pygame.Rect(25 + idx*72, 360, 66, 26)
            if current_track["difficulty"] == diff:
                pygame.draw.rect(self.screen, COLOR_GOLD, diff_rect, border_radius=4)
                diff_text = self.font_mini.render(diff[:2], True, BG_DARK)
            else:
                pygame.draw.rect(self.screen, PANEL_DARK, diff_rect, border_radius=4)
                pygame.draw.rect(self.screen, PANEL_LIGHT, diff_rect, width=1, border_radius=4)
                diff_text = self.font_mini.render(diff[:2], True, TEXT_MUTED)
            self.screen.blit(diff_text, diff_text.get_rect(center=diff_rect.center))
            
        stats_y = 415
        labels = [("Record", "278,691"), ("Rate", "91.61%"), ("Combo", f"MAX {current_track['notes']}")]
        for label, val in labels:
            lbl_surf = self.font_mini.render(label, True, TEXT_MUTED)
            val_surf = self.font_small.render(val, True, TEXT_WHITE)
            self.screen.blit(lbl_surf, (25, stats_y))
            self.screen.blit(val_surf, (130, stats_y - 2))
            stats_y += 28
            
        # --- RIGHT PANEL ---
        categories = ["ALL TRACK", "PLAYABLE", "RESPECT", "FAVORITE"]
        cat_x = 280
        for cat in categories:
            cat_surf = self.font_mini.render(cat, True, COLOR_GOLD if cat == "ALL TRACK" else TEXT_MUTED)
            self.screen.blit(cat_surf, (cat_x, 28))
            cat_x += cat_surf.get_width() + 25
            
        start_y = 75
        item_h = 48
        gap = 6
        max_visible = 9
        
        start_idx = max(0, min(self.selected_track_idx - max_visible//2, len(self.tracks) - max_visible))
        end_idx = min(start_idx + max_visible, len(self.tracks))
        
        for idx in range(start_idx, end_idx):
            track = self.tracks[idx]
            row_y = start_y + (idx - start_idx) * (item_h + gap)
            row_rect = pygame.Rect(280, row_y, 495, item_h)
            
            if idx == self.selected_track_idx:
                pygame.draw.rect(self.screen, COLOR_SELECTED, row_rect, border_radius=4)
                t_color = TEXT_WHITE
                c_color = TEXT_WHITE
            else:
                pygame.draw.rect(self.screen, PANEL_DARK, row_rect, border_radius=4)
                pygame.draw.rect(self.screen, PANEL_LIGHT, row_rect, width=1, border_radius=4)
                t_color = TEXT_WHITE
                c_color = TEXT_MUTED
                
            thumb_rect = pygame.Rect(290, row_y + 8, 32, 32)
            pygame.draw.rect(self.screen, BG_DARK, thumb_rect, border_radius=2)
            
            r_title = self.font_small.render(track["title"], True, t_color)
            self.screen.blit(r_title, (335, row_y + 6))
            
            r_comp = self.font_mini.render(track["composer"], True, c_color)
            self.screen.blit(r_comp, (335, row_y + 26))
            
            for i in range(4):
                cross_color = TEXT_WHITE if idx == self.selected_track_idx else PANEL_LIGHT
                pygame.draw.line(self.screen, cross_color, (700 + i*18, row_y + 20), (708 + i*18, row_y + 28), 2)
                pygame.draw.line(self.screen, cross_color, (708 + i*18, row_y + 20), (700 + i*18, row_y + 28), 2)

        guide_y = SCREEN_HEIGHT - 35
        pygame.draw.rect(self.screen, PANEL_DARK, (280, guide_y - 5, 495, 30), border_radius=4)
        guide_txt = self.font_mini.render("▲▼ / D K : 이동    |    SPACE : 연주 시작", True, TEXT_MUTED)
        self.screen.blit(guide_txt, (300, guide_y))

    def draw_game_elements(self, current_time, game_over, mouse_pos):
        self.screen.fill(BG_DARK)
        
        # 기어 영역 배경 (4개 라인을 완벽히 덮는 가로 320px 블록 배치)
        pygame.draw.rect(self.screen, PANEL_DARK, (GEAR_START_X, 0, GEAR_WIDTH, SCREEN_HEIGHT))
        
        # 각 라인 내부 요소 렌더링
        for i in range(4):
            x = LANE_X[i]
            
            # [수정] 키 입력 상태일 때 해당 라인 전체가 반투명 유백색으로 빛나는 효과 (투명도 상승)
            if self.active_keys[i]:
                active_surf = pygame.Surface((LANE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                active_surf.fill((255, 255, 255, 30)) 
                self.screen.blit(active_surf, (x, 0))
            
            # [수정] 각 레인의 좌측 구분선 그리기 (이로써 K키의 구분선까지 완벽 구현)
            pygame.draw.line(self.screen, PANEL_LIGHT, (x, 0), (x, SCREEN_HEIGHT), 1)
            
            # 하단 키 매핑 텍스트 렌더링 ([수정] 원형 UI 제거, 텍스트만 깔끔하게 노출)
            key_name = pygame.key.name(LANE_KEYS[i]).upper()
            key_text = self.font_button.render(key_name, True, COLOR_GOLD if self.active_keys[i] else TEXT_MUTED)
            key_rect = key_text.get_rect(center=(x + LANE_WIDTH//2, JUDGE_LINE_Y + 50))
            self.screen.blit(key_text, key_rect)

        # [수정] 기어의 가장 우측 마감선 (K키 우측 테두리) 명시적 드로우
        pygame.draw.line(self.screen, PANEL_LIGHT, (GEAR_START_X + GEAR_WIDTH, 0), (GEAR_START_X + GEAR_WIDTH, SCREEN_HEIGHT), 1)

        # 판정선 디자인 수정 (기어 가로폭에 일치화)
        pygame.draw.line(self.screen, TEXT_WHITE, (GEAR_START_X, JUDGE_LINE_Y), (GEAR_START_X + GEAR_WIDTH, JUDGE_LINE_Y), 3)

        # 게임 오브젝트 드로우
        for note in self.manager.noteQueue:
            note.draw(self.screen)

        for p in self.manager.particles:
            p.draw(self.screen)

        # 스코어 및 콤보 UI
        score_txt = self.font_medium.render(f"{self.manager.playerScore:06d}", True, TEXT_WHITE)
        self.screen.blit(score_txt, (30, 25))
        
        hp_title = self.font_mini.render(f"HP {int(self.manager.playerLife)}%", True, TEXT_MUTED)
        self.screen.blit(hp_title, (30, 65))
        pygame.draw.rect(self.screen, PANEL_DARK, (30, 85, 140, 10), border_radius=2)
        if self.manager.playerLife > 0:
            life_w = int(140 * (self.manager.playerLife / 100))
            pygame.draw.rect(self.screen, COLOR_GOLD, (30, 85, life_w, 10), border_radius=2)

        if pygame.time.get_ticks() - self.manager.judge_timer < 500:
            judge_txt = self.font_medium.render(self.manager.last_judgement, True, self.manager.judge_text_color)
            judge_x = 400 - judge_txt.get_width() // 2
            self.screen.blit(judge_txt, (judge_x, SCREEN_HEIGHT // 2 - 60))
            
            if self.manager.comboCount > 0:
                combo_surf = self.font_large.render(f"{self.manager.comboCount}", True, TEXT_WHITE)
                combo_lbl = self.font_mini.render("COMBO", True, COLOR_GOLD)
                
                self.screen.blit(combo_surf, (400 - combo_surf.get_width()//2, SCREEN_HEIGHT // 2 - 25))
                self.screen.blit(combo_lbl, (400 - combo_lbl.get_width()//2, SCREEN_HEIGHT // 2 + 20))

        # 게임 오버 모달
        if game_over:
            self.replay_button.update(mouse_pos)
            self.menu_button.update(mouse_pos)
            
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 10, 14, 220)) 
            self.screen.blit(overlay, (0, 0))
            
            result_box = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 140, 400, 280)
            pygame.draw.rect(self.screen, PANEL_DARK, result_box, border_radius=8)
            pygame.draw.rect(self.screen, PANEL_LIGHT, result_box, width=1, border_radius=8)
            
            if self.manager.playerLife <= 0:
                res_title = self.font_medium.render("GAME OVER", True, COLOR_MISS)
            else:
                res_title = self.font_medium.render("STAGE CLEAR", True, COLOR_GOLD)
                
            res_score = self.font_large.render(f"{self.manager.playerScore:06d}", True, TEXT_WHITE)
            
            self.screen.blit(res_title, (SCREEN_WIDTH//2 - res_title.get_width()//2, SCREEN_HEIGHT//2 - 100))
            self.screen.blit(res_score, (SCREEN_WIDTH//2 - res_score.get_width()//2, SCREEN_HEIGHT//2 - 30))
            
            self.replay_button.draw(self.screen, self.font_button)
            self.menu_button.draw(self.screen, self.font_button)

if __name__ == "__main__":
    game = RhythmGame()
    game.run()