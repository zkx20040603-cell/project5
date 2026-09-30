"""C 담당: 다운로드한 CSV/TSV를 변경하지 않고 검사. Python 표준 라이브러리만 사용."""
import argparse
import csv
import io
import json
import re
from datetime import date
from pathlib import Path

SCHEMA = json.loads((Path(__file__).resolve().parents[1] / "config/accounting_schema.json").read_text(encoding="utf-8"))


def validate(text, delimiter=","):
    errors, warnings, records = [], [], []
    try:
        rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff")), delimiter=delimiter, strict=True))
    except csv.Error as exc:
        return {"errors": [f"CSV 형식 오류: {exc}"], "warnings": [], "rows": 0, "summary": None}
    if not rows or rows[0] != SCHEMA["headers"]:
        return {"errors": ["첫 행의 8개 표 헤더 및 순서가 규격과 다릅니다."], "warnings": [], "rows": 0, "summary": None}
    seen = set()
    for number, values in enumerate(rows[1:], 2):
        if not any(value.strip() for value in values):
            continue
        if len(values) != 8:
            errors.append(f"행 {number}: 열 개수가 8개가 아닙니다. 쉼표 포함 필드의 CSV 인용을 확인하세요.")
            continue
        row = dict(zip(SCHEMA["headers"], (value.strip() for value in values)))
        before = len(errors)
        for key in SCHEMA["required"]:
            if not row[key]:
                errors.append(f"행 {number}: {key} 필수값 누락")
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["일자"]):
                raise ValueError()
            date.fromisoformat(row["일자"])
        except ValueError:
            errors.append(f"행 {number}: 유효한 YYYY-MM-DD 날짜가 필요합니다.")
        for key, allowed in [("구분", "types"), ("카테고리", "categories"), ("결제수단", "payment_methods")]:
            if (key != "결제수단" or row[key]) and row[key] not in SCHEMA[allowed]:
                errors.append(f"행 {number}: {key} 허용 목록에 없는 값")
        amount_text = row["금액"]
        if not re.fullmatch(r"(?:[0-9]+|[1-9][0-9]{0,2}(?:,[0-9]{3})+)", amount_text):
            errors.append(f"행 {number}: 금액은 0 이상의 정수 원화여야 합니다.")
            amount = None
        else:
            amount = int(amount_text.replace(",", ""))
            if amount > SCHEMA["amount_maximum"]:
                errors.append(f"행 {number}: JavaScript 안전 정수 범위 초과")
            if amount == 0:
                warnings.append(f"행 {number}: 규격상 0원 허용. 현재 A/B 코드는 0원 거래를 제외합니다.")
        key = tuple(row.values())
        if key in seen:
            warnings.append(f"행 {number}: 동일한 거래가 있습니다. 중복 입력인지 확인하세요.")
        seen.add(key)
        if len(errors) == before:
            records.append((row["구분"], amount))
    if not records and not errors:
        warnings.append("거래 0건: 현재 대시보드는 실제 0원 장부 대신 데모 데이터를 표시합니다.")
    income = sum(amount for kind, amount in records if kind == "수입")
    expense = sum(amount for kind, amount in records if kind == "지출")
    if max(income, expense) > SCHEMA["amount_maximum"]:
        errors.append("합계가 JavaScript 안전 정수 범위를 초과합니다.")
    return {"errors": errors, "warnings": warnings, "rows": len(records),
            "summary": None if errors else {"total_income": income, "total_expense": expense, "balance": income - expense}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    try:
        result = validate(args.path.read_text(encoding="utf-8-sig"), "\t" if args.path.suffix == ".tsv" else ",")
    except (OSError, UnicodeError) as exc:
        parser.exit(2, f"파일 읽기 실패: {exc}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
