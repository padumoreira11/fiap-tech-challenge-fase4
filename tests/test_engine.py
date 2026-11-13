import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import vital_alerts, prescription_alerts, text_alerts, simulated_observation, audio_features, compare_audio_features, movement_exceeds
from evaluation import word_error_rate
import pytest

def test_vitals():
    assert len(vital_alerts([{'timestamp':'t','heart_rate':'125','spo2':'88','systolic':'120'}])) == 2

def test_dose_and_units():
    rows=[{'timestamp':'1','medication':'A','dose':'10','unit':'mg'}, {'timestamp':'2','medication':'A','dose':'20','unit':'mg'}, {'timestamp':'3','medication':'A','dose':'1','unit':'g'}]
    assert len(prescription_alerts(rows)) == 2
    assert 'unidade mudou' in prescription_alerts(rows)[1]['message']

def test_text():
    assert text_alerts('Paciente relata falta de ar')[0]['source'] == 'texto'

def test_invalid_measurement():
    with pytest.raises(ValueError):
        vital_alerts([{'timestamp':'t','heart_rate':'nan','spo2':'98','systolic':'120'}])

def test_invalid_dose():
    with pytest.raises(ValueError):
        prescription_alerts([{'timestamp':'t','medication':'A','dose':'-1','unit':'mg'}])

def test_simulated_stream():
    assert not vital_alerts([simulated_observation(0)])
    assert len(vital_alerts([simulated_observation(2)])) == 2

def test_audio_pause_and_comparison(tmp_path):
    import wave
    import numpy as np
    rate=16000
    signal=np.concatenate([np.full(rate//2, 4000, dtype='<i2'), np.zeros(rate//2, dtype='<i2'), np.full(rate//2, 4000, dtype='<i2')])
    path=tmp_path/'test.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(signal.tobytes())
    result=audio_features(str(path))
    assert result['pause_count_300ms']==1
    assert result['pause_durations_seconds']==[0.5]
    assert compare_audio_features(result,result)['rms_ratio']==1.0

def test_word_error_rate():
    assert word_error_rate('Olá, mundo!', 'olá mundo')['wer'] == 0
    assert word_error_rate('um dois três', 'um quatro três')['wer'] == pytest.approx(1/3)
    assert word_error_rate('um dois', 'um dois três')['errors'] == 1
    with pytest.raises(ValueError): word_error_rate('', 'texto')

def test_movement_threshold_strict_and_validated():
    assert not movement_exceeds(0.06, 0.06)
    assert movement_exceeds(0.061, 0.06)
    with pytest.raises(ValueError): movement_exceeds(float('nan'), 0.1)
