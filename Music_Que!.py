import pygame
import sys
import random
from collections import deque

# 1. 게임 기본 설정 및 상수
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 색상 정의 (네온 스타일 스타일링)
BLACK = (15, 15, 25)
WHITE = (255, 255, 255)
GRAY = (40, 40, 50)
LINE_COLOR = (60, 60, 80)
BG_GRADIENT = (25, 25, 40)

# 판정별 색상
COLOR_PERFECT = (0, 255, 255)  # 시안
COLOR_GOOD = (50, 255, 50)    # 그린
COLOR_MISS = (255, 50, 50)    # 레드
COLOR_NOTE = (255, 0, 128)    # 핫핑크
GREEN = (50, 255, 50)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)

# 폰트 통일 설정 (OS별 호환성 보장 리스트)
FONT_DEF = ["malgun gothic", "applesdgothicneo", "notosanskorean", "arial"]

# 리듬게임 핵심 설정
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_X = [250, 340, 430, 520]
LANE_WIDTH = 80
JUDGE_LINE_Y = 500
NOTE_SPEED = 0.5  # 밀리초(ms)당 이동할 픽셀 수

# 2. 버튼 클래스
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
    
    def draw(self, surface, font):
        current_color = self.hover_color if self.is_hovered else self.color
        # 버튼 배경 (둥근 모서리 및 네온 테두리)
        pygame.draw.rect(surface, current_color, self.rect, border_radius=12)
        pygame.draw.rect(surface, (150, 200, 255), self.rect, 2, border_radius=12)
        
        # 버튼 텍스트
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

# 3. 이펙트 처리를 위한 파티클 클래스
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.radius = random.randint(4, 7)
        self.color = color
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 10  # 점차 투명해짐
        if self.radius > 0.5:
            self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0:
            p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, self.alpha), (self.radius, self.radius), int(self.radius))
            surface.blit(p_surf, (self.x - self.radius, self.y - self.radius))

# 4. 기획서 기반: Note 클래스
class Note:
    def __init__(self, target_time, lane):
        self.target_time = target_time  # 판정선에 도달해야 하는 절대 시간 (ms)
        self.lane = lane
        self.x = LANE_X[lane]
        self.y = 0
        self.width = LANE_WIDTH
        self.height = 20

    def update(self, current_time):
        time_diff = self.target_time - current_time
        self.y = JUDGE_LINE_Y - (time_diff * NOTE_SPEED)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_NOTE, (self.x, self.y, self.width, self.height), border_radius=5)
        pygame.draw.rect(surface, WHITE, (self.x + 4, self.y + 4, self.width - 8, self.height - 8), border_radius=3)

# 5. 기획서 기반: NoteQueueManager 클래스
class NoteQueueManager:
    def __init__(self):
        self.noteQueue = deque()  # 선입선출을 위한 큐 구조
        self.comboCount = 0
        self.playerScore = 0
        self.playerLife = 100
        
        # UI 연출용 속성
        self.last_judgement = ""
        self.judge_text_color = WHITE
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
            
            if time_error <= 40:      # Perfect
                self.playerScore += 1000
                self.comboCount += 1
                self.last_judgement = "PERFECT"
                self.judge_text_color = COLOR_PERFECT
                self.create_particles(target_note.x + LANE_WIDTH//2, JUDGE_LINE_Y, COLOR_PERFECT)
                self.noteQueue.remove(target_note)
            elif time_error <= 90:    # Good
                self.playerScore += 500
                self.comboCount += 1
                self.last_judgement = "GOOD"
                self.judge_text_color = COLOR_GOOD
                self.create_particles(target_note.x + LANE_WIDTH//2, JUDGE_LINE_Y, COLOR_GOOD)
                self.noteQueue.remove(target_note)
            elif time_error <= 150:   # Bad / Miss
                self.playerLife -= 8
                self.comboCount = 0
                self.last_judgement = "MISS"
                self.judge_text_color = COLOR_MISS
                self.noteQueue.remove(target_note)
            
            self.judge_timer = pygame.time.get_ticks()

    def checkMiss(self, current_time):
        if self.noteQueue:
            front_note = self.noteQueue[0]
            if current_time - front_note.target_time > 150:
                self.noteQueue.popleft()  # Dequeue
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

# 6. 메인 게임 루프 및 관리 클래스
class RhythmGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Queue the Music!")
        self.fps_clock = pygame.time.Clock()
        
        # 폰트 에셋 통합 기획 처리 (FONT_DEF 상수 사용)
        self.font_large = pygame.font.SysFont(FONT_DEF, 46, bold=True)
        self.font_medium = pygame.font.SysFont(FONT_DEF, 30, bold=True)
        self.font_small = pygame.font.SysFont(FONT_DEF, 18, bold=False)
        self.font_button = pygame.font.SysFont(FONT_DEF, 22, bold=True)
        
        self.replay_button = None
        self.init_game()
    
    def init_game(self):
        self.manager = NoteQueueManager()
        self.song_data = []
        start_delay = 2000  
        for i in range(100):
            start_delay += random.choice([400, 600, 800])
            lane = random.randint(0, 3)
            self.song_data.append((start_delay, lane))
        
        self.start_time = pygame.time.get_ticks()
        self.active_keys = [False, False, False, False]
        # 리플레이 버튼 객체 설정 보완 (중앙 하단 배치 최적화)
        self.replay_button = Button(SCREEN_WIDTH//2 - 90, SCREEN_HEIGHT//2 + 55, 180, 45, "다시 플레이", (80, 110, 230), (110, 140, 255))

    def run(self):
        running = True
        game_over = False

        while running:
            current_time = pygame.time.get_ticks() - self.start_time
            mouse_pos = pygame.mouse.get_pos()

            # 1. 이벤트 핸들러
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
                        current_time = 0

            if not game_over:
                # 2. 실시간 노트 서브 스폰 로직
                while self.song_data and self.song_data[0][0] - current_time < 1200:
                    note_time, lane = self.song_data.pop(0)
                    self.manager.spawnNote(Note(note_time, lane))

                # 3. 데이터 갱신 및 상태 관리
                for note in list(self.manager.noteQueue):
                    note.update(current_time)
                
                self.manager.checkMiss(current_time)
                self.manager.update_particles()

                if self.manager.playerLife <= 0 or (not self.song_data and not self.manager.noteQueue):
                    game_over = True

            # 4. 백그라운드 및 메인 뷰 렌더링
            for y in range(SCREEN_HEIGHT):
                ratio = y / SCREEN_HEIGHT
                color = (
                    int(15 + (35 - 15) * ratio),
                    int(15 + (35 - 15) * ratio),
                    int(25 + (60 - 25) * ratio)
                )
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
            
            # 인게임 레인 가이드 및 키 피드백 연출
            for i in range(4):
                x = LANE_X[i]
                if self.active_keys[i]:
                    active_surf = pygame.Surface((LANE_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                    active_surf.fill((100, 200, 255, 35))
                    self.screen.blit(active_surf, (x, 0))
                
                pygame.draw.rect(self.screen, LINE_COLOR, (x, 0, LANE_WIDTH, SCREEN_HEIGHT), 2)
                key_text = self.font_small.render(pygame.key.name(LANE_KEYS[i]).upper(), True, GRAY if not self.active_keys[i] else (100, 255, 255))
                key_rect = key_text.get_rect(center=(x + LANE_WIDTH//2, JUDGE_LINE_Y + 55))
                self.screen.blit(key_text, key_rect)

            # 판정 레이어 그리기
            pygame.draw.line(self.screen, (0, 191, 255), (200, JUDGE_LINE_Y), (600, JUDGE_LINE_Y), 4)
            pygame.draw.line(self.screen, (100, 220, 255), (195, JUDGE_LINE_Y - 2), (605, JUDGE_LINE_Y - 2), 1)

            for note in self.manager.noteQueue:
                note.draw(self.screen)

            for p in self.manager.particles:
                p.draw(self.screen)

            # 5. 대시보드 UI 그리기 (점수판 및 HP 바 패널 컴팩트화)
            # 스코어 보드
            score_txt = self.font_medium.render(f"SCORE: {self.manager.playerScore:06d}", True, (100, 255, 200))
            self.screen.blit(score_txt, (25, 20))
            
            # HP 게이지
            life_txt = self.font_small.render(f"HP: {int(self.manager.playerLife)}%", True, WHITE)
            self.screen.blit(life_txt, (25, 62))
            
            pygame.draw.rect(self.screen, (40, 40, 60), (25, 88, 160, 18), border_radius=4)
            life_ratio = self.manager.playerLife / 100
            life_color = (100, 255, 150) if self.manager.playerLife > 40 else ((255, 180, 70) if self.manager.playerLife > 20 else RED)
            if self.manager.playerLife > 0:
                pygame.draw.rect(self.screen, life_color, (27, 90, int(156 * life_ratio), 14), border_radius=3)

            # 인게임 실시간 판정/콤보 이펙트 텍스트 
            if pygame.time.get_ticks() - self.manager.judge_timer < 500:
                judge_txt = self.font_large.render(self.manager.last_judgement, True, self.manager.judge_text_color)
                self.screen.blit(judge_txt, (SCREEN_WIDTH // 2 - judge_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
                
                if self.manager.comboCount > 0:
                    combo_txt = self.font_medium.render(f"{self.manager.comboCount} COMBO", True, WHITE)
                    self.screen.blit(combo_txt, (SCREEN_WIDTH // 2 - combo_txt.get_width() // 2, SCREEN_HEIGHT // 2 - 10))

            # 6. 라운드 종료 스크린 (게임오버 / 클리어 팝업 모달)
            if game_over:
                self.replay_button.update(mouse_pos)
                
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((10, 10, 20, 225))
                self.screen.blit(overlay, (0, 0))
                
                # 결과 안내 팝업 사각 프레임
                result_box = pygame.Surface((500, 300), pygame.SRCALPHA)
                result_box.fill((25, 25, 45, 230))
                pygame.draw.rect(result_box, (100, 150, 255), (0, 0, 500, 300), 2, border_radius=16)
                self.screen.blit(result_box, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 150))
                
                if self.manager.playerLife <= 0:
                    result_title = self.font_large.render("GAME OVER", True, (255, 90, 90))
                    title_sub_text = "아쉽네요! 다시 도전해 보세요."
                else:
                    result_title = self.font_large.render("STAGE CLEAR!", True, (90, 255, 160))
                    title_sub_text = "멋진 연주였습니다! 축하합니다!"
                    
                result_score = self.font_medium.render(f"최종 스코어: {self.manager.playerScore}", True, (210, 230, 255))
                subtitle = self.font_small.render(title_sub_text, True, (180, 180, 200))
                
                # 팝업 컨텐츠 내부 정밀 y축 오프셋 정렬
                self.screen.blit(result_title, (SCREEN_WIDTH//2 - result_title.get_width()//2, SCREEN_HEIGHT//2 - 110))
                self.screen.blit(subtitle, (SCREEN_WIDTH//2 - subtitle.get_width()//2, SCREEN_HEIGHT//2 - 50))
                self.screen.blit(result_score, (SCREEN_WIDTH//2 - result_score.get_width()//2, SCREEN_HEIGHT//2))
                
                self.replay_button.draw(self.screen, self.font_button)

            pygame.display.flip()
            self.fps_clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = RhythmGame()
    game.run()