# Plano de avaliação de áudio

O protótipo mede transcrição e características acústicas, mas não foi treinado nem validado para identificar doenças. A taxa de erro por palavra (WER) avalia a transcrição contra uma referência humana, após normalizar caixa e pontuação. Valores maiores que 1 são possíveis quando há muitas inserções. Não mede sintomas.

Para executar, selecione um WAV autorizado, transcreva com Azure Speech e informe o texto fiel na referência. Registre número de amostras, condições e taxa agregada como soma de erros dividida pela soma de palavras de referência. Separe indivíduos entre conjuntos de desenvolvimento e teste; não reutilize gravações de uma pessoa nos dois conjuntos. Não faça afirmações clínicas a partir de um áudio sintético.

O [Common Voice](https://commonvoice.mozilla.org/about) contém fala de voluntários e pode apoiar avaliação de reconhecimento de fala; acesso requer e-mail. A lista de [datasets](https://commonvoice.mozilla.org/et/datasets) identifica uma versão em português como CC0 e para ASR. Esse conjunto não deve ser presumido como rotulado para disartria ou fadiga. O [Bridge2AI-Voice](https://physionet.org/content/b2ai-voice/4.0.0/) tem informações de saúde e exige acesso registrado e licença própria. Verificar elegibilidade, autorização, idioma, rótulos e regras da versão escolhida antes de usar qualquer arquivo. Nenhum desses conjuntos foi baixado nem avaliado neste projeto.

Para um classificador de condição vocal seriam necessários rótulos independentes, divisão por indivíduo, conjunto de teste separado, métricas por classe e análise por subgrupo; uma avaliação com dados e supervisão apropriados é indispensável antes de qualquer alegação clínica.
