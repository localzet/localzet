#!/usr/bin/env python3
"""CineMatch / ЛР 6: проверяемая разметка и хронологический split MovieLens."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import Request, urlopen
from time import sleep

VERSION = "cinematch-labels-v1.0.0"
DATA_FILES = ("movies.csv", "ratings.csv", "tags.csv", "links.csv")
GIT_BLOBS = {
    "movies.csv": "2c1b2e74fe24d0fc851aa9745702fcd7777f690a",
    "ratings.csv": "51974adb19938bda0e00b2d8c051438fb33893f0",
    "tags.csv": "224e0c167e6cdd71ec4c6fd9da208ee5a286caaf",
    "links.csv": "d5ccfdf196ebe5b7bbd09d505ea8ca263ecc33ae",
}
OFFICIAL_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
MIRROR_URL = "https://raw.githubusercontent.com/smanihwr/ml-latest-small/master/"
PILOT_FRACTIONS = (0.10, 0.37, 0.63, 0.90)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def verify_source(files: dict[str, bytes], origin: str) -> None:
    """Не допускаем незаметной смены версии CSV при смене сервера."""
    for name in DATA_FILES:
        if name not in files:
            raise ValueError(f"Нет файла {name} в источнике {origin}")
        actual = git_blob_sha(files[name])
        if actual != GIT_BLOBS[name]:
            raise ValueError(
                f"Контрольная сумма {name} из {origin} не совпадает: "
                f"{actual} (ожидали {GIT_BLOBS[name]}). "
                "Нужен датасет зафиксированной версии; не отключайте эту проверку."
            )


def retrieve(source: str | None) -> tuple[dict[str, bytes], str]:
    """Сначала зафиксированное зеркало, затем официальный архив или локальный ZIP."""
    if source:
        path = Path(source).expanduser()
        if path.is_dir():
            files = {name: (path / name).read_bytes() for name in DATA_FILES}
        elif path.is_file() and zipfile.is_zipfile(path):
            with zipfile.ZipFile(path) as z:
                files = {name: z.read(f"ml-latest-small/{name}") for name in DATA_FILES}
        else:
            raise ValueError(
                "--source: нужен каталог с четырьмя CSV или файл ml-latest-small.zip; "
                f"получено {path!s}"
            )
        verify_source(files, str(path))
        return files, str(path)

    def fetch(url: str) -> bytes:
        last_error = None
        for attempt in range(2):
            try:
                with urlopen(Request(url, headers={"User-Agent": "CineMatch-educational-audit/1.0"}), timeout=30) as r:
                    return r.read()
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    sleep(1)
        raise RuntimeError(f"Не удалось скачать {url}: {last_error}") from last_error

    failures = []
    for origin in ("GitHub (проверенная версия)", "GroupLens (официальный архив)"):
        try:
            if origin.startswith("GitHub"):
                files = {name: fetch(MIRROR_URL + name) for name in DATA_FILES}
            else:
                with zipfile.ZipFile(io.BytesIO(fetch(OFFICIAL_URL))) as z:
                    files = {name: z.read(f"ml-latest-small/{name}") for name in DATA_FILES}
            verify_source(files, origin)
            print(f"Источник данных: {origin}; SHA подтверждён", flush=True)
            return files, origin
        except Exception as exc:
            failures.append(f"{origin}: {type(exc).__name__}: {exc}")
            print(f"Источник недоступен/не прошёл проверку: {failures[-1]}", flush=True)

    raise RuntimeError(
        "DATA_SOURCE_UNAVAILABLE: не удалось получить проверенную версию MovieLens.\n"
        + "\n".join(failures)
        + "\nМожно загрузить файл ml-latest-small.zip с GroupLens в Colab "
        "и повторить запуск с --source ml-latest-small.zip. "
        "Если контрольная сумма официального архива не совпадает с зафиксированным зеркалом, "
        "не отключайте проверку: используйте проверенную версию или обновите Data Card."
    )


def read_csv(payload: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(payload.decode("utf-8-sig"))))


def grade(rating: float | None) -> int | None:
    if rating is None:
        return None  # unjudged != 0
    if not 0.5 <= rating <= 5 or rating * 2 != int(rating * 2):
        raise ValueError(f"Некорректная оценка: {rating}")
    return 2 if rating >= 4 else 1 if rating >= 3 else 0


def independent_grade(rating: float) -> int:
    """Независимая реализация через целочисленные полузвёзды (не человек)."""
    halves = int(round(rating * 2))
    assert 1 <= halves <= 10
    return 0 if halves <= 5 else 1 if halves <= 7 else 2


def clean_ratings(raw: list[dict[str, str]], movie_ids: set[int]):
    latest: dict[tuple[int, int], dict] = {}
    exclusions: list[dict] = []
    for index, row in enumerate(raw, start=1):
        try:
            uid, mid = int(row["userId"]), int(row["movieId"])
            timestamp, rating = int(row["timestamp"]), float(row["rating"])
            if uid <= 0 or mid <= 0 or timestamp < 0 or mid not in movie_ids:
                raise ValueError("неверная ссылка / идентификатор / время")
            label = grade(rating)
        except (ValueError, TypeError, KeyError) as error:
            exclusions.append({"source_row": index, "reason": "invalid_row", "details": str(error)})
            continue
        record = {"source_row": index, "userId": uid, "movieId": mid,
                  "rating": rating, "timestamp": timestamp,
                  "relevance": label, "positive": int(label == 2)}
        key = (uid, mid)
        if key in latest:
            old = latest[key]
            if (timestamp, index) > (old["timestamp"], old["source_row"]):
                exclusions.append({"source_row": old["source_row"], "reason": "superseded_user_movie", "details": ""})
                latest[key] = record
            else:
                exclusions.append({"source_row": index, "reason": "superseded_user_movie", "details": ""})
        else:
            latest[key] = record
    return sorted(latest.values(), key=lambda r: (r["userId"], r["timestamp"], r["movieId"])), exclusions


def chronological_split(records: list[dict]) -> tuple[list[dict], int]:
    by_user = defaultdict(lambda: defaultdict(list))
    for row in records:
        by_user[row["userId"]][row["timestamp"]].append(row)
    not_evaluable = 0
    for user, timestamps in by_user.items():
        times = sorted(timestamps)
        n = len(times)
        if n < 3:
            not_evaluable += 1
            for t in times:
                for row in timestamps[t]:
                    row["split"] = "not_evaluable"
            continue
        n_train, n_val = max(1, int(n * 0.60)), max(1, int(n * 0.20))
        if n_train + n_val >= n:
            n_train, n_val = n - 2, 1
        for i, t in enumerate(times):
            split = "train" if i < n_train else "validation" if i < n_train + n_val else "test"
            for row in timestamps[t]:
                row["split"] = split
    return records, not_evaluable


def assert_safe_split(records: list[dict]) -> dict[str, int]:
    groups = defaultdict(set)
    pairs = defaultdict(set)
    split_count = Counter()
    by_user = defaultdict(lambda: defaultdict(list))
    for r in records:
        split = r["split"]
        split_count[split] += 1
        pair = (r["userId"], r["movieId"])
        group = (r["userId"], r["timestamp"])
        assert pair not in pairs[split], "повтор одной оценки внутри split"
        pairs[split].add(pair)
        groups[split].add(group)
        by_user[r["userId"]][split].append(r["timestamp"])
    names = list(split_count)
    for i, name in enumerate(names):
        for other in names[i+1:]:
            assert groups[name].isdisjoint(groups[other]), "одновременные оценки разорваны"
            assert pairs[name].isdisjoint(pairs[other]), "пара user+movie попала в два split"
    for user, parts in by_user.items():
        if "not_evaluable" in parts:
            assert len(parts) == 1
        else:
            assert max(parts["train"]) < min(parts["validation"]) < min(parts["test"]), user
    return dict(split_count)


def train_only_idf(records: list[dict], movies: dict[int, dict[str, str]]) -> dict:
    # Одна запись TF-IDF на фильм, а не на каждую его пользовательскую оценку.
    train_ids = {r["movieId"] for r in records if r["split"] == "train"}
    df = Counter()
    for movie_id in train_ids:
        genres = movies[movie_id]["genres"]
        if genres == "(no genres listed)":
            continue
        df.update(set(genres.split("|")))
    n_docs = len(train_ids)
    return {"n_train_movies": n_docs, "idf": {
        g: round(math.log((1 + n_docs) / (1 + count)) + 1, 12)
        for g, count in sorted(df.items())}}


def pilot(records: list[dict]) -> list[dict]:
    bins = defaultdict(list)
    for r in records:
        if r["split"] == "train":
            bins[r["relevance"]].append(r)
    out = []
    for grade_value in (0, 1, 2):
        rows = sorted(bins[grade_value], key=lambda r: r["source_row"])
        if len(rows) < 4:
            raise ValueError("Слишком мало обучающих наблюдений для пилота")
        for fraction in PILOT_FRACTIONS:
            r = rows[int((len(rows) - 1) * fraction)]
            out.append({"source_row": r["source_row"], "rating": r["rating"],
                        "label_v1": grade(r["rating"]), "control_label": independent_grade(r["rating"]),
                        "split": "train", "agreement": True})
    out.sort(key=lambda r: r["source_row"])
    for i,r in enumerate(out, 1):
        r["pilot_id"] = f"R{i:02d}"
    assert len({r["source_row"] for r in out}) == len(out)
    assert all(r["label_v1"] == r["control_label"] for r in out)
    return out


def write_csv(path: Path, records: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def prepare(payloads: dict[str, bytes], output: Path, source: str):
    movies_rows = read_csv(payloads["movies.csv"])
    ratings_rows = read_csv(payloads["ratings.csv"])
    movies = {int(row["movieId"]): row for row in movies_rows}
    assert len(movies) == len(movies_rows), "повтор movieId"
    records, excluded = clean_ratings(ratings_rows, set(movies))
    records, unevaluable = chronological_split(records)
    split_counts = assert_safe_split(records)
    idf = train_only_idf(records, movies)
    p = pilot(records)
    output.mkdir(parents=True, exist_ok=True)
    columns = ["source_row", "userId", "movieId", "rating", "timestamp", "relevance", "positive", "split"]
    write_csv(output / "clean_interactions.csv", records, columns)
    for part in ("train", "validation", "test", "not_evaluable"):
        write_csv(output / f"{part}.csv", [r for r in records if r["split"] == part], columns)
    write_csv(output / "exclusions.csv", excluded, ["source_row", "reason", "details"])
    write_csv(output / "pilot_labels.csv", p, ["pilot_id", "source_row", "rating", "label_v1", "control_label", "split", "agreement"])
    (output / "train_idf.json").write_text(json.dumps(idf, ensure_ascii=False, indent=2), encoding="utf-8")
    label_counts = {part:{str(j):sum(1 for r in records if r["split"] == part and r["relevance"] == j)
                          for j in (0,1,2)} for part in ("train", "validation", "test")}
    manifest = {
        "version": VERSION, "source": source, "observed_raw_ratings": len(ratings_rows),
        "observed_clean_ratings": len(records), "exclusions": len(excluded),
        "not_evaluable_users": unevaluable, "split_counts": split_counts,
        "class_counts_by_split": label_counts,
        "pilot_items": len(p), "pilot_automatic_rule_agreement": sum(x["agreement"] for x in p),
        "independent_human_raters": 0,
        "input_sha256": {n:hashlib.sha256(b).hexdigest() for n,b in payloads.items()},
        "source_git_blob_sha1": GIT_BLOBS,
        "idf_fit": "train-only unique movie genre strings",
        "train_unique_movies": idf["n_train_movies"],
        "output_sha256": {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(output.iterdir()) if p.is_file() and p.name != "manifest.json"},
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:manifest[k] for k in (
        "version","observed_raw_ratings","observed_clean_ratings","exclusions","split_counts","class_counts_by_split", "pilot_items", "pilot_automatic_rule_agreement")}, ensure_ascii=False, indent=2))
    return manifest


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", help="ml-latest-small.zip или каталог ml-latest-small; иначе загрузка")
    ap.add_argument("--output", default="prepared", help="папка для локальных производных данных")
    args = ap.parse_args()
    payloads, source = retrieve(args.source)
    prepare(payloads, Path(args.output), source)


if __name__ == "__main__":
    main()