"""Проверки ЛР № 6. Выполнить: python -m unittest -v test_prepare"""
from __future__ import annotations

import unittest
from copy import deepcopy
from prepare_dataset import (
    assert_safe_split, chronological_split, clean_ratings,
    grade, independent_grade, pilot, train_only_idf,
)

class PreparationTests(unittest.TestCase):
    def test_every_half_star_boundary(self):
        for n in range(1, 11):
            r = n / 2
            self.assertEqual(grade(r), independent_grade(r))
        self.assertIsNone(grade(None))
        for bad in (0, 5.5, 3.14):
            with self.assertRaises(ValueError): grade(bad)

    def make_rows(self):
        rows = []
        for user in (1, 2, 3):
            for time in range(100, 108):
                rows.append({"userId":str(user), "movieId":str(user*100 + time),
                             "rating":str([2.5, 3.0, 4.0][time % 3]),"timestamp":str(time)})
        return rows

    def test_dedup_and_chronology(self):
        raw = self.make_rows()
        raw.append(dict(raw[0]))
        records, excluded = clean_ratings(raw, {int(r["movieId"]) for r in raw})
        self.assertEqual(len(records), 24)
        self.assertEqual(len(excluded), 1)
        records, incomplete = chronological_split(records)
        self.assertEqual(incomplete, 0)
        self.assertEqual(assert_safe_split(records), {"train":12, "validation":3, "test":9})

    def test_ties_remain_in_one_split(self):
        raw = self.make_rows()
        raw.append({"userId":"1", "movieId":"9999", "rating":"4.0", "timestamp":"101"})
        records, _ = clean_ratings(raw, {int(r["movieId"]) for r in raw})
        records,_ = chronological_split(records)
        self.assertEqual(assert_safe_split(records)["train"],13)
        same_time = {r["split"] for r in records if r["userId"] == 1 and r["timestamp"] == 101}
        self.assertEqual(same_time,{"train"})

    def test_idf_ignores_test_movies(self):
        items = [dict(userId=1,movieId=1, rating=5.0, timestamp=1, relevance=2, positive=1,split="train"),
                 dict(userId=1,movieId=2, rating=4.0, timestamp=2, relevance=2, positive=1,split="test")]
        movies = {1:{"genres":"Comedy|Drama"},2:{"genres":"Thriller"}}
        before = train_only_idf(items,movies)
        modified = deepcopy(movies)
        modified[2]["genres"] = "UNSEEN_FUTURE_ONLY_TOKEN"
        self.assertEqual(before,train_only_idf(items,modified))
        self.assertNotIn("UNSEEN_FUTURE_ONLY_TOKEN",before["idf"])

    def test_pilot_stratified_train_only(self):
        rows=[]
        for i in range(60):
            value = (1.0, 3.5, 4.5)[i%3]
            rows.append(dict(source_row=i+1,userId=i+1,movieId=i+1,rating=value,
                             timestamp=i,relevance=grade(value),positive=int(value>=4),split="train"))
        rows.append(dict(source_row=99,userId=99,movieId=99,rating=5.0,
                         timestamp=99,relevance=2,positive=1,split="test"))
        labels=pilot(rows)
        self.assertEqual(len(labels),12)
        self.assertEqual([sum(x["label_v1"] == g for x in labels) for g in (0,1,2)],[4,4,4])
        self.assertTrue(all(x["source_row"] != 99 for x in labels))

if __name__ == "__main__":
    unittest.main()