# Experimento exploratório com medidas de voz

Foi avaliada regressão logística balanceada com padronização ajustada somente nos dados de treinamento. A validação retira todas as gravações de um identificador por vez; a previsão do indivíduo é a média das probabilidades de suas gravações, com limiar 0,5. Não houve ajuste de hiperparâmetros nem validação externa. Cada avaliação foi feita sem incluir gravações do indivíduo testado no treino.

Fonte: Little, M. (2007), [Parkinsons — UCI](https://archive.ics.uci.edu/dataset/174/parkinsons), DOI [10.24432/C59C74](https://doi.org/10.24432/C59C74), licença CC BY 4.0. O conjunto fornece atributos pré-calculados de voz e rótulos de Parkinson, não áudio bruto nem rótulos de fadiga ou disartria. A documentação menciona 31 pessoas; o agrupamento por prefixo de identificador no arquivo resulta em 32 grupos, que é a unidade adotada aqui. Essa divergência impede assumir que os grupos correspondem exatamente a 32 indivíduos únicos sem documentação adicional.

Na execução local: 195 gravações, 32 grupos (8 rótulo 0 e 24 rótulo 1). A matriz de confusão no nível de grupo, linhas reais e colunas previstas [0, 1], foi `[[4, 4], [4, 20]]`. Acurácia 75%, acurácia balanceada 66,7%, sensibilidade 83,3% e especificidade 50%. Sempre prever a classe majoritária também produziria 75% de acurácia. Com apenas oito grupos da classe 0, quatro falsos positivos tornam a especificidade especialmente incerta. Resultados exploratórios não são estimativas clínicas.

Reprodução (usa rede apenas para baixar o ZIP oficial):

```bash
curl -fsSL https://archive.ics.uci.edu/static/public/174/parkinsons.zip -o /tmp/parkinsons-uci.zip
python experimentos/avaliar_uci_voz.py /tmp/parkinsons-uci.zip
```

Versões utilizadas: scikit-learn 1.9.1, pandas 3.0.5, NumPy 2.5.3. O script imprime contagens, matriz e versões. A base não é distribuída neste repositório.

**Limitação essencial:** o modelo não está integrado ao aplicativo porque as 22 variáveis pré-calculadas não correspondem às métricas extraídas do WAV pelo protótipo. Não se pode aplicar esse resultado ao áudio do usuário, nem apresentá-lo como detecção de cansaço, dificuldade respiratória, disartria ou Parkinson. Para isso seriam necessários dados e rótulos adequados, extração compatível, separação por pessoa, validação externa e revisão especializada.
