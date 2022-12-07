import time
from enum import Enum
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QThread, QEvent, QPoint
from PyQt5.QtGui import QKeyEvent, QKeySequence, QMouseEvent, QCloseEvent, QCursor
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QComboBox,
    QStackedWidget, QAction, QSplitter,
    QHBoxLayout, QVBoxLayout, QShortcut,
    QLineEdit, QListWidget, QTextEdit,
    QTabWidget, QStyledItemDelegate, QListWidgetItem,
    QStatusBar, QMenu, QLabel
)

from panels import (
    BaseWindow, CGridLayoutWidget, CHBoxLayoutWidget,
    CVBoxLayoutWidget
)
from crud.user import get_current_user
from crud.note import list_note, search_note, add_note, update_note, delete_note
from schema.note import Note
from utils.common import gen_html


class NoteOperation(str, Enum):
    PRE_CREATE = "pre-create-item"
    SAVE_CONTENT = "save-content"
    WHOLE_CREATE = "pre-create-and-save"


class ListWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(ListWorker, self).__init__(*args, **kwargs)
        self.result = None

    def run(self):
        self.result = list_note()
        self.finished.emit()

class SearchWorker(QObject):
    finished = pyqtSignal()
    def __init__(self, search_flag, search_content, *args, **kwargs):
        super(SearchWorker, self).__init__(*args, **kwargs)
        self.search_flag = search_flag
        self.search_content = search_content
        self.result = None

    def run(self):
        self.result = search_note(self.search_flag, self.search_content)
        self.finished.emit()


class MainWindow(BaseWindow):
    note_stuff = pyqtSignal(str)
    is_markdown = False
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(1280, 768)
        self.setMinimumSize(1280, 768)

        self.setWindowTitle('Knowledge Hub')
        self.setContentsMargins(0, 0, 0, 0)
        self.center()
        self.initUI()
        self.installEventFilter(self)
        self.note_stuff.connect(self.handle_note_stuff)
        self.list_thread = QThread()
        self.list_worker = ListWorker()
        self.list_worker.moveToThread(self.list_thread)
        self.list_thread.started.connect(self.list_worker.run)
        self.list_worker.finished.connect(self.list_thread.quit)
        self.list_worker.finished.connect(self.list_worker.deleteLater)
        self.list_thread.finished.connect(self.list_thread.deleteLater)
        self.list_thread.start()
        # set items to list widget
        self.list_thread.finished.connect(self.list_recent_20_items)

    def createMenuBar(self):
        current_user = get_current_user()
        # 创建menu bar
        menubar_widget = self.menuBar()
        menubar_widget.setNativeMenuBar(False)
        create_action = QAction('&New File', self)
        create_action.triggered.connect(self.create_file)
        file_menu = menubar_widget.addMenu("&File")
        file_menu.addAction(create_action)
        
        profile_menu = QMenu("{}".format(current_user.name), menubar_widget)
        # profile_menu = menubar_widget.addMenu("{}".format(current_user.name))
        profile_menu.addAction("Profile Window", self.open_profile_window)
        menubar_widget.addMenu(profile_menu)

    def initUI(self):
        self.createMenuBar()
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # 创建主窗口部件
        self.main_widget = CHBoxLayoutWidget()

        # 分割成水平左右两侧
        H_splitter = QSplitter(Qt.Horizontal)

        # 左侧布局
        # - 搜索
        # - 展示列表
        self.left_widget = CVBoxLayoutWidget()
        self.left_widget.setMinimumWidth(250)
        
        self.left_top_widget = CHBoxLayoutWidget()
        self.left_top_widget.setMinimumHeight(50)
        self.left_top_widget.main_layout.setContentsMargins(5, 0, 5, 0)
        
        self.left_bottom_widget = QWidget()
        self.left_bottom_layout = QVBoxLayout()
        self.left_bottom_layout.setSpacing(0)
        self.left_bottom_layout.setContentsMargins(5, 0, 5, 1)
        self.left_bottom_widget.setLayout(self.left_bottom_layout)

        self.type_combobox = QComboBox()
        self.type_combobox.addItems(["tag", "content", "title", "type"])
        self.type_combobox.setItemDelegate(QStyledItemDelegate(self.type_combobox))
        self.type_combobox.setFixedWidth(90)
        self.type_combobox.setEditable(True)
        self.type_combobox.lineEdit().setReadOnly(True)
        self.type_combobox.lineEdit().setAlignment(Qt.AlignCenter)
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_result)
        self.left_top_widget.main_layout.addWidget(self.type_combobox)
        self.left_top_widget.main_layout.addWidget(self.search_input)

        self.result_list = QListWidget()
        font = self.font()
        font.setPointSize(18)
        self.result_list.setFont(font)
        self.left_bottom_layout.addWidget(self.result_list)
        self.result_list.itemDoubleClicked.connect(self.open_note)
        self.result_list.setContextMenuPolicy(3)
        self.result_list.customContextMenuRequested[QPoint].connect(self.list_context_menu)

        self.left_widget.main_layout.addWidget(self.left_top_widget)
        self.left_widget.main_layout.addWidget(self.left_bottom_widget)
        # 右侧布局
        # - 空panel
        # - file tab
        # - toolbar
        # - 编辑区
        self.right_widget = CHBoxLayoutWidget()
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setContentsMargins(0, 0, 0, 0)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)

        self.right_widget.main_layout.addWidget(self.tab_widget)

        H_splitter.addWidget(self.left_widget)
        H_splitter.addWidget(self.right_widget)
        H_splitter.setStretchFactor(1, 10)
        self.main_widget.main_layout.addWidget(H_splitter)

        # create new file
        cmd_n = QShortcut(QKeySequence("Ctrl+n"), self)
        cmd_n.activated.connect(self.create_file)
        # markdown convert
        cmd_t = QShortcut(QKeySequence('Ctrl+t'), self)
        cmd_t.activated.connect(self.toggle_markdown)
        # save
        cmd_s = QShortcut(QKeySequence('Ctrl+s'), self)
        cmd_s.activated.connect(lambda: self.note_stuff.emit(NoteOperation.SAVE_CONTENT))
        self.setCentralWidget(self.main_widget)

    def create_file_window(self):
        self.new_file_widget = CGridLayoutWidget()
        self.new_file_widget.setFixedSize(240, 240)
        self.new_file_widget.setObjectName("new_file_window")

        self.input_widget = CGridLayoutWidget(no_spacing=False, no_content_margin=False)
        self.new_file_name_label = QLabel("标 题")
        self.new_file_name_label.setAlignment(Qt.AlignCenter)
        self.new_file_name_label.setFixedHeight(30)
        self.new_file_name_label.setFont(self.gen_font(16))
        self.new_file_name_input = QLineEdit()
        self.new_file_name_input.setFixedHeight(30)
        self.new_file_tag_label = QLabel("分 类")
        self.new_file_tag_label.setAlignment(Qt.AlignCenter)
        self.new_file_tag_label.setFixedHeight(30)
        self.new_file_tag_label.setFont(self.gen_font(16))
        self.new_file_tag_input = QLineEdit()
        self.new_file_tag_input.setFixedHeight(30)
        self.input_widget.main_layout.addWidget(self.new_file_name_label, 0, 0, 1, 1)
        self.input_widget.main_layout.addWidget(self.new_file_name_input, 0, 1, 1, 3)
        self.input_widget.main_layout.addWidget(self.new_file_tag_label, 1, 0, 1, 1)
        self.input_widget.main_layout.addWidget(self.new_file_tag_input, 1, 1, 1, 3)

        self.button_widget = CGridLayoutWidget(no_spacing=False, no_content_margin=False)
        self.new_file_confirm_button = QPushButton("确 定")
        self.new_file_confirm_button.setObjectName("new-file-confirm-button")
        self.new_file_confirm_button.setFont(self.gen_font(16))
        self.new_file_cancel_button = QPushButton("取 消")
        self.new_file_cancel_button.setObjectName("new-file-cancel-button")
        self.new_file_cancel_button.setFont(self.gen_font(16))
        self.new_file_confirm_button.clicked.connect(lambda: self.note_stuff.emit(NoteOperation.PRE_CREATE))
        self.new_file_cancel_button.clicked.connect(self.new_file_widget.close)
        self.button_widget.main_layout.addWidget(self.new_file_confirm_button, 2, 1, 1, 2)
        self.button_widget.main_layout.addWidget(self.new_file_cancel_button, 2, 3, 1, 2)
        
        self.new_file_widget.main_layout.addWidget(self.input_widget, 0, 0, 2, 4)
        self.new_file_widget.main_layout.addWidget(self.button_widget, 2, 0, 1, 4)
        self.new_file_widget.setWindowFlags(Qt.WindowStaysOnTopHint)

    def create_file(self):
        self.create_file_window()
        self.new_file_widget.show()

    def toggle_markdown(self):
        current_tab_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.currentWidget()
        if current_tab_index != -1:
            edit_widget = current_tab.findChild(QStackedWidget, 'edit_widget')
            edit_area = edit_widget.findChild(QTextEdit, "edit_area")
            edit_preview = edit_widget.findChild(QTextEdit, "edit_preview")
            html_preview = gen_html(edit_area.toPlainText())
            edit_preview.setHtml(html_preview)
            if edit_preview.hasFocus() or edit_area.hasFocus():
                if not self.is_markdown and edit_widget.indexOf(edit_area) == 0:
                    edit_widget.setCurrentWidget(edit_preview)
                    self.is_markdown = True
                else:
                    edit_widget.setCurrentWidget(edit_area)
                    self.is_markdown = False
            
    def list_recent_20_items(self):
        result = self.list_worker.result
        for item in result:
            self.result_list.addItem(item.title)
        else:
            self.status_bar.clearMessage()
            self.status_bar.showMessage("initial list successful")

    def search_result(self):
        search_type = self.type_combobox.currentText()
        search_content = self.search_input.text().strip()
        # Thread worker here
        self.search_thread = QThread()
        self.search_worker = SearchWorker(search_flag=search_type, search_content=search_content)
        self.search_worker.moveToThread(self.search_thread)
        self.search_thread.started.connect(self.search_worker.run)
        self.search_worker.finished.connect(self.search_thread.quit)
        self.search_worker.finished.connect(self.search_worker.deleteLater)
        self.search_thread.finished.connect(self.search_thread.deleteLater)
        self.search_thread.start()
        # set items to list widget
        self.search_thread.finished.connect(self.list_search_items)

    def list_search_items(self):
        items = self.search_worker.result
        if items != []:
            self.result_list.clear()
            for item in items:
                self.result_list.addItem(item.title)

        self.status_bar.clearMessage()
        self.status_bar.showMessage("search complete")

    def create_tab(self, title: str):
        new_tab_widget = CVBoxLayoutWidget()
        new_tab_widget.setObjectName(title)
        tool_bar_widget = QWidget()
        tool_bar_widget.setFixedHeight(30)
        tool_bar_layout = QHBoxLayout()
        tool_bar_layout.setSpacing(0)
        tool_bar_layout.setContentsMargins(0, 0, 0, 0)
        tool_bar_widget.setLayout(tool_bar_layout)

        edit_widget = QStackedWidget()
        edit_widget.setObjectName("edit_widget")
        edit_area = QTextEdit()
        edit_area.setObjectName("edit_area")
        edit_area.setTabStopWidth(edit_area.fontMetrics().width(' ')*4)
        edit_preview = QTextEdit()
        edit_preview.setObjectName("edit_preview")
        edit_preview.setReadOnly(True)
        edit_preview.setTabStopWidth(edit_preview.fontMetrics().width(' ')*4)
        edit_widget.addWidget(edit_area)
        edit_widget.addWidget(edit_preview)
        edit_widget.focusInEvent

        new_tab_widget.main_layout.addWidget(tool_bar_widget)
        new_tab_widget.main_layout.addWidget(edit_widget)
        self.tab_widget.addTab(new_tab_widget, title)
        self.tab_widget.setCurrentWidget(new_tab_widget)
        res = search_note(search_flag="title", search_content=title)
        if res != []:
            if res[-1].content != "":
                edit_area.setText(res[-1].content)


    def handle_note_stuff(self, msg: str):
        """Process note related stuff
        """
        if NoteOperation.PRE_CREATE == msg:
            self.file_creation()
        
        if NoteOperation.SAVE_CONTENT == msg:
            self.save(save_all=True)

    def open_note(self, clicked_item: QListWidgetItem):
        exists_tab = False
        tab = None
        for each_tab in self.tab_widget.findChildren(QWidget):
            if each_tab.objectName() == clicked_item.text():
                exists_tab = True
                tab = each_tab
        if exists_tab:
            self.tab_widget.setCurrentWidget(tab)
        else:
            self.create_tab(clicked_item.text())
        
    def save(self, save_all=False):
        current_tab_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.currentWidget()
        if current_tab_index != -1:
            tab_name = self.tab_widget.tabText(current_tab_index)
            edit_widget = current_tab.findChild(QStackedWidget, 'edit_widget')
            edit_area = edit_widget.findChild(QTextEdit, "edit_area")
            content = edit_area.toPlainText()
            notes = search_note(search_flag='title', search_content=tab_name)
            if notes != []:
                if notes[-1].content != content:
                    notes[-1].content = content
                    try:
                        update_note(notes[-1])
                    except Exception as e:
                        self.message_box(str(e))
                        return
                    
            else:
                # TODO: create new file logic
                self.create_file(save_all=save_all)

    def file_creation(self, save_all=False):
        """
        Logic:
            - save title and tag:
                - read content from create file window
                - construct Note instance
                - save
                - open_tab
                - add to list_widget
                - close create file window
            - whole save:
                - read tab text edit content
                - read content from create file window
                - construct Note instance
                - save
                - update current tab title
                - add to list_widget
                - close create file window
        """
        try:
            title = self.new_file_name_input.text()
            tag = self.new_file_tag_input.text()
            content = None
            if title == "" or tag == "":
                self.message_box("请填写标题和分类")
                return
            
            if save_all:
                current_tab_index = self.tab_widget.currentIndex()
                current_tab = self.tab_widget.currentWidget()
                if current_tab_index != -1:
                    # tab_name = self.tab_widget.tabText(current_tab_index)
                    edit_widget = current_tab.findChild(QStackedWidget, 'edit_widget')
                    edit_area = edit_widget.findChild(QTextEdit, "edit_area")
                    content = edit_area.toPlainText()

            now_timestamp = int(time.time()*1000)
            note = Note(
                uuid=get_current_user().uid,
                title=title,
                type="markdown",
                tag=tag,
                content=content,
                created_at=int(time.time()),
                modified_at=int(now_timestamp),
                is_deleted=0,
                is_template=0,
                is_trash=0
            )
            add_note(note)
            self.status_bar.clearMessage()
            self.status_bar.showMessage("新建文件成功")
        except Exception as e:
            self.message_box(str(e))
            return
        else:
            self.result_list.insertItem(0, note.title)
            if save_all:
                # update current tab name
                current_tab.setObjectName(title)
            else:
                # create new tab
                self.create_tab(note.title)
            self.new_file_widget.close()

    def open_profile_window(self):
        """TODO: User info update code here"""
        self.message_box("hello")

    def close_tab(self, index: int):
        for each_tab in self.tab_widget.findChildren(QWidget):
            if self.tab_widget.indexOf(each_tab) == index:
                each_tab.deleteLater()
        self.tab_widget.removeTab(index)

    def delete_note_from_list(self, point: QPoint):
        item = self.result_list.itemAt(point.x(), point.y())
        self.result_list.removeItemWidget(item)
        # list_item = self.result_list.takeItem(self.result_list.row(item))
        delete_note(item.text())


    def list_context_menu(self, point: QPoint):
        popMenu = QMenu()
        delete_action = QAction('删除', self)
        delete_action.triggered.connect(lambda: self.delete_note_from_list(point))
        delete_action = popMenu.addAction(delete_action)
        popMenu.exec_(QCursor.pos())


    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        # TODO: show something here
        if event.type() == 129:
            self.status_bar.clearMessage()

        return super().eventFilter(obj, event)

    def closeEvent(self, event: QCloseEvent) -> None:
        # TODO: save all temp tabs
        return super().closeEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        return super().keyPressEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.type() in [QMouseEvent.MouseButtonPress, QMouseEvent.MouseButtonDblClick]:
            ...
        return super().mousePressEvent(event)