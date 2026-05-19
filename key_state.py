import pygame


RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

'''
88건반 피아노의 각 건반을 정수로 인덱싱
건반 인덱스(0~87) <=> MIDI 번호(21~108)
중간 도(C4)=60
'''
white_midi = [
    21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 
    52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 
    83, 84, 86, 88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108
]
black_midi = [
    22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 
    66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106
]
# 설정값 (draw_piano 함수와 동일하게 유지)
white_key_w = 20
black_key_w = 12

def white_midi_cordinate(midi):
    """흰 건반 MIDI 번호를 입력받아 (x, y) 튜플 반환"""
    if midi not in white_midi:
        return None
    # white_midi 리스트에서 해당 midi의 순서(index)를 찾음
    idx = white_midi.index(midi)
    # x = i * white_key_w
    return (idx * white_key_w+10,100) # 키의 정중앙을 맞추기 위해 +10 (white_key_w/2) shift


def black_midi_cordinate(midi):
    """검은 건반 MIDI 번호를 입력받아 (x, y) 튜플 반환"""
    if midi not in black_midi:
        return None
    # 검은 건반은 항상 특정 흰 건반(midi - 1)의 오른쪽에 위치함
    # 예: 22(A#0)은 21(A0)과 23(B0) 사이
    prev_white_midi = midi - 1
    idx = white_midi.index(prev_white_midi)
    # draw_piano의 로직: x = (i + 1) * white_key_w - (black_key_w // 2)
    x = (idx + 1) * white_key_w - (black_key_w // 2)
    return (x+6,70) # 키의 정중앙을 맞추기 위해 +6 (black_key_w/2) shift

# 흑/백 통합(midi -> cordinate)
def midi_cordinate(midi):
    if midi in white_midi:
        return white_midi_cordinate(midi)
    elif midi in black_midi:
        return black_midi_cordinate(midi)

# 흰 건반을 누를 때
def press_white_key(screen, midi):
    return pygame.draw.circle(screen, RED, white_midi_cordinate(midi), 5)

# 검은 건반을 누를 때
def press_black_key(screen, midi):
    return pygame.draw.circle(screen, RED, black_midi_cordinate(midi), 5)

# 건반(흑/백 무관)을 누를 때
def press_key(screen, midi):
    if midi in white_midi:
        return press_white_key(screen, midi)
    elif midi in black_midi:
        return press_black_key(screen, midi)

# 흰 건반에서 손을 뗄 때
def release_white_key(screen, midi):
    return pygame.draw.circle(screen, WHITE, white_midi_cordinate(midi), 5)

# 검은 건반에서 손을 뗄 때
def release_black_key(screen, midi):
    return pygame.draw.circle(screen, BLACK, black_midi_cordinate(midi), 5)

# 건반(흑/백 무관)에서 손을 뗄 때
def release_key(screen, midi):
    if midi in white_midi:
        return release_white_key(screen, midi)
    elif midi in black_midi:
        return release_black_key(screen, midi)