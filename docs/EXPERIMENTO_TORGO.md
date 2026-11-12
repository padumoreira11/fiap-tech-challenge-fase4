# Avaliação exploratória de áudio TORGO

Fonte: Rudzicz, Namasivayam e Wolff (2012), *The TORGO database of acoustic and articulatory speech from speakers with dysarthria*, Language Resources and Evaluation 46, 523–541. [Página oficial e licença de uso acadêmico](https://www.cs.toronto.edu/~complingweb/data/TORGO/torgo.html). Dados da Universidade de Toronto, em inglês, uso acadêmico não lucrativo e sujeitos às condições da fonte. Os arquivos originais não são redistribuídos neste repositório.

Foram usadas as primeiras 50 gravações de pelo menos um segundo encontradas na ordem dos arquivos WAV de microfone de cabeça para cada participante dos arquivos F e FC: três participantes identificadas como disártricas e três controles, 300 gravações ao todo. O método não foi selecionado por busca de desempenho: usa pausas, nível RMS, variação de RMS e saturação, regressão logística balanceada e padronização ajustada apenas no treino. Cada rodada exclui todas as gravações de uma participante; a probabilidade média das 50 gravações da participante excluída é comparada a 0,5.

Resultado exploratório: matriz de confusão por participante, linhas reais e colunas previstas [controle, disartria], `[[3, 0], [1, 2]]`. Acurácia e acurácia balanceada foram 5/6 (83,3%); sensibilidade 2/3 (66,7%), especificidade 3/3 (100%) e acurácia da classe majoritária 50%. **Cada erro muda a métrica em 16,7 pontos percentuais; os valores são altamente instáveis.** O resultado não mede desempenho em gravações avulsas nem comprova capacidade clínica. Não há validação externa, correspondência controlada de frases, nem avaliação em português; seleção dos primeiros arquivos, condições de captação e duração podem confundir o classificador. Não é evidência de detecção de fadiga, respiração ou disartria em novos pacientes.

Reprodução a partir dos arquivos F e FC obtidos da fonte oficial, com espaço em disco suficiente:

```bash
python experimentos/preparar_torgo.py --output /tmp/torgo-f --limit 50 /caminho/F.tar.bz2
python experimentos/preparar_torgo.py --output /tmp/torgo-fc --limit 50 /caminho/FC.tar.bz2
python experimentos/unir_manifestos.py --output /tmp/torgo-manifest.csv /tmp/torgo-f/manifest.csv /tmp/torgo-fc/manifest.csv
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experimentos/avaliar_audio_rotulado.py /tmp/torgo-manifest.csv
```

O experimento não foi implantado na interface nem deve ser aplicado a pessoas: faltam dados apropriados em português, amostra maior, avaliação independente e revisão especializada.
