# Django_GPT

Hugging Face `pipeline()` 모델들을 Django 웹 서비스의 기능으로 구성한 프로젝트입니다.
로그인 여부에 따라 접근이 제한되는 세 가지 필수 AI 기능(감정 분석 / 문서 요약 / 유해 표현 분석)을
제공합니다. (챌린지 과제는 포함하지 않습니다.)

## 기능 및 URL

| 탭 | URL | 접근 권한 |
| --- | --- | --- |
| 😊 감정 분석 | `/sentiment/` | 비로그인 허용 |
| 📄 문서 요약 | `/summarize/` | 로그인 필요 |
| 🚨 유해 표현 분석 | `/moderate/` | 로그인 필요 |

각 기능은 페이지 URL(`/xxx/`)과 실행용 POST URL(`/xxx/run/`)로 나뉘어 있으며, 서로 다른 Django
URL Pattern과 View 함수로 명확히 분리되어 있습니다 (`my_gpt/urls.py`, `my_gpt/views.py`).

## 사용 모델

| 기능 | Model ID | Hugging Face Task | License |
| --- | --- | --- | --- |
| 감정 분석 | `cardiffnlp/twitter-roberta-base-sentiment-latest` | text-classification | CC-BY-4.0 |
| 문서 요약 | `sshleifer/distilbart-cnn-6-6` | summarization | Apache-2.0 |
| 유해 표현 분석 | `unitary/toxic-bert` | text-classification (multi-label) | Apache-2.0 |


### 입력 언어 및 출력 레이블

- 감정 분석: 입력 언어 영어, 출력 레이블 `negative` / `neutral` / `positive` (+ 신뢰도 점수)
- 문서 요약: 입력 언어 영어, 출력은 요약 텍스트 (원문 길이 / 요약문 길이 / 요약 비율 함께 제공)
- 유해 표현 분석: 입력 언어 영어, 출력 레이블 `toxic`, `severe_toxic`, `obscene`, `threat`,
  `insult`, `identity_hate` (Multi-label, 각 레이블별 점수 제공)


## 실행 방법

1. 가상환경 생성 및 활성화 (권장)

   ```bash
   python3 -m venv venv  # Windows: python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. 패키지 설치

   ```bash
   pip install -r requirements.txt
   ```

3. 환경변수 설정

   ```bash
   cp .env.example .env
   # .env 파일을 열어 DJANGO_SECRET_KEY 등을 원하는 값으로 수정
   ```

   이 프로젝트에서 사용하는 세 모델은 모두 공개(public) 모델이므로 `HUGGINGFACE_TOKEN`은
   비워두어도 정상 동작합니다. Gated/Private 모델을 추가로 사용하는 경우에만 값을 채워주세요.

4. DB 마이그레이션

   ```bash
   python manage.py makemigrations my_gpt
   python manage.py migrate
   ```

5. 관리자 계정 생성 (로그인 필요 기능 테스트용)

   ```bash
   python manage.py createsuperuser
   ```

6. 개발 서버 실행

   ```bash
   python manage.py runserver
   ```

7. 브라우저에서 접속

   ```
   http://127.0.0.1:8000/sentiment/   (비로그인 접근 가능)
   http://127.0.0.1:8000/summarize/   (로그인 필요)
   http://127.0.0.1:8000/moderate/    (로그인 필요)
   http://127.0.0.1:8000/accounts/login/
   http://127.0.0.1:8000/accounts/logout/
   http://127.0.0.1:8000/admin/
   ```

   최초 모델 실행 시 Hugging Face Hub에서 모델 가중치를 다운로드하므로 다소 시간이 걸릴 수
   있습니다. 이후 요청부터는 `lru_cache`로 캐시된 동일 Pipeline 객체를 재사용합니다
   (`my_gpt/services/*.py`).

## 로그인 제한 동작

`/summarize/`, `/moderate/`는 `my_gpt/decorators.py`의 `model_login_required` 데코레이터로
보호됩니다. 비로그인 상태로 직접 URL에 접근하면:

```
/summarize/ 접근
→ /accounts/login/?next=/summarize/&required=1 로 리다이렉트
→ 로그인 페이지에서 "로그인 후 이용해주세요" Alert 출력
→ 로그인 성공 시 /summarize/ 로 자동 복귀
```

