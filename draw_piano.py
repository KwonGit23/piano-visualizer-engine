# draw_piano.py
import pygame

def draw_piano(screen):
    # 1. 기본 설정
    white_key_w = 20
    white_key_h = 120
    black_key_w = 12
    black_key_h = 80
    num_white_keys = 52

    # 2. 흰 건반 그리기
    for i in range(num_white_keys):
        x = i * white_key_w
        # 흰색 면 채우기
        pygame.draw.rect(screen, (255, 255, 255), (x, 0, white_key_w, white_key_h))
        # 검은색 테두리 그리기 (마지막 인자 1이 선 두께를 의미)
        pygame.draw.rect(screen, (0, 0, 0), (x, 0, white_key_w, white_key_h), 1)

    # 3. 검은 건반 그리기
    black_key_pattern = [True, False, True, True, False, True, True]
    
    for i in range(num_white_keys - 1):
        pattern_idx = i % 7
        if black_key_pattern[pattern_idx]:
            x = (i + 1) * white_key_w - (black_key_w // 2)
            pygame.draw.rect(screen, (0, 0, 0), (x, 0, black_key_w, black_key_h))
