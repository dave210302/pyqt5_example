## Ex 3-1. 창 띄우기.

import sys
from PyQt5.QtWidgets import QApplication, QWidget

# QWdget이 부모 클래스
# 부모 클래스를 상속 받아서 MyApp이라는 자식 클래스를 생성
# 부모의 특성을 받아서 내가 무언가 살짝 바꾸고 싶을 때
class MyApp(QWidget):

    # 생성자. 아무것도 입력되어 있지 않은 기본 상태를 마련해줌
    def __init__(self):
        #Super는 부모 클래스를 가리킴. 부모 클래스의 초기 생성자. QWidget 클래스의 init 함수 호출
        super().__init__()
        #myapp 자식 클래스와 부모 클래스의 차이점. initUI라는 함수
        self.initUI()

    def initUI(self):
        #창의 이름을 설정
        self.setWindowTitle('My First Application')
        #왼쪽 모서리 위 빈 공간 위치 설정
        self.move(500, 500)
        #창의 크기 설정
        self.resize(600, 600)
        #위의 설정 대로 창을 생성
        self.show()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   #실제 무언가 창을 띄우고 싶음. ex라는 이름의 객체로 창을 만듦. 2개 띄우고 싶으면 myapp으로 두개 만듦
   ex = MyApp()
   sys.exit(app.exec_())