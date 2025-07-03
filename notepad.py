import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction,
                             QFileDialog, QTabWidget, QVBoxLayout, QWidget,
                             QStatusBar, QLabel, QDialog, QLineEdit, QPushButton,
                             QHBoxLayout, QMenu, QMessageBox)
from PyQt5.QtGui import QIcon, QKeySequence, QTextCursor
from PyQt5.QtCore import Qt, QSettings

class FindDialog(QDialog):
    # 텍스트에서 원하는 단어를 검색하기 위한 다이얼로그 창 생성
    # __init__은 "이 창을 처음 만들 때 무엇을 준비할지"
    def __init__(self, parent=None):  # parent=None은 이 창이 다른 창에 연결될 수도 있고, 아닐 수도 있다는 뜻
        super().__init__(parent) 
        self.setWindowTitle("Find") # 창의 제목을 "Find"로 표시
        self.layout = QVBoxLayout(self) # 위에서 아래로 순서대로 배치하는 레이아웃

        self.find_input = QLineEdit(self) # 글자를 한 줄 입력할 수 있는 칸
        self.find_input.setPlaceholderText("Find...") # 입력칸에 흐릿하게 "Find..."라고 작성
        self.layout.addWidget(self.find_input) # 입력창을 창에 삽입

        self.button_box = QHBoxLayout() #가로로 버튼을 놓는 공간
        self.find_next_button = QPushButton("Find Next", self) # "Find Next"라고 써진 버튼 생성
        self.button_box.addWidget(self.find_next_button) # 버튼을 버튼박스에 넣음
        self.layout.addLayout(self.button_box) # 버튼박스를 아까 만들었던 전체 레이아웃에 넣음

class ReplaceDialog(QDialog):
    # 텍스트에서 단어를 찾아 다른 단어로 바꾸는 다이얼로그 창 생성
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Replace")
        self.layout = QVBoxLayout(self) # 위젯들을 위에서 아래로 배치할 수 있는 세로 레이아웃 설정

        self.find_input = QLineEdit(self) # 사용자로부터 "찾을 단어"를 입력받는 텍스트 입력칸 생성
        self.find_input.setPlaceholderText("Find...")
        self.layout.addWidget(self.find_input) #입력칸을 다이얼로그 창의 레이아웃에 추가

        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Replace with...")
        self.layout.addWidget(self.replace_input)

        self.button_box = QHBoxLayout() # 버튼을 가로로 나란히 배치할 수 있는 레이아웃 생성
        self.replace_button = QPushButton("Replace", self) # "Replace"라는 글자가 쓰인 버튼 생성 (한 번 바꾸기)
        self.replace_all_button = QPushButton("Replace All", self) #  "Replace All" 버튼 생성 (모두 바꾸기)
        self.button_box.addWidget(self.replace_button) # "Replace" 버튼을 버튼 박스에 추가
        self.button_box.addWidget(self.replace_all_button) # "Replace All" 버튼도 버튼 박스에 추가
        self.layout.addLayout(self.button_box) # 버튼 박스를 전체 레이아웃에 넣어서 다이얼로그 창에 표시

class NotepadWindow(QMainWindow):
    # 메모장 메인 윈도우 초기화, 사용자 설정 불러오기 및 UI 구성 시작
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "Notepad")
        self.initUI()

    # 전체 UI 구성: 탭, 상태바, 메뉴, 초기 탭 생성 등
    def initUI(self):
        self.setWindowTitle('Notepad')
        self.setGeometry(100, 100, 800, 600) # 창이 왼쪽 위에서 100,100 위치에, 크기는 가로 800, 세로 600으로 뜨게 함

        self.tab_widget = QTabWidget() # 여러 문서를 다룰 수 있는 탭들을 만들 수 있는 영역
        self.tab_widget.setTabsClosable(True) # 탭마다 닫기(X) 버튼을 만들 수 있게 함
        self.tab_widget.tabCloseRequested.connect(self.close_tab) # 탭의 X 버튼을 누르면 close_tab() 함수가 실행
        self.tab_widget.currentChanged.connect(self.update_status_bar) # 탭을 바꾸면 아래쪽 상태 표시줄도 새로 업데이트
        self.setCentralWidget(self.tab_widget) # 이 탭 영역을 창의 중심(main area)에 배치

        self.status_bar = QStatusBar() # 창의 맨 아래쪽에 상태 표시줄 생성
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ln 1, Col 1") # "현재 커서가 몇 줄, 몇 칸에 있는지" 알려주는 라벨 생성 
        self.status_bar.addPermanentWidget(self.status_label) # 상태 표시줄에 붙임

        self.recent_files = self.settings.value("recent_files", [], type=str) # 저장되어 있는 최근에 열었던 파일 목록을 불러옴, 아무 것도 없으면 [] (빈 목록)으로 시작

        self.create_actions() # 메뉴에 들어갈 버튼(열기, 저장 등)을 만드는 함수
        self.create_menus() # 상단 메뉴바를 구성하는 함수

        self.new_tab() # 메모장이 처음 열릴 때 빈 탭 오픈
        self.update_status_bar() # 상태표시줄도 초기에 한 번 업데이트

    # 메뉴에서 사용할 액션(버튼)의 정의 및 동작 연결
    # - 새 탭, 새 창, 열기, 저장, 되돌리기 등
    def create_actions(self):
        # File Menu Actions
        self.new_tab_action = QAction('New Tab', self) # “New Tab” 메뉴 생성
        self.new_tab_action.triggered.connect(self.new_tab) # “New Tab” 메뉴 클릭하면 self.new_tab() 함수 실행

        self.new_window_action = QAction('New Window', self)
        self.new_window_action.triggered.connect(self.new_window)

        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self.save_file)

        self.save_as_action = QAction('Save As...', self)
        self.save_as_action.triggered.connect(self.save_as_file)

        self.exit_action = QAction('Exit', self)
        self.exit_action.triggered.connect(self.close)

        # Edit Menu Actions
        self.undo_action = QAction('Undo', self) # Undo라는 이름의 메뉴 항목을 만들고, 이 항목은 내 윈도우에 붙일 거
        self.undo_action.setShortcut(QKeySequence.Undo) # "Undo 메뉴를 누르지 않아도 Ctrl + Z를 누르면 같은 기능이 실행
        self.undo_action.triggered.connect(self.undo) # Undo 메뉴를 누르거나 Ctrl+Z를 누르면, 내가 만든 undo 기능을 실행

        self.find_action = QAction("Find", self)
        self.find_action.setShortcut(QKeySequence.Find)
        self.find_action.triggered.connect(self.find_text)

        self.replace_action = QAction("Replace", self)
        self.replace_action.setShortcut(QKeySequence.Replace)
        self.replace_action.triggered.connect(self.replace_text)

        # View Menu Actions
        self.zoom_in_action = QAction('Zoom In', self)
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)

        self.zoom_out_action = QAction('Zoom Out', self)
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)

        self.status_bar_action = QAction("Status Bar", self, checkable=True) # 상태바를 켜고 끌 수 있는 체크 가능한 메뉴 항목 생성
        self.status_bar_action.setChecked(True) # 시작할 때 상태바 메뉴를 체크된 상태로 설정
        self.status_bar_action.triggered.connect(self.toggle_status_bar) # 메뉴 클릭 시 상태바 표시 여부를 바꾸는 함수 실행

    # 상단 메뉴바 구성: File, Edit, View 메뉴 및 최근 파일 리스트 포함
    def create_menus(self):
        menubar = self.menuBar() # 상단 메뉴바 영역을 가져와서 변수 menubar에 저장

        # File Menu
        file_menu = menubar.addMenu('File') # "File"이라는 이름의 메뉴를 메뉴바에 추가
        file_menu.addAction(self.new_tab_action) # "File" 메뉴 안에 "New Tab", "New Window", "Open" 기능을 추가
        file_menu.addAction(self.new_window_action)
        file_menu.addAction(self.open_action)

        self.recent_menu = QMenu("Recent", self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_files_menu() # 최근에 열었던 파일 목록을 'Recent' 메뉴에 새로 갱신해서 보여주는 함수 호출

        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator() # 구분선 추가
        file_menu.addAction(self.exit_action) # "Exit" 메뉴 추가

        # Edit Menu
        edit_menu = menubar.addMenu('Edit') # "Edit"이라는 이름의 메뉴를 추가
        edit_menu.addAction(self.undo_action) # "Undo(되돌리기)" 기능 추가
        edit_menu.addSeparator() # 메뉴 사이에 구분선
        edit_menu.addAction(self.find_action) # "Find(찾기)" 기능 메뉴에 추가
        edit_menu.addAction(self.replace_action) # "Replace(바꾸기)" 기능 메뉴에 추가

        # View Menu
        view_menu = menubar.addMenu('View') # "View"라는 메뉴를 추가
        zoom_menu = view_menu.addMenu('Zoom') # "Zoom"이라는 하위 메뉴
        zoom_menu.addAction(self.zoom_in_action) # "Zoom In(확대)", "Zoom Out(축소)" 기능 추가
        zoom_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.status_bar_action) # 상태 표시줄(하단 정보)을 켜고 끌 수 있는 토글 메뉴 추가

    # 현재 선택된 탭의 텍스트 편집기 반환
    def current_editor(self):
        return self.tab_widget.currentWidget() # 지금 활성화된 탭 안의 글쓰기 공간(QTextEdit)을 반환

    # 새 탭을 열어 새 텍스트 편집기 추가
    # 기존 파일 경로/내용이 있다면 함께 불러오기
    def new_tab(self, checked=False, file_path=None, content=''):
        editor = QTextEdit() # 새 글쓰기 영역 생성
        editor.setFontPointSize(12) # 글씨 크기를 12pt로 설정
        editor.cursorPositionChanged.connect(self.update_status_bar) # 커서 위치가 바뀌면 상태 표시줄(몇 줄 몇 칸)에 반영하도록 연결
        index = self.tab_widget.addTab(editor, "Untitled") # 새 탭에 글쓰기 영역을 넣고 제목은 "Untitled"로 표시
        self.tab_widget.setCurrentIndex(index) # 새로 만든 탭을 현재 탭으로 전환
        editor.setProperty("file_path", file_path) # 이 에디터가 어떤 파일을 불러온 것인지 저장(없으면 None)
        editor.setText(content) # 내용이 있다면 불러와서 에디터에 보여줌

    # 특정 탭을 닫고, 마지막 하나라면 전체 창 종료
    # 탭을 닫는 함수이며, 닫을 탭의 번호(index)를 입력으로 받음
    def close_tab(self, index):
        if self.tab_widget.count() > 1: # 열려 있는 탭이 2개 이상이면 → 하나만 닫고 창은 유지
            self.tab_widget.removeTab(index) # 해당 번호의 탭(index)을 닫음
        else:
            self.close() # 만약 열려 있는 탭이 1개뿐이면 → 탭을 닫는 대신 창을 아예 종료

    # 새로운 독립된 메모장 창 열기 (멀티 윈도우 지원)
    # 새로운 창을 열기 위한 함수 정의
    def new_window(self):
        new_win = NotepadWindow() # 메모장 창을 하나 새로 만듬
        new_win.show() # 새 창을 화면에 띄움
        if not hasattr(QApplication.instance(), 'windows'): # QApplication 객체에 windows라는 속성이 없으면
            QApplication.instance().windows = [] # windows라는 이름으로 빈 리스트를 만들어서 저장(열려 있는 창들을 모아놓기 위한 공간)
        QApplication.instance().windows.append(new_win) # 방금 만든 새 창(new_win)을 리스트에 추가 → 이렇게 하면 창이 닫히지 않고 유지됨 → 가비지 컬렉션(자동 삭제) 방지

    # 파일을 열고 내용 읽기
    # 이미 열린 파일이면 기존 탭 활성화
    # 빈 탭이 있으면 재사용, 아니면 새 탭 생성
    def open_file(self, file_path=None):
        if not file_path: # 파일 경로가 지정되지 않았을 때만 실행
            options = QFileDialog.Options() # 파일 열기 대화상자에 들어갈 설정을 준비
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options) # 사용자가 파일을 선택하게 하고, 그 경로를 file_path에 저장
        
        if file_path: # 파일을 선택한 경우에만 실제 열기 작업을 시작
            try: # 파일을 읽기 모드(r)로 열고, 그 안의 내용을 문자열로 읽음. UTF-8
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i in range(self.tab_widget.count()): # 열려 있는 탭을 모두 반복
                    if self.tab_widget.widget(i).property("file_path") == file_path: #  i번째 탭에 연결된 파일 경로가 지금 열려고 하는 file_path랑 같으면
                        self.tab_widget.setCurrentIndex(i) # 그 이미 열려 있는 탭으로 화면을 전환 (i번째 탭을 선택)
                        return # 함수 실행을 여기서 끝내고 나감

                editor = self.current_editor() # 현재 선택된 탭의 에디터를 가져옴
                #빈 탭이 있으면 그 탭을 재사용
                if editor and not editor.toPlainText() and not editor.property("file_path"): # 에디터가 있고, 내용은 없고, 아직 어떤 파일도 연결 안 돼 있으면
                     self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1]) # 이름을 파일 이름으로 바꿔줌. 탭 관리 위젯 불러와서 활성 탭의 인덱스를 가져오고 파일 경로를 /기준으로 나눠서 리스트로 바꿈. 나눈 것중 맨 마지막 항목인 파일이름 가져와 탭명 교체.
                     editor.setProperty("file_path", file_path) # 이 에디터가 어떤 파일과 연결되어 있는지 저장함
                     editor.setText(content) # 파일 내용을 에디터에 보여줌
                else: # 빈 탭이 아닌 경우: 새 탭을 열어서 표시
                    self.new_tab(file_path=file_path, content=content) # 새 탭을 열고, 파일 내용과 경로를 전달
                    self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1]) # 새 탭의 이름도 파일 이름으로 설정. 
                
                self.add_to_recent_files(file_path) # 이 파일을 최근 열었던 파일 목록에 저장함

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}") # 파일 열기 도중 오류가 생기면, 팝업으로 오류 메시지를 띄움

    # 현재 탭의 내용을 파일에 저장
    # 기존 경로가 없으면 "다른 이름으로 저장" 호출
    def save_file(self):
        editor = self.current_editor() # 현재 활성화된 탭의 텍스트 편집기(QTextEdit)를 가져옴
        if not editor: return # 편집기가 없다면 (탭이 비었거나 오류) 함수 종료
        file_path = editor.property("file_path") # 이 에디터가 어느 파일과 연결돼 있는지 확인 (file_path 속성)
        if file_path: # 파일 경로가 있는 경우 (이미 저장된 파일일 경우)
            try:
                with open(file_path, 'w', encoding='utf-8') as f: # 해당 경로에 파일을 **쓰기 모드(w)**로 열고 utf-8 인코딩 사용
                    f.write(editor.toPlainText()) # 에디터에 있는 텍스트 내용을 파일에 저장
                self.add_to_recent_files(file_path) # 이 파일을 최근 열었던 파일 목록에 추가
            except Exception as e: # 저장 도중 오류가 발생하면
                QMessageBox.critical(self, "Error", f"Could not save file: {e}") # 팝업으로 에러 메시지 출력
        else:
            self.save_as_file() # 저장 경로가 없다면, "다른 이름으로 저장" 함수 호출

    # "다른 이름으로 저장" 기능 처리
    # 사용자에게 저장 경로를 받아 저장 수행
    def save_as_file(self):
        editor = self.current_editor() # 현재 에디터를 불러오고
        if not editor: return # 없으면 함수 종료
        options = QFileDialog.Options() #  다이얼로그 옵션 설정
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)", options=options) # 저장할 경로를 사용자로부터 입력 받음. .txt 파일 또는 모든 파일 형식 허용
        if file_path: # 사용자가 경로를 입력했을 경우
            editor.setProperty("file_path", file_path) # 에디터 객체에 이 파일 경로를 연결시킴
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1]) # 탭 이름을 파일 이름(경로 맨 뒤)으로 설정
            self.save_file() # 설정이 끝났으니 다시 save_file()을 호출해서 실제 저장 수행

    # 현재 탭의 마지막 작업 되돌리기
    def undo(self):
        if editor := self.current_editor(): # 현재 선택된 탭의 에디터가 있으면, 변수 editor에 저장(대입하면서 조건 확인)
            editor.undo() # 해당 에디터에서 마지막 작업을 되돌림(예: 입력한 글자 삭제됨)

    # "찾기" 다이얼로그를 띄우고, 입력된 단어를 아래로 검색
    # 찾는 단어가 없으면 사용자에게 메시지 출력
    def find_text(self):
        editor = self.current_editor() # 현재 선택된 탭의 에디터(텍스트박스)를 가져옴
        if not editor: return # 에디터가 없으면 아무 작업도 하지 않고 종료

        dialog = FindDialog(self) # '찾기' 입력창이 있는 다이얼로그(FindDialog 클래스의 인스턴스)를 만듦
        def find_next(): #  "Find Next" 버튼을 눌렀을 때 실행될 내부 함수 정의 시작
            query = dialog.find_input.text() # 사용자가 찾고 싶은 단어(query)를 입력창에서 가져옴
            if not editor.find(query): # 현재 커서 위치 이후에서 query 단어를 찾음. 없으면 아래 코드 실행
                # Wrap search to the beginning
                cursor = editor.textCursor() # 에디터에서 현재 커서를 가져옴
                cursor.movePosition(QTextCursor.Start) # 커서를 문서 맨 앞으로 이동시킴
                editor.setTextCursor(cursor) #  커서를 실제 에디터에 반영함
                if not editor.find(query): # 처음부터 다시 검색했는데도 query가 없다면 아래 코드 실행
                    QMessageBox.information(self, "Find", f"Cannot find '{query}'") # 메시지박스 출력: "찾는 단어를 찾을 수 없습니다"라는 뜻

        dialog.find_next_button.clicked.connect(find_next) # "Find Next" 버튼이 눌리면 위의 find_next 함수가 실행되도록 연결
        dialog.exec_() # 다이얼로그 실행 (모달로 띄움 – 사용자가 창을 닫기 전까지 다른 작업 불가)

    # "바꾸기" 다이얼로그 띄우고 단어 교체
    # 선택된 단어만 바꾸기 또는 전체 바꾸기 기능 포함
    def replace_text(self):
        editor = self.current_editor() # 현재 작업 중인 글쓰기 창(에디터)을 가져옴
        if not editor: return # 만약 에디터가 없으면(=아무 문서도 열려 있지 않으면) 종료

        # "무엇을 찾고", "무엇으로 바꿀지" 입력하는 작은 창을 띄우는 준비
        dialog = ReplaceDialog(self)
        def replace(): # 글자 한 번만 바꾸는 작은 기능을 만든다고 선언
            find_text = dialog.find_input.text() # 사용자가 "찾을 말"로 입력한 글자를 가져옴
            replace_text = dialog.replace_input.text() # 사용자가 "바꿀 말"로 입력한 글자를 가져옴
            cursor = editor.textCursor() # 지금 글쓰기 창에서 커서 위치를 가져옴
            if cursor.hasSelection() and cursor.selectedText() == find_text: # 만약 글자가 선택되어 있고, 그 선택된 글자가 찾을 말과 같으면
                cursor.insertText(replace_text) # 선택된 글자를 "바꿀 말"로 바꿔줌
            find_next() # 바꾼 다음에, 다음 같은 글자를 찾아줌

        def replace_all(): # 글자 전체를 한꺼번에 바꾸는 기능
            find_text = dialog.find_input.text() # 찾을 말과 바꿀 말을 가져옴
            replace_text = dialog.replace_input.text() 
            text = editor.toPlainText() # 글쓰기 창 안의 모든 글을 하나의 긴 글로 가져옴
            new_text = text.replace(find_text, replace_text) # 찾을 말을 바꿀 말로 전부 바꿔줌
            if text != new_text: # 진짜로 바뀐 게 있는지 확인
                editor.setPlainText(new_text) # 바뀐 글을 다시 글쓰기 창에 넣음

        def find_next(): # 다음 같은 단어를 찾는 기능
            query = dialog.find_input.text() # 찾을 말을 가져옴
            if not editor.find(query): # 그 말이 안 보이면
                QMessageBox.information(self, "Replace", f"Cannot find '{query}'") # "그 단어를 찾을 수 없어요" 라는 알림 창을 띄움

        dialog.replace_button.clicked.connect(replace) # "바꾸기" 버튼을 누르면 replace() 함수가 실행
        dialog.replace_all_button.clicked.connect(replace_all) # "전체 바꾸기" 버튼을 누르면 replace_all() 함수가 실행
        dialog.exec_() # 바꾸기 창을 실제로 화면에 띄움


    # 현재 탭의 글자 크기를 키움 (최대 72pt까지)
    def zoom_in(self):
        if editor := self.current_editor(): # 지금 사용 중인 글쓰기 창(에디터)이 있다면 가져옴
            font = editor.font() # 글쓰기 창에 사용되는 글꼴(font)을 가져옴
            size = font.pointSize() # 그 글꼴의 현재 크기 확인
            if size < 72: # 글자 크기가 72보다 작으면
                font.setPointSize(size + 2) # 글자 크기를 현재보다 2만큼 확대
                editor.setFont(font) # 바뀐 글꼴을 다시 글쓰기 창에 적용

    #현재 탭의 글자 크기를 줄임 (최소 6pt까지)
    def zoom_out(self):
        if editor := self.current_editor(): # 글쓰기 창이 있는지 확인하고 가져옴
            font = editor.font() # 글꼴과 그 크기를 확인
            size = font.pointSize()
            if size > 6: # 글자 크기가 6보다 크면
                font.setPointSize(size - 2) # 글자 크기를 2만큼 줄이고 다시 적용
                editor.setFont(font)

    # 하단 상태바 표시 여부 토글
    def toggle_status_bar(self):
        self.status_bar.setVisible(self.status_bar_action.isChecked()) # 상태바를 체크 상태에 따라 보이거나 숨김

    # 커서의 현재 줄(Line), 칼럼(Column) 정보를 상태바에 표시
    def update_status_bar(self):
        editor = self.current_editor() # 지금 열려 있는 글쓰기 창 소환
        if editor: # 글쓰기 창이 열려 있다면 실행
            cursor = editor.textCursor() # 깜빡이는 커서의 위치 정보 확인
            line = cursor.blockNumber() + 1 # 커서가 있는 줄 번호와 칸 번호를 1부터 시작하게 설정
            col = cursor.columnNumber() + 1
            self.status_label.setText(f"Ln {line}, Col {col}") # 상태바에 "Ln O, Col O"형태로 띄움

    # 최근 열었던 파일 리스트 관리 (최대 5개 저장)
    # 설정에 저장하여 다음 실행 시 복원 가능하게 함
    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files: # 이미 최근 파일 목록에 있으면 삭제
            self.recent_files.remove(file_path) 
        self.recent_files.insert(0, file_path) # 그 파일을 맨 앞(가장 최근 위치)에 추가
        self.recent_files = self.recent_files[:5] # 최근 파일은 최대 5개까지만 저장
        self.settings.setValue("recent_files", self.recent_files) # 이 목록을 앱 설정에 저장. 다시 열었을때 기억 목적
        self.update_recent_files_menu() # 메뉴에도 이 최근 파일 목록을 다시 보여줘야 하기에 갱신

    # 최근 파일 목록을 'Recent' 메뉴에 갱신
    # 각 파일 클릭 시 바로 열 수 있도록 연결
    def update_recent_files_menu(self):
        self.recent_menu.clear() # 최근 파일 메뉴를 클리어하고 새로 채움
        for file_path in self.recent_files: # 저장된 최근 파일들 하나씩 꺼내서 메뉴에 넣을 준비
            action = QAction(file_path, self) # 메뉴에 나타나는 파일 이름 생성
            action.triggered.connect(lambda checked, path=file_path: self.open_file(path)) # 누군가 이 메뉴 항목(action)을 누르면,해당 파일(file_path)을 열어주는 함수(self.open_file)를 실행
            self.recent_menu.addAction(action) # 만든 서브 메뉴 항목을 메인 메뉴에 추가

    # 창을 닫을 때 사용자 인터페이스 상태(크기, 위치 등) 저장
    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry()) # 지금 창의 크기, 위치를 저장. 다음에 똑같이 열 수 있는 환경 저장
        QApplication.instance().quit() # 프로그램을 완전 종료
        event.accept() # 창 닫기 이벤트를 허용


# 프로그램 실행 시 수행되는 메인 루틴
# - 애플리케이션 생성
# - 메모장 창 띄우기
# - 창 상태 복원
# - 여러 창 관리용 리스트 등록
def main(): # 프로그램을 시작할 때 실행되는 메인 함수
    app = QApplication(sys.argv) # PyQt 앱을 시작하기 위해 앱 객체 생성
    app.setQuitOnLastWindowClosed(False) # 창이 하나도 안 남았다고 해도, 프로그램을 완전히 종료하지 않고 계속 돌게 함. 나중에 창을 다시 열 수 있게 하기 위함
    
    notepad = NotepadWindow() # 메모장 클래스를 활용해서 창을 하나 생성
    
    geometry = notepad.settings.value("geometry") # 이전에 창을 닫을 때 저장했던 위치/크기 정보 불러옴. 없으면 None
    if geometry: # 만약 저장된 위치/크기 정보가 있다면, 그걸로 창을 복원
        notepad.restoreGeometry(geometry)
    else: # 없다면, 화면 왼쪽 위(100, 100)에 너비 800, 높이 600 크기 메모장 생성
        notepad.setGeometry(100, 100, 800, 600)
        
    notepad.show() # 메모장 창을 실제로 화면에 띄움
    
    if not hasattr(app, 'windows'): # app 객체 안에 windows라는 리스트가 있는지 확인하고, 없으면 생성
        app.windows = []
    app.windows.append(notepad) # 지금 만든 메모장 창을 windows 리스트에 넣음
    
    sys.exit(app.exec_()) # PyQt 앱을 본격적으로 실행

# 이 파일이 직접 실행되었을 때만 main() 호출해서 앱을 시작
if __name__ == '__main__':
    main()
