# ЛР 7 · Удачные и проблемные результаты validation

10 успешных и 10 неудачных пользователей, выбраны по фиксированному правилу из всех 610. Единица анализа — пользователь.

**Важно:** метка 0 в топе может означать *unjudged*, а не низкую оценку; проверка производится только по фактическим validation-оценкам. Список всех случаев и значения метрик — в `validation_cases.csv` и `validation_detail.jsonl`.

## 10 успешных случаев

**userId 335** · NDCG@10=0.9380549636 · HitRate@10=1.0000000000
- История train: 16; положительных в validation: 4; попаданий: 4.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 2]; 2. Forrest Gump (1994) [movieId=356, рел. 2]; 3. Matrix, The (1999) [movieId=2571, рел. 0]; 4. Pulp Fiction (1994) [movieId=296, рел. 2]; 5. Silence of the Lambs, The (1991) [movieId=593, рел. 1]
- Положительные validation: Braveheart (1995) (110); Pulp Fiction (1994) (296); Shawshank Redemption, The (1994) (318); Forrest Gump (1994) (356)
- Вывод: хотя бы один понравившийся фильм найден

**userId 54** · NDCG@10=0.7727357110 · HitRate@10=1.0000000000
- История train: 18; положительных в validation: 2; попаданий: 2.
- Рекомендации: 1. Forrest Gump (1994) [movieId=356, рел. 2]; 2. Matrix, The (1999) [movieId=2571, рел. 0]; 3. Silence of the Lambs, The (1991) [movieId=593, рел. 2]; 4. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 0]; 5. Fight Club (1999) [movieId=2959, рел. 0]
- Положительные validation: Forrest Gump (1994) (356); Silence of the Lambs, The (1991) (593)
- Вывод: хотя бы один понравившийся фильм найден

**userId 480** · NDCG@10=0.7337583661 · HitRate@10=1.0000000000
- История train: 501; положительных в validation: 39; попаданий: 7.
- Рекомендации: 1. Pulp Fiction (1994) [movieId=296, рел. 2]; 2. Star Wars: Episode VI - Return of the Jedi (1983) [movieId=1210, рел. 1]; 3. Toy Story (1995) [movieId=1, рел. 0]; 4. Terminator 2: Judgment Day (1991) [movieId=589, рел. 2]; 5. Saving Private Ryan (1998) [movieId=2028, рел. 2]
- Положительные validation: GoldenEye (1995) (10); Twelve Monkeys (a.k.a. 12 Monkeys) (1995) (32); Seven (a.k.a. Se7en) (1995) (47); Pulp Fiction (1994) (296); Stargate (1994) (316)
- Вывод: хотя бы один понравившийся фильм найден

**userId 555** · NDCG@10=0.7273298443 · HitRate@10=1.0000000000
- История train: 325; положительных в validation: 56; попаданий: 6.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 2]; 2. Matrix, The (1999) [movieId=2571, рел. 2]; 3. Pulp Fiction (1994) [movieId=296, рел. 2]; 4. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 2]; 5. Braveheart (1995) [movieId=110, рел. 2]
- Положительные validation: City of Lost Children, The (Cité des enfants perdus, La) (1995) (29); Twelve Monkeys (a.k.a. 12 Monkeys) (1995) (32); Braveheart (1995) (110); Star Wars: Episode IV - A New Hope (1977) (260); Léon: The Professional (a.k.a. The Professional) (Léon) (1994) (293)
- Вывод: хотя бы один понравившийся фильм найден

**userId 443** · NDCG@10=0.7041249493 · HitRate@10=1.0000000000
- История train: 22; положительных в validation: 7; попаданий: 4.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 2]; 2. Forrest Gump (1994) [movieId=356, рел. 2]; 3. Pulp Fiction (1994) [movieId=296, рел. 2]; 4. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 2]; 5. Braveheart (1995) [movieId=110, рел. 0]
- Положительные validation: Star Wars: Episode IV - A New Hope (1977) (260); Pulp Fiction (1994) (296); Shawshank Redemption, The (1994) (318); Forrest Gump (1994) (356); American History X (1998) (2329)
- Вывод: хотя бы один понравившийся фильм найден

**userId 599** · NDCG@10=0.6776720746 · HitRate@10=1.0000000000
- История train: 1486; положительных в validation: 68; попаданий: 6.
- Рекомендации: 1. Forrest Gump (1994) [movieId=356, рел. 1]; 2. Matrix, The (1999) [movieId=2571, рел. 2]; 3. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 2]; 4. Star Wars: Episode V - The Empire Strikes Back (1980) [movieId=1196, рел. 2]; 5. Schindler's List (1993) [movieId=527, рел. 0]
- Положительные validation: Heat (1995) (6); Rumble in the Bronx (Hont faan kui) (1995) (112); Before Sunrise (1995) (215); Star Wars: Episode IV - A New Hope (1977) (260); Blade Runner (1982) (541)
- Вывод: хотя бы один понравившийся фильм найден

**userId 513** · NDCG@10=0.6164336326 · HitRate@10=1.0000000000
- История train: 19; положительных в validation: 5; попаданий: 3.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 2]; 2. Forrest Gump (1994) [movieId=356, рел. 0]; 3. Matrix, The (1999) [movieId=2571, рел. 0]; 4. Pulp Fiction (1994) [movieId=296, рел. 2]; 5. Silence of the Lambs, The (1991) [movieId=593, рел. 2]
- Положительные validation: Apollo 13 (1995) (150); Pulp Fiction (1994) (296); Shawshank Redemption, The (1994) (318); Fugitive, The (1993) (457); Silence of the Lambs, The (1991) (593)
- Вывод: хотя бы один понравившийся фильм найден

**userId 483** · NDCG@10=0.6032621821 · HitRate@10=1.0000000000
- История train: 436; положительных в validation: 91; попаданий: 6.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 2]; 2. Forrest Gump (1994) [movieId=356, рел. 0]; 3. Silence of the Lambs, The (1991) [movieId=593, рел. 0]; 4. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 2]; 5. Star Wars: Episode V - The Empire Strikes Back (1980) [movieId=1196, рел. 2]
- Положительные validation: Mallrats (1995) (180); French Kiss (1995) (236); Star Wars: Episode IV - A New Hope (1977) (260); Shawshank Redemption, The (1994) (318); James and the Giant Peach (1996) (661)
- Вывод: хотя бы один понравившийся фильм найден

**userId 423** · NDCG@10=0.5905698853 · HitRate@10=1.0000000000
- История train: 13; положительных в validation: 2; попаданий: 2.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 0]; 2. Forrest Gump (1994) [movieId=356, рел. 2]; 3. Matrix, The (1999) [movieId=2571, рел. 0]; 4. Pulp Fiction (1994) [movieId=296, рел. 2]; 5. Silence of the Lambs, The (1991) [movieId=593, рел. 0]
- Положительные validation: Pulp Fiction (1994) (296); Forrest Gump (1994) (356)
- Вывод: хотя бы один понравившийся фильм найден

**userId 124** · NDCG@10=0.5870288029 · HitRate@10=1.0000000000
- История train: 30; положительных в validation: 8; попаданий: 4.
- Рекомендации: 1. Forrest Gump (1994) [movieId=356, рел. 2]; 2. Matrix, The (1999) [movieId=2571, рел. 0]; 3. Pulp Fiction (1994) [movieId=296, рел. 2]; 4. Silence of the Lambs, The (1991) [movieId=593, рел. 2]; 5. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 2]
- Положительные validation: Toy Story (1995) (1); Star Wars: Episode IV - A New Hope (1977) (260); Pulp Fiction (1994) (296); Forrest Gump (1994) (356); Silence of the Lambs, The (1991) (593)
- Вывод: хотя бы один понравившийся фильм найден

## 10 проблемных случаев

**userId 318** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 527; положительных в validation: 93; попаданий: 0.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 0]; 2. Braveheart (1995) [movieId=110, рел. 0]; 3. Fight Club (1999) [movieId=2959, рел. 0]; 4. Usual Suspects, The (1995) [movieId=50, рел. 0]; 5. Godfather, The (1972) [movieId=858, рел. 0]
- Положительные validation: Seven (a.k.a. Se7en) (1995) (47); Hate (Haine, La) (1995) (97); Clockers (1995) (159); Monty Python's Life of Brian (1979) (1080); Reservoir Dogs (1992) (1089)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 89** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 323; положительных в validation: 88; попаданий: 0.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 0]; 2. Matrix, The (1999) [movieId=2571, рел. 0]; 3. Pulp Fiction (1994) [movieId=296, рел. 0]; 4. Silence of the Lambs, The (1991) [movieId=593, рел. 0]; 5. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 0]
- Положительные validation: Happy Go Lovely (1951) (3315); Snow Dogs (2002) (5048); Big Fat Liar (2002) (5092); Medallion, The (2003) (6686); Little Murders (1971) (8238)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 606** · NDCG@10=0.1427951440 · HitRate@10=0.0000000000
- История train: 669; положительных в validation: 88; попаданий: 0.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 1]; 2. Braveheart (1995) [movieId=110, рел. 1]; 3. Jurassic Park (1993) [movieId=480, рел. 0]; 4. Toy Story (1995) [movieId=1, рел. 0]; 5. Fugitive, The (1993) [movieId=457, рел. 0]
- Положительные validation: Sense and Sensibility (1995) (17); Twelve Monkeys (a.k.a. 12 Monkeys) (1995) (32); Basketball Diaries, The (1995) (147); Beauty of the Day (Belle de jour) (1967) (154); Before Sunrise (1995) (215)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 610** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 781; положительных в validation: 77; попаданий: 0.
- Рекомендации: 1. Apollo 13 (1995) [movieId=150, рел. 0]; 2. Lion King, The (1994) [movieId=364, рел. 0]; 3. Aladdin (1992) [movieId=588, рел. 0]; 4. Dances with Wolves (1990) [movieId=590, рел. 0]; 5. Princess Bride, The (1987) [movieId=1197, рел. 0]
- Положительные validation: Sexy Beast (2000) (4378); Session 9 (2001) (4725); Zoolander (2001) (4816); Super Troopers (2001) (5110); Blade II (2002) (5254)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 111** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 387; положительных в validation: 69; попаданий: 0.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 0]; 2. Pulp Fiction (1994) [movieId=296, рел. 0]; 3. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 0]; 4. Braveheart (1995) [movieId=110, рел. 0]; 5. Star Wars: Episode V - The Empire Strikes Back (1980) [movieId=1196, рел. 0]
- Положительные validation: Bad Boys (1995) (145); Mrs. Doubtfire (1993) (500); Aladdin (1992) (588); Pretty Woman (1990) (597); Truman Show, The (1998) (1682)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 597** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 277; положительных в validation: 69; попаданий: 0.
- Рекомендации: 1. Shawshank Redemption, The (1994) [movieId=318, рел. 0]; 2. Matrix, The (1999) [movieId=2571, рел. 0]; 3. Pulp Fiction (1994) [movieId=296, рел. 0]; 4. Silence of the Lambs, The (1991) [movieId=593, рел. 0]; 5. Fight Club (1999) [movieId=2959, рел. 0]
- Положительные validation: Nobody's Fool (1994) (281); True Romance (1993) (555); Notorious (1946) (930); Laura (1944) (942); Fish Called Wanda, A (1988) (1079)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 462** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 273; положительных в validation: 59; попаданий: 0.
- Рекомендации: 1. Braveheart (1995) [movieId=110, рел. 0]; 2. Schindler's List (1993) [movieId=527, рел. 0]; 3. Godfather, The (1972) [movieId=858, рел. 0]; 4. Jurassic Park (1993) [movieId=480, рел. 0]; 5. Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981) [movieId=1198, рел. 0]
- Положительные validation: Thin Blue Line, The (1988) (1189); Godfather: Part II, The (1974) (1221); Chinatown (1974) (1252); Deer Hunter, The (1978) (1263); Paradise Lost: The Child Murders at Robin Hood Hills (1996) (1361)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 122** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 175; положительных в validation: 54; попаданий: 0.
- Рекомендации: 1. Braveheart (1995) [movieId=110, рел. 0]; 2. Schindler's List (1993) [movieId=527, рел. 0]; 3. Lord of the Rings: The Fellowship of the Ring, The (2001) [movieId=4993, рел. 0]; 4. Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981) [movieId=1198, рел. 0]; 5. Lord of the Rings: The Return of the King, The (2003) [movieId=7153, рел. 0]
- Положительные validation: From Dusk Till Dawn (1996) (70); Natural Born Killers (1994) (288); Demolition Man (1993) (442); True Romance (1993) (555); Cable Guy, The (1996) (784)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 477** · NDCG@10=0.0000000000 · HitRate@10=0.0000000000
- История train: 360; положительных в validation: 54; попаданий: 0.
- Рекомендации: 1. Braveheart (1995) [movieId=110, рел. 0]; 2. Fight Club (1999) [movieId=2959, рел. 0]; 3. Usual Suspects, The (1995) [movieId=50, рел. 0]; 4. Schindler's List (1993) [movieId=527, рел. 0]; 5. Godfather, The (1972) [movieId=858, рел. 0]
- Положительные validation: Powder (1995) (24); Screamers (1995) (76); Living in Oblivion (1995) (176); Airheads (1994) (413); Blade Runner (1982) (541)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

**userId 221** · NDCG@10=0.0965076627 · HitRate@10=0.0000000000
- История train: 198; положительных в validation: 53; попаданий: 0.
- Рекомендации: 1. Forrest Gump (1994) [movieId=356, рел. 1]; 2. Matrix, The (1999) [movieId=2571, рел. 0]; 3. Star Wars: Episode IV - A New Hope (1977) [movieId=260, рел. 0]; 4. Braveheart (1995) [movieId=110, рел. 0]; 5. Star Wars: Episode V - The Empire Strikes Back (1980) [movieId=1196, рел. 0]
- Положительные validation: Fresh (1994) (456); Terminator 2: Judgment Day (1991) (589); Some Like It Hot (1959) (910); Maltese Falcon, The (1941) (913); Sunset Blvd. (a.k.a. Sunset Boulevard) (1950) (922)
- Вывод: ни один положительный holdout не найден; глобальный рейтинг не учитывает индивидуальный вкус

## Что показывает baseline

Высокие значения достигаются, когда личный интерес случайно совпадает с популярными фильмами. Ошибки возникают из-за отсутствия персонализации: для всех пользователей используется один глобальный порядок, кроме исключения фильмов из обучающей истории.
**Гипотеза для следующего эксперимента:** content-based профиль пользователя по жанрам и косинусное сходство на тех же train и validation.
