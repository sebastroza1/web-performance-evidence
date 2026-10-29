import unittest
from perf.report import compare, make_markdown, make_svg


class ReportTests(unittest.TestCase):
    def test_expected_improvement(self):
        rows = compare({"FCP": {"before": 4.04, "after": 2.41, "unit": "s"}})
        self.assertEqual(rows[0]["reduction_pct"], 40.3)
        self.assertEqual(rows[0]["status"], "improved")

    def test_cls_regression_still_good(self):
        row = compare({"CLS": {"before": 0.002, "after": 0.062}})[0]
        self.assertEqual(row["status"], "regressed")
        self.assertEqual(row["web_vitals_category"], "good")

    def test_lcp_outside_good_threshold(self):
        row = compare({"LCP": {"before": 4.04, "after": 3.46, "unit": "s"}})[0]
        self.assertEqual(row["web_vitals_category"], "needs_improvement_or_worse")

    def test_no_production_scope(self):
        with self.assertRaisesRegex(ValueError, "local_p75"):
            make_markdown({"scope": "production", "metrics": {}})

    def test_report_contains_source_boundary(self):
        report = make_markdown({"scope": "local_p75", "source": "owner_provided", "not_field_or_production_data": True, "metrics": {"CLS": {"before": 0.002, "after": 0.062}}})
        self.assertIn("NOT production field data", report)
        self.assertIn("regressed", report)

    def test_rejects_negative_or_zero_baseline(self):
        with self.assertRaises(ValueError):
            compare({"FCP": {"before": 0, "after": 1}})
        with self.assertRaises(ValueError):
            compare({"FCP": {"before": 1, "after": -1}})

    def test_rejects_missing_provenance(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            make_markdown({"scope": "local_p75", "metrics": {"FCP": {"before": 2, "after": 1}}})

    def test_higher_is_better_direction(self):
        row = compare({"Requests served": {"before": 10, "after": 15, "direction": "higher_is_better"}})[0]
        self.assertEqual(row["status"], "improved")
        self.assertEqual(row["reduction_pct"], 50.0)

    def test_rejects_non_finite_values(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            compare({"FCP": {"before": "NaN", "after": 1}})

    def test_svg_is_accessible_and_marks_regressions(self):
        payload = {"scope": "local_p75", "metrics": {"CLS": {"before": 0.002, "after": 0.062}}}
        chart = make_svg(payload)
        self.assertIn('role="img"', chart)
        self.assertIn("regressed", chart)
        self.assertIn("#f59e0b", chart)


if __name__ == "__main__":
    unittest.main()
