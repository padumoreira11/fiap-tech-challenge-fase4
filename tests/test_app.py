from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_new_analysis_clears_monitor_and_text():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    app.text_area(key='clinical_text').set_value('teste anterior').run()
    next(button for button in app.button if button.label == 'Iniciar simulação ao vivo').click().run()
    assert len(app.dataframe) == 1
    next(button for button in app.button if button.label == 'Iniciar nova análise').click().run()
    assert not app.exception
    assert app.text_area(key='clinical_text').value == ''
    assert len(app.dataframe) == 0
