# Biz-DNA 소상공인 경영진단 - 바로 실행

## 1. Windows
Python 3.11 이상 설치 후 `run_windows.bat` 더블클릭.

## 2. macOS / Linux
터미널에서 `bash run_mac_linux.sh` 실행.

## 3. 접속
브라우저에서 http://localhost:8501

## 4. 빠른 시연
`점주 진단` → `카페 예시` 선택 → 각 진단문항 확인 → `진단 실행` → 그래프 및 PDF 다운로드.
`운영기관 대시보드`와 `개선과제·성과추적`은 로컬 SQLite 저장 동의 후 이용 가능.

## 5. 구성
- `app.py`: 점주 웹 입력 및 대시보드
- `engine.py`, `advanced.py`: 진단·성장단계·추천 알고리즘
- `report.py`: 기본형/정밀형 PDF
- `storage.py`, `analytics.py`: 로컬 진단 DB 및 상권집계
- `followup.py`: 개선과제·성과관리
- `ai_analysis.py`: 선택적 AI 분석 연결 코드 (별도 API 키 및 동의 필요)
- `sample_*.json`: 가상점포 데이터

## 6. 보안 및 정확도 제한
본 버전은 로컬 시연용입니다. 인증, 권한분리, 암호화, 운영 서버 보안이 없으므로 인터넷 공개 및 실제 민감정보 입력 금지.
카드매출·유동인구·상권 DB 실시간 연결 없음. 업종별 가중치 및 판정기준은 검증 전 시범값.
