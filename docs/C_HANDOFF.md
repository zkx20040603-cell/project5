# C 담당 산출물 및 인계

기준: 2026-09-30, main `57a7b8d`. A 작업은 진행 중이라는 팀원 설명을 기준으로 한다.

## 구현한 항목

- `config/accounting_schema.json`: 기존 B 샘플과 호환되는 8열 규격 및 드롭다운 목록.
- `scripts/validate_sheet.py`: 원본을 변경하지 않는 CSV/TSV 검사 도구. 오류가 있으면 종료 코드 1, 합계는 null로 반환한다. 원문 개인정보는 오류 로그에 출력하지 않는다.
- `tests/test_validate_sheet.py`: 날짜, 잘못된 금액, CSV 쉼표, 필수값, 합계, 중복·빈 행 검증.
- `.github/workflows/qa-schema.yml`: 배포 권한 없는 PR 검증 작업. 기존 A 배포 작업과 B 코드는 변경하지 않는다.
- `docs/SHEET_GUIDE.md`, `docs/OPERATIONS.md`, `docs/QA_REPORT.md`: 입력 규칙, 운영 절차, 실행 결과와 미완료 항목.

## 실행

저장소 루트에서 Python 3.10 이상으로 실행한다. 추가 패키지는 필요 없다.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/validate_sheet.py data/copy_paste_to_sheets.tsv
python3 scripts/validate_sheet.py downloaded_sheet.csv
```

경고는 실패가 아니다. 오류가 있으면 집계 결과를 사용하지 않는다. 검증기는 원본 입력의 품질을 확인하며 A/B 프로그램에 자동 연결하지 않았다. A가 연동할 때 별도로 실행 단계를 추가한다.

## 외부 적용 대기

- Google 로그인 및 편집 권한: 실제 시트 데이터 검증 규칙 적용·확인.
- GitHub 원본 저장소 쓰기 권한 없음: 개인 포크에서 PR로 제출, 원본 관리자 리뷰 및 원격 QA 승인 필요.
- A 구현 완료 및 실제 거래 입력: 원본 → 처리 결과 → 화면 금액 대사.
- iOS Safari / Android Chrome 실기기 확인.

문서/도구 작성 완료와 운영 승인 완료는 구분한다. 위 항목이 해결되기 전에는 C 전체 완료로 표시하지 않는다.
