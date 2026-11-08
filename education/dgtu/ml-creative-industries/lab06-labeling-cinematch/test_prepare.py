"""Проверки ЛР № 6. Выполнить: python -m unittest -v test_prepare"""
from __future__ import annotations

import unittest
from unittest.mock import patch
from copy import deepcopy
from prepare_dataset import (
    assert_safe_split, chronological_split, clean_ratings,
    grade, independent_grade, pilot, train_only_idf,
    git_blob_sha, retrieve, verify_source, DATA_FILES,
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


    def fixture_files(self):
        return {
            "movies.csv": b"movieId,title,genres\n1,Example (2000),Drama\n",
            "ratings.csv": b"userId,movieId,rating,timestamp\n1,1,4.0,101\n",
            "tags.csv": b"userId,movieId,tag,timestamp\n",
            "links.csv": b"movieId,imdbId,tmdbId\n",
        }

    def test_source_sha_rejects_corruption(self):
        files = self.fixture_files()
        expected = {name: git_blob_sha(blob) for name, blob in files.items()}
        with patch.dict("prepare_dataset.GIT_BLOBS", expected):
            verify_source(files, "fixture")
            wrong = dict(files, **{"ratings.csv": files["ratings.csv"] + b"\n"})
            with self.assertRaisesRegex(ValueError, "Контрольная сумма"):
                verify_source(wrong, "fixture")

    def test_retrieve_prefers_fixed_mirror(self):
        files = self.fixture_files()
        expected = {name: git_blob_sha(blob) for name, blob in files.items()}

        class Response:
            def __init__(self, payload):
                self.payload = payload
            def __enter__(self):
                return self
            def __exit__(self, *args):
                return False
            def read(self):
                return self.payload

        def fetch(request, timeout):
            name = request.full_url.rsplit("/", 1)[-1]
            self.assertIn(name, DATA_FILES)
            return Response(files[name])

        with patch.dict("prepare_dataset.GIT_BLOBS", expected), patch("prepare_dataset.urlopen", side_effect=fetch):
            payloads, origin = retrieve(None)
        self.assertEqual(payloads, files)
        self.assertIn("GitHub", origin)

    def test_retrieve_explains_offline_failure(self):
        with patch("prepare_dataset.urlopen", side_effect=OSError("offline")), patch("prepare_dataset.sleep"):
            with self.assertRaisesRegex(RuntimeError, "DATA_SOURCE_UNAVAILABLE") as caught:
                retrieve(None)
        self.assertIn("GroupLens", str(caught.exception))
        self.assertIn("GitHub", str(caught.exception))

if __name__ == "__main__":
    unittest.main()