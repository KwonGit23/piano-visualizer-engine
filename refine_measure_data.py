#refine_measure_data.py
def refine_measure_data(each_measure: list):
    d = dict()
    for di in each_measure:
        start_time = di["start"]
        end_time = di["start"] + di["duration"]
        pitch = di["pitch"]

        # 1. 음이 시작되는 지점 처리
        if start_time not in d:
            d[start_time] = [pitch]  # list(pitch) 대신 [pitch] 사용
        else:
            d[start_time].append(pitch)

        # 2. 음이 끝나는 지점 처리 (- 붙이기)
        if end_time not in d:
            d[end_time] = [-pitch]   # list(-pitch) 대신 [-pitch] 사용
        else:
            d[end_time].append(-pitch)
            
    return sorted(d.items())

'''
data = {
    "measures": {
        "4": [
        { "id": "bass_4_1", "start": 0.0, "duration": 1.0, "pitch": 38 },
        { "id": "bass_4_2", "start": 1.0, "duration": 1.0, "pitch": 45 },
        { "id": "bass_4_3", "start": 2.0, "duration": 1.0, "pitch": 50 },
        { "id": "bass_4_4", "start": 3.0, "duration": 1.0, "pitch": 54 },
        { "id": "treble_4_1", "start": 3.5, "duration": 0.25, "pitch": 69 },
        { "id": "treble_4_2", "start": 3.75, "duration": 0.125, "pitch": 71 },
        { "id": "treble_4_3", "start": 3.875, "duration": 0.125, "pitch": 73 }
        ]
    }
}
print(refine_measure_data(data["measures"]["4"]
>> [(0.0, [38]), (1.0, [-38, 45]), ...]
'''