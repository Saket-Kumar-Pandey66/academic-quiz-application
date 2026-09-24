import unittest
import tempfile
from pathlib import Path

from project import calculate_score, initialize_sqlite, fetch_questions


class TestQuizApplication(unittest.TestCase):

    def test_score_all_correct(self):
        self.assertEqual(calculate_score([1, 2, 3], [1, 2, 3]), 12)

    def test_score_all_wrong(self):
        self.assertEqual(calculate_score([1, 1, 1], [2, 3, 4]), -3)

    def test_score_mixed(self):
        self.assertEqual(calculate_score([1, 2, 1], [1, 3, 1]), 7)

    def test_randomized_sample_has_no_duplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            db = str(Path(temp) / "test.db")
            conn = initialize_sqlite(db)
            questions = fetch_questions(conn, 1)
            selected_ids = [q["question"] for q in questions[:10]]
            self.assertEqual(len(selected_ids), len(set(selected_ids)))
            conn.close()

    def test_database_contains_all_categories(self):
        with tempfile.TemporaryDirectory() as temp:
            db = str(Path(temp) / "test.db")
            conn = initialize_sqlite(db)
            for category_id in (1, 2, 3):
                self.assertGreater(len(fetch_questions(conn, category_id)), 0)
            conn.close()


if __name__ == "__main__":
    unittest.main()
