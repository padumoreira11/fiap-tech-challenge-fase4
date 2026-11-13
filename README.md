# Fase 4 — Monitor multimodal

Protótipo acadêmico em Streamlit. A análise de sinais e prescrições usa regras demonstrativas; a detecção de termos é literal. O vídeo usa YOLOv8 pose para localizar pessoas e pontos corporais em amostras, sem diagnosticar nem inferir anomalia de movimento. O Azure Speech transcreve áudio; Azure Language analisa sentimento e frases-chave. Alertas aparecem no painel e no relatório baixável; não são enviados a terceiros.

## Execução

```bash
cd fase4
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Na interface, informe região/chave Speech e endpoint/chave Language. O Azure é um serviço pago conforme sua conta; não inclua chaves no repositório. Use arquivos sintéticos ou autorizados. Para WAV compatível: `ffmpeg -i entrada.mp3 -ar 16000 -ac 1 -c:a pcm_s16le saida.wav`. A primeira execução do vídeo pode baixar pesos do YOLO. Use o mesmo paciente e período apenas com dados fictícios e compare manualmente os resultados no painel.

Os CSVs em `exemplos/` ilustram os campos e devem estar em ordem cronológica. Os limiares são arbitrários para a demonstração; não os empregue em assistência. O relatório JSON contém transcrição e resultados e deve ser tratado como sensível se dados reais forem utilizados.

O arquivo `exemplos/consulta_sintetica.wav` contém fala gerada para testar transcrição. `exemplos/video_sintetico_sem_pessoa.mp4` testa a ausência de detecção; não é vídeo clínico nem serve para avaliar movimentos. Uma gravação voluntária foi analisada localmente e está excluída do versionamento. As chaves podem ser informadas nos campos protegidos da aplicação; não as coloque em documentos nem no Git.

Na aba Vídeo, os campos de início e fim permitem analisar apenas um intervalo sem modificar a gravação original; o fim é exclusivo. Para a gravação voluntária testada, foram usados 2 e 23 segundos.

O limiar de deslocamento é configurável para explorar o compromisso entre sinalizações e omissões; o valor padrão 0,15 é ilustrativo. A escolha feita no vídeo de demonstração não é validada para outras câmeras, distâncias ou pessoas.

Para demonstrar a ingestão contínua de um arquivo CSV local, execute `python monitor.py exemplos/sinais.csv alertas.jsonl --interval 3`. O processo consulta o arquivo repetidamente, mostra novos alertas no terminal e os registra em JSONL, evitando duplicatas na reinicialização. A entrada deve ser atualizada por um produtor externo; execute somente uma instância escritora e use dados sintéticos. O arquivo de saída contém dados potencialmente sensíveis e é ignorado pelo Git. Isto não conecta sensores nem envia alertas por rede, não garante latência ou disponibilidade e não deve ser usado na assistência.

## Limitações e trabalho restante

O vídeo sinaliza deslocamentos elevados entre poses de amostras consecutivas, com limiar experimental; isso não valida anomalias clínicas nem desvios de procedimento. A análise acústica calcula energia e silêncio, sem detectar fadiga, disartria ou respiração. As duas integrações Azure foram verificadas com uma frase sintética, não com dados clínicos. Uma sequência simulada atualiza sinais e alertas a cada três segundos; não há conexão com sensores nem entrega real à equipe. Nenhuma acurácia clínica foi estabelecida. Portanto o protótipo não cumpre integralmente o enunciado. O vídeo de entrega e avaliação em conjuntos rotulados precisam ser realizados e documentados com resultados verdadeiros.

Na aba Áudio, é possível comparar medidas de energia e pausas com uma gravação de referência. As condições de gravação e o conteúdo influenciam as medidas, que não indicam condição médica.

Testes locais: `python -m pytest tests`.
