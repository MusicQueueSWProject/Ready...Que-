from collections import deque
import pygame
from src.config import LANE_KEYS, LANE_WIDTH, JUDGE_LINE_Y
from src.config import COLOR_PERFECT, COLOR_GOOD, COLOR_MISS, TEXT_WHITE
from src.particle import Particle


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
                self.create_particles(target_note.x + LANE_WIDTH // 2, JUDGE_LINE_Y, COLOR_PERFECT)
                self.noteQueue.remove(target_note)
            elif time_error <= 95:
                self.playerScore += 500
                self.comboCount += 1
                self.last_judgement = "GOOD"
                self.judge_text_color = COLOR_GOOD
                self.create_particles(target_note.x + LANE_WIDTH // 2, JUDGE_LINE_Y, COLOR_GOOD)
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
