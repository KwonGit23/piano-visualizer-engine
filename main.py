# main.py
import pygame
import pygame.midi
import sys
import json
import os
import draw_piano as dp
import key_state as ks
import refine_measure_data as rmd
from midi_to_json import convert_midi_to_json

def build_timeline(measures_data, start_m, end_m, bpm, beats_per_measure):
    combined_events = []
    seconds_per_beat = 60.0 / bpm
    
    valid_keys = [k for k in measures_data.keys() if start_m <= int(k) <= end_m]
    sorted_measure_keys = sorted(valid_keys, key=int)
    
    for m_key in sorted_measure_keys:
        measure_num = int(m_key)
        beat_offset = (measure_num - start_m) * beats_per_measure
        refined_measure = rmd.refine_measure_data(measures_data[m_key])
        
        for t_beat, notes in refined_measure:
            total_beats = t_beat + beat_offset
            total_seconds = total_beats * seconds_per_beat
            combined_events.append((total_seconds, notes))
            
    combined_events.sort(key=lambda x: x[0])
    return combined_events

def user_interface_menu():
    """
    사용자가 코드를 건드리지 않도록 파일 탐색, 속도, 마디 입력을 총괄하는 인터페이스
    """
    print("\n=============================================")
    print("🎬  PIANO MIDI VISUALIZER SYSTEM START")
    print("=============================================")
    
    # 0. 전용 폴더 경로 정의 및 자동 생성 (없으면 새로 만듦)
    MIDI_DIR = "midi_files"
    JSON_DIR = "json_files"
    os.makedirs(MIDI_DIR, exist_ok=True)
    os.makedirs(JSON_DIR, exist_ok=True)
    
    # 1. 지정된 폴더 내 .mid 파일 목록 자동 검색
    mid_files = [f for f in os.listdir(MIDI_DIR) if f.endswith('.mid')]
    
    if not mid_files:
        print(f"❌ 에러: '{MIDI_DIR}' 폴더에 .mid 파일이 하나도 없습니다.")
        print(f"💡 팁: 테스트하고 싶은 .mid 파일을 [{MIDI_DIR}] 폴더 안에 넣어주세요!")
        input("\n엔터를 누르면 종료됩니다...")
        sys.exit()
        
    print(f"\n📂 [{MIDI_DIR}] 폴더에서 발견된 MIDI 파일 목록:")
    for i, filename in enumerate(mid_files, 1):
        print(f"  [{i}] {filename}")
        
    # 2. 곡 선택 입력
    while True:
        try:
            choice = input("\n▶️ 재생할 음악의 번호를 선택하세요: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(mid_files):
                selected_midi = mid_files[idx]
                break
            print("⚠️ 번호가 범위에서 벗어났습니다. 다시 입력해 주세요.")
        except ValueError:
            print("⚠️ 숫자만 입력할 수 있습니다.")

    # 3. 자동 JSON 변환 파이프라인 경로 설정
    song_title = os.path.splitext(selected_midi)[0]
    
    # 입력용 미디 경로와 출력용 JSON 경로를 각각의 폴더로 결합
    selected_midi_path = os.path.join(MIDI_DIR, selected_midi)
    target_json_path = os.path.join(JSON_DIR, f"{song_title}.json")
    
    # 이미 변환된 JSON이 있다면 스킵, 없다면 해당 폴더에 새로 자동 생성
    if not os.path.exists(target_json_path):
        print(f"\n⚙️ 최초 1회 파일 자동 변환 중... ({selected_midi} ➡️ {target_json_path})")
        convert_midi_to_json(selected_midi_path, target_json_path)
        
    # JSON 로드
    with open(target_json_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
        
    measures_data = json_data["measures"]
    metadata = json_data.get("metadata", {})
    bpm = metadata.get("bpm", 120)
    
    # JSON 메타데이터에서 동적으로 박자표 정보 추출 (데이터가 없는 레거시 파일일 경우 기본값 4)
    beats_per_measure = metadata.get("beats_per_measure", 4)
    
    print(f"\n🎵 선택된 곡: {metadata.get('title')} (템포: {bpm} BPM / 박자: {beats_per_measure}박자 계열)")

    # 4. 재생 속도 입력
    speed_input = input("▶️ 재생 속도를 입력하세요 (정속: 1.0, 배속 예: 1.2 / 0.8) [엔터=1.0]: ").strip()
    try:
        speed_factor = float(speed_input) if speed_input else 1.0
    except ValueError:
        print("⚠️ 입력이 올바르지 않아 기본 속도(1.0)로 설정합니다.")
        speed_factor = 1.0

    # 5. 마디 범위 입력
    all_measures = sorted(map(int, measures_data.keys()))
    print(f"📊 이 곡은 총 {all_measures[0]}부터 {all_measures[-1]}마디까지 존재합니다.")
    range_input = input(f"▶️ 재생할 마디 범위를 입력하세요 (예: 1-8) [엔터=전체재생]: ").strip()
    
    try:
        if '-' in range_input:
            start_m, end_m = map(int, range_input.split('-'))
        else:
            start_m, end_m = all_measures[0], all_measures[-1]
    except ValueError:
        print("⚠️ 형식이 올바르지 않아 전체 마디를 재생합니다.")
        start_m, end_m = all_measures[0], all_measures[-1]

    return measures_data, bpm, metadata, speed_factor, start_m, end_m, beats_per_measure

def main():
    # 통합 유저 인터페이스 메뉴 호출 및 beats_per_measure 변수 추가 수령
    measures_data, bpm, metadata, SPEED_FACTOR, start_m, end_m, beats_per_measure = user_interface_menu()

    midi_out = None
    try:
        print(f"\n🚀 비주얼라이저 가동! (속도: {SPEED_FACTOR}배속 / 구간: {start_m}~{end_m}마디)")

        # Pygame 및 그래픽 초기화
        pygame.init()
        screen = pygame.display.set_mode((1080, 400)) 
        pygame.display.set_caption(f"{metadata.get('title')} Visualizer")
        clock = pygame.time.Clock()
        
        # MIDI 시스템 초기화
        pygame.midi.init()
        port = pygame.midi.get_default_output_id()
        if port != -1:
            midi_out = pygame.midi.Output(port)
            midi_out.set_instrument(0) 
        
        # 타임라인 빌드 시 동적 박자 정보(beats_per_measure) 함께 전달
        note_events = build_timeline(measures_data, start_m, end_m, bpm, beats_per_measure)
        event_index = 0
        active_notes = set()
        start_time = pygame.time.get_ticks()

        running = True
        while running:
            current_time = ((pygame.time.get_ticks() - start_time) / 1000.0) * SPEED_FACTOR
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            while event_index < len(note_events) and current_time >= note_events[event_index][0]:
                target_time, notes = note_events[event_index]
                for note in notes:
                    if note > 0:
                        active_notes.add(note)
                        if midi_out:
                            midi_out.note_on(note, 100)
                    else:
                        active_notes.discard(abs(note))
                        if midi_out:
                            midi_out.note_off(abs(note), 0)
                event_index += 1

            if event_index >= len(note_events) and not active_notes:
                print("✨ 연주가 완료되었습니다.")
                running = False

            screen.fill((200, 200, 200)) 
            dp.draw_piano(screen)        
            
            for note in active_notes:
                ks.press_key(screen, note)

            pygame.display.flip()
            clock.tick(60)

    except Exception as e:
        print(f"❌ 실행 중 에러 발생: {e}")
    finally:
        if midi_out:
            del midi_out
        pygame.midi.quit()
        pygame.quit()

if __name__ == '__main__':
    main()