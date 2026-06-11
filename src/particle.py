import random
import pygame


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
