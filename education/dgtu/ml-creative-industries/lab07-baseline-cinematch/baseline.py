#!/usr/bin/env python3
"""CineMatch, ЛР 7: детерминированный baseline популярности для MovieLens.

Скрипт использует ровно тот же split, что и ЛР 6. Для единого источника
правды предобработка импортируется из соседней директории ЛР 6.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path

VERSION = "cinematch-popularity-baseline-v1.0.0"
K = 10
POSITIVE_THRESHOLD = 4.0
LABEL_RULE = "lab06-grade-v1"
TIE_BREAK = "movieId ascending"


def load_lab6_module():
    path = Path(__file__).resolve().parent.parent / "lab06-labeling-cinematch" / "prepare_dataset.py"
    if not path.exists():
        raise FileNotFoundError(
            f"Не найден модуль ЛР 6: {path}. "
            "Для воспроизведения клонируйте целиком репозиторий localzet/localzet."
        )
    spec = importlib.util.spec_from_file_location("cinematch_lab6_prepare", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def prepare_if_needed(prepared_dir: Path, source: str | None):
    """Проверяем те же raw bytes и единый split ЛР 6, без двойной загрузки."""
    lab6 = load_lab6_module()
    payloads, origin = lab6.retrieve(source)
    if source is not None or not (prepared_dir / "manifest.json").exists():
        lab6.prepare(payloads, prepared_dir, origin)
    manifest = json.loads((prepared_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest["version"] != lab6.VERSION:
        raise ValueError("Неподдерживаемая версия clean data, требуется " + lab6.VERSION)
    for name in ("train.csv", "validation.csv"):
        actual = hashlib.sha256((prepared_dir/name).read_bytes()).hexdigest()
        expected = manifest["output_sha256"].get(name)
        if expected != actual:
            raise ValueError(f"Не совпадает контрольная сумма {name}; подготовьте split заново")
    if manifest["source_git_blob_sha1"] != lab6.GIT_BLOBS:
        raise ValueError("В prepared другой исходный MovieLens")
    # Контроль пересечений train/validation без чтения test.
    train, valid = (read_csv(prepared_dir / f"{part}.csv") for part in ("train", "validation"))
    for rows, name in ((train, "train"), (valid, "validation")):
        if len(rows) != manifest["split_counts"][name]:
            raise ValueError(f"Количество {name} отличается от manifest.json")
    train_pairs={(int(r["userId"]),int(r["movieId"])) for r in train}
    val_pairs={(int(r["userId"]),int(r["movieId"])) for r in valid}
    train_times={(int(r["userId"]),int(r["timestamp"])) for r in train}
    val_times={(int(r["userId"]),int(r["timestamp"])) for r in valid}
    if len(train_pairs)!=len(train) or len(val_pairs)!=len(valid):
        raise ValueError("Дубли пар userId+movieId в split")
    if not train_pairs.isdisjoint(val_pairs) or not train_times.isdisjoint(val_times):
        raise ValueError("Утечка: пересечение train / validation")
    train_max = {}
    for r in train:
        uid,t=int(r["userId"]),int(r["timestamp"])
        train_max[uid]=max(t,train_max.get(uid,-1))
    if any(train_max.get(int(r["userId"]),-1)>=int(r["timestamp"]) for r in valid):
        raise ValueError("Нарушен хронологический порядок train / validation")
    return payloads, manifest


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def parse_interactions(rows: list[dict]) -> list[dict]:
    parsed = []
    for row in rows:
        r = {"source_row": int(row["source_row"]),
             "userId": int(row["userId"]),
             "movieId": int(row["movieId"]),
             "rating": float(row["rating"]),
             "timestamp": int(row["timestamp"]),
             "relevance": int(row["relevance"]),
             "positive": int(row["positive"]),
             "split": row["split"]}
        assert r["positive"] == int(r["rating"] >= POSITIVE_THRESHOLD)
        parsed.append(r)
    return parsed


def build_scores(train: list[dict], catalog_ids: set[int]) -> dict[int, int]:
    """Только положительные оценки train. Никакой параметр не fit-ится по val/test."""
    result = Counter(row["movieId"] for row in train if row["positive"])
    assert set(result).issubset(catalog_ids)
    return dict(result)


def rank_catalog(scores: dict[int,int], catalog_ids: set[int]) -> list[int]:
    """От большего числа лайков к меньшему; tie по числовому movieId."""
    return sorted(catalog_ids, key=lambda mid: (-scores.get(mid, 0), mid))


def top_k(global_ranking: list[int], already_rated: set[int], k: int=K) -> list[int]:
    if k < 1:
        raise ValueError("k должно быть положительным")
    out = []
    for mid in global_ranking:
        if mid not in already_rated:
            out.append(mid)
            if len(out) == k:
                break
    return out


def gain(label: int) -> int:
    return 2**label - 1


def dcg_at_k(labels: list[int], k: int=K) -> float:
    return sum(gain(rel) / math.log2(i + 2) for i, rel in enumerate(labels[:k]))


def evaluate_user(recs: list[int], validation: list[dict], k: int=K) -> dict:
    """Неоценённые кандидаты = unjudged, нулевой вклад в *офлайн*-метрику.

    Это НЕ утверждение о негативных предпочтениях пользователя.
    """
    gt = {r["movieId"]: r["relevance"] for r in validation}
    labels = [gt.get(mid, 0) for mid in recs]
    ideal = sorted((r["relevance"] for r in validation), reverse=True)[:k]
    ideal_dcg = dcg_at_k(ideal, k)
    ndcg = dcg_at_k(labels, k) / ideal_dcg if ideal_dcg > 0 else None
    n_positive = sum(1 for r in validation if r["relevance"] == 2)
    n_hit = sum(1 for mid in recs if gt.get(mid) == 2)
    recall = n_hit / n_positive if n_positive else None
    hitrate = float(n_hit > 0) if n_positive else None
    return {
        "ndcg_at_10": ndcg,
        "recall_at_10": recall,
        "hitrate_at_10": hitrate,
        "positive_holdout": n_positive,
        "matched_positive": n_hit,
        "holdout_judged": len(validation),
        "recommended_labels": labels,
    }


def mean_defined(values):
    nums = [v for v in values if v is not None]
    return sum(nums) / len(nums) if nums else None


def serialize_float(x):
    return "" if x is None else f"{x:.10f}"


def settings_dict(manifest: dict) -> dict:
    return {
        "version": VERSION,
        "data_version": manifest["version"],
        "input_git_blob_sha1": manifest["source_git_blob_sha1"],
        "split_method": "per-user temporal groups 60/20/20, as in Lab 6",
        "split_counts": {k:manifest["split_counts"][k] for k in ("train","validation","test")},
        "evaluation_split": "validation_only",
        "catalog_universe": "all movieIds from movies.csv",
        "score": "number of train ratings >= 4.0 for each film",
        "exclude_seen": "only user's train-rated movieIds",
        "k": K,
        "tie_break": TIE_BREAK,
        "label_rule": LABEL_RULE,
        "evaluation": "macro per user, unjudged candidates contribute zero gain only in offline proxy",
        "ndcg_gain": "2**relevance-1; discount log2(rank+1), relevance 0,1,2",
        "recall_hitrate_positive": "relevance == 2",
        "evaluation_denominators": "NDCG among users with IDCG>0; recall/HR among users with positive holdout",
        "seed": None,
        "randomness": "none",
        "test_used": False,
    }


def render_case(case: dict, movies: dict[int,str], detail:dict) -> str:
    recs = detail["recommendations"]
    matched = [x for x in recs if x["relevance"] == 2]
    holdouts = detail["validation_positives"]
    return "\n".join([
        f"**userId {case['userId']}** · NDCG@10={serialize_float(case['ndcg_at_10']) or 'N/A'} · HitRate@10={serialize_float(case['hitrate_at_10']) or 'N/A'}",
        f"- История train: {case['train_count']}; положительных в validation: {case['positive_holdout']}; попаданий: {case['matched_positive']}.",
        "- Рекомендации: " + "; ".join(f"{x['rank']}. {movies.get(x['movieId'],'?')} [movieId={x['movieId']}, рел. {x['relevance']}]" for x in recs[:5]),
        "- Положительные validation: " + ("; ".join(f"{movies.get(mid,'?')} ({mid})" for mid in holdouts[:5]) or "нет"),
        "- Вывод: " + ("хотя бы один понравившийся фильм найден" if matched else "не найден ни один положительный holdout; общая популярность не отражает интересы этого пользователя"),
    ])


def generate_output(train, validation, movies, manifest, output: Path):
    assert train and validation and movies
    train_by_user = defaultdict(list)
    val_by_user = defaultdict(list)
    for r in train: train_by_user[r["userId"]].append(r)
    for r in validation: val_by_user[r["userId"]].append(r)
    assert set(val_by_user).issubset(set(train_by_user))
    scores = build_scores(train, set(movies))
    global_ranking = rank_catalog(scores, set(movies))
    cfg = settings_dict(manifest)
    cfg_hash = hashlib.sha256(json.dumps(cfg, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    results = []
    details = []
    for uid in sorted(val_by_user):
        already = {r["movieId"] for r in train_by_user[uid]}
        recs = top_k(global_ranking, already, K)
        assert len(recs) == K and not set(recs).intersection(already)
        evaluated = evaluate_user(recs, val_by_user[uid], K)
        grades = {r["movieId"]:r["relevance"] for r in val_by_user[uid]}
        vals = {
            "userId": uid,
            "train_count": len(train_by_user[uid]),
            "validation_count": len(val_by_user[uid]),
            "positive_holdout": evaluated["positive_holdout"],
            "matched_positive": evaluated["matched_positive"],
            "ndcg_at_10": evaluated["ndcg_at_10"],
            "recall_at_10": evaluated["recall_at_10"],
            "hitrate_at_10": evaluated["hitrate_at_10"],
            "recommended_movie_ids": ";".join(map(str,recs)),
            "recommended_relevance": ";".join(map(str,evaluated["recommended_labels"])),
        }
        results.append(vals)
        details.append({
            "userId": uid,
            "train_count": vals["train_count"],
            "validation_count": vals["validation_count"],
            "validation_positives": sorted(mid for mid,g in grades.items() if g == 2),
            "recommendations": [{"rank": i+1, "movieId": mid,
                "title":movies[mid], "train_positive_count": scores.get(mid,0),
                "relevance": grades.get(mid, 0),
                "judged_in_validation": mid in grades}
                for i,mid in enumerate(recs)],
        })
    output.mkdir(parents=True,exist_ok=True)
    columns = ["userId","train_count","validation_count","positive_holdout","matched_positive",
               "ndcg_at_10","recall_at_10","hitrate_at_10","recommended_movie_ids","recommended_relevance"]
    with (output/"validation_cases.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
        for case in results:
            writer.writerow({k:serialize_float(case[k]) if k in ("ndcg_at_10","recall_at_10","hitrate_at_10") else case[k] for k in columns})
    with (output/"validation_detail.jsonl").open("w",encoding="utf-8") as f:
        for d in details: f.write(json.dumps(d,ensure_ascii=False,sort_keys=True)+"\n")
    def average(field):return mean_defined([r[field] for r in results])
    metrics = {
        "baseline": VERSION,
        "data_version": manifest["version"],
        "settings_sha256": cfg_hash,
        "evaluated_users": len(results),
        "users_with_positive_holdout": sum(r["positive_holdout"]>0 for r in results),
        "users_with_graded_holdout": sum(r["ndcg_at_10"] is not None for r in results),
        "train_rows":len(train),"validation_rows":len(validation),
        "unique_catalog_movies":len(movies),
        "train_scored_movies":sum(x>0 for x in scores.values()),
        "mean_ndcg_at_10":average("ndcg_at_10"),
        "mean_recall_at_10":average("recall_at_10"),
        "mean_hitrate_at_10":average("hitrate_at_10"),
        "users_with_hit": sum(r["matched_positive"]>0 for r in results),
        "test_used_for_model_or_scoring":False,
        "evaluation_caveat":"Offline proxy: missing ratings are unjudged, not proven negatives.",
    }
    (output/"metrics.json").write_text(json.dumps(metrics,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (output/"settings.json").write_text(json.dumps(cfg,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (output/"environment.json").write_text(json.dumps({"python":platform.python_version(),"implementation":platform.python_implementation(),"stdlib_only":True},indent=2)+"\n",encoding="utf-8")
    successes=sorted([x for x in results if x["matched_positive"]>0],key=lambda x:(-x["ndcg_at_10"],x["userId"]))[:10]
    failures=sorted([x for x in results if x["positive_holdout"]>0 and x["matched_positive"]==0],key=lambda x:(-x["positive_holdout"],x["userId"]))[:10]
    by_user={d["userId"]:d for d in details}
    lines=["# ЛР 7 · Удачные и проблемные результаты validation", "", 
        "Случаи взяты из полного машинного файла validation_cases.csv; критерий успеха — совпадение хотя бы с одним положительным фильмом в validation.",
        "В примерах `рел. 0` может означать **неизвестную** оценку, а не явно отрицательную.", "",
        "## 10 успехов",""]
    lines += [render_case(x,movies,by_user[x["userId"]])+"\n" for x in successes]
    lines += ["## 10 проблемных случаев", ""]
    lines += [render_case(x,movies,by_user[x["userId"]])+"\n" for x in failures]
    if len(successes)<10 or len(failures)<10:
        lines += [f"Ограничение размера выборки: успешных={len(successes)}, проблемных={len(failures)}."]
    lines += ["## Интерпретация", "", 
              "Удача достигается за счёт совпадения индивидуальных предпочтений с общим трендом.",
              "Неудачи показывают отсутствие персонализации: один порядок фильмов для всех, кроме исключения уже оценённого.",
              "Следующая гипотеза для ЛР 8: профиль пользователя по любимым жанрам и TF-IDF/cosine ranking на прежнем split."]
    (output/"cases.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return metrics


def run(source: str | None, prepared: Path, output: Path) -> None:
    payloads, manifest = prepare_if_needed(prepared, source)
    train=parse_interactions(read_csv(prepared/"train.csv"))
    validation=parse_interactions(read_csv(prepared/"validation.csv"))
    # Catalog extracted from the same frozen source as Lab 6, never other dataset.
    lab6=load_lab6_module()
    movies={int(r["movieId"]):r["title"] for r in lab6.read_csv(payloads["movies.csv"])}
    metrics=generate_output(train,validation,movies,manifest,output)
    print(json.dumps(metrics,ensure_ascii=False,indent=2))
    print("\nГотово:",output.resolve())


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",help="каталог ml-latest-small или ZIP; иначе загрузка зеркала с проверкой SHA")
    parser.add_argument("--prepared",type=Path,default=Path("prepared"))
    parser.add_argument("--output",type=Path,default=Path("results"))
    args=parser.parse_args()
    try:
        run(args.source,args.prepared,args.output)
    except (OSError,RuntimeError,ValueError,AssertionError) as exc:
        parser.exit(2,f"Baseline не выполнен: {exc}\n")


if __name__=="__main__":main()