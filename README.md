# 🟡 포켓몬 유사도 맞추기 게임

포켓몬 데이터(types, evolutions, description, height, weight)를 기반으로  
랜덤으로 출제된 3마리 포켓몬과 관계도가 높은 정답 포켓몬을 맞추는 게임입니다.    
포켓몬의 경우 1세대 부터 9세대 까지 입니다.
---

## 📂 사용 데이터
- 출처: **https://pokeapi.co/api/v2/pokemon**

- **types (속성)**  
- **evolutions (진화)**  
- **description (설명)**  
- **height (신장)**  
- **weight (체중)**  

---

## ⚙️ 실행 환경

1. 가상환경 실행
conda activate 본인_가상환경_이름



2. 프로젝트 디렉토리 이동
cd 프로젝트_저장_경로



<img width="600" alt="실행1" src="https://github.com/user-attachments/assets/41610c10-8c43-482f-a0e4-6d1ffe63ee50" />


3. 실행  
- 최초 실행 시 **pokeAPI 데이터 로딩**이 필요하며 약 **15분** 소요됩니다.  
- 이후에는 캐싱 데이터 활용 예정.  
⚠️ **주의**: VSCode 내 CMD 환경에서 동작이 불안정할 수 있으므로 **콘다 프롬포트** 실행을 권장합니다.

---

## 🖥️ 게임 진행 방식

### 1. 문제 출제
- 데이터 로딩 완료 후, 랜덤으로 **관계성이 높은 3마리 포켓몬**이 출제됩니다.  

<p align="center">
<img width="700" alt="동작1" src="https://github.com/user-attachments/assets/53d16c97-f491-4d77-a4a2-d808c634fbcf" />
<img width="700" alt="동작2" src="https://github.com/user-attachments/assets/cd29558e-5f0e-4874-a841-27e7e98798e1" />
</p>

---

### 2. 정답 입력
- 포켓몬 이름을 입력하면:
- 정답 포켓몬 이미지 출력  
- 출제된 3마리와의 **유사도 관계 표** 표시  

<p align="center">
<img width="400" alt="동작4" src="https://github.com/user-attachments/assets/8ab646ad-bc9c-4ee1-85b6-6d4b37ce8414" />
<img width="550" alt="동작3" src="https://github.com/user-attachments/assets/47ca9cda-dea6-4962-8435-5a8579ac25b7" />
</p>

⚠️ 잘못 입력 시 안내 메시지 출력:
입력한 포켓몬 이름이 데이터에 없습니다. 다시 입력해주세요



---

### 3. 문제 진행 선택
정답 확인 후:  
1. 같은 문제 다시 풀기  
2. 다음 문제로 넘어가기 → 새로운 3마리 랜덤 포켓몬 등장  

<p align="center">
  <img width="450" alt="동작5" src="https://github.com/user-attachments/assets/46063198-7b04-4d48-bbdf-9a78d5d33738" />
</p>

---

## 📊 유사도 판정
포켓몬 간 유사도는 다음 다섯 가지 요소를 기반으로 계산됩니다.  

- **높은 유사도**: types, evolutions, description, height, weight 가 유사한 경우  
- **낮은 유사도**: 위 요소들이 크게 다를 경우  

<p align="center">
  <img width="420" alt="동작7" src="https://github.com/user-attachments/assets/7468c07a-4963-44be-8bd6-5469d2bf5c66" />
  <img width="420" alt="동작6" src="https://github.com/user-attachments/assets/dd6b4123-6ea9-4e51-b500-7a042ff33078" />
</p>

---

## ✅ 정리
- pokeAPI에서 데이터를 불러와 진행  
- 매 라운드마다 3마리 힌트 포켓몬 제시  
- 정답 입력 시 이미지 + 관계표 확인 가능  
- 잘못 입력하면 친절한 에러 메시지 제공  
- 다음 문제로 계속 이어서 플레이 가능  

---

## 🚀 앞으로의 업데이트
- 최초 로딩 속도 개선  
- 다양한 유사도 알고리즘 적용 예정  
- 한국어 / 영어 이름 입력 동시 지원  
