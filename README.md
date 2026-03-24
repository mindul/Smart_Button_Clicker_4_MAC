# Smart Button Clicker for MAC OS

[개요]
* 목적 : 사이버교육 과정을 수강하다가 다음 페이지를 수동으로 누르기가 귀찮을 경우
  이 프로그램을 이용하면 다음 페이지 버튼을 자동으로 눌러서 넘겨준다.

* 동작 원리 : 
 마우스 포인터가 위치한 곳의 200x200 픽셀 공간을 
 미리 저장해둔 "다음 페이지" 이미지 파일과 비교해서 
 맞으면 왼쪽 버튼을 자동으로 클릭하여 다음 페이지로 넘어간다. 

* 작성자 : doo & Gemini 3 Flash 

[사용법] 
usage: button_clicker.py [-h] [--capture] [target]

Quartz 기반 고성능 이미지 감지 클릭커

positional arguments:
  target         감지할 이미지 파일 경로 (기본값: button.jpg)

optional arguments:
  -h, --help     show this help message and exit
  --capture, -c  타겟 이미지를 직접 캡처하여 저장
  
  [사용 예시]
  
  <최초 실행 시> 
  1단계 : '다음 페이지' 이미지를 마우스로 드래그&드랍 블럭을 잡아서 먼저 저장
  $ python3 button_clicker.py -c 
  2단계 : 