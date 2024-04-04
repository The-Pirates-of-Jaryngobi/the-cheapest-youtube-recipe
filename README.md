# 최저가 요리 유튜브 레시피 검색 서비스

## 프로젝트 개요
### 프로젝트 주제
사용자가 원하는 요리의 메뉴명을 입력하면, 각 재료와 용량을 비교하여 가장 저렴한 가격으로 요리할 수 있는 유튜버의 레시피를 제공하는 서비스

### 프로젝트 기능
음식명을 검색 시 최저가에 해당하는 레시피의 유튜브 정보와 재료의 정보 출력
- 메뉴명 검색 : 사용자가 원하는 요리의 메뉴명을 입력하여 검색
- 정보 수집 : 크롤링 등을 통해 각종 플랫폼에서 음식명, 레시피, 재료 정보를 수집하고 저장
- 최저가 레시피 로직 : 저장된 레시피 정보와 최신 식료품 가격 정보를 결합하여 가장 저렴한 요리 레시피 추출
- 사용자 편의성 : 인터페이스를 직관적이고 어디서든 사용하기 쉽도록 설계하여 사용자들이 쉽게 검색하고 결과를 확인할 수 있도록 함

## 활용 기술
| 분류 | 기술 |
| --- | --- |
| 데이터 수집/분석 | Python, Pandas, BeautifulSoup, Requests, Selenium |
| 데이터 프로세싱 및 저장 | Airflow, PostgreSQL, AWS RDS(AWS Aurora) |
| 프론트엔드 | Vue, Vuetify, Framer, Figma |
| 백엔드 | Django, DRF |
| 머신러닝 및 NLP | Gemini, HuggingFace, ratsgonlp, autogluon, spaCy, PyTorch |
| 배포 및 자동화 | AWS EC2, AWS S3, CodeBuild, GitHub Actions |
| 협업 도구 | GitHub, Notion, Slack |

## 프로젝트 내용
### Software Architecture
![Software Architecture](/img/sw_archi.drawio.png)

### Infra Architecture
![Infra Architecture](/img/final_infra.drawio.png)

### Data Architecture
![Data Architecture](/img/data_pipeline.drawio.png)

### ERD
![ERD](/img/service_erd.drawio.png)

## 결과물
![Result](/img/project_result.png)

## 회고(4L)
- **Liked**
    - Text 데이터 처리 관련 문제를 해결해 나가는 과정을 잘 헤어나간 것 같습니다.
    - 데이터 및 개발 관련 다양한 기술들을 활용하고 도전할 수 있어서 좋았습니다.
- **Learned**
    - 새로운 DL 기술 및 프론트엔드 프레임워크 Vue.js에 대해 학습하여 경험을 쌓았습니다.
    - 팀원들 각자의 장점을 배우고, 협업 방식과 의사소통 기술을 배울 수 있었습니다.
- **Lacked**
    - 대규모 데이터나 실시간 데이터, DBT 기술 등 데이터 관련 여러 기술들을 경험하지 못했습니다.
    - 제약 사항이 큰 장애물이 될 것을 예상하지 못해 세팅이 오래 걸리고, 연결이 부족했습니다.
- **Longed for**
    - 최소한 기능을 구현했으므로, 데이터를 추가하며 웹사이트 기능 개선을 하면 좋을 것 같습니다.
    - NLP DL 모델 개발 : 추후 유료 툴, 자문 등을 통해 개선해나가면 좋을 것 같습니다.

## 팀원 및 역할

| 이름 | 역할 |
| --- | --- |
| 윤혜원 | PM, ETL(menu table), Web(Design, Frontend) |
| 김민회 | ETL(Coupang crawling), Web(Frontend) |
| 김바롬 | Infra(AWS, Airflow), Web(Backend) |
| 김원경 | Tech Lead, ERD, Web(Backend), DL |
| 이재호 | ERD, ETL(Youtube), ELT, Web(Backend) |