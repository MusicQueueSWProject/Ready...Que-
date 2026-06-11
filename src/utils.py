import pygame


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
