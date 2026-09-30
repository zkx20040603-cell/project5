import csv
import io
import unittest
from scripts.validate_sheet import SCHEMA, validate


def fixture(rows):
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(SCHEMA["headers"])
    writer.writerows(rows)
    return out.getvalue()


class ValidationTests(unittest.TestCase):
    def row(self, **changes):
        data = dict(zip(SCHEMA["headers"], ["2026-09-01", "수입", "회비", "테스트", "100000", "", "", ""]))
        data.update(changes)
        return list(data.values())

    def test_totals_and_quoted_commas(self):
        result = validate(fixture([self.row(), self.row(구분="지출", 금액="30,000", 항목명="식사, 음료")]))
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["summary"]["balance"], 70000)

    def test_invalid_fields(self):
        for changes in [{"일자": "2026-02-30"}, {"일자": "2026-9-1"}, {"금액": "-1"}, {"금액": "1.5"}, {"금액": "1,00"}, {"금액": "9007199254740992"}, {"구분": "오타"}, {"항목명": ""}, {"카테고리": "오타"}]:
            with self.subTest(changes=changes):
                result = validate(fixture([self.row(**changes)]))
                self.assertTrue(result["errors"])
                self.assertIsNone(result["summary"])

    def test_zero_duplicate_blank(self):
        row = self.row(금액="0")
        result = validate(fixture([row, [], row]))
        self.assertEqual(result["rows"], 2)
        self.assertEqual(len(result["warnings"]), 3)

    def test_empty_and_broken_width(self):
        self.assertTrue(validate("")["errors"])
        self.assertTrue(validate(fixture([self.row() + ["extra"]]))["errors"])
        self.assertTrue(validate(fixture([]))["warnings"])

    def test_leap_day_bom(self):
        self.assertFalse(validate("\ufeff" + fixture([self.row(일자="2024-02-29")]))["errors"])


if __name__ == "__main__":
    unittest.main()
