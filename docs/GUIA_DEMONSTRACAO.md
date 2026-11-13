# Guia de demonstração — até 15 minutos

Antes de gravar, inicie a aplicação conforme o README, configure as chaves sem exibi-las na gravação e clique em “Iniciar nova análise”. Utilize apenas os dados de exemplo e a gravação voluntária autorizada. Não grave a tela de chaves nem publique o vídeo da pessoa sem sua autorização.

1. **Contexto (1 min):** apresente a solução como protótipo educacional; explique que ela não realiza diagnóstico nem está conectada a um hospital.
2. **Vídeo (3 min):** na aba Vídeo, carregue a gravação voluntária local, informe início 2 e fim 23 segundos e execute. Mostre as 21 amostras com uma pessoa e nenhum deslocamento acima do limiar. Explique que os extremos foram excluídos porque a pessoa caminhava para ou da câmera; a ausência de sinalização não valida normalidade.
3. **Áudio e texto (4 min):** carregue `exemplos/consulta_sintetica.wav`, meça características e transcreva com Azure Speech. Use como referência: “Esta é uma consulta simulada. Estou sentindo falta de ar e cansaço desde ontem.” Compare a transcrição e mostre WER; acesse Texto e execute Azure Language. Mostre o alerta literal e explique que ele não interpreta negação nem constitui diagnóstico.
4. **Sinais e prescrição (3 min):** carregue os dois CSVs em `exemplos/`, execute e mostre os dois alertas de sinais e a mudança de dose. Na aba Monitoramento simulado, inicie a sequência e aguarde a terceira amostra. Mostre a fila local da equipe simulada, registre o recebimento dos alertas e baixe o JSON. É uma simulação local, sem envio a uma equipe real. A confirmação individual da fila é persistida no banco local, não no JSON da análise.
5. **Conclusão (2 min):** explique que detecção validada de alterações vocais, validação clínica de movimento, integração com sensores e notificação externa não estão implementadas. Apresente o relatório e os testes sem afirmar desempenho não medido.

Revise previamente o resultado exibido na sessão real; não use números de uma execução anterior como se fossem de uma nova. A publicação e a gravação final pertencem ao grupo.
