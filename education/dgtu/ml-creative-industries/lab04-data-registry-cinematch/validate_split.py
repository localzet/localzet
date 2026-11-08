#!/usr/bin/env python3
"""Временной group split CineMatch (ЛР 4). CSV загружается отдельно из GroupLens."""
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path


def make_split(rows):
    # Сначала устраняем повторные (userId, movieId), оставляя последнее событие.
    latest = {}
    for row in rows:
        key = (int(row["userId"]), int(row["movieId"]))
        stamp = int(row["timestamp"])
        if key not in latest or stamp >= int(latest[key]["timestamp"]):
            latest[key] = row

    users = defaultdict(lambda: defaultdict(list))
    for row in latest.values():
        users[int(row["userId"])][int(row["timestamp"])].append(row)

    assigned = {"train": [], "validation": [], "test": []}
    skipped_users = 0
    for user_id, time_groups in sorted(users.items()):
        stamps = sorted(time_groups)
        n = len(stamps)
        if n < 3:
            skipped_users += 1
            continue
        n_train = max(1, int(n * 0.60))
        n_val = max(1, int(n * 0.20))
        if n_train + n_val >= n:
            n_train, n_val = n - 2, 1
        for i, timestamp in enumerate(stamps):
            part = ("train" if i < n_train else
                    "validation" if i < n_train + n_val else "test")
            assigned[part].extend(time_groups[timestamp])

    pair_keys = {}
    time_keys = {}
    for part, segment in assigned.items():
        pair_keys[part] = {
            (int(r["userId"]), int(r["movieId"])) for r in segment
        }
        time_keys[part] = {
            (int(r["userId"]), int(r["timestamp"])) for r in segment
        }
        assert len(pair_keys[part]) == len(segment), f"Повтор пары в {part}"

    parts = list(assigned)
    for i, part_a in enumerate(parts):
        for part_b in parts[i + 1:]:
            assert pair_keys[part_a].isdisjoint(pair_keys[part_b]), "Утечка user+movie"
            assert time_keys[part_a].isdisjoint(time_keys[part_b]), "Утечка user+timestamp"

    for user_id in users:
        periods = []
        for part in parts:
            times = [
                int(x["timestamp"]) for x in assigned[part]
                if int(x["userId"]) == user_id
            ]
            if times:
                periods.append((part, min(times), max(times)))
        if periods:
            assert len(periods) == 3, f"Неполное разбиение пользователя {user_id}"
            assert periods[0][2] < periods[1][1] < periods[2][1], (
                "Нарушена временная очередность"
            )

    return assigned, skipped_users, len(latest)


def self_test():
    rows = []
    for uid in range(1, 5):
        for ts in range(100, 107):
            for offset in (0, 1):
                rows.append({
                    "userId": str(uid),
                    "movieId": str(ts * 10 + offset),
                    "rating": "4.0",
                    "timestamp": str(ts),
                })
    rows.append(rows[0].copy())
    assigned, skipped, unique_count = make_split(rows)
    assert skipped == 0 and unique_count == 56
    assert sum(map(len, assigned.values())) == 56
    print("SELF-TEST PASS: синтетические записи, нет пересечений")
    print({key: len(value) for key, value in assigned.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ratings", nargs="?", type=Path, help="путь к ratings.csv")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.ratings is None:
        parser.error("укажите ratings.csv либо --self-test")
    payload = args.ratings.read_bytes()
    with args.ratings.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    expected = {"userId", "movieId", "rating", "timestamp"}
    assert rows and expected.issubset(rows[0]), "Неверная схема файла"
    assigned, skipped, unique_count = make_split(rows)
    print("SOURCE SHA-256:", hashlib.sha256(payload).hexdigest())
    print("RAW rows:", len(rows), "unique user+movie:", unique_count)
    print("Excluded users (<3 timestamps):", skipped)
    print("Split rows:", {k: len(v) for k, v in assigned.items()})
    print("Eligible rows:", sum(map(len, assigned.values())))
    print("PASS: нет пересечений и временной утечки")
    print("Оценка качества модели этим скриптом не выполняется")


if __name__ == "__main__":
    main()
