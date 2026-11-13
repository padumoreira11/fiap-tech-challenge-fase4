from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_new_analysis_clears_monitor_and_text(tmp_path, monkeypatch):
    monkeypatch.setenv('FIAP_QUEUE_PATH', str(tmp_path/'queue.sqlite3'))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    app.text_area(key='clinical_text').set_value('teste anterior').run()
    next(button for button in app.button if button.label == 'Iniciar simulação ao vivo').click().run()
    assert len(app.dataframe) == 1
    next(button for button in app.button if button.label == 'Iniciar nova análise').click().run()
    assert not app.exception
    assert app.text_area(key='clinical_text').value == ''
    assert len(app.dataframe) == 0


def test_simulation_delivers_alert_and_records_receipt(tmp_path, monkeypatch):
    import time
    monkeypatch.setenv('FIAP_QUEUE_PATH', str(tmp_path/'queue.sqlite3'))
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    next(button for button in app.button if button.label == 'Iniciar simulação ao vivo').click().run()
    app.session_state['simulation_start'] = time.time() - 7
    app.run()
    assert not app.exception
    receipts=[b for b in app.button if b.label == 'Registrar recebimento']
    assert len(receipts) == 2
    receipts[0].click().run()
    assert not app.exception
    assert len([b for b in app.button if b.label == 'Registrar recebimento']) == 1
