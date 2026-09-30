# 배포 및 운영

## 현재 연결 방식

`js/app.js`는 README의 공개 Google Sheets CSV를 직접 요청한다. 실패하거나 유효 행이 없으면 `data/mock_data.json`, 이어 내장 데모 데이터를 표시한다. 현재 화면은 `data/accounting_data.json`을 읽지 않는다.

따라서 현재 공개 CSV 방식에는 GCP 서비스 계정이나 GitHub 인증 Secrets가 필요 없다. 초기 C 가이드의 GCP 절차는 비공개 Sheets API 방식으로 전환할 때만 적용한다. 게시 ID `2PACX-...`는 API용 SPREADSHEET_ID가 아니다. A와 방식 확정 전 키를 추가 발급하지 않는다.

## Pages

기존 `.github/workflows/deploy.yml`은 main push 및 수동 실행으로 저장소를 배포한다. 현재 수집 스크립트 실행이나 schedule 단계는 없다. 해당 변경은 A 담당이다.

관리자는 Settings → Pages → Build and deployment → Source를 GitHub Actions로 확인한다. Actions의 Deploy Dashboard to GitHub Pages 실행 결과 및 deployment URL을 확인한다. 현재 공개 주소는 https://hanjisubusiness22222.github.io/project5/ 이며 페이지 열림만으로 원본 데이터 동기화 성공을 판정하지 않는다.

배포 워크플로우는 contents:read, pages:write, id-token:write를 사용한다. C 검증 워크플로우는 contents:read만 사용한다. main 병합에는 ROLES.md의 1인 이상 리뷰 및 체크 성공 규칙을 따른다.

## 장애 대응

| 증상 | 확인 및 조치 |
|---|---|
| 샘플 데이터 모드 | 게시 CSV에 실제 헤더/행이 있는지, 올바른 탭이 게시됐는지 확인. 데모 합계를 회계 결과로 사용하지 않음 |
| 시트 수정이 안 보임 | 편집 파일과 게시 원본 확인, 게시 반영 후 새로고침. 즉시 반영 보장 없음 |
| 일부 행이 안 보임 | 빈 날짜·0원·음수 및 헤더 검사. 검증기로 CSV 확인 |
| 금액 차이 | 필터 초기화 후 전체 합계 비교. 중복, 누락, 소수 금액, 데모 여부 확인 |
| Pages 배포 실패 | Actions 실패 단계와 Pages 소스·환경 권한 확인. A에게 로그 전달하되 인증값은 제외 |
| 공개되면 안 되는 자료 입력 | 원본 삭제만으로 캐시·Git 이력이 사라지지 않음. 게시 중지와 노출 범위를 관리자가 점검. 키가 노출됐다면 폐기/교체 |

## 비공개 API 전환 시

A와 B를 함께 변경해야 한다. GCP에서 Sheets API 활성화, 서비스 계정에 해당 시트 뷰어 권한만 부여, JSON 키는 GCP_SA_KEY Secret에 저장한다. SPREADSHEET_ID와 SHEET_NAME도 A와 이름을 맞춘다. 키를 저장소·브라우저 코드·로그에 넣지 않는다. 비공개 원본이라도 배포한 JSON은 공개될 수 있으므로 게시 필드 승인 및 공개 CSV 게시 중지 여부도 결정한다.

## 공식 참고

- Google 게시 범위와 갱신: https://support.google.com/docs/answer/183965
- Pages 소스 설정: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- Actions 기반 Pages: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
