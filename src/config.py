import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- DJMAX 감성의 모던 & 차분한 색상 팔레트 ---
BG_DARK = (10, 10, 14)
PANEL_DARK = (20, 20, 26)
PANEL_LIGHT = (45, 45, 55)
TEXT_WHITE = (240, 240, 245)
TEXT_MUTED = (130, 132, 145)
COLOR_GOLD = (215, 165, 55)
COLOR_SELECTED = (235, 85, 45)

# 판정 색상
COLOR_PERFECT = (220, 180, 60)
COLOR_GOOD = (70, 150, 220)
COLOR_MISS = (170, 55, 55)
COLOR_NOTE_BODY = (230, 235, 245)
COLOR_NOTE_HIGHLIGHT = (180, 190, 210)

FONT_DEF = ["malgun gothic", "applesdgothicneo", "notosanskorean", "arial", "sans-serif"]

# --- 리듬게임 핵심 설정 ---
LANE_KEYS = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
LANE_X = [240, 320, 400, 480]
LANE_WIDTH = 80
GEAR_START_X = 240
GEAR_WIDTH = 320
JUDGE_LINE_Y = 500
NOTE_SPEED = 0.5
