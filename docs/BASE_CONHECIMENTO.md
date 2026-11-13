# Base de conhecimento e matriz de requisitos

Fonte principal: `../../IADT - Fase 4 - Tech challenge.pdf` (enunciado, páginas 2–4). O PDF distingue objetivos, requisitos e exemplos; Azure Speech e Text Analytics são obrigatórios. Os livros estão em `../Materiais_Fase_4/`.

| Requisito | Abordagem | Situação |
| --- | --- | --- |
| Vídeo: eventos ou movimentos fora do padrão | YOLOv8 pose amostra quadros e sinaliza deslocamento elevado de pontos-chave | Parcial: limiar experimental, sem validação de anomalia ou de procedimento |
| Áudio: transcrição e alterações vocais | Azure Speech, WER, medições exploratórias e experimento separado com atributos UCI | Parcial: experimento não recebe WAV nem valida fadiga, disartria ou respiração |
| Termos críticos e sentimento | Busca literal e Azure Language | Executado com uma frase sintética; requer avaliação mais ampla |
| Sinais vitais | Limiares ilustrativos, simulação e monitor de arquivo CSV com consulta periódica | Protótipo demonstrativo; sem sensores reais ou validação clínica |
| Prescrições | Variação relativa e mudança de unidade | Implementado em lote; não avalia adequação clínica |
| Movimentação durante internação | Deslocamento entre amostras sucessivas de pontos-chave | Parcial: não rastreia identidade nem monitora continuamente |
| Alertas | Simulação envia alertas para fila local com confirmação persistente de recebimento | Demonstração local da equipe simulada; não envia a equipe real |
| Git, relatório e vídeo até 15 minutos | Código, relatório e roteiro neste diretório | Vídeo e publicação dependem do grupo |

As aulas de análise de vídeo, áudio e texto (Aula 03, p. 3; Aula 04, p. 3; Aula 05, p. 3; Aula 06, p. 3) cobrem, respectivamente, pontos-chave e MediaPipe, transcrição, classificação e sumarização. Esses exemplos apoiam o desenho, mas não substituem os serviços Azure especificados. As aulas de AWS e OpenAI são referências complementares, não equivalentes automáticos aos requisitos Azure.

Fluxo: vídeo → pose; áudio → Azure Speech → transcrição → Azure Language e termos; CSV → regras → alertas; painel reúne os resultados. Os resultados não são uma fusão clínica validada. Uma fusão futura exigirá sincronização por paciente e tempo, incerteza e testes com dados rotulados.
