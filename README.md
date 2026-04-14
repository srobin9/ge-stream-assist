```markdown
# Gemini Enterprise RAG (StreamAssist) Demo

이 프로젝트는 Google Cloud의 **Gemini Enterprise (Vertex AI Agent Builder)**를 활용하여, Cloud Storage(GCS)에 저장된 사내 문서를 기반으로 실시간 스트리밍 질의응답(RAG)을 수행하는 Python 데모입니다.

특히, 종량제(Standard)가 아닌 **Enterprise Edition (시트 기반 과금)** 환경에서 서비스 계정(Service Account) 가장(Impersonation)을 통해 안전하게 API를 호출하는 엔터프라이즈급 인증 아키텍처를 구현했습니다.

## 🏗 아키텍처 핵심
* **Data Source:** Google Cloud Storage (GCS) 버킷 내 비정형 문서 (PDF, 이미지 등)
* **Engine:** Vertex AI Agent Builder (Discovery Engine API - `streamAssist` v1)
* **Identity & Billing:** Gemini Enterprise User Seat 할당 및 Service Account Impersonation 활용
* **Output:** Grounding Metadata(출처 근거)를 기반으로 한 실시간 텍스트 스트리밍 및 표/마크다운 렌더링

---

## 🚀 사전 준비 (Prerequisites)

1. **Google Cloud 프로젝트** 및 결제 계정 활성화
2. **Gemini Enterprise 라이선스** (30일 무료 트라이얼 또는 구독 활성화)
3. 문서가 업로드된 **GCS 버킷**
4. Python 3.8 이상 환경

---

## ⚙️ 인프라 및 권한 설정 가이드 (A to Z)

### 1. 에디션 및 시트(Seat) 할당
1. GCP 콘솔의 `Gemini Enterprise` 메뉴에서 에디션을 **Enterprise**로 변경합니다.
2. `Manage Users` 메뉴에서 API를 호출할 **서비스 계정(Service Account)**을 사용자로 추가합니다.

### 2. IAM 권한 설정
* **Discovery Engine Service Agent:** GCS 버킷에 대한 `Storage Object Viewer` 권한 부여 (인덱싱 용도)
* **실제 개발자 계정 (개인 이메일):** 서비스 계정의 권한을 위임받기 위해 해당 서비스 계정에 대한 `Service Account Token Creator (서비스 계정 토큰 생성자)` 권한 부여

### 3. Data Store 구성
1. `Gemini Enterprise > Apps` 메뉴에서 신규 앱 생성
2. `Data Store` 소스로 GCS 버킷 지정 및 데이터 Import(인덱싱) 완료
3. 생성된 앱의 **Engine ID** 메모

---

## 💻 설치 및 실행 방법

### 1. 라이브러리 설치
최신 버전의 Discovery Engine 라이브러리가 필요합니다.
```bash
pip install google-cloud-discoveryengine>=0.11.1
```

### 2. 인증 환경 구성 (가장 중요)
보안을 위해 서비스 계정 키(JSON)를 다운로드하지 않고, Impersonation(가장) 방식을 사용합니다.
```bash
# 본인 계정으로 로그인하되, 서비스 계정으로 위장하여 토큰 발급
gcloud auth application-default login --impersonate-service-account="your-service-account@your-project.iam.gserviceaccount.com"
```

### 3. 환경 변수 설정
```bash
export GCP_PROJECT_ID="your-project-id"
export GCP_ENGINE_ID="your-engine-id"
```

### 4. 스크립트 실행
```bash
python demo_ge_enterprise.py "GCS 버킷에 있는 한양 성곽길 지도에 대해 요약해줘."
```

## 📊 모니터링 (Audit Logging)
GCP 콘솔의 **Log Explorer**에서 아래 쿼리를 통해, 호출이 Enterprise Seat에서 정상 차감되는지(종량제 과금이 아닌지) 확인할 수 있습니다.
```text
protoPayload.serviceName="discoveryengine.googleapis.com"
protoPayload.methodName="google.cloud.discoveryengine.v1.AssistantService.StreamAssist"
```
*로그 내 `logName`이 `gemini_enterprise_user_activity`로 기록되며, `userIamPrincipal`에 서비스 계정이 기록됨을 확인합니다.*
```

---

## 2. Cloud Shell에서 GitHub로 코드 올리기

현재 작업 중인 구글 클라우드의 Activated Shell(Cloud Shell)에서 바로 GitHub 레포지토리로 코드를 푸시하는 방법입니다.

### 1단계: GitHub에서 원격 저장소(Repository) 생성
1. GitHub에 로그인하여 새로운 Repository를 생성합니다. (예: `gemini-enterprise-demo`)
2. 생성 후 나타나는 **Repository URL**을 복사해 둡니다. (예: `[https://github.com/사용자명/gemini-enterprise-demo.git](https://github.com/사용자명/gemini-enterprise-demo.git)`)

### 2단계: GitHub 개인 액세스 토큰(PAT) 발급
비밀번호 대신 사용할 안전한 토큰이 필요합니다.
1. GitHub 우측 상단 프로필 > **[Settings]** 클릭
2. 좌측 하단 **[Developer settings]** > **[Personal access tokens]** > **[Tokens (classic)]** 클릭
3. **[Generate new token (classic)]** 클릭 후, `repo` 체크박스(저장소 접근 권한)를 체크하고 생성합니다.
4. **생성된 토큰 문자열을 반드시 복사해 둡니다.** (다시 볼 수 없습니다.)

### 3단계: Cloud Shell에서 Git 초기화 및 커밋
Cloud Shell 터미널로 돌아와서 코드 파일들이 있는 디렉토리로 이동한 후 아래 명령어를 순서대로 실행합니다.

```bash
# 1. Git 초기화
git init

# 2. 사용자 정보 설정 (최초 1회)
git config --global user.name "본인의 GitHub 닉네임"
git config --global user.email "본인의 GitHub 이메일"

# 3. 파일 추가 및 커밋 (README.md, 파이썬 파일 등 모두 포함)
git add .
git commit -m "Initial commit: Gemini Enterprise RAG demo"
```

### 4단계: GitHub와 연결 및 푸시
```bash
# 1. 원격 저장소 연결 (1단계에서 복사한 URL 사용)
git remote add origin https://github.com/사용자명/gemini-enterprise-demo.git

# 2. 메인 브랜치 이름 변경 (보통 master에서 main으로 변경)
git branch -M main

# 3. GitHub로 코드 푸시
git push -u origin main
```

**⚠️ 로그인 프롬프트 주의사항:**
마지막 `git push` 명령어를 치면 **Username**과 **Password**를 물어봅니다.
*   **Username:** 본인의 GitHub 아이디
*   **Password:** 본인의 GitHub 비밀번호가 아니라, **2단계에서 복사해 둔 '개인 액세스 토큰(PAT)' 문자열**을 붙여넣고 엔터를 치셔야 합니다. (보안상 터미널 화면에 문자가 입력되는 것이 보이지 않으니, 붙여넣기 후 바로 엔터를 누르세요.)

여기까지 완료하시면 파트너사에게 GitHub 링크 하나만 전달하여 깔끔하게 데모를 공유하실 수 있습니다! 더 필요한 부분이 있으시면 언제든 말씀해주세요.
