import pygame
from src.config import COLOR_GOLD, PANEL_LIGHT, TEXT_WHITE
from src.utils import draw_graded_rounded_rect


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
