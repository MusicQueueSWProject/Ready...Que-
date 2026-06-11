import pygame
from src.config import LANE_X, LANE_WIDTH, JUDGE_LINE_Y, NOTE_SPEED
from src.config import COLOR_NOTE_BODY, COLOR_NOTE_HIGHLIGHT, TEXT_WHITE
from src.utils import draw_graded_rounded_rect


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
        note_rect = pygame.Rect(self.x + 4, self.y - self.height // 2, self.width - 8, self.height)
        draw_graded_rounded_rect(surface, note_rect, COLOR_NOTE_BODY, COLOR_NOTE_HIGHLIGHT, corner_radius=6)
        pygame.draw.rect(surface, TEXT_WHITE, note_rect, width=1, border_radius=6)
