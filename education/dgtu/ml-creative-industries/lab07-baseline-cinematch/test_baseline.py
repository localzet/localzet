import unittest
import tempfile
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from baseline import build_scores, rank_catalog, top_k, evaluate_user, dcg_at_k, settings_dict, generate_output, K

class BaselineTests(unittest.TestCase):
    def test_scores_fit_train_only(self):
        training=[{'movieId':7,'positive':1},{'movieId':7,'positive':1},{'movieId':3,'positive':0},{'movieId':1,'positive':1}]
        scored=build_scores(training,{1,3,7})
        self.assertEqual(scored,{7:2,1:1})
        self.assertEqual(rank_catalog(scored,{1,3,7}),[7,1,3])

    def test_ties_and_exclusion(self):
        ids=[1,2,3,4,5]
        self.assertEqual(top_k(ids,{1,3},2),[2,4])
        self.assertEqual(rank_catalog({4:1,2:1},set(ids)),[2,4,1,3,5])

    def test_metric_at_perfect_ranking(self):
        holdout=[{'movieId':6,'relevance':2},{'movieId':2,'relevance':1},{'movieId':10,'relevance':0}]
        out=evaluate_user([6,2,7],holdout,3)
        self.assertAlmostEqual(out['ndcg_at_10'],1.0)
        self.assertAlmostEqual(out['recall_at_10'],1.0)
        self.assertAlmostEqual(out['hitrate_at_10'],1.0)

    def test_empty_hit_and_unjudged(self):
        holdout=[{'movieId':7,'relevance':2}]
        out=evaluate_user([3,5],holdout,2)
        self.assertEqual((out['ndcg_at_10'],out['recall_at_10'],out['hitrate_at_10']),(0,0,0))
        self.assertEqual(out['recommended_labels'],[0,0])

    def test_no_positive_holdout_denominators(self):
        holdout=[{'movieId':7,'relevance':0}]
        out=evaluate_user([2,3],holdout,2)
        self.assertIsNone(out['ndcg_at_10'])
        self.assertIsNone(out['recall_at_10'])
        self.assertIsNone(out['hitrate_at_10'])

    def test_ndcg_graded_gain(self):
        self.assertAlmostEqual(dcg_at_k([2,1],2),3+1/1.584962500721156)

    def test_no_test_dependency(self):
        train=[{'movieId':1,'positive':1},{'movieId':1,'positive':1}]
        before=build_scores(train,{1,2,3})
        fake_test=[{'movieId':2,'positive':1}]*99
        self.assertEqual(before,build_scores(train,{1,2,3}))
        self.assertEqual(top_k(rank_catalog(before,{1,2,3}),set(),3),[1,2,3])
        self.assertNotIn('test_rows',str(before))

    def test_complete_report_synthetic(self):
        train=[]; validation=[]
        movies={mid:f"Movie {mid}" for mid in range(1,31)}
        for uid in range(1,5):
            for mid in range(1,7):
                train.append({"userId":uid,"movieId":mid,"positive":int(mid%2==0)})
            for mid in range(7,10):
                validation.append({"userId":uid,"movieId":mid,
                                   "relevance":2 if mid==8 else 1})
        manifest={"version":"cinematch-labels-v1.0.0","source_git_blob_sha1":{},
                  "split_counts":{"train":24,"validation":12,"test":8}}
        with tempfile.TemporaryDirectory() as d:
            m=generate_output(train,validation,movies,manifest,Path(d))
            self.assertEqual(m["evaluated_users"],4)
            self.assertEqual(m["validation_rows"],12)
            self.assertTrue((Path(d)/"cases.md").exists())
            records=(Path(d)/"validation_cases.csv").read_text().splitlines()
            self.assertEqual(len(records),5)
            self.assertFalse(m["test_used_for_model_or_scoring"])

    def test_settings_deterministic(self):
        manifest={'version':'v1','source_git_blob_sha1':{}}
        self.assertEqual(settings_dict({'version':'v1','source_git_blob_sha1':{},'split_counts':{'train':1,'validation':2,'test':3}}),settings_dict({'version':'v1','source_git_blob_sha1':{},'split_counts':{'train':1,'validation':2,'test':3}}))
        self.assertIsNone(settings_dict({'version':'v1','source_git_blob_sha1':{},'split_counts':{'train':1,'validation':2,'test':3}})['seed'])

if __name__ == '__main__':unittest.main()