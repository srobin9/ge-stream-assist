# Gemini Enterprise RAG (StreamAssist) Demo
이 프로젝트는 Google Cloud의 **Gemini Enterprise (Vertex AI Agent Builder)** 를 활용하여, Cloud Storage(GCS)에 저장된 사내 문서를 기반으로 실시간 스트리밍 질의응답(RAG)을 수행하는 Python 데모입니다.
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
4. Python 3.8 이상 환경`

---

## ⚙️ 인프라 및 권한 설정 가이드

### 1. SA 생성 및 IAM 권한 설정
(1) Python code를 실행할 **Service Account 생성**
  * GCS 콘솔에서 `IAM & Admin` > `Service Accounts` 메뉴로 이동
  * 콘솔 화면 상단의 **+ Create service account** 클릭
  * `Create service account` 화면에서 **Service Account name** 입력 후 Create and continue 클릭
  * `Permissions` 화면에서 **Discovery Engine Admin**과 **Storage Object Viewer**의 2개 Role을 추가 후 Save 클릭  
2) **Impersonnate Service Account** 설정
  * Python code를 실행하는 **실제 개발자 계정 (개인 이메일)** 이 서비스 계정의 권한을 위임받기 위해서는 해당 서비스 계정에 대한 `Service Account Token Creator (서비스 계정 토큰 생성자)` 권한 부여 필요
  * GCS 콘솔에서 생성된 SA를 클릭한 후 **Principals with access` 탭으로 이동한 후 **+ Grant access** 클릭
  * New principals에 **개발자 이메일** 입력
  * Role에 **Service Account Token Creator** 입력 후 Save 클릭
  * GCS Project의 Owner 계정이더라도 서비스 계정의 임시 토큰 발행 권한은 없기 때문에 Owner 계정도 해당 서비스 계정에 대한 `Service Account Token Creator (서비스 계정 토큰 생성자)` 권한 부여 필요

### 2. GE User로 생성한 SA 추가 
1) GCP 콘솔에서 `Gemini Enterprise` > `Manage users`메뉴로 이동한 후 **Add user** 클릭
2) streamAssistAPI를 호출할 **서비스 계정(Service Account)** 의 메일 주소를 `Users email addresses`에 추가
3) `Assign the following subscription`에서 **Gemini Enterprise 라이선스** 선택 후 Submit 클릭

### 3. Gemini Enterprise App & Data Store(GCS) 구성
1) Gemini Enterprise 신규 앱 생성
  * `Gemini Enterprise` > `Apps` 메뉴에서 **+ Create app** 클릭
  * `App name` 입력하고 `location` 선택 후 `Create` 클릭
  * 생성된 앱의 **Engine ID** 메모
2) Cloud Storage Data Store 구성
  * `Gemini Enterprise` > `Data stores` 메뉴에서 **+ Create data store** 클릭
  * `Source` 화면에서 **Cloud Storage** Select
  * `Data` 화면의 `Unstructured Data Import(Document Search & RAG)`에서 **Documents** 선택
  * `Select a folder or a file you want to import`에서 `Folder` 선택 후 `Browser` 클릭하여 원하는 GCS Bucket 및 Folder 선택하고 Select 클릭
  * `Data` 화면으로 돌아와서 Continue 클릭
  * `Configuration` 화면에서 적절한 `Location` 선택하고 `Data Store Name` 입력한 후 Create 클릭
  * GCS Bucket에 저장된 Data들에 대한 Parsing 작업을 수동으로 하기 위해 생성된 Data Store 이름 클릭 후 이동한 화면의 우측 상단에 있는 **Manual Synce** 클릭 

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
