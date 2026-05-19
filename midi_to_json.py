# midi_to_json.py
import pretty_midi
import json
import os

def convert_midi_to_json(midi_filename, json_filename):
    if not os.path.exists(midi_filename):
        print(f"❌ 에러: {midi_filename} 파일이 존재하지 않습니다.")
        return

    try:
        print(f"📦 '{midi_filename}' 분석 중...")
        midi_data = pretty_midi.PrettyMIDI(midi_filename)
        
        # 템포 추출 정보 아래에 박자표 동적 추출 로직
        tempo_times, tempo_bpms = midi_data.get_tempo_changes()
        if len(tempo_bpms) > 0:
            bpm = int(tempo_bpms[0])
        else:
            bpm = int(midi_data.estimate_bpm())
            
        # 💡 박자표(Time Signature) 변경 내역 검출
        time_sigs = midi_data.time_signature_changes
        if time_sigs:
            # 첫 번째 박자표의 분자(numerator)를 가져옴 (예: 3/4박자 -> 3, 4/4박자 -> 4)
            beats_per_measure = time_sigs[0].numerator
        else:
            beats_per_measure = 4  # 박자 정보가 없는 경우 기본값 4
            
        title = os.path.splitext(os.path.basename(midi_filename))[0]
        
        json_structure = {
            "metadata": {
                "title": title,
                "composer": "Unknown (Converted)",
                "bpm": bpm,
                "beats_per_measure": beats_per_measure  # 📝 JSON 메타데이터에 저장!
            },
            "measures": {}
        }

        all_notes = []
        for instrument in midi_data.instruments:
            if not instrument.is_drum:
                for note in instrument.notes:
                    all_notes.append(note)
        
        all_notes.sort(key=lambda x: x.start)

        note_id_counter = 1
        
        for note in all_notes:
            total_start_beats = note.start * (bpm / 60.0)
            total_end_beats = note.end * (bpm / 60.0)
            
            duration_beats = total_end_beats - total_start_beats
            
            # 동적으로 할당된 beats_per_measure 기준으로 마디 분할 연산 진행
            measure_num = int(total_start_beats // beats_per_measure) + 1
            start_beat_in_measure = total_start_beats % beats_per_measure
            
            note_obj = {
                "id": f"note_{note_id_counter}",
                "start": round(start_beat_in_measure, 3),
                "duration": round(duration_beats, 3),
                "pitch": note.pitch
            }
            
            measure_key = str(measure_num)
            if measure_key not in json_structure["measures"]:
                json_structure["measures"][measure_key] = []
                
            json_structure["measures"][measure_key].append(note_obj)
            note_id_counter += 1

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=2, ensure_ascii=False)
            
        print(f"✨ 변환 완료! 저장된 파일: {json_filename}")
        print(f"📊 박자 설정: {beats_per_measure}박자 기반 마디 생성 완료")

    except Exception as e:
        print(f"❌ 변환 중 에러 발생: {e}")


'''
if __name__ == "__main__":
    # ⚙️ 변환할 파일 경로 설정 (같은 폴더에 다운받은 .mid 파일명을 적으세요)
    input_midi = "Flower_dance.mid" 
    output_json = "Flower_dance.json"
    
    convert_midi_to_json(input_midi, output_json)
'''