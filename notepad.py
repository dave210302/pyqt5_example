
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction,
                             QFileDialog, QTabWidget, QVBoxLayout, QWidget,
                             QStatusBar, QLabel, QDialog, QLineEdit, QPushButton,
                             QHBoxLayout, QMenu, QMessageBox)
from PyQt5.QtGui import QIcon, QKeySequence, QTextCursor
from PyQt5.QtCore import Qt, QSettings

class FindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Find")
        self.layout = QVBoxLayout(self)

        self.find_input = QLineEdit(self)
        self.find_input.setPlaceholderText("Find...")
        self.layout.addWidget(self.find_input)

        self.button_box = QHBoxLayout()
        self.find_next_button = QPushButton("Find Next", self)
        self.button_box.addWidget(self.find_next_button)
        self.layout.addLayout(self.button_box)

class ReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Replace")
        self.layout = QVBoxLayout(self)

        self.find_input = QLineEdit(self)
        self.find_input.setPlaceholderText("Find...")
        self.layout.addWidget(self.find_input)

        self.replace_input = QLineEdit(self)
        self.replace_input.setPlaceholderText("Replace with...")
        self.layout.addWidget(self.replace_input)

        self.button_box = QHBoxLayout()
        self.replace_button = QPushButton("Replace", self)
        self.replace_all_button = QPushButton("Replace All", self)
        self.button_box.addWidget(self.replace_button)
        self.button_box.addWidget(self.replace_all_button)
        self.layout.addLayout(self.button_box)

class NotepadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("MyCompany", "Notepad")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Notepad')
        self.setGeometry(100, 100, 800, 600)

        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.update_status_bar)
        self.setCentralWidget(self.tab_widget)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Ln 1, Col 1")
        self.status_bar.addPermanentWidget(self.status_label)

        self.recent_files = self.settings.value("recent_files", [], type=str)

        self.create_actions()
        self.create_menus()

        self.new_tab()
        self.update_status_bar()

    def create_actions(self):
        # File Menu Actions
        self.new_tab_action = QAction('New Tab', self)
        self.new_tab_action.triggered.connect(self.new_tab)

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
        self.undo_action = QAction('Undo', self)
        self.undo_action.setShortcut(QKeySequence.Undo)
        self.undo_action.triggered.connect(self.undo)

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

        self.status_bar_action = QAction("Status Bar", self, checkable=True)
        self.status_bar_action.setChecked(True)
        self.status_bar_action.triggered.connect(self.toggle_status_bar)

    def create_menus(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.new_tab_action)
        file_menu.addAction(self.new_window_action)
        file_menu.addAction(self.open_action)

        self.recent_menu = QMenu("Recent", self)
        file_menu.addMenu(self.recent_menu)
        self.update_recent_files_menu()

        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction(self.undo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)
        edit_menu.addAction(self.replace_action)

        # View Menu
        view_menu = menubar.addMenu('View')
        zoom_menu = view_menu.addMenu('Zoom')
        zoom_menu.addAction(self.zoom_in_action)
        zoom_menu.addAction(self.zoom_out_action)
        view_menu.addAction(self.status_bar_action)

    def current_editor(self):
        return self.tab_widget.currentWidget()

    def new_tab(self, checked=False, file_path=None, content=''):
        editor = QTextEdit()
        editor.setFontPointSize(12)
        editor.cursorPositionChanged.connect(self.update_status_bar)
        index = self.tab_widget.addTab(editor, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        editor.setProperty("file_path", file_path)
        editor.setText(content)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.close()

    def new_window(self):
        new_win = NotepadWindow()
        new_win.show()
        if not hasattr(QApplication.instance(), 'windows'):
            QApplication.instance().windows = []
        QApplication.instance().windows.append(new_win)

    def open_file(self, file_path=None):
        if not file_path:
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i in range(self.tab_widget.count()):
                    if self.tab_widget.widget(i).property("file_path") == file_path:
                        self.tab_widget.setCurrentIndex(i)
                        return

                editor = self.current_editor()
                if editor and not editor.toPlainText() and not editor.property("file_path"):
                     self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])
                     editor.setProperty("file_path", file_path)
                     editor.setText(content)
                else:
                    self.new_tab(file_path=file_path, content=content)
                    self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])
                
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    def save_file(self):
        editor = self.current_editor()
        if not editor: return
        file_path = editor.property("file_path")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(editor.toPlainText())
                self.add_to_recent_files(file_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {e}")
        else:
            self.save_as_file()

    def save_as_file(self):
        editor = self.current_editor()
        if not editor: return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            editor.setProperty("file_path", file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), file_path.split('/')[-1])
            self.save_file()

    def undo(self):
        if editor := self.current_editor():
            editor.undo()

    def find_text(self):
        editor = self.current_editor()
        if not editor: return

        dialog = FindDialog(self)
        def find_next():
            query = dialog.find_input.text()
            if not editor.find(query):
                # Wrap search to the beginning
                cursor = editor.textCursor()
                cursor.movePosition(QTextCursor.Start)
                editor.setTextCursor(cursor)
                if not editor.find(query):
                    QMessageBox.information(self, "Find", f"Cannot find '{query}'")

        dialog.find_next_button.clicked.connect(find_next)
        dialog.exec_()

    def replace_text(self):
        editor = self.current_editor()
        if not editor: return

        dialog = ReplaceDialog(self)
        def replace():
            find_text = dialog.find_input.text()
            replace_text = dialog.replace_input.text()
            cursor = editor.textCursor()
            if cursor.hasSelection() and cursor.selectedText() == find_text:
                cursor.insertText(replace_text)
            find_next()

        def replace_all():
            find_text = dialog.find_input.text()
            replace_text = dialog.replace_input.text()
            text = editor.toPlainText()
            new_text = text.replace(find_text, replace_text)
            if text != new_text:
                editor.setPlainText(new_text)

        def find_next():
            query = dialog.find_input.text()
            if not editor.find(query):
                QMessageBox.information(self, "Replace", f"Cannot find '{query}'")

        dialog.replace_button.clicked.connect(replace)
        dialog.replace_all_button.clicked.connect(replace_all)
        dialog.exec_()


    def zoom_in(self):
        if editor := self.current_editor():
            font = editor.font()
            size = font.pointSize()
            if size < 72:
                font.setPointSize(size + 2)
                editor.setFont(font)

    def zoom_out(self):
        if editor := self.current_editor():
            font = editor.font()
            size = font.pointSize()
            if size > 6:
                font.setPointSize(size - 2)
                editor.setFont(font)

    def toggle_status_bar(self):
        self.status_bar.setVisible(self.status_bar_action.isChecked())

    def update_status_bar(self):
        editor = self.current_editor()
        if editor:
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            col = cursor.columnNumber() + 1
            self.status_label.setText(f"Ln {line}, Col {col}")

    def add_to_recent_files(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:5] # Keep only the last 5
        self.settings.setValue("recent_files", self.recent_files)
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        for file_path in self.recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, path=file_path: self.open_file(path))
            self.recent_menu.addAction(action)

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        QApplication.instance().quit()
        event.accept()


def main():
    app = QApplication(sys.argv)
    # Allows to have multiple windows
    app.setQuitOnLastWindowClosed(False)
    
    notepad = NotepadWindow()
    
    # Restore geometry
    geometry = notepad.settings.value("geometry")
    if geometry:
        notepad.restoreGeometry(geometry)
    else:
        notepad.setGeometry(100, 100, 800, 600)
        
    notepad.show()
    
    # Keep track of windows
    if not hasattr(app, 'windows'):
        app.windows = []
    app.windows.append(notepad)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
