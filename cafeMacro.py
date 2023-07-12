import sys
import os
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon
import loginApi as api
from ui import Ui_MainWindow


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

main_ui = Ui_MainWindow()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        main_ui.setupUi(self)     
        self.show()
        self.setWindowTitle("Cafe Macro")
        self.browser = None
        self.PATH_IMG1 = None
        self.PATH_IMG2 = None

        window_ico = resource_path('favicon.ico')
        self.setWindowIcon(QIcon(window_ico))

        main_ui.input_id.setText("itthere2")
        main_ui.input_pwd.setText("naver1!2@L")

        self.selected_category_name = []
        self.selected_category_href = []

        main_ui.btn_login.clicked.connect(self.btn_loginClicked)
        # main_ui.btn_login.clicked.connect(self.test)
        main_ui.btn_getCate.clicked.connect(self.brn_getCateClicked)
        main_ui.btn_start.clicked.connect(self.btn_startClicked)
        main_ui.btn_add.clicked.connect(self.btn_addClicked)
        main_ui.btn_del.clicked.connect(self.btn_delClicked)
        main_ui.btn_get_image_1.clicked.connect(self.btn_get_image_1Clicked)
        main_ui.btn_get_image_2.clicked.connect(self.btn_get_image_2Clicked)
        main_ui.btn_delete_image_1.clicked.connect(self.btn_delete_image_1Clicked)
        main_ui.btn_delete_image_2.clicked.connect(self.btn_delete_image_2Clicked)

    def test(self):
        for i in range(0,4):
            main_ui.post_urls.append('str')

    def btn_get_image_1Clicked(self):
        image_path = QFileDialog.getOpenFileName(self)      
        self.PATH_IMG1 = image_path[0]
        main_ui.image_1.setText(self.PATH_IMG1)
        self.PATH_IMG1 = self.PATH_IMG1.replace("/", "\\")
    
    def btn_get_image_2Clicked(self):
        image_path = QFileDialog.getOpenFileName(self)          
        self.PATH_IMG2 = image_path[0]
        main_ui.image_2.setText(self.PATH_IMG2)
        self.PATH_IMG2 = self.PATH_IMG2.replace("/", "\\")

    def btn_delete_image_1Clicked(self):
        if self.PATH_IMG1:
            self.PATH_IMG1 = None
            main_ui.image_1.setText("")
        else:
            return 
    
    def btn_delete_image_2Clicked(self):
        if self.PATH_IMG2:
            self.PATH_IMG2 = None
            main_ui.image_2.setText("")
        else:
            return 

    def btn_addClicked(self):
        if main_ui.category_list.currentItem():
            main_ui.selected.addItem(self.current_cafe + ' - ' +main_ui.category_list.currentItem().text())
            self.selected_category_href.append(self.final_hrefs_true[self.category_name_true.index(main_ui.category_list.currentItem().text())])
            self.selected_category_name.append(main_ui.category_list.currentItem().text())

        return

    def btn_delClicked(self):
        if main_ui.selected.currentItem():
            tmp = main_ui.selected.currentRow()
            main_ui.selected.takeItem(main_ui.selected.currentRow())
            self.selected_category_href.remove(self.selected_category_href[tmp])
            self.selected_category_name.remove(self.selected_category_name[tmp])

    def move_current_item(self, src, dst):
        if src.currentItem():
            row = src.currentRow()
            dst.addItem(src.takeItem(row))

    def btn_loginClicked(self):
        id = main_ui.input_id.text()
        pwd = main_ui.input_pwd.text()

        if all([id, pwd]):
            if self.browser is None:
                self.browser = api.naverCafePostStart()
        else:
            QMessageBox.information(self, 'Cafe Macro', '아이디와 비밀번호를 입력해주세요')
            return 
                
        main_ui.selected.clear()
        main_ui.cafe_list.clear()
        main_ui.category_list.clear()
        
        api.naverLogin(id, pwd, self.browser)
        if self.browser.current_url == 'https://nid.naver.com/nidlogin.login':
            self.browser.close()
            QMessageBox.information(self, 'Cafe Macro', '로그인에 실패하였습니다. 로그인 정보를 다시 확인해주세요.')
            self.browser = None
            return 

        self.cafe_hrefs, self.cafe_name = api.checkSubscriptionCafe(self.browser)
        
        main_ui.cafe_list.addItems(self.cafe_name)

    def brn_getCateClicked(self):
        if self.browser is None:
            QMessageBox.information(self,'Cafe Macro','로그인 먼저 해주세요.')
            return
        
        main_ui.category_list.clear()
        
        self.final_hrefs_true, self.category_name_true = api.CafeCategoryGet(self.browser, self.cafe_hrefs[main_ui.cafe_list.currentIndex().row()])
        self.current_cafe = self.cafe_name[main_ui.cafe_list.currentIndex().row()]
        main_ui.category_list.addItems(self.category_name_true)
        

    def btn_startClicked(self):
        if self.browser is None:
            QMessageBox.information(self,'Cafe Macro','로그인 먼저 해주세요.')
            return
        
        if self.selected_category_href:
            pass
        else:
            QMessageBox.information(self,'Cafe Macro','선택된 게시판이 없습니다!')
            return 

        if self.PATH_IMG2 and self.PATH_IMG1:
            PATH_IMG = [self.PATH_IMG1, self.PATH_IMG2]
        elif self.PATH_IMG1:
            PATH_IMG = [self.PATH_IMG1]
        elif self.PATH_IMG2:
            PATH_IMG = [self.PATH_IMG2]
        else:
            PATH_IMG = []

        if main_ui.tags.toPlainText():
            tag_list = main_ui.tags.toPlainText().replace(" ", "").split(',')
        else:
            tag_list = []
            
        self.comments = main_ui.post.toPlainText()

        if main_ui.links.toPlainText():
            self.url_list = main_ui.links.toPlainText().replace(" ", "").split("\n")
        else:
            self.url_list = []

        self.post_urls = api.CafePostWriting(self.browser, main_ui.post_title.text(), self.selected_category_href, self.comments, PATH_IMG, tag_list, self.url_list)

        for i in self.post_urls:
            main_ui.post_urls.append(i)

        self.browser = None
        

if __name__=="__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())