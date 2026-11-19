# Entregable 4 · resultados (test_v1)

Partidas resueltas en hasta 10 jugadas; los paros cuentan como no resueltas. «Histórico» = trazas del D3 (results/d3/raw, commit 10da2ec); «reproducido» = corrida nueva en este repositorio.

| Sistema | Origen | Resueltas | Intentos incompatibles (estricta) | Paros | Llamadas/partida | s modelo/partida |
|---|---|---:|---:|---:|---:|---:|
| D1 · prompting directo | histórico | 2/30 | 99.1% (214/216) | 0 | 9.7 | 6.6 |
| D1 · prompting directo | reproducido | 2/30 | 99.1% (214/216) | 0 | 9.7 | 5.3 |
| D2 · LoRA sin agentes | histórico | 14/30 | 81.1% (150/185) | 0 | 7.2 | 5.7 |
| D2 · LoRA sin agentes | reproducido | 14/30 | 81.1% (150/185) | 0 | 7.2 | 4.7 |
| D3 · tres agentes (LoRA común) | histórico | 25/30 | 15.4% (10/65) | 5 | 46.5 | 98.0 |
| D3 · tres agentes (LoRA común) | reproducido | 25/30 | 15.4% (10/65) | 5 | 45.5 | 284.9 |
| D4 · Selector con adaptador propio | reproducido | 29/30 | 12.7% (9/71) | 1 | 36.6 | 247.9 |
| Control · filtro por reglas | histórico | 30/30 | 0.0% (0/64) | 0 | 0.0 | 0.0 |
| Control · filtro por reglas | reproducido | 30/30 | 0.0% (0/64) | 0 | 0.0 | 0.0 |

## Comparaciones pareadas (McNemar exacto, exploratorio)

- D3 → D4 (reproducidos): 4 victorias y 0 derrotas discordantes del segundo; p=0.125 (n=30).

## Selector aislado (mismas entradas, temperatura 0)

| Conjunto | Pesos · prompt | Páginas | Conserva compatibles | Precisión | Páginas exactas | Descarta al secreto | Amarillo de un valor: conserva | Fuera de protocolo |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| d3_test_trace[amarillo] | base_d3 | 280 | 61.3% (38/62) | 1.7% (38/2269) | 6/280 | 15/40 | 55.6% (15/27) | 44 |
| d3_test_trace[amarillo] | d3_d3 | 280 | 64.5% (40/62) | 45.5% (40/88) | 237/280 | 18/40 | 40.7% (11/27) | 0 |
| d3_test_trace[amarillo] | d4_d3 | 280 | 91.9% (57/62) | 58.8% (57/97) | 238/280 | 5/40 | 85.2% (23/27) | 0 |
| d3_valid_trace[amarillo] | ckpt_r1_1000 | 84 | 65.0% (13/20) | 65.0% (13/20) | 71/84 | 6/12 | 55.6% (5/9) | 0 |
| d3_valid_trace[amarillo] | ckpt_r2_0670 | 84 | 95.0% (19/20) | 76.0% (19/25) | 78/84 | 1/12 | 88.9% (8/9) | 0 |
| d3_valid_trace[amarillo] | ckpt_r2_final | 84 | 95.0% (19/20) | 76.0% (19/25) | 78/84 | 1/12 | 88.9% (8/9) | 0 |
| d3_valid_trace[amarillo] | d3_amarillo | 84 | 55.0% (11/20) | 78.6% (11/14) | 72/84 | 8/12 | 44.4% (4/9) | 0 |
| d3_valid_trace[amarillo] | d3_d3 | 84 | 60.0% (12/20) | 66.7% (12/18) | 71/84 | 7/12 | 44.4% (4/9) | 0 |
| test_generado | base_d3 | 156 | 56.0% (191/341) | 15.5% (191/1234) | 1/156 | 33/58 | 36.7% (11/30) | 44 |
| test_generado | d3_d3 | 156 | 88.3% (301/341) | 95.6% (301/315) | 111/156 | 29/58 | 50.0% (15/30) | 0 |
| test_generado | d4_d3 | 156 | 80.9% (276/341) | 90.2% (276/306) | 122/156 | 6/58 | 93.3% (28/30) | 0 |
| valid_generado[amarillo] | ckpt_r1_1000 | 73 | 78.7% (37/47) | 86.0% (37/43) | 58/73 | 5/33 | 87.5% (14/16) | 0 |
| valid_generado[amarillo] | ckpt_r2_0670 | 73 | 91.5% (43/47) | 81.1% (43/53) | 61/73 | 3/33 | 100.0% (16/16) | 0 |
| valid_generado[amarillo] | ckpt_r2_final | 73 | 93.6% (44/47) | 80.0% (44/55) | 61/73 | 3/33 | 100.0% (16/16) | 0 |
| valid_generado[amarillo] | d3_amarillo | 73 | 68.1% (32/47) | 88.9% (32/36) | 54/73 | 12/33 | 81.2% (13/16) | 0 |
| valid_generado[amarillo] | d3_d3 | 73 | 72.3% (34/47) | 85.0% (34/40) | 55/73 | 9/33 | 87.5% (14/16) | 0 |

## Entrenamiento

- Rondas: finetune/logs/d4_selector_r1.log desde la iteración 0; finetune/logs/d4_selector_r2.log desde la iteración 1000.
- Pérdida de entrenamiento final 0.034; validación (iteración acumulada→pérdida): 1→0.028, 250→0.062, 500→0.040, 750→0.036, 1000→0.030, 1001→0.030, 1335→0.032, 1670→0.030, 2005→0.027, 2340→0.026.
- Pico de memoria 5.6 GB; tokens entrenados 219907.
- Curva: `results/d4/loss_d4_selector.png`.

## Fallos · D1 · prompting directo (reproducido)

- Karma: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Malzahar, Xerath, Xerath, Ryze, None, Ryze, None, Ryze.
- Zoe: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Kai'Sa, Kassadin, Malzahar, Kai'Sa, Kassadin, Kassadin, Malzahar.
- Nocturne: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Kassadin, None, Kassadin, Kassadin, Kog'Maw, Kassadin.
- Veigar: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Malzahar, Xerath, Azir, Kassadin, Malzahar, Kai'Sa, None.
- LeBlanc: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kassadin, Azir, Kassadin, Malzahar, None, None, Malzahar, Malzahar.
- Morgana: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Kog'Maw, Vel'Koz, None, None, None, None, None.
- Thresh: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Vel'Koz, None, None, Vel'Koz, None, None.
- Ashe: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kai'Sa, Kog'Maw, None, Kog'Maw, Kog'Maw, None, Vel'Koz, None.
- Zilean: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Vel'Koz, Vel'Koz, Vel'Koz, Urgot, Urgot, None.
- Xin Zhao: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Kha'Zix, Rengar, Zaahen, None, Zaahen, Zaahen, Nasus.
- Tryndamere: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Varus, Nasus, Zaahen, Garen, Rengar, Riven, Fiora.
- Pantheon: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Kha'Zix, Rengar, Zaahen, Zaahen, K'Sante, None, K'Sante.
- Vladimir: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Vel'Koz, None, Kog'Maw, Vel'Koz, None, Kog'Maw, None.
- Lissandra: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Kai'Sa, Kassadin, Malzahar, Kai'Sa, Kassadin, Kassadin, Malzahar.
- Elise: 10 jugadas; 10 intentos agotados; Kassadin, Urgot, Urgot, Urgot, Urgot, Twisted Fate, Twitch, Twitch, Twitch, Twitch.
- Ekko: 10 jugadas; 10 intentos agotados; Kassadin, Azir, Nasus, Zaahen, None, None, Zaahen, Garen, None, None.
- Briar: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kai'Sa, Kog'Maw, Rek'Sai, Kai'Sa, Rek'Sai, None, Kai'Sa, Kog'Maw.
- Mordekaiser: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Varus, Nasus, Zaahen, Rengar, K'Sante, Kai'Sa, None.
- Diana: 10 jugadas; 10 intentos agotados; Kassadin, Azir, Nasus, Zaahen, None, None, K'Sante, Garen, Garen, Zaahen.
- Aatrox: 10 jugadas; 10 intentos agotados; Kassadin, Urgot, Singed, Zaahen, Zaahen, Zaahen, Zaahen, Nasus, None, None.
- Zeri: 10 jugadas; 10 intentos agotados; Kassadin, Urgot, Urgot, Urgot, Urgot, Twisted Fate, Twitch, Twitch, Twitch, Twitch.
- Zac: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, Kassadin, Rek'Sai, Kha'Zix, None, Kha'Zix, Kha'Zix.
- Xerath: 10 jugadas; 10 intentos agotados; Kassadin, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot.
- Kog'Maw: 10 jugadas; 10 intentos agotados; Kassadin, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot, Urgot.
- Dr. Mundo: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Varus, Nasus, Zaahen, None, None, Zaahen, Zaahen.
- Jhin: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Vel'Koz, None, None, None, Kassadin, None, None.
- Soraka: 10 jugadas; 10 intentos agotados; Kassadin, Malzahar, Kai'Sa, Kog'Maw, Vel'Koz, None, Vel'Koz, Vel'Koz, None, Vel'Koz.
- Ezreal: 10 jugadas; 10 intentos agotados; Kassadin, Kai'Sa, Kog'Maw, Veigar, Varus, Draven, Jayce, Jayce, Jayce, Jayce.

## Fallos · D2 · LoRA sin agentes (reproducido)

- Karma: 10 jugadas; 10 intentos agotados; Aatrox, Ahri, LeBlanc, Lux, Syndra, Lux, Syndra, LeBlanc, LeBlanc, Lux.
- Samira: 10 jugadas; 10 intentos agotados; Aatrox, Kalista, Mel, Xayah, Zeri, Neeko, Renata Glasc, Xayah, None, Kai'Sa.
- Nocturne: 10 jugadas; 10 intentos agotados; Aatrox, Akali, Diana, Leona, Sejuani, Vi, Sejuani, Vi, Sejuani, Vi.
- Morgana: 10 jugadas; 10 intentos agotados; Aatrox, Ahri, Ashe, Nidalee, Nidalee, Nidalee, Ashe, Nidalee, Nidalee, Nidalee.
- Zilean: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Twitch, Fiddlesticks, Twitch, Twitch, Twitch, Twitch, Twitch, Twitch.
- Tryndamere: 10 jugadas; 10 intentos agotados; Aatrox, Darius, Garen, Garen, Garen, Garen, Garen, Garen, Garen, Garen.
- Pantheon: 10 jugadas; 10 intentos agotados; Aatrox, Blitzcrank, Darius, Fizz, Lee Sin, Master Yi, Gragas, Gragas, Gragas, Alistar.
- Vladimir: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Draven, Viktor, Swain, Swain, Swain, LeBlanc, Urgot, Viktor.
- Mordekaiser: 10 jugadas; 10 intentos agotados; Aatrox, Darius, Garen, Gragas, Garen, Garen, Garen, Garen, Garen, Garen.
- Zac: 10 jugadas; 10 intentos agotados; Aatrox, Yasuo, Yasuo, Yasuo, Lucian, Yasuo, Yasuo, Yasuo, Yasuo, Yasuo.
- Xerath: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Draven, Graves, Viktor, Viktor, Viktor, Talon, Viktor, Viktor.
- Kog'Maw: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Draven, Ziggs, Lucian, Twitch, Varus, Ziggs, Ziggs, Ziggs.
- Dr. Mundo: 10 jugadas; 10 intentos agotados; Aatrox, Blitzcrank, Warwick, Warwick, Warwick, Warwick, Warwick, Warwick, Warwick, Warwick.
- Malzahar: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Draven, Viktor, Swain, Viktor, Swain, Viktor, Swain, Viktor.
- Soraka: 10 jugadas; 10 intentos agotados; Aatrox, Ahri, Ashe, Nidalee, Nidalee, Nidalee, Nidalee, Nidalee, Nidalee, Nidalee.
- Ezreal: 10 jugadas; 10 intentos agotados; Aatrox, Corki, Draven, Varus, Ziggs, Kog'Maw, Twitch, Kog'Maw, Karthus, Kog'Maw.

## Fallos · D3 · tres agentes (LoRA común) (reproducido)

- Samira: 2 jugadas; call_limit; Aatrox, Kai'Sa.
- Morgana: 3 jugadas; call_limit; Aatrox, Ahri, LeBlanc.
- Thresh: 2 jugadas; call_limit; Aatrox, Lucian.
- Ashe: 4 jugadas; call_limit; Aatrox, Ahri, Tristana, Nidalee.
- Soraka: 3 jugadas; call_limit; Aatrox, Ahri, Sona.

## Fallos · D4 · Selector con adaptador propio (reproducido)

- Samira: 2 jugadas; call_limit; Aatrox, Kai'Sa.
