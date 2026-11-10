"""Protótipo educacional: alertas demonstrativos, não decisões clínicas."""
import csv
import re
import math


def vital_alerts(rows):
    alerts = []
    limits = {'heart_rate': (50, 120, 'bpm'), 'spo2': (90, 100, '%'),
              'systolic': (90, 180, 'mmHg')}
    for row in rows:
        for key, (low, high, unit) in limits.items():
            value = float(row[key])
            if not math.isfinite(value):
                raise ValueError(f'{key} precisa ser um número finito')
            if not low <= value <= high:
                alerts.append({'source': 'sinais vitais', 'time': row['timestamp'],
                    'message': f'{key}: {value:g} {unit} fora da faixa demonstrativa [{low}, {high}]'})
    return alerts


def prescription_alerts(rows):
    alerts, previous = [], {}
    for row in rows:
        key = row['medication'].strip().lower()
        dose = float(row['dose'])
        if not math.isfinite(dose) or dose < 0:
            raise ValueError('A dose precisa ser um número finito não negativo')
        if row['unit'] and key in previous:
            old, unit = previous[key]
            if unit != row['unit']:
                alerts.append({'source': 'prescrição', 'time': row['timestamp'], 'message': f'{key}: unidade mudou de {unit} para {row["unit"]}; comparação de dose indisponível'})
            elif old > 0 and abs(dose-old)/old >= .5:
                alerts.append({'source': 'prescrição', 'time': row['timestamp'], 'message': f'{key}: dose mudou de {old:g} para {dose:g} {unit} (limiar demonstrativo ≥50%)'})
        previous[key] = (dose, row['unit'])
    return alerts


def parse_csv(file):
    import io
    return list(csv.DictReader(io.StringIO(file.getvalue().decode('utf-8-sig'))))


def simulated_observation(index):
    """Deterministic synthetic stream for the demonstration, not a patient feed."""
    samples = [(76, 98, 120), (80, 97, 122), (125, 89, 124), (82, 97, 121)]
    hr, spo2, pressure = samples[min(index, len(samples) - 1)]
    return {'timestamp': f'amostra {index + 1}', 'heart_rate': hr,
            'spo2': spo2, 'systolic': pressure}


def text_alerts(text):
    terms = ['falta de ar', 'dor no peito', 'desmaio', 'dificuldade para respirar']
    return [{'source': 'texto', 'time': '', 'message': f'Termo encontrado: {term}. Verificar contexto e negação.'}
            for term in terms if re.search(re.escape(term), text, re.I)]


def azure_text(text, endpoint, key):
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    client = TextAnalyticsClient(endpoint, AzureKeyCredential(key))
    sentiment = client.analyze_sentiment([text], language='pt')[0]
    phrases = client.extract_key_phrases([text], language='pt')[0]
    if sentiment.is_error or phrases.is_error:
        raise RuntimeError('Azure Language não conseguiu processar o texto.')
    return {'sentiment': sentiment.sentiment, 'key_phrases': phrases.key_phrases}


def azure_speech(path, region, key):
    import azure.cognitiveservices.speech as speechsdk
    config = speechsdk.SpeechConfig(subscription=key, region=region)
    config.speech_recognition_language = 'pt-BR'
    audio = speechsdk.audio.AudioConfig(filename=path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=config, audio_config=audio)
    import threading
    done = threading.Event()
    parts, errors = [], []
    recognizer.recognized.connect(lambda e: parts.append(e.result.text) if e.result.reason == speechsdk.ResultReason.RecognizedSpeech else None)
    recognizer.session_stopped.connect(lambda e: done.set())
    def cancelled(e):
        details = e.result.cancellation_details
        if details.reason != speechsdk.CancellationReason.EndOfStream:
            errors.append(f'{details.reason}: {details.error_details or "sem detalhes"}')
        done.set()
    recognizer.canceled.connect(cancelled)
    recognizer.start_continuous_recognition_async().get()
    completed = done.wait(300)
    recognizer.stop_continuous_recognition_async().get()
    if not completed or errors:
        raise RuntimeError('Transcrição incompleta ou cancelada: ' + '; '.join(errors))
    return ' '.join(parts)


def video_analyze(path, model_name='yolov8n-pose.pt', start_seconds=0, end_seconds=None):
    import cv2
    from ultralytics import YOLO
    model = YOLO(model_name)
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError('Não foi possível abrir o vídeo.')
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = total_frames / fps if total_frames > 0 else None
    if start_seconds < 0 or (end_seconds is not None and end_seconds <= start_seconds):
        cap.release()
        raise ValueError('O fim deve ser maior que o início, e o início não pode ser negativo.')
    if duration is not None and start_seconds >= duration:
        cap.release()
        raise ValueError('O início está fora do vídeo.')
    every = max(1, round(fps))
    samples, missing, frame_no, previous = [], 0, 0, None
    try:
        while True:
            ok, frame = cap.read()
            if not ok: break
            current_time = frame_no / fps
            if end_seconds is not None and current_time >= end_seconds:
                break
            if current_time >= start_seconds and frame_no % every == 0:
                result = model.predict(frame, verbose=False, conf=.35)[0]
                count = len(result.keypoints) if result.keypoints is not None else 0
                item = {'second': round(frame_no/fps, 2), 'people': count}
                if count == 1:
                    # Normalize coordinates by image dimensions so resolution does not affect displacement.
                    points = result.keypoints.xyn[0].cpu().numpy()
                    confidence = result.keypoints.conf[0].cpu().numpy()
                    current = {i: (float(p[0]), float(p[1])) for i, p in enumerate(points) if confidence[i] >= .5}
                    if previous:
                        shared = set(previous) & set(current)
                        if len(shared) >= 5:
                            distance = sum(((current[i][0]-previous[i][0])**2 + (current[i][1]-previous[i][1])**2)**.5 for i in shared)/len(shared)
                            item['mean_keypoint_displacement'] = round(distance, 4)
                            item['movement_flag'] = distance > .15
                    previous = current
                else:
                    previous = None
                samples.append(item)
                if count == 0: missing += 1
            frame_no += 1
    finally:
        cap.release()
    if not samples: raise ValueError('O vídeo não contém quadros legíveis.')
    # Ausência de detecção é limitação observacional, não anomalia clínica.
    return {'frames_read': frame_no, 'fps': fps, 'duration_seconds': duration,
            'interval_start_seconds': start_seconds, 'interval_end_seconds': end_seconds,
            'samples': samples, 'no_pose_samples': missing}


def audio_features(path):
    """Signal quality and pause estimates, not clinical voice classification."""
    import wave
    import numpy as np
    with wave.open(path, 'rb') as f:
        if f.getsampwidth() != 2 or f.getnchannels() != 1:
            raise ValueError('Use WAV PCM de 16 bits e canal mono.')
        rate = f.getframerate()
        signal = np.frombuffer(f.readframes(f.getnframes()), dtype='<i2').astype(float) / 32768
    if len(signal) < rate:
        raise ValueError('O áudio deve ter pelo menos um segundo.')
    windows = [signal[i:i+rate] for i in range(0, len(signal)-rate+1, rate)]
    rms = [float(np.sqrt(np.mean(w*w))) for w in windows]
    window_size = max(1, round(rate * .05))
    chunks = [signal[i:i+window_size] for i in range(0, len(signal), window_size)]
    silent = [float(np.sqrt(np.mean(chunk*chunk))) < .01 for chunk in chunks]
    pauses, current = [], 0.0
    for chunk, is_silent in zip(chunks, silent):
        if is_silent:
            current += len(chunk) / rate
        elif current:
            if current >= .3: pauses.append(round(current, 3))
            current = 0.0
    if current >= .3: pauses.append(round(current, 3))
    clipped = float(np.mean(np.abs(signal) >= .99))
    return {'duration_seconds': round(len(signal)/rate, 2), 'sample_rate': rate,
            'rms_per_second': [round(x, 5) for x in rms],
            'quiet_seconds': sum(x < .01 for x in rms),
            'pause_count_300ms': len(pauses), 'pause_durations_seconds': pauses,
            'clipped_fraction': round(clipped, 5),
            'note': 'Pausas e energia dependem de ruído, volume e contexto. Não identificam fadiga, disartria ou doença.'}


def compare_audio_features(reference, current):
    """Compare recordings without assigning medical meaning or a risk category."""
    def average(values):
        return sum(values) / len(values) if values else 0
    base = average(reference['rms_per_second'])
    observed = average(current['rms_per_second'])
    return {'reference_duration_seconds': reference['duration_seconds'],
            'current_duration_seconds': current['duration_seconds'],
            'reference_mean_rms': round(base, 5), 'current_mean_rms': round(observed, 5),
            'rms_ratio': round(observed / base, 3) if base > 0 else None,
            'reference_pause_count': reference['pause_count_300ms'],
            'current_pause_count': current['pause_count_300ms'],
            'note': 'Gravações com microfone, distância, ambiente ou conteúdo diferentes não são diretamente comparáveis. Não é diagnóstico.'}
