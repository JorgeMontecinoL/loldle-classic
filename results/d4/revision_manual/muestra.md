# Muestra para revisión manual de etiquetas del Selector

40 ejemplos de `finetune/data/d4_selector/train.jsonl`, estratificados por tipo (amarillo_dificil: 20, amarillo: 8, con_candidatos: 6, vacia: 6), semilla 4242. Para cada fila marcada, el revisor comprueba a mano contra el estado (`memory`, `excluded`, `years_allowed`) si el veredicto es correcto y anota ✔ o ✘ en la columna Revisor. Las filas no marcadas se revisan sólo si el revisor lo decide.

## Ejemplo 2394 · amarillo_dificil · página 1/7 · secreto (sólo motor) Alistar

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"]}, "gray": {"resource": ["Manaless"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox, Rengar, Alistar · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Aatrox | Male · Top · Darkin · Manaless · Melee · Runeterra,Shurima · 2013 | Aatrox x excluded | |
| Ahri | Female · Middle · Vastayan · Mana · Ranged · Ionia · 2011 | Ahri x gender | |
| Akali | Female · Top,Middle · Human · Energy · Melee · Ionia · 2010 | Akali x gender | |
| Akshan | Male · Middle · Human · Mana · Ranged · Shurima · 2021 | Akshan x range_type | |
| Alistar | Male · Support · Minotaur · Mana · Melee · Noxus,Runeterra · 2009 | Alistar x excluded | |
| Ambessa | Female · Top · Human · Energy · Melee · Noxus,Piltover · 2024 | Ambessa x gender | |
| Amumu | Male · Jungle · Undead,Yordle · Mana · Melee · Shurima · 2009 | Amumu ok | |
| Anivia | Female · Middle · God,Spirit · Mana · Ranged · Freljord · 2009 | Anivia x gender | |
| Annie | Female · Middle · Human,Magicborn · Mana · Ranged · Noxus,Runeterra · 2009 | Annie x gender | |
| Aphelios | Male · Bottom · Human,Spiritualist · Mana · Ranged · Targon · 2019 | Aphelios x range_type | |
| Ashe | Female · Bottom,Support · Human,Iceborn · Mana · Ranged · Freljord · 2009 | Ashe x gender | |
| Aurelion Sol | Male · Middle · Celestial,Dragon · Mana · Ranged · Runeterra,Targon · 2016 | Aurelion Sol x range_type | |
| Aurora | Female · Top,Middle · Vastayan · Mana · Ranged · Freljord · 2024 | Aurora x gender | |
| Azir | Male · Middle · God-Warrior · Mana · Ranged · Shurima · 2014 | Azir x range_type | |
| Bard | Male · Support · Celestial · Mana · Ranged · Runeterra · 2015 | Bard x range_type | |
| Bel'Veth | Female · Jungle · Void-Being · Manaless · Melee · Void · 2022 | Bel'Veth x gender | |
| Blitzcrank | Male · Support · Golem · Mana · Melee · Zaun · 2009 | Blitzcrank x regions | |
| Brand | Male · Jungle,Middle,Support · Human,Magically Altered · Mana · Ranged · Freljord,Runeterra · 2011 | Brand x range_type | |
| Braum | Male · Support · Human,Iceborn · Mana · Melee · Freljord · 2014 | Braum x regions | |
| Briar | Female · Jungle · Golem · Health costs · Melee · Noxus · 2023 | Briar x gender | |
| Caitlyn | Female · Bottom · Human · Mana · Ranged · Piltover · 2011 | Caitlyn x gender | |
| Camille | Female · Top · Cyborg,Human · Mana · Melee · Piltover · 2016 | Camille x gender | |
| Cassiopeia | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus,Shurima · 2010 | Cassiopeia x gender | |
| Cho'Gath | Other · Top · Void-Being · Mana · Melee · Void · 2009 | Cho'Gath x gender | |
| Corki | Male · Middle · Yordle · Mana · Ranged · Bandle City,Piltover · 2009 | Corki x range_type | |

candidates: Amumu

## Ejemplo 1183 · amarillo_dificil · página 4/7 · secreto (sólo motor) Nidalee

Estado: `{"green": {"gender": ["Female"], "resource": ["Mana"], "regions": ["Ixtal"], "range_type": ["Ranged"]}, "gray": {"range_type": ["Melee"], "positions": ["Middle", "Support"], "species": ["God-Warrior", "Vastayan"], "gender": ["Male"], "regions": ["Shurima"]}, "yellow": {"positions": [["Jungle", "Middle"]], "species": [["Human", "Magicborn"]]}, "year": {"lt": 2014}, "used": ["Qiyana", "Neeko", "Azir"]}`  
Excluidos: Qiyana, Neeko, Azir · years_allowed: [2009, 2010, 2011, 2012, 2013]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Lucian | Male · Bottom · Human · Mana · Ranged · Demacia,Shadow Isles · 2013 | Lucian x gender | |
| Lulu | Female · Support · Yordle · Mana · Ranged · Bandle City · 2012 | Lulu x regions | |
| Lux | Female · Middle,Support · Human,Magicborn · Mana · Ranged · Demacia · 2010 | Lux x regions | |
| Malphite | Male · Top · Golem · Mana · Melee · Ixtal,Shurima · 2009 | Malphite x gender | |
| Malzahar | Male · Middle · Human,Void-Being · Mana · Ranged · Shurima,Void · 2010 | Malzahar x gender | |
| Maokai | Male · Support · Spirit · Mana · Melee · Shadow Isles · 2011 | Maokai x gender | |
| Master Yi | Male · Jungle · Human,Spiritualist · Mana · Melee · Ionia · 2009 | Master Yi x gender | |
| Mel | Female · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus,Piltover · 2025 | Mel x regions | |
| Milio | Male · Support · Human,Magicborn · Mana · Ranged · Ixtal · 2023 | Milio x gender | |
| Miss Fortune | Female · Bottom · Human · Mana · Ranged · Bilgewater · 2010 | Miss Fortune x regions | |
| Mordekaiser | Male · Top · Revenant · Shield · Melee · Noxus,Shadow Isles · 2010 | Mordekaiser x gender | |
| Morgana | Female · Middle,Support · Aspect,Human,Magically Altered · Mana · Ranged · Demacia,Targon · 2009 | Morgana x regions | |
| Naafiri | Female · Jungle,Middle · Darkin,Dog · Mana · Melee · Shurima · 2023 | Naafiri x regions | |
| Nami | Female · Support · Vastayan · Mana · Ranged · Bilgewater,Runeterra · 2012 | Nami x regions | |
| Nasus | Male · Top · God-Warrior · Mana · Melee · Shurima · 2009 | Nasus x gender | |
| Nautilus | Male · Support · Revenant · Mana · Melee · Bilgewater · 2012 | Nautilus x gender | |
| Neeko | Female · Middle,Support · Vastayan · Mana · Ranged · Ixtal · 2018 | Neeko x excluded | |
| Nidalee | Female · Jungle · Human,Spiritualist · Mana · Ranged · Ixtal · 2009 | Nidalee ok | |
| Nilah | Female · Bottom · Human,Magically Altered · Mana · Melee · Bilgewater · 2022 | Nilah x regions | |
| Nocturne | Other · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2011 | Nocturne x gender | |
| Nunu & Willump | Male · Jungle · Human,Yeti · Mana · Melee · Freljord · 2009 | Nunu & Willump x gender | |
| Olaf | Male · Top · Human,Iceborn · Mana · Melee · Freljord · 2010 | Olaf x gender | |
| Orianna | Female · Middle · Golem · Mana · Ranged · Piltover · 2011 | Orianna x regions | |
| Ornn | Male · Top · God,Spirit · Mana · Melee · Freljord · 2017 | Ornn x gender | |
| Pantheon | Male · Top,Jungle,Support · Aspect,Human · Mana · Melee · Targon · 2010 | Pantheon x gender | |

candidates: Nidalee

## Ejemplo 364 · amarillo_dificil · página 6/7 · secreto (sólo motor) Varus

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Ranged"], "positions": ["Bottom"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Jungle", "Middle", "Support", "Top"], "gender": ["Female"], "species": ["Golem"], "regions": ["Noxus", "Piltover"]}, "yellow": {"species": [["Darkin"], ["Human", "Magically Altered"], ["Human"]], "regions": [["Runeterra", "Shurima"], ["Freljord", "Runeterra"]]}, "year": {"eq": 2012, "gt": 2011, "lt": 2013}, "used": ["Aatrox", "Brand", "Orianna", "Draven"]}`  
Excluidos: Aatrox, Brand, Orianna, Draven · years_allowed: [2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x range_type | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x regions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x positions | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x range_type | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x range_type | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x range_type | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x range_type | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x positions | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x positions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x range_type | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x positions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x species | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x range_type | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x positions | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus ok | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x positions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x positions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Varus

## Ejemplo 66 · amarillo_dificil · página 3/7 · secreto (sólo motor) Jax

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "species": ["Darkin", "Human", "Minotaur", "Undead", "Yordle"], "positions": ["Support"], "regions": ["Bilgewater"]}, "yellow": {"positions": [["Top"], ["Jungle"]], "regions": [["Runeterra", "Shurima"], ["Noxus", "Runeterra"], ["Shurima"]]}, "year": {"eq": 2009, "lt": 2013}, "used": ["Aatrox", "Alistar", "Amumu", "Gangplank"]}`  
Excluidos: Aatrox, Alistar, Amumu, Gangplank · years_allowed: [2009]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV x species | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax ok | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x range_type | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x range_type | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x gender | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x species | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x gender | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x gender | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x gender | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus x range_type | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x species | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x gender | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x gender | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x species | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x range_type | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x positions | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x gender | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x resource | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x range_type | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x gender | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x resource | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona x gender | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x gender | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x gender | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x species | |

candidates: Jax

## Ejemplo 1699 · amarillo_dificil · página 6/7 · secreto (sólo motor) Varus

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Ranged"], "positions": ["Bottom"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Jungle", "Middle", "Support", "Top"], "regions": ["Noxus"]}, "yellow": {"species": [["Darkin"], ["Human", "Magically Altered"], ["Human"]], "regions": [["Runeterra", "Shurima"], ["Freljord", "Runeterra"]]}, "year": {"eq": 2012, "gt": 2011, "lt": 2013}, "used": ["Aatrox", "Brand", "Draven"]}`  
Excluidos: Aatrox, Brand, Draven · years_allowed: [2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x range_type | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x regions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x positions | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x range_type | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x range_type | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x range_type | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x range_type | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x positions | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x positions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x range_type | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x positions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x species | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x range_type | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x positions | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus ok | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x positions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x positions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Varus

## Ejemplo 1119 · amarillo_dificil · página 5/7 · secreto (sólo motor) Rammus

Estado: `{"green": {"resource": ["Mana"], "gender": ["Male"], "range_type": ["Melee"], "regions": ["Shurima"]}, "gray": {"gender": ["Female"], "range_type": ["Ranged"], "positions": ["Support"], "species": ["God-Warrior", "Human", "Plant", "Undead", "Yordle"], "regions": ["Ixtal"]}, "yellow": {"positions": [["Jungle"], ["Top"]]}, "year": {"eq": 2009, "lt": 2012}, "used": ["Zyra", "Amumu", "Nasus"]}`  
Excluidos: Zyra, Amumu, Nasus · years_allowed: [2009]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Poppy | Female · Top,Jungle · Yordle · Mana · Melee · Demacia · 2010 | Poppy x gender | |
| Pyke | Male · Support · Revenant · Mana · Melee · Bilgewater · 2018 | Pyke x regions | |
| Qiyana | Female · Jungle,Middle · Human,Magicborn · Mana · Melee · Ixtal · 2019 | Qiyana x gender | |
| Quinn | Female · Top · Human · Mana · Ranged · Demacia · 2013 | Quinn x gender | |
| Rakan | Male · Support · Vastayan · Mana · Melee · Ionia · 2017 | Rakan x regions | |
| Rammus | Male · Top,Jungle · Unknown · Mana · Melee · Shurima · 2009 | Rammus ok | |
| Rek'Sai | Female · Jungle · Void-Being · Rage · Melee · Shurima,Void · 2014 | Rek'Sai x resource | |
| Rell | Female · Support · Human,Magically Altered,Magicborn · Mana · Melee · Noxus · 2020 | Rell x gender | |
| Renata Glasc | Female · Support · Chemically Altered,Human · Mana · Ranged · Zaun · 2022 | Renata Glasc x gender | |
| Renekton | Male · Top · God-Warrior · Fury · Melee · Shurima · 2011 | Renekton x resource | |
| Rengar | Male · Jungle · Vastayan · Ferocity · Melee · Ixtal,Shurima · 2012 | Rengar x resource | |
| Riven | Female · Top · Human · Manaless · Melee · Ionia,Noxus · 2011 | Riven x resource | |
| Rumble | Male · Top · Yordle · Heat · Melee · Bandle City · 2011 | Rumble x resource | |
| Ryze | Male · Middle · Human,Magically Altered · Mana · Ranged · Runeterra · 2009 | Ryze x range_type | |
| Samira | Female · Bottom · Human · Mana · Ranged · Noxus,Shurima · 2020 | Samira x gender | |
| Sejuani | Female · Jungle · Human,Iceborn · Mana · Melee · Freljord · 2012 | Sejuani x gender | |
| Senna | Female · Bottom,Support · Human,Undead · Mana · Ranged · Shadow Isles · 2019 | Senna x gender | |
| Seraphine | Female · Bottom,Support · Human,Magicborn · Mana · Ranged · Piltover,Zaun · 2020 | Seraphine x gender | |
| Sett | Male · Top · Human,Vastayan · Grit · Melee · Ionia · 2020 | Sett x resource | |
| Shaco | Male · Jungle · Spirit · Mana · Melee · Runeterra · 2009 | Shaco x regions | |
| Shen | Male · Top · Human,Spiritualist · Energy · Melee · Ionia · 2010 | Shen x resource | |
| Shyvana | Female · Jungle · Dragon,Magically Altered · Fury · Melee · Demacia · 2011 | Shyvana x resource | |
| Singed | Male · Top · Chemically Altered,Human · Mana · Melee · Piltover,Zaun · 2009 | Singed x regions | |
| Sion | Male · Top · Revenant · Mana · Melee · Noxus · 2009 | Sion x regions | |
| Sivir | Female · Bottom · Human · Mana · Ranged · Shurima · 2009 | Sivir x gender | |

candidates: Rammus

## Ejemplo 1081 · amarillo_dificil · página 5/7 · secreto (sólo motor) Alistar

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"]}, "gray": {"resource": ["Manaless"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"eq": null, "gt": null, "lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Poppy | Female · Top,Jungle · Yordle · Mana · Melee · Demacia · 2010 | Poppy x gender | |
| Pyke | Male · Support · Revenant · Mana · Melee · Bilgewater · 2018 | Pyke x regions | |
| Qiyana | Female · Jungle,Middle · Human,Magicborn · Mana · Melee · Ixtal · 2019 | Qiyana x gender | |
| Quinn | Female · Top · Human · Mana · Ranged · Demacia · 2013 | Quinn x gender | |
| Rakan | Male · Support · Vastayan · Mana · Melee · Ionia · 2017 | Rakan x regions | |
| Rammus | Male · Top,Jungle · Unknown · Mana · Melee · Shurima · 2009 | Rammus x positions | |
| Rek'Sai | Female · Jungle · Void-Being · Rage · Melee · Shurima,Void · 2014 | Rek'Sai x gender | |
| Rell | Female · Support · Human,Magically Altered,Magicborn · Mana · Melee · Noxus · 2020 | Rell x gender | |
| Renata Glasc | Female · Support · Chemically Altered,Human · Mana · Ranged · Zaun · 2022 | Renata Glasc x gender | |
| Renekton | Male · Top · God-Warrior · Fury · Melee · Shurima · 2011 | Renekton x positions | |
| Rengar | Male · Jungle · Vastayan · Ferocity · Melee · Ixtal,Shurima · 2012 | Rengar ok | |
| Riven | Female · Top · Human · Manaless · Melee · Ionia,Noxus · 2011 | Riven x gender | |
| Rumble | Male · Top · Yordle · Heat · Melee · Bandle City · 2011 | Rumble x positions | |
| Ryze | Male · Middle · Human,Magically Altered · Mana · Ranged · Runeterra · 2009 | Ryze x range_type | |
| Samira | Female · Bottom · Human · Mana · Ranged · Noxus,Shurima · 2020 | Samira x gender | |
| Sejuani | Female · Jungle · Human,Iceborn · Mana · Melee · Freljord · 2012 | Sejuani x gender | |
| Senna | Female · Bottom,Support · Human,Undead · Mana · Ranged · Shadow Isles · 2019 | Senna x gender | |
| Seraphine | Female · Bottom,Support · Human,Magicborn · Mana · Ranged · Piltover,Zaun · 2020 | Seraphine x gender | |
| Sett | Male · Top · Human,Vastayan · Grit · Melee · Ionia · 2020 | Sett x positions | |
| Shaco | Male · Jungle · Spirit · Mana · Melee · Runeterra · 2009 | Shaco ok | |
| Shen | Male · Top · Human,Spiritualist · Energy · Melee · Ionia · 2010 | Shen x positions | |
| Shyvana | Female · Jungle · Dragon,Magically Altered · Fury · Melee · Demacia · 2011 | Shyvana x gender | |
| Singed | Male · Top · Chemically Altered,Human · Mana · Melee · Piltover,Zaun · 2009 | Singed x positions | |
| Sion | Male · Top · Revenant · Mana · Melee · Noxus · 2009 | Sion x positions | |
| Sivir | Female · Bottom · Human · Mana · Ranged · Shurima · 2009 | Sivir x gender | |

candidates: Rengar, Shaco

## Ejemplo 881 · amarillo_dificil · página 6/7 · secreto (sólo motor) Swain

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Ranged"], "regions": ["Noxus"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Bottom", "Top"], "species": ["Darkin", "Yordle"], "regions": ["Bandle City", "Piltover", "Runeterra", "Shurima"]}, "yellow": {"positions": [["Middle"]], "species": [["Human"]]}, "year": {"gt": 2009, "lt": 2012}, "used": ["Aatrox", "Corki", "Draven"]}`  
Excluidos: Aatrox, Corki, Draven · years_allowed: [2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x range_type | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x regions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain ok | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x range_type | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x range_type | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x range_type | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x range_type | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x regions | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x regions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x range_type | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x regions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x regions | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x range_type | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x regions | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x regions | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x regions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x regions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Swain

## Ejemplo 741 · amarillo_dificil · página 1/7 · secreto (sólo motor) Akshan

Estado: `{"green": {"gender": ["Male"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"eq": null, "gt": 2013, "lt": null}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Aatrox | Male · Top · Darkin · Manaless · Melee · Runeterra,Shurima · 2013 | Aatrox x excluded | |
| Ahri | Female · Middle · Vastayan · Mana · Ranged · Ionia · 2011 | Ahri x gender | |
| Akali | Female · Top,Middle · Human · Energy · Melee · Ionia · 2010 | Akali x gender | |
| Akshan | Male · Middle · Human · Mana · Ranged · Shurima · 2021 | Akshan ok | |
| Alistar | Male · Support · Minotaur · Mana · Melee · Noxus,Runeterra · 2009 | Alistar x range_type | |
| Ambessa | Female · Top · Human · Energy · Melee · Noxus,Piltover · 2024 | Ambessa x gender | |
| Amumu | Male · Jungle · Undead,Yordle · Mana · Melee · Shurima · 2009 | Amumu x range_type | |
| Anivia | Female · Middle · God,Spirit · Mana · Ranged · Freljord · 2009 | Anivia x gender | |
| Annie | Female · Middle · Human,Magicborn · Mana · Ranged · Noxus,Runeterra · 2009 | Annie x gender | |
| Aphelios | Male · Bottom · Human,Spiritualist · Mana · Ranged · Targon · 2019 | Aphelios x regions | |
| Ashe | Female · Bottom,Support · Human,Iceborn · Mana · Ranged · Freljord · 2009 | Ashe x gender | |
| Aurelion Sol | Male · Middle · Celestial,Dragon · Mana · Ranged · Runeterra,Targon · 2016 | Aurelion Sol ok | |
| Aurora | Female · Top,Middle · Vastayan · Mana · Ranged · Freljord · 2024 | Aurora x gender | |
| Azir | Male · Middle · God-Warrior · Mana · Ranged · Shurima · 2014 | Azir ok | |
| Bard | Male · Support · Celestial · Mana · Ranged · Runeterra · 2015 | Bard ok | |
| Bel'Veth | Female · Jungle · Void-Being · Manaless · Melee · Void · 2022 | Bel'Veth x gender | |
| Blitzcrank | Male · Support · Golem · Mana · Melee · Zaun · 2009 | Blitzcrank x range_type | |
| Brand | Male · Jungle,Middle,Support · Human,Magically Altered · Mana · Ranged · Freljord,Runeterra · 2011 | Brand x release_year | |
| Braum | Male · Support · Human,Iceborn · Mana · Melee · Freljord · 2014 | Braum x range_type | |
| Briar | Female · Jungle · Golem · Health costs · Melee · Noxus · 2023 | Briar x gender | |
| Caitlyn | Female · Bottom · Human · Mana · Ranged · Piltover · 2011 | Caitlyn x gender | |
| Camille | Female · Top · Cyborg,Human · Mana · Melee · Piltover · 2016 | Camille x gender | |
| Cassiopeia | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus,Shurima · 2010 | Cassiopeia x gender | |
| Cho'Gath | Other · Top · Void-Being · Mana · Melee · Void · 2009 | Cho'Gath x gender | |
| Corki | Male · Middle · Yordle · Mana · Ranged · Bandle City,Piltover · 2009 | Corki x regions | |

candidates: Akshan, Aurelion Sol, Azir, Bard

## Ejemplo 508 · amarillo_dificil · página 6/7 · secreto (sólo motor) Tahm Kench

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "species": ["Darkin", "Human", "Iceborn", "Revenant", "Vastayan"], "regions": ["Freljord", "Ionia"]}, "yellow": {"positions": [["Top"], ["Support"]], "regions": [["Runeterra", "Shurima"], ["Bilgewater"]]}, "year": {"gt": 2014, "lt": 2017}, "used": ["Aatrox", "Braum", "Pyke", "Rakan"]}`  
Excluidos: Aatrox, Braum, Pyke, Rakan · years_allowed: [2015, 2016]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x positions | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x range_type | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x range_type | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x species | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench ok | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x species | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x species | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x range_type | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x range_type | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x species | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x range_type | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x range_type | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x species | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x range_type | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x range_type | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x range_type | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x range_type | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Tahm Kench

## Ejemplo 1461 · amarillo_dificil · página 4/7 · secreto (sólo motor) Naafiri

Estado: `{"green": {"range_type": ["Melee"], "gender": ["Female"]}, "gray": {"gender": ["Male"], "resource": ["Health costs", "Manaless"], "positions": ["Top"], "species": ["Golem"], "regions": ["Noxus"]}, "yellow": {"species": [["Darkin"]], "regions": [["Runeterra", "Shurima"]], "positions": [["Jungle"]]}, "year": {"eq": 2023, "gt": 2013, "lt": null}, "used": ["Aatrox", "Briar"]}`  
Excluidos: Aatrox, Briar · years_allowed: [2023]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Lucian | Male · Bottom · Human · Mana · Ranged · Demacia,Shadow Isles · 2013 | Lucian x range_type | |
| Lulu | Female · Support · Yordle · Mana · Ranged · Bandle City · 2012 | Lulu x range_type | |
| Lux | Female · Middle,Support · Human,Magicborn · Mana · Ranged · Demacia · 2010 | Lux x range_type | |
| Malphite | Male · Top · Golem · Mana · Melee · Ixtal,Shurima · 2009 | Malphite x gender | |
| Malzahar | Male · Middle · Human,Void-Being · Mana · Ranged · Shurima,Void · 2010 | Malzahar x range_type | |
| Maokai | Male · Support · Spirit · Mana · Melee · Shadow Isles · 2011 | Maokai x gender | |
| Master Yi | Male · Jungle · Human,Spiritualist · Mana · Melee · Ionia · 2009 | Master Yi x gender | |
| Mel | Female · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus,Piltover · 2025 | Mel x range_type | |
| Milio | Male · Support · Human,Magicborn · Mana · Ranged · Ixtal · 2023 | Milio x range_type | |
| Miss Fortune | Female · Bottom · Human · Mana · Ranged · Bilgewater · 2010 | Miss Fortune x range_type | |
| Mordekaiser | Male · Top · Revenant · Shield · Melee · Noxus,Shadow Isles · 2010 | Mordekaiser x gender | |
| Morgana | Female · Middle,Support · Aspect,Human,Magically Altered · Mana · Ranged · Demacia,Targon · 2009 | Morgana x range_type | |
| Naafiri | Female · Jungle,Middle · Darkin,Dog · Mana · Melee · Shurima · 2023 | Naafiri ok | |
| Nami | Female · Support · Vastayan · Mana · Ranged · Bilgewater,Runeterra · 2012 | Nami x range_type | |
| Nasus | Male · Top · God-Warrior · Mana · Melee · Shurima · 2009 | Nasus x gender | |
| Nautilus | Male · Support · Revenant · Mana · Melee · Bilgewater · 2012 | Nautilus x gender | |
| Neeko | Female · Middle,Support · Vastayan · Mana · Ranged · Ixtal · 2018 | Neeko x range_type | |
| Nidalee | Female · Jungle · Human,Spiritualist · Mana · Ranged · Ixtal · 2009 | Nidalee x range_type | |
| Nilah | Female · Bottom · Human,Magically Altered · Mana · Melee · Bilgewater · 2022 | Nilah x species | |
| Nocturne | Other · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2011 | Nocturne x gender | |
| Nunu & Willump | Male · Jungle · Human,Yeti · Mana · Melee · Freljord · 2009 | Nunu & Willump x gender | |
| Olaf | Male · Top · Human,Iceborn · Mana · Melee · Freljord · 2010 | Olaf x gender | |
| Orianna | Female · Middle · Golem · Mana · Ranged · Piltover · 2011 | Orianna x range_type | |
| Ornn | Male · Top · God,Spirit · Mana · Melee · Freljord · 2017 | Ornn x gender | |
| Pantheon | Male · Top,Jungle,Support · Aspect,Human · Mana · Melee · Targon · 2010 | Pantheon x gender | |

candidates: Naafiri

## Ejemplo 1395 · amarillo_dificil · página 5/7 · secreto (sólo motor) Janna

Estado: `{"green": {}, "gray": {"gender": ["Male"], "resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Poppy | Female · Top,Jungle · Yordle · Mana · Melee · Demacia · 2010 | Poppy x range_type | |
| Pyke | Male · Support · Revenant · Mana · Melee · Bilgewater · 2018 | Pyke x gender | |
| Qiyana | Female · Jungle,Middle · Human,Magicborn · Mana · Melee · Ixtal · 2019 | Qiyana x range_type | |
| Quinn | Female · Top · Human · Mana · Ranged · Demacia · 2013 | Quinn x positions | |
| Rakan | Male · Support · Vastayan · Mana · Melee · Ionia · 2017 | Rakan x gender | |
| Rammus | Male · Top,Jungle · Unknown · Mana · Melee · Shurima · 2009 | Rammus x gender | |
| Rek'Sai | Female · Jungle · Void-Being · Rage · Melee · Shurima,Void · 2014 | Rek'Sai x range_type | |
| Rell | Female · Support · Human,Magically Altered,Magicborn · Mana · Melee · Noxus · 2020 | Rell x range_type | |
| Renata Glasc | Female · Support · Chemically Altered,Human · Mana · Ranged · Zaun · 2022 | Renata Glasc x regions | |
| Renekton | Male · Top · God-Warrior · Fury · Melee · Shurima · 2011 | Renekton x gender | |
| Rengar | Male · Jungle · Vastayan · Ferocity · Melee · Ixtal,Shurima · 2012 | Rengar x gender | |
| Riven | Female · Top · Human · Manaless · Melee · Ionia,Noxus · 2011 | Riven x resource | |
| Rumble | Male · Top · Yordle · Heat · Melee · Bandle City · 2011 | Rumble x gender | |
| Ryze | Male · Middle · Human,Magically Altered · Mana · Ranged · Runeterra · 2009 | Ryze x gender | |
| Samira | Female · Bottom · Human · Mana · Ranged · Noxus,Shurima · 2020 | Samira x release_year | |
| Sejuani | Female · Jungle · Human,Iceborn · Mana · Melee · Freljord · 2012 | Sejuani x range_type | |
| Senna | Female · Bottom,Support · Human,Undead · Mana · Ranged · Shadow Isles · 2019 | Senna x regions | |
| Seraphine | Female · Bottom,Support · Human,Magicborn · Mana · Ranged · Piltover,Zaun · 2020 | Seraphine x regions | |
| Sett | Male · Top · Human,Vastayan · Grit · Melee · Ionia · 2020 | Sett x gender | |
| Shaco | Male · Jungle · Spirit · Mana · Melee · Runeterra · 2009 | Shaco x gender | |
| Shen | Male · Top · Human,Spiritualist · Energy · Melee · Ionia · 2010 | Shen x gender | |
| Shyvana | Female · Jungle · Dragon,Magically Altered · Fury · Melee · Demacia · 2011 | Shyvana x range_type | |
| Singed | Male · Top · Chemically Altered,Human · Mana · Melee · Piltover,Zaun · 2009 | Singed x gender | |
| Sion | Male · Top · Revenant · Mana · Melee · Noxus · 2009 | Sion x gender | |
| Sivir | Female · Bottom · Human · Mana · Ranged · Shurima · 2009 | Sivir ok | |

candidates: Sivir

## Ejemplo 53 · amarillo_dificil · página 2/7 · secreto (sólo motor) Irelia

Estado: `{"green": {"range_type": ["Melee"], "gender": ["Female"], "positions": ["Middle", "Top"], "regions": ["Ionia"]}, "gray": {"gender": ["Male"], "resource": ["Energy", "Manaless"], "species": ["Darkin"], "regions": ["Runeterra", "Shurima"]}, "yellow": {"positions": [["Top"]], "species": [["Human"]]}, "year": {"eq": 2010, "gt": null, "lt": 2013}, "used": ["Aatrox", "Akali"]}`  
Excluidos: Aatrox, Akali · years_allowed: [2010]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x gender | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x positions | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x gender | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x range_type | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x gender | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x range_type | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x positions | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x range_type | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x range_type | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x positions | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x gender | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x gender | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x gender | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x gender | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x range_type | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x gender | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x range_type | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x positions | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x gender | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x range_type | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x range_type | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x positions | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia ok | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x gender | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x range_type | |

candidates: Irelia

## Ejemplo 2251 · amarillo_dificil · página 6/7 · secreto (sólo motor) Vex

Estado: `{"green": {"gender": ["Female"], "resource": ["Mana"], "range_type": ["Ranged"]}, "gray": {"positions": ["Bottom"], "species": ["Chemically Altered", "Human", "Vastayan"], "regions": ["Freljord", "Ionia", "Zaun"]}, "yellow": {"positions": [["Middle", "Top"]]}, "year": {"eq": null, "gt": 2017, "lt": 2024}, "used": ["Jinx", "Aurora", "Xayah"]}`  
Excluidos: Jinx, Aurora, Xayah · years_allowed: [2018, 2019, 2020, 2021, 2022, 2023]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x gender | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x gender | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x species | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x regions | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x gender | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x gender | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x species | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x gender | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x species | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x gender | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x gender | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x gender | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x gender | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x positions | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x gender | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x gender | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x gender | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x gender | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x gender | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x gender | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x gender | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x positions | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x gender | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x gender | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex ok | |

candidates: Vex

## Ejemplo 1332 · amarillo_dificil · página 7/7 · secreto (sólo motor) Brand

Estado: `{"green": {"gender": ["Male"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Vi | Female · Jungle · Human · Mana · Melee · Piltover,Zaun · 2012 | Vi x gender | |
| Viego | Male · Jungle · Undead · Manaless · Melee · Camavor,Shadow Isles · 2021 | Viego x resource | |
| Viktor | Male · Middle · Cyborg,Human · Mana · Ranged · Piltover,Zaun · 2011 | Viktor x regions | |
| Vladimir | Male · Middle · Human,Magically Altered · Bloodthirst · Ranged · Camavor,Noxus,Shadow Isles · 2010 | Vladimir x regions | |
| Volibear | Male · Top · God,Spirit · Mana · Melee · Freljord · 2011 | Volibear x range_type | |
| Warwick | Male · Jungle · Chemically Altered,Cyborg,Human · Mana · Melee · Zaun · 2009 | Warwick x range_type | |
| Wukong | Male · Jungle · Vastayan · Mana · Melee · Ionia · 2011 | Wukong x range_type | |
| Xayah | Female · Bottom · Vastayan · Mana · Ranged · Ionia · 2017 | Xayah x gender | |
| Xerath | Male · Middle,Support · Baccai · Mana · Ranged · Shurima · 2011 | Xerath ok | |
| Xin Zhao | Male · Jungle · Human · Mana · Melee · Demacia,Ionia,Noxus · 2010 | Xin Zhao x range_type | |
| Yasuo | Male · Top,Middle,Bottom · Human,Magicborn · Flow · Melee · Ionia · 2013 | Yasuo x range_type | |
| Yone | Male · Top,Middle · Human,Magically Altered · Manaless · Melee · Ionia · 2020 | Yone x resource | |
| Yorick | Male · Top · Human,Magically Altered · Mana · Melee · Shadow Isles · 2011 | Yorick x range_type | |
| Yunara | Female · Bottom · Human · Mana · Ranged · Ionia · 2025 | Yunara x gender | |
| Yuumi | Female · Support · Cat,Magically Altered · Mana · Ranged · Bandle City · 2019 | Yuumi x gender | |
| Zaahen | Male · Top,Jungle · Darkin · Mana · Melee · Runeterra · 2025 | Zaahen x range_type | |
| Zac | Male · Jungle · Golem · Health costs · Melee · Zaun · 2013 | Zac x range_type | |
| Zed | Male · Jungle,Middle · Human,Magically Altered · Energy · Melee · Ionia · 2012 | Zed x range_type | |
| Zeri | Female · Bottom · Human,Magicborn · Mana · Ranged · Zaun · 2022 | Zeri x gender | |
| Ziggs | Male · Bottom · Yordle · Mana · Ranged · Zaun · 2012 | Ziggs x regions | |
| Zilean | Male · Support · Human,Magicborn · Mana · Ranged · Icathia,Runeterra,Shurima · 2009 | Zilean ok | |
| Zoe | Female · Middle · Aspect,Human · Mana · Ranged · Targon · 2017 | Zoe x gender | |
| Zyra | Female · Support · Human,Plant · Mana · Ranged · Ixtal · 2012 | Zyra x gender | |

candidates: Xerath, Zilean

## Ejemplo 443 · amarillo_dificil · página 3/7 · secreto (sólo motor) Teemo

Estado: `{"green": {"resource": ["Mana"], "range_type": ["Ranged"], "gender": ["Male"]}, "gray": {"gender": ["Female"], "positions": ["Middle", "Support"], "species": ["Human", "Magicborn", "Unknown"], "regions": ["Demacia", "Icathia", "Runeterra", "Shurima"], "range_type": ["Melee"]}, "yellow": {"positions": [["Jungle", "Top"]]}, "year": {"eq": 2009, "gt": null, "lt": 2010}, "used": ["Lux", "Jax"]}`  
Excluidos: Lux, Jax · years_allowed: [2009]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV x range_type | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax x excluded | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x species | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x species | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x gender | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x range_type | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x gender | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x gender | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x gender | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus ok | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x range_type | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x resource | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x range_type | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x range_type | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x resource | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x range_type | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x gender | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x resource | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x positions | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x gender | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x resource | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona x range_type | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x range_type | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x gender | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x range_type | |

candidates: Karthus

## Ejemplo 437 · amarillo_dificil · página 7/7 · secreto (sólo motor) Yorick

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "positions": ["Top"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "species": ["Darkin", "Revenant"], "regions": ["Bilgewater", "Freljord", "Piltover", "Runeterra", "Shurima"], "positions": ["Support"], "range_type": ["Ranged"]}, "yellow": {"species": [["Human"], ["Human", "Iceborn"]]}, "year": {"eq": null, "gt": 2010, "lt": 2012}, "used": ["Aatrox", "Pyke", "Jayce", "Olaf"]}`  
Excluidos: Aatrox, Pyke, Jayce, Olaf · years_allowed: [2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Vi | Female · Jungle · Human · Mana · Melee · Piltover,Zaun · 2012 | Vi x gender | |
| Viego | Male · Jungle · Undead · Manaless · Melee · Camavor,Shadow Isles · 2021 | Viego x positions | |
| Viktor | Male · Middle · Cyborg,Human · Mana · Ranged · Piltover,Zaun · 2011 | Viktor x range_type | |
| Vladimir | Male · Middle · Human,Magically Altered · Bloodthirst · Ranged · Camavor,Noxus,Shadow Isles · 2010 | Vladimir x range_type | |
| Volibear | Male · Top · God,Spirit · Mana · Melee · Freljord · 2011 | Volibear x regions | |
| Warwick | Male · Jungle · Chemically Altered,Cyborg,Human · Mana · Melee · Zaun · 2009 | Warwick x positions | |
| Wukong | Male · Jungle · Vastayan · Mana · Melee · Ionia · 2011 | Wukong x positions | |
| Xayah | Female · Bottom · Vastayan · Mana · Ranged · Ionia · 2017 | Xayah x gender | |
| Xerath | Male · Middle,Support · Baccai · Mana · Ranged · Shurima · 2011 | Xerath x range_type | |
| Xin Zhao | Male · Jungle · Human · Mana · Melee · Demacia,Ionia,Noxus · 2010 | Xin Zhao x positions | |
| Yasuo | Male · Top,Middle,Bottom · Human,Magicborn · Flow · Melee · Ionia · 2013 | Yasuo x positions | |
| Yone | Male · Top,Middle · Human,Magically Altered · Manaless · Melee · Ionia · 2020 | Yone x positions | |
| Yorick | Male · Top · Human,Magically Altered · Mana · Melee · Shadow Isles · 2011 | Yorick ok | |
| Yunara | Female · Bottom · Human · Mana · Ranged · Ionia · 2025 | Yunara x gender | |
| Yuumi | Female · Support · Cat,Magically Altered · Mana · Ranged · Bandle City · 2019 | Yuumi x gender | |
| Zaahen | Male · Top,Jungle · Darkin · Mana · Melee · Runeterra · 2025 | Zaahen x positions | |
| Zac | Male · Jungle · Golem · Health costs · Melee · Zaun · 2013 | Zac x positions | |
| Zed | Male · Jungle,Middle · Human,Magically Altered · Energy · Melee · Ionia · 2012 | Zed x positions | |
| Zeri | Female · Bottom · Human,Magicborn · Mana · Ranged · Zaun · 2022 | Zeri x gender | |
| Ziggs | Male · Bottom · Yordle · Mana · Ranged · Zaun · 2012 | Ziggs x range_type | |
| Zilean | Male · Support · Human,Magicborn · Mana · Ranged · Icathia,Runeterra,Shurima · 2009 | Zilean x range_type | |
| Zoe | Female · Middle · Aspect,Human · Mana · Ranged · Targon · 2017 | Zoe x gender | |
| Zyra | Female · Support · Human,Plant · Mana · Ranged · Ixtal · 2012 | Zyra x gender | |

candidates: Yorick

## Ejemplo 1604 · amarillo_dificil · página 7/7 · secreto (sólo motor) Vi

Estado: `{"green": {"range_type": ["Melee"], "gender": ["Female"], "resource": ["Mana"], "positions": ["Jungle"]}, "gray": {"gender": ["Male"], "resource": ["Manaless"], "positions": ["Top"], "species": ["Darkin", "Undead"], "regions": ["Camavor", "Freljord", "Runeterra", "Shadow Isles", "Shurima", "Targon"], "range_type": ["Ranged"]}, "yellow": {"positions": [["Jungle", "Middle"], ["Jungle", "Middle", "Support"]], "species": [["Aspect", "Human"], ["Human", "Magically Altered"]]}, "year": {"eq": 2012, "gt": 2011, "lt": 2013}, "used": ["Aatrox", "Diana", "Brand", "Hecarim"]}`  
Excluidos: Aatrox, Diana, Brand, Hecarim · years_allowed: [2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Vi | Female · Jungle · Human · Mana · Melee · Piltover,Zaun · 2012 | Vi ok | |
| Viego | Male · Jungle · Undead · Manaless · Melee · Camavor,Shadow Isles · 2021 | Viego x gender | |
| Viktor | Male · Middle · Cyborg,Human · Mana · Ranged · Piltover,Zaun · 2011 | Viktor x range_type | |
| Vladimir | Male · Middle · Human,Magically Altered · Bloodthirst · Ranged · Camavor,Noxus,Shadow Isles · 2010 | Vladimir x range_type | |
| Volibear | Male · Top · God,Spirit · Mana · Melee · Freljord · 2011 | Volibear x gender | |
| Warwick | Male · Jungle · Chemically Altered,Cyborg,Human · Mana · Melee · Zaun · 2009 | Warwick x gender | |
| Wukong | Male · Jungle · Vastayan · Mana · Melee · Ionia · 2011 | Wukong x gender | |
| Xayah | Female · Bottom · Vastayan · Mana · Ranged · Ionia · 2017 | Xayah x range_type | |
| Xerath | Male · Middle,Support · Baccai · Mana · Ranged · Shurima · 2011 | Xerath x range_type | |
| Xin Zhao | Male · Jungle · Human · Mana · Melee · Demacia,Ionia,Noxus · 2010 | Xin Zhao x gender | |
| Yasuo | Male · Top,Middle,Bottom · Human,Magicborn · Flow · Melee · Ionia · 2013 | Yasuo x gender | |
| Yone | Male · Top,Middle · Human,Magically Altered · Manaless · Melee · Ionia · 2020 | Yone x gender | |
| Yorick | Male · Top · Human,Magically Altered · Mana · Melee · Shadow Isles · 2011 | Yorick x gender | |
| Yunara | Female · Bottom · Human · Mana · Ranged · Ionia · 2025 | Yunara x range_type | |
| Yuumi | Female · Support · Cat,Magically Altered · Mana · Ranged · Bandle City · 2019 | Yuumi x range_type | |
| Zaahen | Male · Top,Jungle · Darkin · Mana · Melee · Runeterra · 2025 | Zaahen x gender | |
| Zac | Male · Jungle · Golem · Health costs · Melee · Zaun · 2013 | Zac x gender | |
| Zed | Male · Jungle,Middle · Human,Magically Altered · Energy · Melee · Ionia · 2012 | Zed x gender | |
| Zeri | Female · Bottom · Human,Magicborn · Mana · Ranged · Zaun · 2022 | Zeri x range_type | |
| Ziggs | Male · Bottom · Yordle · Mana · Ranged · Zaun · 2012 | Ziggs x range_type | |
| Zilean | Male · Support · Human,Magicborn · Mana · Ranged · Icathia,Runeterra,Shurima · 2009 | Zilean x range_type | |
| Zoe | Female · Middle · Aspect,Human · Mana · Ranged · Targon · 2017 | Zoe x range_type | |
| Zyra | Female · Support · Human,Plant · Mana · Ranged · Ixtal · 2012 | Zyra x range_type | |

candidates: Vi

## Ejemplo 2105 · amarillo_dificil · página 6/7 · secreto (sólo motor) Varus

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "positions": ["Bottom"], "range_type": ["Ranged"]}, "gray": {"range_type": ["Melee"], "positions": ["Support"], "regions": ["Bilgewater", "Demacia", "Noxus", "Targon"], "gender": ["Female"]}, "yellow": {"species": [["Aspect", "Human"], ["Human", "Magically Altered"], ["Human"]]}, "year": {"eq": 2012, "gt": 2009, "lt": 2022}, "used": ["Taric", "Nilah", "Draven"]}`  
Excluidos: Taric, Nilah, Draven · years_allowed: [2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x positions | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x regions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x positions | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x positions | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x positions | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x positions | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x excluded | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x positions | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x positions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x positions | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x positions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x species | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x positions | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x positions | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus ok | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x positions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x positions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Varus

## Ejemplo 1837 · amarillo_dificil · página 7/7 · secreto (sólo motor) Nunu & Willump

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "positions": ["Top"], "species": ["Darkin"], "regions": ["Bilgewater", "Runeterra", "Shurima"], "gender": ["Female"]}, "yellow": {"species": [["Human", "Spiritualist"]]}, "year": {"lt": 2013}, "used": ["Aatrox", "Illaoi"]}`  
Excluidos: Aatrox, Illaoi · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Vi | Female · Jungle · Human · Mana · Melee · Piltover,Zaun · 2012 | Vi x gender | |
| Viego | Male · Jungle · Undead · Manaless · Melee · Camavor,Shadow Isles · 2021 | Viego x resource | |
| Viktor | Male · Middle · Cyborg,Human · Mana · Ranged · Piltover,Zaun · 2011 | Viktor x range_type | |
| Vladimir | Male · Middle · Human,Magically Altered · Bloodthirst · Ranged · Camavor,Noxus,Shadow Isles · 2010 | Vladimir x range_type | |
| Volibear | Male · Top · God,Spirit · Mana · Melee · Freljord · 2011 | Volibear x positions | |
| Warwick | Male · Jungle · Chemically Altered,Cyborg,Human · Mana · Melee · Zaun · 2009 | Warwick ok | |
| Wukong | Male · Jungle · Vastayan · Mana · Melee · Ionia · 2011 | Wukong x species | |
| Xayah | Female · Bottom · Vastayan · Mana · Ranged · Ionia · 2017 | Xayah x gender | |
| Xerath | Male · Middle,Support · Baccai · Mana · Ranged · Shurima · 2011 | Xerath x range_type | |
| Xin Zhao | Male · Jungle · Human · Mana · Melee · Demacia,Ionia,Noxus · 2010 | Xin Zhao ok | |
| Yasuo | Male · Top,Middle,Bottom · Human,Magicborn · Flow · Melee · Ionia · 2013 | Yasuo x resource | |
| Yone | Male · Top,Middle · Human,Magically Altered · Manaless · Melee · Ionia · 2020 | Yone x resource | |
| Yorick | Male · Top · Human,Magically Altered · Mana · Melee · Shadow Isles · 2011 | Yorick x positions | |
| Yunara | Female · Bottom · Human · Mana · Ranged · Ionia · 2025 | Yunara x gender | |
| Yuumi | Female · Support · Cat,Magically Altered · Mana · Ranged · Bandle City · 2019 | Yuumi x gender | |
| Zaahen | Male · Top,Jungle · Darkin · Mana · Melee · Runeterra · 2025 | Zaahen x positions | |
| Zac | Male · Jungle · Golem · Health costs · Melee · Zaun · 2013 | Zac x resource | |
| Zed | Male · Jungle,Middle · Human,Magically Altered · Energy · Melee · Ionia · 2012 | Zed x resource | |
| Zeri | Female · Bottom · Human,Magicborn · Mana · Ranged · Zaun · 2022 | Zeri x gender | |
| Ziggs | Male · Bottom · Yordle · Mana · Ranged · Zaun · 2012 | Ziggs x range_type | |
| Zilean | Male · Support · Human,Magicborn · Mana · Ranged · Icathia,Runeterra,Shurima · 2009 | Zilean x range_type | |
| Zoe | Female · Middle · Aspect,Human · Mana · Ranged · Targon · 2017 | Zoe x gender | |
| Zyra | Female · Support · Human,Plant · Mana · Ranged · Ixtal · 2012 | Zyra x gender | |

candidates: Warwick, Xin Zhao

## Ejemplo 2078 · amarillo · página 4/7 · secreto (sólo motor) Viktor

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Ranged"]}, "gray": {"positions": ["Bottom"], "species": ["Yordle"]}, "yellow": {"regions": [["Zaun"]]}, "year": {"lt": 2012}, "used": ["Ziggs"]}`  
Excluidos: Ziggs, Urgot · years_allowed: [2009, 2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Lucian | Male · Bottom · Human · Mana · Ranged · Demacia,Shadow Isles · 2013 | Lucian x positions | |
| Lulu | Female · Support · Yordle · Mana · Ranged · Bandle City · 2012 | Lulu x gender | |
| Lux | Female · Middle,Support · Human,Magicborn · Mana · Ranged · Demacia · 2010 | Lux x gender | |
| Malphite | Male · Top · Golem · Mana · Melee · Ixtal,Shurima · 2009 | Malphite x range_type | |
| Malzahar | Male · Middle · Human,Void-Being · Mana · Ranged · Shurima,Void · 2010 | Malzahar x regions | |
| Maokai | Male · Support · Spirit · Mana · Melee · Shadow Isles · 2011 | Maokai x range_type | |
| Master Yi | Male · Jungle · Human,Spiritualist · Mana · Melee · Ionia · 2009 | Master Yi x range_type | |
| Mel | Female · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus,Piltover · 2025 | Mel x gender | |
| Milio | Male · Support · Human,Magicborn · Mana · Ranged · Ixtal · 2023 | Milio x regions | |
| Miss Fortune | Female · Bottom · Human · Mana · Ranged · Bilgewater · 2010 | Miss Fortune x gender | |
| Mordekaiser | Male · Top · Revenant · Shield · Melee · Noxus,Shadow Isles · 2010 | Mordekaiser x resource | |
| Morgana | Female · Middle,Support · Aspect,Human,Magically Altered · Mana · Ranged · Demacia,Targon · 2009 | Morgana x gender | |
| Naafiri | Female · Jungle,Middle · Darkin,Dog · Mana · Melee · Shurima · 2023 | Naafiri x gender | |
| Nami | Female · Support · Vastayan · Mana · Ranged · Bilgewater,Runeterra · 2012 | Nami x gender | |
| Nasus | Male · Top · God-Warrior · Mana · Melee · Shurima · 2009 | Nasus x range_type | |
| Nautilus | Male · Support · Revenant · Mana · Melee · Bilgewater · 2012 | Nautilus x range_type | |
| Neeko | Female · Middle,Support · Vastayan · Mana · Ranged · Ixtal · 2018 | Neeko x gender | |
| Nidalee | Female · Jungle · Human,Spiritualist · Mana · Ranged · Ixtal · 2009 | Nidalee x gender | |
| Nilah | Female · Bottom · Human,Magically Altered · Mana · Melee · Bilgewater · 2022 | Nilah x gender | |
| Nocturne | Other · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2011 | Nocturne x gender | |
| Nunu & Willump | Male · Jungle · Human,Yeti · Mana · Melee · Freljord · 2009 | Nunu & Willump x range_type | |
| Olaf | Male · Top · Human,Iceborn · Mana · Melee · Freljord · 2010 | Olaf x range_type | |
| Orianna | Female · Middle · Golem · Mana · Ranged · Piltover · 2011 | Orianna x gender | |
| Ornn | Male · Top · God,Spirit · Mana · Melee · Freljord · 2017 | Ornn x range_type | |
| Pantheon | Male · Top,Jungle,Support · Aspect,Human · Mana · Melee · Targon · 2010 | Pantheon x range_type | |

candidates: (vacía)

## Ejemplo 605 · amarillo · página 6/7 · secreto (sólo motor) Urgot

Estado: `{"green": {"gender": ["Male"], "positions": ["Top"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "species": ["Darkin"], "regions": ["Bilgewater", "Runeterra", "Shurima"], "gender": ["Female"], "positions": ["Bottom"]}, "yellow": {"species": [["Human", "Magically Altered"]]}, "year": {"eq": null, "gt": null, "lt": 2013}, "used": ["Aatrox", "Nilah"]}`  
Excluidos: Aatrox, Nilah · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x positions | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x positions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x positions | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x positions | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x positions | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x positions | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x positions | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x species | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x positions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x range_type | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x positions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x positions | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x positions | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot ok | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x positions | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x positions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x positions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: Urgot

## Ejemplo 127 · amarillo · página 2/7 · secreto (sólo motor) Camille

Estado: `{"green": {"range_type": ["Melee"], "positions": ["Top"], "gender": ["Female"]}, "gray": {"gender": ["Male"], "resource": ["Energy", "Manaless"], "species": ["Darkin"], "regions": ["Runeterra", "Shurima"]}, "yellow": {"species": [["Human"]], "regions": [["Noxus", "Piltover"]]}, "year": {"eq": null, "gt": 2013, "lt": 2024}, "used": ["Aatrox", "Ambessa"]}`  
Excluidos: Aatrox, Ambessa, Camille · years_allowed: [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x gender | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x positions | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x positions | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x range_type | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x positions | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x range_type | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x positions | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x range_type | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x range_type | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x species | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x positions | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x positions | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x gender | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x gender | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x range_type | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x positions | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x range_type | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x regions | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x positions | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x range_type | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x range_type | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x regions | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x positions | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x positions | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x range_type | |

candidates: (vacía)

## Ejemplo 622 · amarillo · página 2/7 · secreto (sólo motor) Sivir

Estado: `{"green": {}, "gray": {"gender": ["Male"], "resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x gender | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x range_type | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x gender | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x gender | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x gender | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x regions | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x range_type | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x gender | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x gender | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x range_type | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x gender | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x gender | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x gender | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x gender | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x gender | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x gender | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x gender | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x range_type | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x gender | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x gender | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x gender | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x range_type | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x range_type | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x gender | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna ok | |

candidates: Janna

## Ejemplo 2243 · amarillo · página 3/7 · secreto (sólo motor) Miss Fortune

Estado: `{"green": {"resource": ["Mana"]}, "gray": {"gender": ["Male"], "resource": ["Fury", "Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin", "God", "Spirit"], "regions": ["Freljord", "Runeterra", "Shurima"]}, "yellow": {"species": [["Human", "Magically Altered"], ["Human", "Iceborn"]]}, "year": {"eq": 2010, "gt": 2009, "lt": 2013}, "used": ["Aatrox", "Tryndamere", "Olaf", "Ornn"]}`  
Excluidos: Aatrox, Tryndamere, Olaf, Ornn, Lux, Miss Fortune · years_allowed: [2010]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV x gender | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax x gender | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x gender | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x gender | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x release_year | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x gender | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x regions | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x species | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x release_year | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus x gender | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x gender | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x resource | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x range_type | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x gender | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x resource | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x gender | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x species | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x resource | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x gender | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x species | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x resource | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona x range_type | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x range_type | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x regions | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x gender | |

candidates: (vacía)

## Ejemplo 686 · amarillo · página 7/7 · secreto (sólo motor) Skarner

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless", "Rage"], "species": ["Darkin", "God-Warrior", "Human", "Magically Altered", "Yordle"], "regions": ["Bilgewater", "Freljord", "Runeterra", "Shurima"], "range_type": ["Ranged"], "gender": ["Female"], "positions": ["Bottom"]}, "yellow": {"positions": [["Top"]]}, "year": {"gt": 2009, "lt": 2013}, "used": ["Aatrox", "Gnar", "Nilah", "Nasus"]}`  
Excluidos: Aatrox, Gnar, Nilah, Nasus · years_allowed: [2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Vi | Female · Jungle · Human · Mana · Melee · Piltover,Zaun · 2012 | Vi x gender | |
| Viego | Male · Jungle · Undead · Manaless · Melee · Camavor,Shadow Isles · 2021 | Viego x resource | |
| Viktor | Male · Middle · Cyborg,Human · Mana · Ranged · Piltover,Zaun · 2011 | Viktor x range_type | |
| Vladimir | Male · Middle · Human,Magically Altered · Bloodthirst · Ranged · Camavor,Noxus,Shadow Isles · 2010 | Vladimir x range_type | |
| Volibear | Male · Top · God,Spirit · Mana · Melee · Freljord · 2011 | Volibear x regions | |
| Warwick | Male · Jungle · Chemically Altered,Cyborg,Human · Mana · Melee · Zaun · 2009 | Warwick x species | |
| Wukong | Male · Jungle · Vastayan · Mana · Melee · Ionia · 2011 | Wukong x positions | |
| Xayah | Female · Bottom · Vastayan · Mana · Ranged · Ionia · 2017 | Xayah x gender | |
| Xerath | Male · Middle,Support · Baccai · Mana · Ranged · Shurima · 2011 | Xerath x range_type | |
| Xin Zhao | Male · Jungle · Human · Mana · Melee · Demacia,Ionia,Noxus · 2010 | Xin Zhao x species | |
| Yasuo | Male · Top,Middle,Bottom · Human,Magicborn · Flow · Melee · Ionia · 2013 | Yasuo x resource | |
| Yone | Male · Top,Middle · Human,Magically Altered · Manaless · Melee · Ionia · 2020 | Yone x resource | |
| Yorick | Male · Top · Human,Magically Altered · Mana · Melee · Shadow Isles · 2011 | Yorick x species | |
| Yunara | Female · Bottom · Human · Mana · Ranged · Ionia · 2025 | Yunara x gender | |
| Yuumi | Female · Support · Cat,Magically Altered · Mana · Ranged · Bandle City · 2019 | Yuumi x gender | |
| Zaahen | Male · Top,Jungle · Darkin · Mana · Melee · Runeterra · 2025 | Zaahen x species | |
| Zac | Male · Jungle · Golem · Health costs · Melee · Zaun · 2013 | Zac x resource | |
| Zed | Male · Jungle,Middle · Human,Magically Altered · Energy · Melee · Ionia · 2012 | Zed x resource | |
| Zeri | Female · Bottom · Human,Magicborn · Mana · Ranged · Zaun · 2022 | Zeri x gender | |
| Ziggs | Male · Bottom · Yordle · Mana · Ranged · Zaun · 2012 | Ziggs x range_type | |
| Zilean | Male · Support · Human,Magicborn · Mana · Ranged · Icathia,Runeterra,Shurima · 2009 | Zilean x range_type | |
| Zoe | Female · Middle · Aspect,Human · Mana · Ranged · Targon · 2017 | Zoe x gender | |
| Zyra | Female · Support · Human,Plant · Mana · Ranged · Ixtal · 2012 | Zyra x gender | |

candidates: (vacía)

## Ejemplo 855 · amarillo · página 2/7 · secreto (sólo motor) Locke

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Melee"]}, "gray": {"positions": ["Jungle", "Top"], "regions": ["Freljord", "Ionia"]}, "yellow": {"species": [["Human", "Spiritualist"]]}, "year": {"eq": null, "gt": 2009, "lt": null}, "used": ["Udyr"]}`  
Excluidos: Udyr, Locke · years_allowed: [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x positions | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x gender | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x resource | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x range_type | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x positions | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x gender | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x gender | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x range_type | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x range_type | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x gender | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x species | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x species | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x positions | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x resource | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x resource | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x positions | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x range_type | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x gender | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x positions | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x range_type | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x range_type | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x gender | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x gender | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x positions | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x gender | |

candidates: (vacía)

## Ejemplo 1480 · amarillo · página 6/7 · secreto (sólo motor) Urgot

Estado: `{"green": {"resource": ["Mana"], "range_type": ["Ranged"], "gender": ["Male"]}, "gray": {"gender": ["Female"], "species": ["Vastayan"], "regions": ["Freljord", "Shurima", "Targon"], "positions": ["Bottom", "Jungle", "Middle"], "range_type": ["Melee"]}, "yellow": {"positions": [["Middle", "Top"]], "species": [["Human"], ["Human", "Spiritualist"], ["Human", "Yeti"]]}, "year": {"gt": 2009, "lt": 2019}, "used": ["Aurora", "Akshan", "Aphelios", "Nunu & Willump"]}`  
Excluidos: Aurora, Akshan, Aphelios, Nunu & Willump, Urgot · years_allowed: [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x range_type | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x positions | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x positions | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x range_type | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x range_type | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x range_type | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x range_type | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x species | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x positions | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x range_type | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x positions | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x positions | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x range_type | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x excluded | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x regions | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x positions | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x positions | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: (vacía)

## Ejemplo 530 · con_candidatos · página 3/7 · secreto (sólo motor) Leona

Estado: `{"green": {"range_type": ["Melee"], "gender": ["Female"], "resource": ["Mana"], "species": ["Aspect", "Human"], "regions": ["Targon"]}, "gray": {"gender": ["Male"], "resource": ["Manaless"], "positions": ["Jungle", "Middle", "Top"], "species": ["Darkin"], "regions": ["Ionia", "Noxus", "Runeterra", "Shurima"]}, "yellow": {"species": [["Darkin", "Human", "Magically Altered"]]}, "year": {"lt": 2012}, "used": ["Aatrox", "Diana", "Kayn"]}`  
Excluidos: Aatrox, Diana, Kayn · years_allowed: [2009, 2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV x gender | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax x gender | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x range_type | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x range_type | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x range_type | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x gender | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x range_type | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x range_type | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x range_type | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus x range_type | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x gender | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x resource | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x species | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x excluded | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x range_type | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x gender | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x range_type | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x gender | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x range_type | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x range_type | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x gender | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona ok | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x species | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x range_type | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x gender | |

candidates: Leona

## Ejemplo 719 · con_candidatos · página 5/7 · secreto (sólo motor) Rumble

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Yordle"]}, "gray": {"resource": ["Courage", "Mana"], "positions": ["Middle"], "species": ["Human", "Void-Being"], "regions": ["Noxus", "Shurima", "Void"]}, "yellow": {}, "year": {"gt": 2009, "lt": 2016}, "used": ["Kassadin", "Kled"]}`  
Excluidos: Kassadin, Kled · years_allowed: [2010, 2011, 2012, 2013, 2014, 2015]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Poppy | Female · Top,Jungle · Yordle · Mana · Melee · Demacia · 2010 | Poppy x gender | |
| Pyke | Male · Support · Revenant · Mana · Melee · Bilgewater · 2018 | Pyke x positions | |
| Qiyana | Female · Jungle,Middle · Human,Magicborn · Mana · Melee · Ixtal · 2019 | Qiyana x gender | |
| Quinn | Female · Top · Human · Mana · Ranged · Demacia · 2013 | Quinn x gender | |
| Rakan | Male · Support · Vastayan · Mana · Melee · Ionia · 2017 | Rakan x positions | |
| Rammus | Male · Top,Jungle · Unknown · Mana · Melee · Shurima · 2009 | Rammus x positions | |
| Rek'Sai | Female · Jungle · Void-Being · Rage · Melee · Shurima,Void · 2014 | Rek'Sai x gender | |
| Rell | Female · Support · Human,Magically Altered,Magicborn · Mana · Melee · Noxus · 2020 | Rell x gender | |
| Renata Glasc | Female · Support · Chemically Altered,Human · Mana · Ranged · Zaun · 2022 | Renata Glasc x gender | |
| Renekton | Male · Top · God-Warrior · Fury · Melee · Shurima · 2011 | Renekton x species | |
| Rengar | Male · Jungle · Vastayan · Ferocity · Melee · Ixtal,Shurima · 2012 | Rengar x positions | |
| Riven | Female · Top · Human · Manaless · Melee · Ionia,Noxus · 2011 | Riven x gender | |
| Rumble | Male · Top · Yordle · Heat · Melee · Bandle City · 2011 | Rumble ok | |
| Ryze | Male · Middle · Human,Magically Altered · Mana · Ranged · Runeterra · 2009 | Ryze x range_type | |
| Samira | Female · Bottom · Human · Mana · Ranged · Noxus,Shurima · 2020 | Samira x gender | |
| Sejuani | Female · Jungle · Human,Iceborn · Mana · Melee · Freljord · 2012 | Sejuani x gender | |
| Senna | Female · Bottom,Support · Human,Undead · Mana · Ranged · Shadow Isles · 2019 | Senna x gender | |
| Seraphine | Female · Bottom,Support · Human,Magicborn · Mana · Ranged · Piltover,Zaun · 2020 | Seraphine x gender | |
| Sett | Male · Top · Human,Vastayan · Grit · Melee · Ionia · 2020 | Sett x species | |
| Shaco | Male · Jungle · Spirit · Mana · Melee · Runeterra · 2009 | Shaco x positions | |
| Shen | Male · Top · Human,Spiritualist · Energy · Melee · Ionia · 2010 | Shen x species | |
| Shyvana | Female · Jungle · Dragon,Magically Altered · Fury · Melee · Demacia · 2011 | Shyvana x gender | |
| Singed | Male · Top · Chemically Altered,Human · Mana · Melee · Piltover,Zaun · 2009 | Singed x species | |
| Sion | Male · Top · Revenant · Mana · Melee · Noxus · 2009 | Sion x species | |
| Sivir | Female · Bottom · Human · Mana · Ranged · Shurima · 2009 | Sivir x gender | |

candidates: Rumble

## Ejemplo 983 · con_candidatos · página 3/7 · secreto (sólo motor) Jarvan IV

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Melee"], "positions": ["Jungle"]}, "gray": {"positions": ["Support"], "species": ["Revenant", "Undead", "Yordle"], "regions": ["Bilgewater", "Shurima"]}, "yellow": {}, "year": {"eq": null, "gt": 2009, "lt": 2012}, "used": ["Nautilus", "Amumu"]}`  
Excluidos: Nautilus, Amumu · years_allowed: [2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV ok | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax x positions | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x range_type | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x range_type | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x gender | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x positions | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x gender | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x gender | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x gender | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus x range_type | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x positions | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x gender | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x gender | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x regions | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x resource | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x release_year | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x gender | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x resource | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x range_type | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x gender | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x resource | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona x gender | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x gender | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x gender | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x positions | |

candidates: Jarvan IV

## Ejemplo 2378 · con_candidatos · página 2/7 · secreto (sólo motor) Hwei

Estado: `{"green": {"resource": ["Mana"], "range_type": ["Ranged"], "positions": ["Middle", "Support"], "species": ["Human", "Magicborn"]}, "gray": {"gender": ["Female"], "range_type": ["Melee"], "positions": ["Bottom"], "regions": ["Bilgewater", "Demacia"]}, "yellow": {"species": [["Human", "Magically Altered"]]}, "year": {"gt": 2022}, "used": ["Nilah", "Lux"]}`  
Excluidos: Nilah, Lux · years_allowed: [2023, 2024, 2025, 2026]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x range_type | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x range_type | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x resource | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x positions | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x range_type | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x positions | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x range_type | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x positions | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x positions | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x range_type | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x range_type | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x range_type | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x range_type | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x resource | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x resource | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x range_type | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x positions | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x range_type | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x range_type | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x positions | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei ok | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x range_type | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x range_type | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x range_type | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x positions | |

candidates: Hwei

## Ejemplo 971 · con_candidatos · página 1/7 · secreto (sólo motor) Rammus

Estado: `{"green": {}, "gray": {}, "yellow": {}, "year": {"eq": null, "gt": null, "lt": null}, "used": []}`  
Excluidos: — · years_allowed: —

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Aatrox | Male · Top · Darkin · Manaless · Melee · Runeterra,Shurima · 2013 | Aatrox ok | |
| Ahri | Female · Middle · Vastayan · Mana · Ranged · Ionia · 2011 | Ahri ok | |
| Akali | Female · Top,Middle · Human · Energy · Melee · Ionia · 2010 | Akali ok | |
| Akshan | Male · Middle · Human · Mana · Ranged · Shurima · 2021 | Akshan ok | |
| Alistar | Male · Support · Minotaur · Mana · Melee · Noxus,Runeterra · 2009 | Alistar ok | |
| Ambessa | Female · Top · Human · Energy · Melee · Noxus,Piltover · 2024 | Ambessa ok | |
| Amumu | Male · Jungle · Undead,Yordle · Mana · Melee · Shurima · 2009 | Amumu ok | |
| Anivia | Female · Middle · God,Spirit · Mana · Ranged · Freljord · 2009 | Anivia ok | |
| Annie | Female · Middle · Human,Magicborn · Mana · Ranged · Noxus,Runeterra · 2009 | Annie ok | |
| Aphelios | Male · Bottom · Human,Spiritualist · Mana · Ranged · Targon · 2019 | Aphelios ok | |
| Ashe | Female · Bottom,Support · Human,Iceborn · Mana · Ranged · Freljord · 2009 | Ashe ok | |
| Aurelion Sol | Male · Middle · Celestial,Dragon · Mana · Ranged · Runeterra,Targon · 2016 | Aurelion Sol ok | |
| Aurora | Female · Top,Middle · Vastayan · Mana · Ranged · Freljord · 2024 | Aurora ok | |
| Azir | Male · Middle · God-Warrior · Mana · Ranged · Shurima · 2014 | Azir ok | |
| Bard | Male · Support · Celestial · Mana · Ranged · Runeterra · 2015 | Bard ok | |
| Bel'Veth | Female · Jungle · Void-Being · Manaless · Melee · Void · 2022 | Bel'Veth ok | |
| Blitzcrank | Male · Support · Golem · Mana · Melee · Zaun · 2009 | Blitzcrank ok | |
| Brand | Male · Jungle,Middle,Support · Human,Magically Altered · Mana · Ranged · Freljord,Runeterra · 2011 | Brand ok | |
| Braum | Male · Support · Human,Iceborn · Mana · Melee · Freljord · 2014 | Braum ok | |
| Briar | Female · Jungle · Golem · Health costs · Melee · Noxus · 2023 | Briar ok | |
| Caitlyn | Female · Bottom · Human · Mana · Ranged · Piltover · 2011 | Caitlyn ok | |
| Camille | Female · Top · Cyborg,Human · Mana · Melee · Piltover · 2016 | Camille ok | |
| Cassiopeia | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus,Shurima · 2010 | Cassiopeia ok | |
| Cho'Gath | Other · Top · Void-Being · Mana · Melee · Void · 2009 | Cho'Gath ok | |
| Corki | Male · Middle · Yordle · Mana · Ranged · Bandle City,Piltover · 2009 | Corki ok | |

candidates: Aatrox, Ahri, Akali, Akshan, Alistar, Ambessa, Amumu, Anivia, Annie, Aphelios, Ashe, Aurelion Sol, Aurora, Azir, Bard, Bel'Veth, Blitzcrank, Brand, Braum, Briar, Caitlyn, Camille, Cassiopeia, Cho'Gath, Corki

## Ejemplo 1830 · con_candidatos · página 4/7 · secreto (sólo motor) Brand

Estado: `{"green": {"gender": ["Male"]}, "gray": {"resource": ["Manaless"], "range_type": ["Melee"], "positions": ["Top"], "species": ["Darkin"]}, "yellow": {"regions": [["Runeterra", "Shurima"]]}, "year": {"eq": null, "gt": null, "lt": 2013}, "used": ["Aatrox"]}`  
Excluidos: Aatrox · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Lucian | Male · Bottom · Human · Mana · Ranged · Demacia,Shadow Isles · 2013 | Lucian x regions | |
| Lulu | Female · Support · Yordle · Mana · Ranged · Bandle City · 2012 | Lulu x gender | |
| Lux | Female · Middle,Support · Human,Magicborn · Mana · Ranged · Demacia · 2010 | Lux x gender | |
| Malphite | Male · Top · Golem · Mana · Melee · Ixtal,Shurima · 2009 | Malphite x range_type | |
| Malzahar | Male · Middle · Human,Void-Being · Mana · Ranged · Shurima,Void · 2010 | Malzahar ok | |
| Maokai | Male · Support · Spirit · Mana · Melee · Shadow Isles · 2011 | Maokai x range_type | |
| Master Yi | Male · Jungle · Human,Spiritualist · Mana · Melee · Ionia · 2009 | Master Yi x range_type | |
| Mel | Female · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus,Piltover · 2025 | Mel x gender | |
| Milio | Male · Support · Human,Magicborn · Mana · Ranged · Ixtal · 2023 | Milio x regions | |
| Miss Fortune | Female · Bottom · Human · Mana · Ranged · Bilgewater · 2010 | Miss Fortune x gender | |
| Mordekaiser | Male · Top · Revenant · Shield · Melee · Noxus,Shadow Isles · 2010 | Mordekaiser x range_type | |
| Morgana | Female · Middle,Support · Aspect,Human,Magically Altered · Mana · Ranged · Demacia,Targon · 2009 | Morgana x gender | |
| Naafiri | Female · Jungle,Middle · Darkin,Dog · Mana · Melee · Shurima · 2023 | Naafiri x gender | |
| Nami | Female · Support · Vastayan · Mana · Ranged · Bilgewater,Runeterra · 2012 | Nami x gender | |
| Nasus | Male · Top · God-Warrior · Mana · Melee · Shurima · 2009 | Nasus x range_type | |
| Nautilus | Male · Support · Revenant · Mana · Melee · Bilgewater · 2012 | Nautilus x range_type | |
| Neeko | Female · Middle,Support · Vastayan · Mana · Ranged · Ixtal · 2018 | Neeko x gender | |
| Nidalee | Female · Jungle · Human,Spiritualist · Mana · Ranged · Ixtal · 2009 | Nidalee x gender | |
| Nilah | Female · Bottom · Human,Magically Altered · Mana · Melee · Bilgewater · 2022 | Nilah x gender | |
| Nocturne | Other · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2011 | Nocturne x gender | |
| Nunu & Willump | Male · Jungle · Human,Yeti · Mana · Melee · Freljord · 2009 | Nunu & Willump x range_type | |
| Olaf | Male · Top · Human,Iceborn · Mana · Melee · Freljord · 2010 | Olaf x range_type | |
| Orianna | Female · Middle · Golem · Mana · Ranged · Piltover · 2011 | Orianna x gender | |
| Ornn | Male · Top · God,Spirit · Mana · Melee · Freljord · 2017 | Ornn x range_type | |
| Pantheon | Male · Top,Jungle,Support · Aspect,Human · Mana · Melee · Targon · 2010 | Pantheon x range_type | |

candidates: Malzahar

## Ejemplo 237 · vacia · página 1/7 · secreto (sólo motor) Jarvan IV

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"], "species": ["Human"], "regions": ["Demacia"]}, "gray": {"resource": ["Manaless"], "positions": ["Top"], "species": ["Darkin"], "regions": ["Runeterra", "Shurima"], "gender": ["Female"], "range_type": ["Ranged"]}, "yellow": {}, "year": {"eq": null, "gt": null, "lt": 2013}, "used": ["Aatrox", "Quinn"]}`  
Excluidos: Aatrox, Quinn · years_allowed: [2009, 2010, 2011, 2012]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Aatrox | Male · Top · Darkin · Manaless · Melee · Runeterra,Shurima · 2013 | Aatrox x excluded | |
| Ahri | Female · Middle · Vastayan · Mana · Ranged · Ionia · 2011 | Ahri x gender | |
| Akali | Female · Top,Middle · Human · Energy · Melee · Ionia · 2010 | Akali x gender | |
| Akshan | Male · Middle · Human · Mana · Ranged · Shurima · 2021 | Akshan x range_type | |
| Alistar | Male · Support · Minotaur · Mana · Melee · Noxus,Runeterra · 2009 | Alistar x species | |
| Ambessa | Female · Top · Human · Energy · Melee · Noxus,Piltover · 2024 | Ambessa x gender | |
| Amumu | Male · Jungle · Undead,Yordle · Mana · Melee · Shurima · 2009 | Amumu x species | |
| Anivia | Female · Middle · God,Spirit · Mana · Ranged · Freljord · 2009 | Anivia x gender | |
| Annie | Female · Middle · Human,Magicborn · Mana · Ranged · Noxus,Runeterra · 2009 | Annie x gender | |
| Aphelios | Male · Bottom · Human,Spiritualist · Mana · Ranged · Targon · 2019 | Aphelios x range_type | |
| Ashe | Female · Bottom,Support · Human,Iceborn · Mana · Ranged · Freljord · 2009 | Ashe x gender | |
| Aurelion Sol | Male · Middle · Celestial,Dragon · Mana · Ranged · Runeterra,Targon · 2016 | Aurelion Sol x range_type | |
| Aurora | Female · Top,Middle · Vastayan · Mana · Ranged · Freljord · 2024 | Aurora x gender | |
| Azir | Male · Middle · God-Warrior · Mana · Ranged · Shurima · 2014 | Azir x range_type | |
| Bard | Male · Support · Celestial · Mana · Ranged · Runeterra · 2015 | Bard x range_type | |
| Bel'Veth | Female · Jungle · Void-Being · Manaless · Melee · Void · 2022 | Bel'Veth x gender | |
| Blitzcrank | Male · Support · Golem · Mana · Melee · Zaun · 2009 | Blitzcrank x species | |
| Brand | Male · Jungle,Middle,Support · Human,Magically Altered · Mana · Ranged · Freljord,Runeterra · 2011 | Brand x range_type | |
| Braum | Male · Support · Human,Iceborn · Mana · Melee · Freljord · 2014 | Braum x species | |
| Briar | Female · Jungle · Golem · Health costs · Melee · Noxus · 2023 | Briar x gender | |
| Caitlyn | Female · Bottom · Human · Mana · Ranged · Piltover · 2011 | Caitlyn x gender | |
| Camille | Female · Top · Cyborg,Human · Mana · Melee · Piltover · 2016 | Camille x gender | |
| Cassiopeia | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus,Shurima · 2010 | Cassiopeia x gender | |
| Cho'Gath | Other · Top · Void-Being · Mana · Melee · Void · 2009 | Cho'Gath x gender | |
| Corki | Male · Middle · Yordle · Mana · Ranged · Bandle City,Piltover · 2009 | Corki x range_type | |

candidates: (vacía)

## Ejemplo 1029 · vacia · página 3/7 · secreto (sólo motor) Taric

Estado: `{"green": {"resource": ["Mana"], "regions": ["Demacia", "Targon"], "gender": ["Male"], "range_type": ["Melee"], "positions": ["Support"]}, "gray": {"gender": ["Female"], "range_type": ["Ranged"], "species": ["Golem"], "regions": ["Zaun"]}, "yellow": {"positions": [["Middle", "Support"]], "species": [["Aspect", "Human", "Magically Altered"]]}, "year": {"eq": 2009}, "used": ["Morgana", "Blitzcrank"]}`  
Excluidos: Morgana, Blitzcrank · years_allowed: [2009]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Jarvan IV | Male · Jungle · Human · Mana · Melee · Demacia · 2011 | Jarvan IV x regions | |
| Jax | Male · Top,Jungle · Unknown · Mana · Melee · Icathia,Runeterra,Shurima · 2009 | Jax x regions | |
| Jayce | Male · Top · Human · Mana · Ranged · Piltover · 2012 | Jayce x regions | |
| Jhin | Male · Bottom · Human,Spiritualist · Mana · Ranged · Ionia · 2016 | Jhin x regions | |
| Jinx | Female · Bottom · Chemically Altered,Human · Mana · Ranged · Zaun · 2013 | Jinx x regions | |
| K'Sante | Male · Top · Human · Mana · Melee · Shurima · 2022 | K'Sante x regions | |
| Kai'Sa | Female · Bottom · Human,Void-Being · Mana · Ranged · Shurima,Void · 2018 | Kai'Sa x regions | |
| Kalista | Female · Bottom · Undead · Mana · Ranged · Camavor,Shadow Isles · 2014 | Kalista x regions | |
| Karma | Female · Middle,Support · Human,Spiritualist · Mana · Ranged · Ionia · 2011 | Karma x regions | |
| Karthus | Male · Jungle · Undead · Mana · Ranged · Noxus,Shadow Isles · 2009 | Karthus x regions | |
| Kassadin | Male · Middle · Human,Void-Being · Mana · Melee · Shurima,Void · 2009 | Kassadin x regions | |
| Katarina | Female · Middle · Human · Manaless · Melee · Noxus · 2009 | Katarina x resource | |
| Kayle | Female · Top · Aspect,Human,Magically Altered · Mana · Melee · Demacia,Targon · 2009 | Kayle x gender | |
| Kayn | Male · Jungle · Darkin,Human,Magically Altered · Mana · Melee · Ionia,Noxus,Runeterra,Shurima · 2017 | Kayn x regions | |
| Kennen | Male · Top · Yordle · Energy · Ranged · Ionia · 2010 | Kennen x resource | |
| Kha'Zix | Male · Jungle · Void-Being · Mana · Melee · Void · 2012 | Kha'Zix x regions | |
| Kindred | Female · Jungle · God,Spirit · Mana · Ranged · Runeterra · 2015 | Kindred x regions | |
| Kled | Male · Top · Yordle · Courage · Melee · Noxus · 2016 | Kled x resource | |
| Kog'Maw | Male · Bottom · Void-Being · Mana · Ranged · Void · 2010 | Kog'Maw x regions | |
| LeBlanc | Female · Middle · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | LeBlanc x regions | |
| Lee Sin | Male · Jungle · Human,Spiritualist · Energy · Melee · Ionia · 2011 | Lee Sin x resource | |
| Leona | Female · Support · Aspect,Human · Mana · Melee · Targon · 2011 | Leona x regions | |
| Lillia | Female · Jungle · Spirit · Mana · Melee · Ionia · 2020 | Lillia x regions | |
| Lissandra | Female · Middle · Human,Iceborn · Mana · Ranged · Freljord · 2013 | Lissandra x regions | |
| Locke | Male · Middle · Human · Mana · Melee · Demacia · 2026 | Locke x regions | |

candidates: (vacía)

## Ejemplo 1267 · vacia · página 4/7 · secreto (sólo motor) Ahri

Estado: `{"green": {"gender": ["Female"], "resource": ["Mana"]}, "gray": {"range_type": ["Melee"], "positions": ["Top"], "species": ["Human"], "regions": ["Demacia"]}, "yellow": {}, "year": {"lt": 2012}, "used": ["Fiora"]}`  
Excluidos: Fiora, Ahri, Orianna · years_allowed: [2009, 2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Lucian | Male · Bottom · Human · Mana · Ranged · Demacia,Shadow Isles · 2013 | Lucian x gender | |
| Lulu | Female · Support · Yordle · Mana · Ranged · Bandle City · 2012 | Lulu x release_year | |
| Lux | Female · Middle,Support · Human,Magicborn · Mana · Ranged · Demacia · 2010 | Lux x species | |
| Malphite | Male · Top · Golem · Mana · Melee · Ixtal,Shurima · 2009 | Malphite x gender | |
| Malzahar | Male · Middle · Human,Void-Being · Mana · Ranged · Shurima,Void · 2010 | Malzahar x gender | |
| Maokai | Male · Support · Spirit · Mana · Melee · Shadow Isles · 2011 | Maokai x gender | |
| Master Yi | Male · Jungle · Human,Spiritualist · Mana · Melee · Ionia · 2009 | Master Yi x gender | |
| Mel | Female · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus,Piltover · 2025 | Mel x species | |
| Milio | Male · Support · Human,Magicborn · Mana · Ranged · Ixtal · 2023 | Milio x gender | |
| Miss Fortune | Female · Bottom · Human · Mana · Ranged · Bilgewater · 2010 | Miss Fortune x species | |
| Mordekaiser | Male · Top · Revenant · Shield · Melee · Noxus,Shadow Isles · 2010 | Mordekaiser x gender | |
| Morgana | Female · Middle,Support · Aspect,Human,Magically Altered · Mana · Ranged · Demacia,Targon · 2009 | Morgana x species | |
| Naafiri | Female · Jungle,Middle · Darkin,Dog · Mana · Melee · Shurima · 2023 | Naafiri x range_type | |
| Nami | Female · Support · Vastayan · Mana · Ranged · Bilgewater,Runeterra · 2012 | Nami x release_year | |
| Nasus | Male · Top · God-Warrior · Mana · Melee · Shurima · 2009 | Nasus x gender | |
| Nautilus | Male · Support · Revenant · Mana · Melee · Bilgewater · 2012 | Nautilus x gender | |
| Neeko | Female · Middle,Support · Vastayan · Mana · Ranged · Ixtal · 2018 | Neeko x release_year | |
| Nidalee | Female · Jungle · Human,Spiritualist · Mana · Ranged · Ixtal · 2009 | Nidalee x species | |
| Nilah | Female · Bottom · Human,Magically Altered · Mana · Melee · Bilgewater · 2022 | Nilah x range_type | |
| Nocturne | Other · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2011 | Nocturne x gender | |
| Nunu & Willump | Male · Jungle · Human,Yeti · Mana · Melee · Freljord · 2009 | Nunu & Willump x gender | |
| Olaf | Male · Top · Human,Iceborn · Mana · Melee · Freljord · 2010 | Olaf x gender | |
| Orianna | Female · Middle · Golem · Mana · Ranged · Piltover · 2011 | Orianna x excluded | |
| Ornn | Male · Top · God,Spirit · Mana · Melee · Freljord · 2017 | Ornn x gender | |
| Pantheon | Male · Top,Jungle,Support · Aspect,Human · Mana · Melee · Targon · 2010 | Pantheon x gender | |

candidates: (vacía)

## Ejemplo 11 · vacia · página 2/7 · secreto (sólo motor) Locke

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "resource": ["Mana"], "species": ["Human"]}, "gray": {"resource": ["Manaless"], "positions": ["Support", "Top"], "species": ["Darkin"], "regions": ["Freljord", "Runeterra", "Shurima", "Zaun"]}, "yellow": {"species": [["Human", "Iceborn"]], "positions": [["Jungle", "Middle"]]}, "year": {"eq": null, "gt": 2015, "lt": null}, "used": ["Aatrox", "Braum", "Ekko"]}`  
Excluidos: Aatrox, Braum, Ekko · years_allowed: [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x positions | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x gender | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x resource | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x range_type | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x excluded | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x gender | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x gender | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x range_type | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x range_type | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x gender | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x species | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x species | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x positions | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x resource | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x range_type | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x species | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x range_type | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x gender | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x species | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x range_type | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x range_type | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x gender | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x gender | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x species | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x gender | |

candidates: (vacía)

## Ejemplo 1197 · vacia · página 2/7 · secreto (sólo motor) Olaf

Estado: `{"green": {"gender": ["Male"], "resource": ["Mana"], "range_type": ["Melee"], "positions": ["Top"]}, "gray": {"positions": ["Support"], "species": ["Golem"], "regions": ["Noxus", "Zaun"]}, "yellow": {"species": [["Human"]]}, "year": {"eq": null, "gt": 2009, "lt": 2012}, "used": ["Blitzcrank", "Darius"]}`  
Excluidos: Blitzcrank, Darius, Yorick · years_allowed: [2010, 2011]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Darius | Male · Top · Human · Mana · Melee · Noxus · 2012 | Darius x excluded | |
| Diana | Female · Jungle,Middle · Aspect,Human · Mana · Melee · Targon · 2012 | Diana x gender | |
| Dr. Mundo | Male · Top,Jungle · Chemically Altered,Human · Health costs · Melee · Zaun · 2009 | Dr. Mundo x resource | |
| Draven | Male · Bottom · Human · Mana · Ranged · Noxus · 2012 | Draven x range_type | |
| Ekko | Male · Jungle,Middle · Human · Mana · Melee · Zaun · 2015 | Ekko x positions | |
| Elise | Female · Jungle · Human,Magically Altered · Mana · Ranged · Noxus,Shadow Isles · 2012 | Elise x gender | |
| Evelynn | Female · Jungle · Demon,Spirit · Mana · Melee · Runeterra · 2009 | Evelynn x gender | |
| Ezreal | Male · Bottom · Human,Magicborn · Mana · Ranged · Piltover · 2010 | Ezreal x range_type | |
| Fiddlesticks | Male · Jungle · Demon,Spirit · Mana · Ranged · Runeterra · 2009 | Fiddlesticks x range_type | |
| Fiora | Female · Top · Human · Mana · Melee · Demacia · 2012 | Fiora x gender | |
| Fizz | Male · Middle · Yordle · Mana · Melee · Bilgewater · 2011 | Fizz x positions | |
| Galio | Male · Middle · Golem · Mana · Melee · Demacia · 2010 | Galio x positions | |
| Gangplank | Male · Top · Human · Mana · Melee · Bilgewater · 2009 | Gangplank x species | |
| Garen | Male · Top · Human · Manaless · Melee · Demacia · 2010 | Garen x resource | |
| Gnar | Male · Top · Yordle · Rage · Ranged · Freljord · 2014 | Gnar x resource | |
| Gragas | Male · Top,Jungle · Human,Iceborn · Mana · Melee · Freljord · 2010 | Gragas x positions | |
| Graves | Male · Jungle · Human · Mana · Ranged · Bilgewater · 2011 | Graves x range_type | |
| Gwen | Female · Top · Human,Magically Altered · Mana · Melee · Camavor,Shadow Isles · 2021 | Gwen x gender | |
| Hecarim | Male · Jungle · Undead · Mana · Melee · Camavor,Shadow Isles · 2012 | Hecarim x positions | |
| Heimerdinger | Male · Top · Yordle · Mana · Ranged · Piltover · 2009 | Heimerdinger x range_type | |
| Hwei | Male · Middle,Support · Human,Magicborn · Mana · Ranged · Ionia · 2023 | Hwei x range_type | |
| Illaoi | Female · Top · Human,Spiritualist · Mana · Melee · Bilgewater · 2015 | Illaoi x gender | |
| Irelia | Female · Top,Middle · Human,Spiritualist · Mana · Melee · Ionia · 2010 | Irelia x gender | |
| Ivern | Male · Jungle · Human,Magically Altered · Mana · Melee · Freljord,Ionia · 2016 | Ivern x positions | |
| Janna | Female · Support · God,Spirit · Mana · Ranged · Shurima,Zaun · 2009 | Janna x gender | |

candidates: (vacía)

## Ejemplo 620 · vacia · página 6/7 · secreto (sólo motor) Singed

Estado: `{"green": {"gender": ["Male"], "range_type": ["Melee"], "positions": ["Top"], "resource": ["Mana"]}, "gray": {"resource": ["Manaless"], "species": ["Darkin"], "regions": ["Bilgewater", "Noxus", "Runeterra", "Shurima"]}, "yellow": {"species": [["Human"]]}, "year": {"eq": 2009, "lt": 2012}, "used": ["Aatrox", "Darius", "Gangplank"]}`  
Excluidos: Aatrox, Darius, Gangplank · years_allowed: [2009]

| Fila | Atributos | Etiqueta | Revisor |
|---|---|---|---|
| Skarner | Male · Top,Jungle · Brackern · Mana · Melee · Ixtal · 2011 | Skarner x positions | |
| Smolder | Male · Bottom · Dragon · Mana · Ranged · Camavor,Noxus · 2024 | Smolder x range_type | |
| Sona | Female · Support · Human,Magicborn · Mana · Ranged · Demacia,Ionia · 2010 | Sona x gender | |
| Soraka | Female · Support · Celestial · Mana · Ranged · Ionia,Targon · 2009 | Soraka x gender | |
| Swain | Male · Middle,Support · Human,Magically Altered · Mana · Ranged · Noxus · 2010 | Swain x range_type | |
| Sylas | Male · Jungle,Middle · Human,Magicborn · Mana · Melee · Demacia,Freljord · 2019 | Sylas x positions | |
| Syndra | Female · Middle · Human,Magicborn · Mana · Ranged · Ionia · 2012 | Syndra x gender | |
| Tahm Kench | Male · Top,Support · Demon,Spirit · Mana · Melee · Bilgewater,Runeterra · 2015 | Tahm Kench x positions | |
| Taliyah | Female · Jungle,Middle · Human,Magicborn · Mana · Ranged · Shurima · 2016 | Taliyah x gender | |
| Talon | Male · Jungle,Middle · Human · Mana · Melee · Noxus · 2011 | Talon x positions | |
| Taric | Male · Support · Aspect,Human · Mana · Melee · Demacia,Targon · 2009 | Taric x positions | |
| Teemo | Male · Top · Yordle · Mana · Ranged · Bandle City · 2009 | Teemo x range_type | |
| Thresh | Male · Support · Undead · Mana · Ranged · Shadow Isles · 2013 | Thresh x range_type | |
| Tristana | Female · Bottom · Yordle · Mana · Ranged · Bandle City · 2009 | Tristana x gender | |
| Trundle | Male · Top · Iceborn,Troll · Mana · Melee · Freljord · 2010 | Trundle x species | |
| Tryndamere | Male · Top · Human,Magically Altered · Fury · Melee · Freljord · 2009 | Tryndamere x resource | |
| Twisted Fate | Male · Middle,Bottom · Human,Magicborn · Mana · Ranged · Bilgewater · 2009 | Twisted Fate x range_type | |
| Twitch | Male · Bottom · Chemically Altered,Rat · Mana · Ranged · Zaun · 2009 | Twitch x range_type | |
| Udyr | Male · Top,Jungle · Human,Spiritualist · Mana · Melee · Freljord,Ionia · 2009 | Udyr x positions | |
| Urgot | Male · Top · Chemically Altered,Cyborg,Human · Mana · Ranged · Noxus,Zaun · 2010 | Urgot x range_type | |
| Varus | Male · Bottom · Darkin,Human · Mana · Ranged · Ionia,Runeterra,Shurima · 2012 | Varus x range_type | |
| Vayne | Female · Bottom · Human · Mana · Ranged · Demacia · 2011 | Vayne x gender | |
| Veigar | Male · Middle · Yordle · Mana · Ranged · Bandle City,Runeterra,Shadow Isles · 2009 | Veigar x range_type | |
| Vel'Koz | Male · Support · Void-Being · Mana · Ranged · Void · 2014 | Vel'Koz x range_type | |
| Vex | Female · Middle · Yordle · Mana · Ranged · Bandle City,Shadow Isles · 2021 | Vex x gender | |

candidates: (vacía)

