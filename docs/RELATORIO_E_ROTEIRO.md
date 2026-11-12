# Relatório técnico e roteiro de demonstração

## Problema e fluxo

O desafio solicita monitoramento multimodal e alertas para uma equipe médica. Este protótipo recebe vídeo, áudio e CSVs, apresenta achados em um painel e permite exportar JSON. A transcrição usa Azure Speech e o texto pode ser analisado com Azure Language. O vídeo usa YOLOv8 pose em amostras de um quadro por segundo; sinais vitais e variações de prescrição usam regras ilustrativas.

## Resultados e avaliação

Os arquivos sintéticos de exemplo contêm frequência cardíaca 125 bpm, SpO2 88% e aumento de dose de 10 para 20 mg. As regras configuradas devem gerar dois alertas de sinais e um de prescrição. São dados inventados e o resultado esperado não comprova desempenho clínico. Os testes locais verificam os cálculos; não representam avaliação de sensibilidade ou especificidade. Registrar aqui resultados reais do grupo após executar Azure e vídeos com dados apropriados, sem inventar métricas.

Na verificação de 10/11/2026, cinco testes automatizados passaram. O vídeo sintético de dois segundos sem pessoa teve 10 quadros lidos e duas amostras sem pose, conforme esperado. Esse teste apenas verifica o fluxo e não demonstra detecção de movimento. O áudio de demonstração é fala sintetizada em português, com duração de 5,69 segundos; a extração local de energia foi executada. O Azure Speech transcreveu corretamente a frase sintética “Esta é uma consulta simulada. Estou sentindo falta de ar e cansaço desde ontem.” O Azure Language retornou sentimento negativo e frases-chave incluindo “consulta simulada” e “cansaço”; a regra literal sinalizou “falta de ar”. Um único exemplo não mede a acurácia dos serviços.

Foi adicionada uma simulação de quatro amostras com atualização a cada três segundos. A terceira amostra contém 125 bpm e SpO2 de 89% e gera dois alertas pelas regras demonstrativas. Seis testes automatizados passaram e a inicialização da interface da simulação foi verificada. O fluxo não recebe sinais em tempo real de dispositivos nem envia mensagens externas.

A análise acústica exploratória calcula energia por segundo, pausas estimadas em janelas de 50 ms e proporção de amostras saturadas, com comparação opcional a uma gravação de referência. No áudio sintético de 5,69 segundos, não foram detectadas pausas de pelo menos 300 ms nem saturação pelo critério implementado. Um teste com sinal artificial contendo pausa conhecida de 0,5 segundo passou. Estes indicadores dependem da gravação e não classificam fadiga, disartria ou dificuldade respiratória; dados rotulados e validação seriam necessários para isso. Sete testes automatizados passaram após essa ampliação.

A comparação da transcrição obtida com a frase sintética conhecida resultou em zero erros em 14 palavras (WER 0 neste único exemplo, após normalizar caixa e pontuação). Isto não é uma estimativa de desempenho populacional. A aplicação agora calcula WER para referências informadas; os oito testes automatizados passaram. O plano de avaliação e fontes potenciais estão em `AVALIACAO_AUDIO.md`.

Uma verificação posterior adicionou o teste de reinício da análise, totalizando nove testes aprovados. A revisão de alertas registra a lista revisada e avisa quando ela muda.

Na gravação voluntária de demonstração, foram analisadas inicialmente 25 amostras a intervalos de um segundo. Uma pessoa foi detectada em todas; o deslocamento excedeu o limiar experimental de 0,15 em aproximadamente 1 e 24 segundos. O participante esclareceu que estava se afastando ou aproximando da câmera nesses momentos. Na reanálise do intervalo de 2 segundos (inclusive) a 23 segundos (exclusivo), houve uma pessoa em cada uma das 21 amostras e nenhum deslocamento acima do limiar. O resultado não valida a detecção de anomalias; ilustra como movimentos de entrada e saída afetam o indicador. O vídeo pessoal não deve ser publicado sem consentimento e foi excluído do versionamento.

O participante informou movimentos lentos entre 3 e 16 segundos e mais rápidos entre 17 e 21 segundos. A média dos deslocamentos normalizados nas amostras foi 0,0434 (14 pontos) e 0,0645 (5 pontos), respectivamente. Nenhum excedeu o limiar 0,15: portanto o limiar atual não sinalizou os movimentos rápidos descritos. Trata-se de uma gravação e de uma referência aproximada, não de validação de anomalias.

Uma avaliação de fala separada no TORGO usou 300 gravações de seis participantes e validação que separa participantes. Foram cinco classificações corretas e uma incorreta no nível de participante. As limitações, a matriz de confusão e os passos de reprodução constam em `EXPERIMENTO_TORGO.md`; o modelo não está implantado como detector clínico.

## Roteiro de até 15 minutos

1. Apresentar o problema, limitações e arquitetura (2 min).
2. Carregar vídeo autorizado e mostrar poses detectadas e limites da análise (3 min).
3. Transcrever áudio sintético no Azure Speech e enviar texto ao Azure Language (3 min).
4. Carregar os dois CSVs, verificar os três alertas esperados e exportar JSON (3 min).
5. Mostrar código, testes, lacunas e próximos passos (3 min).

Não alegar detecção de anomalia de movimento, fadiga ou alerta em tempo real enquanto não implementadas e validadas. A publicação do vídeo e do repositório exige execução e revisão pelo grupo.
