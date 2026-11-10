import json
import os
import tempfile
from pathlib import Path
import streamlit as st
from engine import vital_alerts, prescription_alerts, text_alerts, parse_csv, azure_speech, azure_text, video_analyze, audio_features, compare_audio_features, simulated_observation
from evaluation import word_error_rate

st.set_page_config(page_title='Monitor multimodal', layout='wide')
st.title('Monitor multimodal — Fase 4')
st.warning('Protótipo educacional. Não é dispositivo médico; limiares e alertas são demonstrativos e não diagnosticam nem substituem avaliação profissional.')
st.caption('Use somente dados sintéticos ou autorizados. O envio ao Azure ocorre quando os botões correspondentes são acionados.')
if 'report' not in st.session_state: st.session_state.report = {'alerts': []}
if 'upload_epoch' not in st.session_state: st.session_state.upload_epoch = 0
report = st.session_state.report
if st.button('Iniciar nova análise'):
    st.session_state.report = {'alerts': []}
    st.session_state.upload_epoch += 1
    for key in ('simulation_start', 'simulation_completed', 'clinical_text', 'reference_transcript'):
        st.session_state.pop(key, None)
    st.rerun()

with st.expander('Configuração Azure'):
    region = st.text_input('Região Speech', value=os.getenv('SPEECH_REGION', ''))
    skey = st.text_input('Chave Speech', value=os.getenv('SPEECH_KEY', ''), type='password')
    endpoint = st.text_input('Endpoint Azure Language', value=os.getenv('LANGUAGE_ENDPOINT', ''))
    lkey = st.text_input('Chave Azure Language', value=os.getenv('LANGUAGE_KEY', ''), type='password')

v, a, t, s, live = st.tabs(['Vídeo', 'Áudio', 'Texto', 'Sinais e prescrições', 'Monitoramento simulado'])
with v:
    video = st.file_uploader('Vídeo de fisioterapia', type=['mp4','mov','avi'], key=f'video_{st.session_state.upload_epoch}')
    col1, col2 = st.columns(2)
    start = col1.number_input('Analisar a partir de (segundos)', min_value=0.0, value=0.0, step=1.0)
    end = col2.number_input('Analisar até (segundos; 0 = final)', min_value=0.0, value=0.0, step=1.0)
    if video and st.button('Analisar vídeo com YOLO pose'):
        try:
            with tempfile.TemporaryDirectory() as d:
                path = Path(d)/('video'+Path(video.name).suffix); path.write_bytes(video.getvalue())
                with st.spinner('Analisando um quadro por segundo; o modelo pode ser baixado na primeira execução...'):
                    report['video'] = video_analyze(str(path), start_seconds=start, end_seconds=end or None)
            st.success('Análise concluída.')
        except Exception as e: st.error(f'Falha no vídeo: {e}')
    if 'video' in report:
        st.json(report['video']); st.info('O deslocamento médio acima de 0,15 da dimensão da imagem é sinalizado como evento para revisão, não como anomalia clínica. Câmera, oclusão e várias pessoas afetam o resultado.')
with a:
    audio = st.file_uploader('Áudio WAV PCM mono 16 kHz', type=['wav'], key=f'audio_{st.session_state.upload_epoch}')
    baseline = st.file_uploader('Áudio de referência opcional, WAV PCM mono', type=['wav'], key=f'baseline_{st.session_state.upload_epoch}')
    if audio and st.button('Medir características acústicas locais'):
        try:
            with tempfile.TemporaryDirectory() as d:
                path=Path(d)/'audio.wav'; path.write_bytes(audio.getvalue())
                report['audio_features']=audio_features(str(path))
                if baseline:
                    ref_path=Path(d)/'referencia.wav'; ref_path.write_bytes(baseline.getvalue())
                    report['audio_comparison']=compare_audio_features(audio_features(str(ref_path)),report['audio_features'])
                else:
                    report.pop('audio_comparison',None)
        except Exception as e: st.error(f'Falha na análise acústica: {e}')
    if 'audio_features' in report: st.json(report['audio_features'])
    if 'audio_comparison' in report: st.json(report['audio_comparison'])
    st.caption('Pausas e nível acústico são medições exploratórias; não detectam fadiga, disartria ou dificuldade respiratória.')
    if audio and st.button('Transcrever com Azure Speech'):
        if not skey or not region: st.error('Informe chave e região do Speech.')
        else:
            try:
                with tempfile.TemporaryDirectory() as d:
                    path=Path(d)/'audio.wav'; path.write_bytes(audio.getvalue())
                    report['transcript']=azure_speech(str(path),region,skey)
                    st.session_state['clinical_text'] = report['transcript']
                    for key in ('speech_evaluation', 'language', 'text_alerts', 'review'):
                        report.pop(key, None)
                st.success('Transcrição concluída.')
            except Exception as e: st.error(f'Falha na transcrição: {e}')
    if 'transcript' in report: st.text_area('Transcrição', report['transcript'], height=160, disabled=True)
    if 'transcript' in report:
        reference_text = st.text_area('Transcrição de referência para avaliação opcional', key='reference_transcript')
        if st.button('Comparar transcrição com referência'):
            try: report['speech_evaluation'] = word_error_rate(reference_text, report['transcript'])
            except ValueError as e: st.error(str(e))
        if 'speech_evaluation' in report: st.json(report['speech_evaluation'])
        st.caption('WER conta substituições, exclusões e inserções após normalizar maiúsculas e pontuação. Não mede condição médica.')
with t:
    text=st.text_area('Texto clínico ou transcrição', key='clinical_text', height=160)
    if st.button('Identificar termos e analisar no Azure Language'):
        if not text.strip(): st.error('Informe um texto.')
        else:
            report['text_alerts']=text_alerts(text)
            if endpoint and lkey:
                try: report['language']=azure_text(text,endpoint,lkey)
                except Exception as e: st.error(f'Falha no Azure Language: {e}')
            else: st.warning('Termos analisados localmente; configure Azure Language para sentimento e frases-chave.')
    if 'language' in report: st.json(report['language'])
    if 'text_alerts' in report: st.json(report['text_alerts'])
    st.caption('Busca literal não entende negações; sentimento não é diagnóstico.')
with s:
    vital=st.file_uploader('CSV de sinais vitais',type='csv',key=f'vitals_{st.session_state.upload_epoch}')
    meds=st.file_uploader('CSV de prescrições em ordem cronológica',type='csv',key=f'meds_{st.session_state.upload_epoch}')
    if st.button('Detectar desvios'):
        try:
            report['vital_alerts']=vital_alerts(parse_csv(vital)) if vital else []
            report['prescription_alerts']=prescription_alerts(parse_csv(meds)) if meds else []
            st.success('Análise concluída.')
        except (KeyError,ValueError,UnicodeError) as e: st.error(f'CSV inválido: {e}')
    st.json(report.get('vital_alerts',[])+report.get('prescription_alerts',[]))
with live:
    st.caption('Demonstração com quatro amostras artificiais, uma a cada três segundos. Não há conexão com sensores reais.')
    if st.button('Iniciar simulação ao vivo'):
        import time
        st.session_state['simulation_start'] = time.time()
        st.session_state['simulation_completed'] = False
        report['live_observations'] = []
        report['live_alerts'] = []
    @st.fragment(run_every=3)
    def live_monitor():
        import time
        if 'simulation_start' not in st.session_state:
            st.write('Simulação parada.')
            return
        elapsed = time.time() - st.session_state['simulation_start']
        count = min(4, int(elapsed // 3) + 1)
        observations = [simulated_observation(i) for i in range(count)]
        report['live_observations'] = observations
        report['live_alerts'] = vital_alerts(observations)
        st.dataframe(observations, use_container_width=True)
        if report['live_alerts']:
            st.error('Desvio demonstrativo detectado: solicite revisão da equipe.')
            st.dataframe(report['live_alerts'], use_container_width=True)
        if count == 4:
            st.success('Simulação concluída. O monitor acompanha apenas esta sequência de demonstração.')
            if not st.session_state.get('simulation_completed'):
                st.session_state['simulation_completed'] = True
                st.rerun(scope='app')
    live_monitor()

st.subheader('Painel de alertas')
alerts=report.get('vital_alerts',[])+report.get('prescription_alerts',[])+report.get('text_alerts',[])+report.get('live_alerts',[])
alerts += [{'source':'vídeo', 'time':str(x['second'])+' s', 'message':'Deslocamento elevado de pontos corporais; revisar vídeo.'} for x in report.get('video',{}).get('samples',[]) if x.get('movement_flag')]
if alerts: st.dataframe(alerts, use_container_width=True)
else: st.write('Nenhum alerta gerado nesta sessão.')
if alerts:
    st.info('Fluxo demonstrativo: alertas disponíveis neste painel para revisão da equipe. Nenhuma notificação externa é enviada.')
    if st.button('Registrar revisão dos alertas'):
        from datetime import datetime, timezone
        report['review'] = {'status': 'revisado na demonstração', 'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'alerts': list(alerts)}
if 'review' in report:
    if report['review']['alerts'] == alerts: st.write(report['review'])
    else: st.warning('Os alertas mudaram após a revisão anterior; revise a lista atual.')
report['alerts']=alerts
st.download_button('Baixar relatório JSON', json.dumps(report,ensure_ascii=False,indent=2), 'relatorio.json','application/json')
