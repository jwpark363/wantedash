# LLM + 구글 드라이브 이용한 시트 자동화 시스템
- Chat GPT 4.1 LLM 모델 사용
- Langchain
- Google Drive Tool 개발
    1. 폴더 검색 및 생성
    2. 파일 검색 및 생성
    3. 스프레드시트의 특정 시트 마지막줄에 CSV 문자열 추가
    4. 파일(docx, doc) 파일 업로드


<img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/main.png" width=350>

### 시스템 구조
- 프론트 : html + javascript
- 백엔드 : fastapi, langchain, gpt 4.1, google driver tools
<img src="https://raw.githubusercontent.com/jwpark363/wantedash/refs/heads/main/system.png">

### 역할
- 관리자 : 구글드라이브의 기준 정보 파일 관리
- 백앤드 에이전트 : langchain + gpt 4.1 + google driver tools
    1. 기준 정보 이용한 시스템 프롬프트 생성
    2. 에이전트 초기화
    3. 수강생의 정보를 입력받아 기준 정보 기준으로 업무 처리
