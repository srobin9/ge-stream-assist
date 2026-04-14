import os
import sys
from google.cloud import discoveryengine_v1 as discoveryengine
# 또는 버전을 명시하지 않고 기본 최신 버전을 바라보게 할 수도 있습니다.
# from google.cloud import discoveryengine

def get_answers_stream(project_id: str, location: str, engine_id: str, query_text: str):
    # 클라이언트 초기화
    client = discoveryengine.AssistantServiceClient()

    # StreamAssist 엔드포인트 경로 구성
    name = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}/assistants/default_assistant"

    # 요청 객체 생성
    request = discoveryengine.StreamAssistRequest(
        name=name,
        query=discoveryengine.Query(text=query_text)
    )

    print(f"--- 실행 정보 ---")
    print(f"Project ID: {project_id}")
    print(f"Engine ID : {engine_id}")
    print(f"질문 내용 : {query_text}")
    print(f"------------------\n")
    print("답변: ", end="")
    sys.stdout.flush()

# API 호출 (스트리밍)
    try:
        responses = client.stream_assist(request=request)
        last_text_length = 0
        has_printed = False

        for response in responses:
            answer = getattr(response, 'answer', None)
            if not answer:
                continue
            
            current_text = ""
            
            # 1. 일반적인 텍스트 필드 확인
            if getattr(answer, 'answer_text', ''):
                current_text = answer.answer_text
            
            # 2. Replies 배열 내의 구조 확인
            elif hasattr(answer, 'replies'):
                for reply in answer.replies:
                    # 2-A. 기본 content 필드 확인
                    if getattr(reply, 'content', ''):
                        current_text += reply.content
                    elif getattr(reply, 'text', ''):
                        current_text += reply.text
                    
                    # 2-B. Grounding(RAG)이 적용된 세그먼트 데이터 추출 (★추가된 핵심 로직)
                    if hasattr(reply, 'grounded_content'):
                        gc = reply.grounded_content
                        if hasattr(gc, 'text_grounding_metadata'):
                            tgm = gc.text_grounding_metadata
                            if hasattr(tgm, 'segments'):
                                # 모든 세그먼트 조각의 텍스트를 하나로 이어붙임
                                for segment in tgm.segments:
                                    if getattr(segment, 'text', ''):
                                        current_text += segment.text
            
            # 3. 추출된 텍스트가 있다면 스트리밍 출력
            if current_text:
                new_chunk = current_text[last_text_length:]
                if new_chunk:
                    sys.stdout.write(new_chunk)
                    sys.stdout.flush()
                    last_text_length = len(current_text)
                    has_printed = True

        if not has_printed:
            print("\n[알림] API 응답은 성공했으나 출력할 텍스트를 찾지 못했습니다.")
            print(f"최종 응답 구조: {response}")

    except Exception as e:
        print(f"\n[오류 발생]: {e}")
        
    print("\n\n[스트리밍 완료]")

if __name__ == "__main__":
    # 1. 환경 변수에서 설정 값 읽기
    project_id = os.environ.get("GCP_PROJECT_ID")
    engine_id = os.environ.get("GCP_ENGINE_ID")
    location = os.environ.get("GCP_LOCATION", "global") # 기본값 global

    # 2. 필수 환경 변수 체크
    if not project_id or not engine_id:
        print("오류: GCP_PROJECT_ID와 GCP_ENGINE_ID 환경 변수를 설정해야 합니다.")
        sys.exit(1)

    # 3. 명령행 인자(Parameter)에서 질문 읽기
    if len(sys.argv) < 2:
        print("사용법: python demo_streamassist.py \"질문 내용을 입력하세요\"")
        sys.exit(1)
    user_query = sys.argv[1]
    get_answers_stream(
        project_id=project_id, 
        location=location, 
        engine_id=engine_id, 
        query_text=user_query
    )
