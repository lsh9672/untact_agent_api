# 4-2 현장실습 백엔드 실무 경험 (2021.09.01 ~ 2021.12.31)

## 각 파일들

### admin_untact

- 장비들(라즈베리파이등의 교육용장비)을 관리하기 위한 api

  (장비접속정보를 초기화함)

### scp \_untact

- 장비들에 수정된 코드를 배포하기 위해서 만든 코드

- 각각의 장비들에 깃허브 연동이 어렵고, 젠킨스 같은 별도의 CI를 구축할수 없는 환경이므로 scp를 이용해서 코드를 배포함.

### untact_django

- 장비들의 접속정보(접속유무)를 LMS 쪽으로 넘겨주는 api서버

- 장비 접속유무 뿐만 아니라 LMS로 부터 접속하고자 하는 장비번호와 장비종류를 받아서 해당 장비로 리다이렉션 시켜주는 역할을 함.


## 구성도 및  DB 테이블

(구성도)

![image](https://user-images.githubusercontent.com/56991244/164122445-32e78581-aa3b-4a83-b1c7-aa69d2270e4e.png)

(DB 테이블)

![image](https://user-images.githubusercontent.com/56991244/164122475-590b47b3-4da7-4d3c-b9c2-625f00943c2e.png)

## 결과화면

(이 api를 이용한 실제 서비스 화면)

#### 결과1 - 장비상태 확인 이전 화면(이부분은 해당 api를 사용한 것은 아님)

![image](https://user-images.githubusercontent.com/56991244/164122526-f4872454-69d4-4370-903f-d8c6cb0bf87d.png)

#### 결과2 - 장비상태 확인

![image](https://user-images.githubusercontent.com/56991244/164122611-37318e0d-6bd3-4b2a-a962-ba654f236e8d.png)

#### 결과3 - 원격으로 주피터랩에 접속

![image](https://user-images.githubusercontent.com/56991244/164122675-3aaed17b-de8d-479b-acec-81c4ef0c2056.png)


