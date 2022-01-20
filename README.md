# 4-2 현장실습 백엔드 실무 경험 (2021.09.01 ~ 2021.12.31)

> ### admin_untact

- 장비들(라즈베리파이등의 교육용장비)을 관리하기 위한 api

  (장비접속정보를 초기화함)

> ### scp \_untact

- 장비들에 수정된 코드를 배포하기 위해서 만든 코드

- 각각의 장비들에 깃허브 연동이 어렵고, 젠킨스 같은 별도의 CI를 구축할수 없는 환경이므로 scp를 이용해서 코드를 배포함.

> ### untact_django

- 장비들의 접속정보(접속유무)를 LMS 쪽으로 넘겨주는 api서버

- 장비 접속유무 뿐만 아니라 LMS로 부터 접속하고자 하는 장비번호와 장비종류를 받아서 해당 장비로 리다이렉션 시켜주는 역할을 함.