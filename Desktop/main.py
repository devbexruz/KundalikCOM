
#######   #      #  #######    ######   #######   ########   #######  
   #      ##    ##  #     ##  #      #  #      #     #      #         
   #      #  ##  #  #######   #      #  #######      #       ######   
   #      #      #  #         #      #  #    #       #             #  
#######   #      #  #          ######   #     #      #      #######   




import sys
import pyperclip
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import requests
from database import DatabaseConnect
from server import ServerConnect
import kundalikcom_func
# QtDesigner sahifalarini import qilish
from ui_pyfiles.main import Ui_MainWindow as Ui_MainWindow
from ui_pyfiles.edit import Ui_Frame as Ui_EditFrame
from ui_pyfiles.login import Ui_Frame as Ui_LoginFrame
from ui_pyfiles.refresh_logins_data import Ui_Frame as Ui_KundalikRefreshFrame
from ui_pyfiles.kundalik_login import Ui_Frame as Ui_KundalikLoginFrame
from ui_pyfiles.buy_dialog import Ui_Frame as Ui_BuyDialogFrame
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from datetime import datetime


# Qo'shimcha
from functools import partial
from threading import Thread
import webbrowser

# Databasega bog'lanish
database = DatabaseConnect()

# Serverga bog'lanish
server = ServerConnect()




#######################################################################################################

#      #  #######            ####     ######   ########  #######   #      #     ####    ########  ########  
#      #     #              #    #   #      #     #         #      #      #    #    #      #      #         
#      #     #             ########  #            #         #      #      #   ########     #      #######   
#      #     #             #      #  #      #     #         #       #    #    #      #     #      #         
 ######   #######          #      #   ######      #      #######     ####     #      #     #      ########  

app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()

ui = Ui_MainWindow()
ui.setupUi(MainWindow)
loading_label = QtWidgets.QLabel(MainWindow)
loading_label.setText("Biroz kuting ...")
loading_label.setStyleSheet("""
    background-color: rgb(27, 29, 36, 200);
    font-size: 40px;
    """)
loading_label.setEnabled(False)
# loading_label.setGeometry(QtCore.QRect(0, 0, MainWindow.size().width(), MainWindow.size().height()))
loading_label.setGeometry(QtCore.QRect(0, 0, 0, 0))
loading_label.setAlignment(QtCore.Qt.AlignCenter)


# Sahifalarni activlashtirish

RefreshKundalikFrame = QtWidgets.QDialog()
RefreshKundalikFrame.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
refresh_kundalik_ui = Ui_KundalikRefreshFrame()
refresh_kundalik_ui.setupUi(RefreshKundalikFrame)

# RefreshKundalikFrame.show()

KundalikLoginFrame = QtWidgets.QDialog()
kundalik_login_ui = Ui_KundalikLoginFrame()
kundalik_login_ui.setupUi(KundalikLoginFrame)

# KundalikLoginFrame.show()

EditFrame = QtWidgets.QDialog()
edit_ui = Ui_EditFrame()
edit_ui.setupUi(EditFrame)

# EditFrame.show()

LoginFrame = QtWidgets.QFrame()
login_ui = Ui_LoginFrame()
login_ui.setupUi(LoginFrame)
# LoginFrame.show()

BuyDialogFrame = QtWidgets.QDialog()
BuyDialogFrame.setWindowFlags(QtCore.Qt.FramelessWindowHint)

buy_dialog_ui = Ui_BuyDialogFrame()
buy_dialog_ui.setupUi(BuyDialogFrame)
# BuyDialogFrame.show()


# Taxrirlash icon
icon4 = QtGui.QIcon()
icon4.addPixmap(QtGui.QPixmap("icons/edit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)



#############################################################################################################

#######  #      #  #     #   ##### 
#        #      #  # #   #  #     #
#######  #      #  #  #  #  #      
#        #      #  #   # #  #     #
#        ########  #     #   ##### 



def AsosiyMenyuniOchish():
    profile_data = database.get_profile()
    if profile_data["sex"] or profile_data["sex"] is None:
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/man.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ui.hisob_button.setIcon(icon1)
    else:
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/woman.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ui.hisob_button.setIcon(icon1)
    data = server.get_school(profile_data["token"])
    try:
        ui.maktab_nomi.setText(data["school_name"])
    except:
        pass
    ui.lineEdit.setText(profile_data["full_name"])
    ui.lineEdit_2.setText(profile_data["username"])
    user_data = server.about_user(profile_data["token"])
    ui.lineEdit_3.setText(f"{ user_data['balance']:,} so'm")
    mal = server.check(profile_data["token"])
    if not mal["how"]:
        return mal["message"]

    end_date = datetime.strptime(mal["end_active_date"], "%Y-%m-%dT%H:%M:%S.%f")
    ui.label_33.setText(f"{end_date.day}.{end_date.month}.{end_date.year}")
    ui.label_26.setText(f"{end_date.day}.{end_date.month}.{end_date.year}")

    if mal["size"] <= 0:
        ui.stackedWidget.setCurrentIndex(0)
        ui.pushButton_6.setEnabled(False)
        ui.admins_button.setEnabled(False)
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setText("Sizda Linsenziya vaqti tugagan")
        msg.setInformativeText("Hisob bo'limidan letsenziya sotib olishingiz mumkin.")
        msg.setWindowTitle("Xabar")
        msg.exec_()
        ui.label_31.setStyleSheet("color: red")
        ui.label_33.setStyleSheet("color: red")
        ui.label_26.setStyleSheet("color: red")
        ui.label_27.setStyleSheet("color: red")
        ui.label_31.setText("Tugagan")
        ui.label_27.setText("Tugagan")
        ui.stackedWidget.setCurrentIndex(0)
    else:
        ui.pushButton_6.setEnabled(True)
        ui.admins_button.setEnabled(True)
        time_size = timedelta(seconds=mal["size"])
        if time_size.days//30 == 0:
            if time_size.days%30 == 0:
                if time_size.seconds//3600 == 0:
                    ui.label_31.setText(f"{(time_size.seconds//60)%60} minut")
                    ui.label_27.setText(f"{(time_size.seconds//60)%60} minut")
                else:
                    if (time_size.seconds//60)%60 == 0:
                        matn = f"{time_size.seconds//3600} soat"
                    else:
                        matn = f"{time_size.seconds//3600} soat {(time_size.seconds//60)%60} minut"
                    ui.label_31.setText(matn)
                    ui.label_27.setText(matn)
            else:
                if (time_size.seconds//3600)%24 == 0:
                    matn = f"{time_size.days%30} kun"
                else:
                    matn = f"{time_size.days%30} kun {(time_size.seconds//3600)%24} soat"
                ui.label_31.setText(matn)
                ui.label_27.setText(matn)
        else:
            if time_size.days%30 == 0:
                matn = f"{time_size.days//30} oy"
            else:
                matn = f"{time_size.days//30} oy {time_size.days%30} kun"
            ui.label_31.setText(matn)
            ui.label_27.setText(matn)

    MainWindow.showMaximized()
    if mal["size"] > 0:
        database.new_logins = mal["all_logins"]
        ui.login_check.start()

    report_mal = database.get_4_day()
    ui.label_15.setText(str(report_mal["day_1"]["foiz"])+"%")
    ui.label_24.setText(str(report_mal["day_2"]["foiz"])+"%")
    ui.label_19.setText(str(report_mal["day_3"]["foiz"])+"%")
    ui.label_49.setText(str(report_mal["day_4"]["foiz"])+"%")



    if report_mal["day_1"]["foiz"]==-1:
        ui.frame_13.setStyleSheet("""border-radius: 10px;
            font-size: 24px;
            background-color: rgb(48, 49, 49);""")
        ui.label_15.setText("0%")
    elif report_mal["day_1"]["foiz"]<50:
        ui.frame_13.setStyleSheet("""
            font-size: 24px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 15, 0, 255), stop:0.517241 rgba(226, 136, 5, 255), stop:1 rgba(255, 114, 0, 255));
            """)
    else:
        ui.frame_13.setStyleSheet("""
            font-size: 24px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 241, 0), stop:0.517241 rgba(74, 255, 0), stop:1 rgba(0, 232, 255));
            """)

    if report_mal["day_2"]["foiz"]==-1:
        ui.label_24.setStyleSheet("""border-radius: 10px;
            font-size: 20px;
            background-color: rgb(48, 49, 49);""")
        ui.label_15.setText("0%")
    elif report_mal["day_2"]["foiz"]<50:
        ui.frame_16.setStyleSheet("""
            font-size: 20px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 15, 0, 255), stop:0.517241 rgba(226, 136, 5, 255), stop:1 rgba(255, 114, 0, 255));
            """)
    else:
        ui.frame_16.setStyleSheet("""
            font-size: 20px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 241, 0), stop:0.517241 rgba(74, 255, 0), stop:1 rgba(0, 232, 255));
            """)

    
    if report_mal["day_3"]["foiz"]==-1:
        ui.frame_14.setStyleSheet("""border-radius: 10px;
            font-size: 17px;
            background-color: rgb(48, 49, 49);""")
        ui.label_19.setText("0%")
    elif report_mal["day_3"]["foiz"]<50:
        ui.frame_14.setStyleSheet("""
            font-size: 17px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 15, 0, 255), stop:0.517241 rgba(226, 136, 5, 255), stop:1 rgba(255, 114, 0, 255));
            """)
    else:
        ui.frame_14.setStyleSheet("""
            font-size: 17px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 241, 0), stop:0.517241 rgba(74, 255, 0), stop:1 rgba(0, 232, 255));
            """)

    if report_mal["day_4"]["foiz"]==-1:
        ui.frame_36.setStyleSheet("""border-radius: 10px;
            font-size: 14px;
            background-color: rgb(48, 49, 49);""")
        ui.label_49.setText("0%")
    elif report_mal["day_4"]["foiz"]<50:
        ui.frame_36.setStyleSheet("""
            font-size: 14px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 15, 0, 255), stop:0.517241 rgba(226, 136, 5, 255), stop:1 rgba(255, 114, 0, 255));
            """)
    else:
        ui.frame_36.setStyleSheet("""
            font-size: 14px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 241, 0), stop:0.517241 rgba(74, 255, 0), stop:1 rgba(0, 232, 255));
            """)
    
    ui.label_13.setText(report_mal["day_3"]["date"].replace("-","."))
    ui.label_50.setText(report_mal["day_4"]["date"].replace("-","."))
    price_1, price_2 = server.get_pc_price()
    
    # Home page da browser view ni to'liq qo'yish
    ui.textBrowser.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'Mongolian Baiti\'; font-size:7.8pt; font-weight:400; font-style:normal;\">\n"
        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:20pt; font-weight:600; color:#00ff00;\">________________________________________________________________</span></p>\n"
        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:26pt; font-weight:600; color:#00ff00;\">🎁 Bonus</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:26pt; font-weight:600; color:rgba(100,255,255,0.8);\">Ulashing va bepul letsenziyaga ega bo\'ling</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; font-weight:600; color:#ffffff;\">Ushbu xizmatimizni boshqalarga ulashing va xizmatimizni har bir sotib olgan foydalanuvchi uchun </span><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; font-weight:600; color:#00ff00;\">1 oylik</span><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; font-weight:600; color:#ffffff;\"> bepul letsenziyani qo\'lga kiriting!</span></p>\n"
        
        f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:#00ffff; background-color:#333333;\"> Havola: </span><a name=\"text-to-copy\"></a><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:#0000ff;\"> </span><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:#0000ff;\"> https://projectsplatform.uz/register?ref=</span><a name=\"user_id\"></a><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:#0000ff;\"></span><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:#0000ff;\">{profile_data['id']}</span><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; color:rgba(100,255,255,0.8);\"> </span></p>\n"
        
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:22pt; font-weight:600; color:#00ff00;\">Hoziroq ushbu referal havolangizdan nusxa olib telegram orqali ulashing</span></p>\n"
        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Oxygen,Ubuntu,Cantarell,Fira Sans,Droid Sans,Helvetica Neue,sans-serif\'; font-size:20pt; font-weight:600; color:#00ff00;\">________________________________________________________________</span></p>\n"
        "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8.25pt;\"><br /></p>\n"
        "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:24pt; font-weight:600; color:#ffd500;\"><br /></p>\n"
        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt; font-weight:600; color:#ffd500;\">KundalikCOM</span><span style=\" font-size:24pt; font-weight:600;\"> </span><span style=\" font-size:24pt; font-weight:600; color:#00ffff;\">Desktop</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt; font-weight:600;\">-) O\'quvchi va Ota onalar </span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-style:italic; color:#6c6c6c;\">  Barcha eMaktab.uz dagi hisoblarni boshqarish imkoniyati</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt; font-weight:600;\">-) Maktab reytingini oshirish</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:24pt; font-weight:600;\">-) Login parollarni online kiritish</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:16pt; font-style:italic; color:#6c6c6c;\">  o\'quvchilardan login va parollarini bitta bitta yozib olmasdan bitta elon orqali elekron tarzda login parollarni yig\'ish eko tizimi.</span></p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:24pt; font-weight:600;\"><br /></p>\n"
        f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:20pt;\">Bir oylik letsenziya: </span><span style=\" font-size:20pt; font-weight:600; color:#ff8000;\">{'{:,}'.format(price_1)}</span><span style=\" font-size:20pt;\"> </span><span style=\" font-size:20pt; color:#0189ff;\">so\'m</span></p>\n"
        f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:20pt;\">3 oy yoki undan ko'proq harid qilinsa bir oylik: </span><span style=\" font-size:20pt; font-weight:600; color:#ff0000;\">-20%</span><span style=\" font-size:20pt;\"> chegirma bilan </span><span style=\" font-size:20pt; font-weight:600; color:#00ff00;\">{'{:,}'.format(price_2)}</span><span style=\" font-size:20pt;\"> </span><span style=\" font-size:20pt; color:#0073ff;\">so\'m</span><span style=\" font-size:20pt;\"> dan</span></p>"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:20pt;\">Har </span><span style=\" font-size:20pt; color:#0000ff;\">9</span><span style=\" font-size:20pt;\"> oy olinsa </span><span style=\" font-size:20pt; font-weight:600; color:#00ff26;\">+3</span><span style=\" font-size:20pt;\"> oy bonusga beriladi</span></p></body></html>")
    hisoblar_soni = database.get_len_logins()
    ui.label_14.setText(f"Jami: {hisoblar_soni} ta")
    ui.label_23.setText(f"Jami: {hisoblar_soni} ta")
    ui.label_18.setText(f"Jami: {hisoblar_soni} ta")
    ui.label_48.setText(f"Jami: {hisoblar_soni} ta")

# QThread orqali Ma'lumotlarni olish
class LoginsAddThreadClass(QtCore.QThread):
    db_refresh = pyqtSignal()
    def __init__(self, ui, database, loading, loading_quit):
        super().__init__()
        self.ui = ui
        self.loading = loading
        self.database = database
        self.loading_quit = loading_quit

    def run(self):
        self.loading()
        i = 0
        n = len(database.new_logins)
        loading_label.setText(f"Barcha yangi login parollarni tekshirib chiqish\nBajarildi: 0/{n}")
        for login in database.new_logins.keys():
            parol = database.new_logins[login]
            how, data = kundalikcom_func.login_user(requests.session(), login, parol)
            loading_label.setGeometry(QtCore.QRect(0, 0, MainWindow.size().width(), MainWindow.size().height()))
            if how and data["user_id"] in self.database.dict_data["all_data_logins"]:
                self.database.dict_data["all_data_logins"][data["user_id"]]["browser"] = data["browser"]
                self.database.dict_data["all_data_logins"][data["user_id"]]["login"] = login
                self.database.dict_data["all_data_logins"][data["user_id"]]["parol"] = parol
            i+=1
            loading_label.setText(f"Barcha yangi login parollarni tekshirib chiqish\n{i}/{n}")
        if n:
            self.db_refresh.emit()
        self.loading_quit()


# Asosiy ekranda loading chiqarish
def loading():
    loading_label.setText("Biroz kuting ...")
    loading_label.setGeometry(QtCore.QRect(0, 0, MainWindow.size().width(), MainWindow.size().height()))


# Asosiy ekrandagi loadingni yopish
def loading_quit():
    loading_label.setGeometry(QtCore.QRect(0, 0, 0, 0))


# Bosh sahifaga o'tkazuvchi funksiya
def show_home_page():
    ui.admins_button_2.setStyleSheet("""
        background-color: rgb(50, 100, 200);
        color: rgb(0,255,0);
        text-align:  center;""")
    ui.admins_button.setStyleSheet("")
    ui.hisob_button.setStyleSheet("")
    ui.stackedWidget.setCurrentIndex(1)
    AsosiyMenyuniOchish()


# Profile sahifasiga o'tkazuvchi funksiya
def show_profile_page():
    ui.hisob_button.setStyleSheet("""
        background-color: rgb(50, 100, 200);
        color: rgb(0,255,0);
        text-align: center;""")
    ui.admins_button_2.setStyleSheet("")
    ui.admins_button.setStyleSheet("")
    ui.stackedWidget.setCurrentIndex(0)
    AsosiyMenyuniOchish()


# Data sahifasiga o'tkazuvchi funksiya
def show_data_page():
    loading()
    # ui.thread_pool.start(Worker(ui, database, loading_quit))
    ui.page_number_label.setText("1")
    try:
        all_data = database.get_classes()
        ui.comboBox.clear()
        ui.comboBox.addItem("Hammasi")
        ui.comboBox.setCurrentIndex(0)
        ui.comboBox_2.setCurrentIndex(0)
        for grade in all_data.keys():
            ui.comboBox.addItem(grade)
        ui.threadclass.start()
        ui.stackedWidget.setCurrentIndex(2)
        ui.admins_button.setStyleSheet("""
            background-color: rgb(50, 100, 200);
            color: rgb(0,255,0);
            text-align:  center;""")
        ui.admins_button_2.setStyleSheet("")
        ui.hisob_button.setStyleSheet("")
    except requests.exceptions.ConnectionError:
        loading_quit()
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    except:
        loading_quit()
    # ui.threadclass.get.connect(add_user)


def get_data_serach():
    ui.page_number_label.setText("1")
    ui.threadclass.start()


# Login uchun code olish funksiyasi
def get_login_code():
    username = login_ui.lineEdit.text().strip()
    password = login_ui.lineEdit_2.text().strip()
    try:
        if "detail" in server.get_login(username, password):
            msg = QtWidgets.QMessageBox(MainWindow)
            msg.setStyleSheet("padding: 4px; font-size: 20px;")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Username yoki parol xato")
            msg.setInformativeText("ProjectsPlatforms.uz saytidan ruyxatdan o'tgan akkountingizga kirishingiz kerak.")
            msg.setWindowTitle("Xatolik!")
            msg.exec_()
            login_ui.lineEdit.setFocus()
            login_ui.lineEdit_2.clear()
        else:
            login_ui.lineEdit_3.setFocus()
    except requests.exceptions.ConnectionError as e:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    except:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Username yoki parol xato")
        msg.setInformativeText("ProjectsPlatforms.uz saytidan ruyxatdan o'tgan akkountingizga kirishingiz kerak.")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()

# Login funksiyasi
def login_func():
    username = login_ui.lineEdit.text().strip()
    password = login_ui.lineEdit_2.text().strip()
    kod = login_ui.lineEdit_3.text().strip()
    try:
        token = server.login(username, password, int(kod))["token"]
        data = server.about_user(token)
        try:
            database.login(token, data)
            profile_data = database.get_profile()
            ui.lineEdit.setText(profile_data["full_name"])
            ui.lineEdit_2.setText(profile_data["username"])
            ui.lineEdit_3.setText(str(profile_data["balance"]))
            LoginFrame.close()

            if database.isLoginedKundalik():
                try:
                    nat = AsosiyMenyuniOchish()
                    if nat != None:
                        msg = QtWidgets.QMessageBox(MainWindow)
                        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
                        msg.setText(nat)
                        msg.setWindowTitle("Xatolik!")
                        msg.show()
                        LoginFrame.show()
                except requests.exceptions.ConnectionError as e:
                    msg = QtWidgets.QMessageBox(MainWindow)
                    msg.setStyleSheet("padding: 4px; font-size: 20px;")
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Internetga ulanmagansiz")
                    msg.setInformativeText("Internetga ulaning")
                    msg.setWindowTitle("Xatolik!")
                    msg.exec_()
                except Exception as e:
                    # print(type(e))
                    LoginFrame.show()
            else:
                KundalikLoginFrame.show()
        except requests.exceptions.ConnectionError as e:
            msg = QtWidgets.QMessageBox(MainWindow)
            msg.setStyleSheet("padding: 4px; font-size: 20px;")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Internetga ulanmagansiz")
            msg.setInformativeText("Internetga ulaning")
            msg.setWindowTitle("Xatolik!")
            msg.exec_()
        except Exception as e:
            # print(type(e))
            LoginFrame.show()
    except requests.exceptions.ConnectionError as e:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    except:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Kod xato kiritildi")
        msg.setInformativeText("Telegram botdan kelgan 6 belgili kodni kiritishingiz kerak")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()


# Logout qilish
def logout():
    database.logout()
    MainWindow.close()
    LoginFrame.show()



# Get users workekr
class GetUsersWorker(QThread):
    end = pyqtSignal()
    def __init__(self, maktab_id, login, parol):
        super().__init__()
        self.maktab_id = maktab_id
        self.login = login
        self.parol = parol
    def run(self):
        kundalikcom_func.get_users(database.browser, self.maktab_id, refresh_kundalik_ui, database, self.login, self.parol)
        self.end.emit()

# KundalikCOM akkountni kiritish administrator
def kundalik_login_func():
    global worker_get_users
    login = kundalik_login_ui.lineEdit.text().strip()
    parol = kundalik_login_ui.lineEdit_2.text().strip()
    how, data = database.login_kundalik(login, parol)
    if how:
        mal = server.set_school(data["token"], data["viloyat"], data["tuman"], data["maktab_nomi"])
        KundalikLoginFrame.close()
        kundalik_login_ui.lineEdit.clear()
        kundalik_login_ui.lineEdit_2.clear()
        refresh_kundalik_ui.label.setText(data["maktab_nomi"])
        ui.maktab_nomi.setText(data["maktab_nomi"])
        # Thread(target=kundalikcom_func.get_users, args=[database.browser, data["maktab_id"], refresh_kundalik_ui, database, login, parol]).start()
        worker_get_users = GetUsersWorker(data["maktab_id"], login, parol)
        worker_get_users.end.connect(database.refresh)
        worker_get_users.start()
        RefreshKundalikFrame.exec_()
    elif data == None:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    elif data:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("padding: 4px; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Login yoki parol xato!")
        msg.setInformativeText("qayta urinib ko'ring")
        msg.setWindowTitle("Kirish xatoligi")
        msg.exec_()
    else:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Ayni paytda eMaktab.uz sayti ishlamayapti, keyinroq qata urinib kuring. Saytda profilaktika ishlari olib borilayotgan bo'lishi ham mumkin")
        msg.setInformativeText("Keyinroq qayta kiring")
        msg.setWindowTitle("Xatolik!")
        msg.exec()


# Biror grade tanlanganda
def changed_combobox(grade):
    ui.comboBox_2.clear()
    if grade == "":
        pass
    elif grade == "Hammasi":
        all_data = database.get_kundalik_profile()["all_classes"]
        ui.comboBox_2.addItem("Hammasi")
        for grade in all_data.keys():
            for class_ in all_data[grade]:
                ui.comboBox_2.addItem(class_)
    else:
        classes = database.get_kundalik_profile()["all_classes"][grade]
        for sinf in classes:
            ui.comboBox_2.addItem(sinf)
    ui.comboBox_2.setCurrentIndex(0)


# QThread orqali Ma'lumotlarni olish
class ThreadClass(QtCore.QThread):
    get = QtCore.pyqtSignal(dict)
    get2 = QtCore.pyqtSignal(dict)
    def __init__(self, ui, database, loading, loading_quit):
        super().__init__()
        self.ui = ui
        self.loading = loading
        self.database = database
        self.loading_quit = loading_quit

    def run(self):
        self.loading()
        page = int(self.ui.page_number_label.text())
        for i in ui.frame_6.children():
            if i.objectName() != "verticalLayout_6":
                i.deleteLater()
        name = self.ui.lineEdit_4.text().strip()
        sinf = self.ui.comboBox_2.currentText()
        if sinf == "Hammasi":
            sinf = ""
        # Worker(group, sinf, name, self.ui, database)
        natija, number = get_data(self.ui.comboBox_3.currentText(), sinf, name, page, self.ui)
        self.ui.label_7.setText(f"Jami: {number}ta")
        pages_number = number//10
        if number%10!=0:
            pages_number+=1
        self.get2.emit({
            "page": page,
            "pages_number": pages_number
            })
        for user_id in natija.keys():
            self.get.emit(natija[user_id])
        self.loading_quit()


# Ma'lumotlarni olish
def get_data(group, sinf, name, page, ui):
    natija = dict()
    if group == "Ota onalar":
        group = "parents"
    else:
        group = "students"

    maktab_id = database.get_kundalik_profile()["maktab_id"]
    res = database.browser.get(f"https://schools.emaktab.uz/v2/school?school={maktab_id}&view=members&group={group}&search={name}&class={sinf}&page={page}")
    soup = BeautifulSoup(res.content, "html.parser")
    try:number = int(soup.find(class_="found").find("strong").get_text().strip())
    except:number = 0
    teen_users = soup.find_all(class_="tdAvatar")
    for user in teen_users:
        try:
            a = user.find("a")
            # o'quvchi ismini o'qish
            user_name = a.get("title").strip()
            # o'quvchi is sini o'qish
            user_id = a.get("href").split("user=")[-1].strip()
            # jinsini aniqlash
            sex = a.get("class")[-1]
            natija[user_id] = {"name": user_name, "id": user_id, "sex": sex}
        except:
            pass
    return natija, number


def set_page_buttons(data):
    page, pages_number = data["page"], data["pages_number"]
    pages_buttons = {
        "p1": ui.p1,
        "p2": ui.p2,
        "p3": ui.p3,
        "p4": ui.p4,
        "p5": ui.p5,
        "p6": ui.p6,
        "p7": ui.p7
    }
    if pages_number<=7:
        ui.label_6.setText(" ")
        ui.label_72.setText(" ")
        for i in range(1, 8):
            if i == page:
                pages_buttons[f"p{i}"].setText(f"{i}")
                pages_buttons[f"p{i}"].setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0.227, x2:1, y2:0.739, stop:0 rgba(0, 255, 0, 255), stop:0.507389 rgba(0, 255, 255, 255), stop:1 rgba(0, 56, 255, 255));
                color: black""")
            elif i <= pages_number:
                pages_buttons[f"p{i}"].setText(f"{i}")
                pages_buttons[f"p{i}"].setStyleSheet("")
            else:
                pages_buttons[f"p{i}"].setText("")
                pages_buttons[f"p{i}"].setStyleSheet(f"color: rgb(0,0,0,0); background-color: rgb(0,0,0,0)")
    elif page <= 4:
        ui.label_6.setText(" ")
        ui.label_72.setText("   ...   ")
        for i in range(1, 8):
            if i == page:
                pages_buttons[f"p{i}"].setText(f"{i}")
                pages_buttons[f"p{i}"].setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0.227, x2:1, y2:0.739, stop:0 rgba(0, 255, 0, 255), stop:0.507389 rgba(0, 255, 255, 255), stop:1 rgba(0, 56, 255, 255));
                color: black""")
            else:
                pages_buttons[f"p{i}"].setText(f"{i}")
                pages_buttons[f"p{i}"].setStyleSheet("")
    elif pages_number - page < 3:
        ui.label_6.setText("   ...   ")
        ui.label_72.setText(" ")
        for i in range(1, 8):
            if pages_number-7+i == page:
                pages_buttons[f"p{i}"].setText(f"{page}")
                pages_buttons[f"p{i}"].setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0.227, x2:1, y2:0.739, stop:0 rgba(0, 255, 0, 255), stop:0.507389 rgba(0, 255, 255, 255), stop:1 rgba(0, 56, 255, 255));
                color: black""")
            else:
                pages_buttons[f"p{i}"].setText(f"{pages_number-7+i}")
                pages_buttons[f"p{i}"].setStyleSheet("")
    else:
        ui.label_6.setText("   ...   ")
        ui.label_72.setText("   ...   ")
        for i in range(1, 8):
            if page-4+i == page:
                pages_buttons[f"p{i}"].setText(f"{page}")
                pages_buttons[f"p{i}"].setStyleSheet("""background-color: qlineargradient(spread:pad, x1:0, y1:0.227, x2:1, y2:0.739, stop:0 rgba(0, 255, 0, 255), stop:0.507389 rgba(0, 255, 255, 255), stop:1 rgba(0, 56, 255, 255));
                color: black""")
            else:
                pages_buttons[f"p{i}"].setText(f"{page-4+i}")
                pages_buttons[f"p{i}"].setStyleSheet("")

class OneLoginThread(QThread):
    # Signal to update icon
    update_icon = pyqtSignal(QIcon)
    # Signal to show messages
    show_message = pyqtSignal(str)

    def __init__(self, user_id, tugma, database):
        super().__init__()
        self.user_id = user_id
        self.tugma = tugma
        self.database = database

    def run(self):
        # Initial icon
        icon6 = QIcon()
        icon6.addPixmap(QPixmap("icons/main-icon.png"), QIcon.Normal, QIcon.Off)
        self.update_icon.emit(icon6)  # Set the initial icon for the button
        
        user = self.database.get_user(self.user_id)

        # Check login and password validity
        if user["login"] is None or user["parol"] is None:
            icon6 = QIcon()
            icon6.addPixmap(QPixmap("icons/play.png"), QIcon.Normal, QIcon.Off)
            self.update_icon.emit(icon6)
            self.show_message.emit("❌ Active qilinmadi\nLogin yoki parol kiritilmagan")
        
        elif self.database.login_user(self.user_id):
            if "end_date" in user and datetime.now().strftime("%Y-%m-%d") == user["end_date"].strftime("%Y-%m-%d"):
                icon6 = QIcon()
                icon6.addPixmap(QPixmap("icons/refresh.png"), QIcon.Normal, QIcon.Off)
            else:
                icon6 = QIcon()
                icon6.addPixmap(QPixmap("icons/play.png"), QIcon.Normal, QIcon.Off)
            self.update_icon.emit(icon6)
        else:
            user = self.database.get_user(self.user_id)
            if "end_date" in user and datetime.now().strftime("%Y-%m-%d") == user["end_date"].strftime("%Y-%m-%d"):
                icon6 = QIcon()
                icon6.addPixmap(QPixmap("icons/refresh.png"), QIcon.Normal, QIcon.Off)
            else:
                icon6 = QIcon()
                icon6.addPixmap(QPixmap("icons/play.png"), QIcon.Normal, QIcon.Off)
            self.update_icon.emit(icon6)
            self.show_message.emit("❌ Active qilinmadi\nInternet sust yoki parol xato bo'lishi mumkin")
def one_user_login(user_id, tugma):
    # QThreadni yaratamiz
    login_thread = OneLoginThread(user_id, tugma, database)
    
    # Signalni tugmaga ulaymiz
    # login_thread.update_icon.connect(tugma.setIcon)
    
    # Signalni xabarlarni ko'rsatish uchun ulaymiz
    # login_thread.show_message.connect(show_message)
    
    # Threadni ishga tushuramiz
    login_thread.start()

# def one_user_login(user_id, tugma):
#     # tugma.clicked.disconnect()
#     user = database.get_user(user_id)
#     icon6 = QtGui.QIcon()
#     icon6.addPixmap(QtGui.QPixmap("icons/main-icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#     tugma.setIcon(icon6)
    
#     if user["login"] == None or user["parol"] == None:
        
#         icon6 = QtGui.QIcon()
#         icon6.addPixmap(QtGui.QPixmap("icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         tugma.setIcon(icon6)
#         show_message("❌ Active qilinmadi\nLogin yoki parol kiritilmagan")
        
#     elif database.login_user(user_id):
#         if "end_date" in  user and datetime.now().strftime("%Y-%m-%d") == user["end_date"].strftime("%Y-%m-%d"):
#             icon6 = QtGui.QIcon()
#             icon6.addPixmap(QtGui.QPixmap("icons/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         else:
#             icon6 = QtGui.QIcon()
#             icon6.addPixmap(QtGui.QPixmap("icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         tugma.setIcon(icon6)
#     else:
        
#         icon6 = QtGui.QIcon()
#         icon6.addPixmap(QtGui.QPixmap("icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
#         tugma.setIcon(icon6)
#         show_message("❌ Active qilinmadi\nlogin yoki parol xato bo'lishi mumkin")

# Parolni ko'rsatib yashirish uchun
def password_toggle(lineEdit, button):
    if button.text() == "ko'rsatish":
        lineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        button.setText("yashirish")
    else:
        lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        button.setText("ko'rsatish")

def add_user(data):
    ui.frame = QtWidgets.QFrame(ui.frame_6)
    ui.frame.setStyleSheet("QFrame{\n"
    "padding: 8px;\n"
    "}\n"
    "QFrame:hover{\n"
    "    background-color: rgb(40, 40, 40,140);\n"
    "}")
    ui.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
    ui.frame.setFrameShadow(QtWidgets.QFrame.Raised)
    ui.frame.setObjectName("frame")
    ui.horizontalLayout_4 = QtWidgets.QHBoxLayout(ui.frame)
    ui.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
    ui.horizontalLayout_4.setObjectName("horizontalLayout_4")
    user = database.get_user(data["id"])
    if "end_date" in  user and datetime.now().strftime("%Y-%m-%d") == user["end_date"].strftime("%Y-%m-%d"):
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("icons/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    else:
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap("icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)

    ui.pushButton_4 = QtWidgets.QPushButton(ui.frame)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(ui.pushButton_4.sizePolicy().hasHeightForWidth())
    ui.pushButton_4.setSizePolicy(sizePolicy)
    ui.pushButton_4.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    ui.pushButton_4.setStyleSheet("QPushButton{\n"
"border-radius: 5px;\n"
"padding: 10px\n"
"}\n"
"QPushButton:pressed{\n"
"    background-color: rgb(20, 100, 100);\n"
"color: rgb(0,255,0);\n"
"}")
    ui.pushButton_4.setText("")
    ui.pushButton_4.setIcon(icon6)
    ui.pushButton_4.setObjectName("pushButton_4")
    ui.horizontalLayout_4.addWidget(ui.pushButton_4)

    # commanda ulash active qilish uchun
    
    # QThreadni yaratamiz
    ui.login_thread = OneLoginThread(data['id'], ui.pushButton_4, database)
    
    # Signalni tugmaga ulaymiz
    ui.login_thread.update_icon.connect(ui.pushButton_4.setIcon)
    
    # Signalni xabarlarni ko'rsatish uchun ulaymiz
    ui.login_thread.show_message.connect(show_message)
    
    # Threadni ishga tushuramiz
    # login_thread.start()
    ui.pushButton_4.clicked.connect(partial(ui.login_thread.start))

    ui.label_75 = QtWidgets.QLabel(ui.frame)
    ui.label_75.setObjectName("label_75")
    ui.horizontalLayout_4.addWidget(ui.label_75)
    ui.label_8 = QtWidgets.QLabel(ui.frame)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(ui.label_8.sizePolicy().hasHeightForWidth())
    ui.label_8.setSizePolicy(sizePolicy)
    ui.label_8.setObjectName("label_8")
    ui.horizontalLayout_4.addWidget(ui.label_8)
    ui.pushButton_2 = QtWidgets.QPushButton(ui.frame)
    sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(ui.pushButton_2.sizePolicy().hasHeightForWidth())
    ui.pushButton_2.setSizePolicy(sizePolicy)
    ui.pushButton_2.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
    ui.pushButton_2.setFocusPolicy(QtCore.Qt.NoFocus)
    ui.pushButton_2.setStyleSheet("QPushButton{\n"
    "font-size: 20px;\n"
    "padding: 8px;\n"
    "border-radius: 10px;\n"
    "background-color: rgb(255,255,255,100);\n"
    "}\n"
    "QPushButton:hover{\n"
    "background-color: rgb(255,255,255);\n"
    "}\n"
    "QPushButton:pressed{\n"
    "    background-color: rgb(50, 255, 255);\n"
    "color: rgb(0,255,0);\n"
    "}")
    ui.pushButton_2.setText("")
    ui.pushButton_2.setIcon(icon4)
    ui.pushButton_2.setObjectName("pushButton_2")
    ui.horizontalLayout_4.addWidget(ui.pushButton_2)
    ui.verticalLayout_6.addWidget(ui.frame)

    
    ui.label_75.setText(data["name"])
    all_data = database.get_logins()
    # O'g'il yoki qiz bola ligiga qarab belgilanadi
    if data["sex"] == "male":
        ui.label_75.setStyleSheet("background-color: rgb(0, 0, 0, 0);\n"
        "color: rgb(180,180,255);")
    else:
        ui.label_75.setStyleSheet("background-color: rgb(0, 0, 0, 0);\n"
        "color: rgb(255,200,180);")

    if data["id"] in all_data and all_data[data["id"]]["login"] != None and all_data[data["id"]]["parol"] != None:
        ui.label_8.setText("Parol kiritilgan")
        ui.label_8.setStyleSheet("background-color: none;\n"
        "color: rgb(0,255,0);")
    else:
        ui.label_8.setText("Parol kiritilmagan")
        ui.label_8.setStyleSheet("background-color: none;\n"
        "color: rgb(255,0,0);")
    kimligi = "O'quvchi" if ui.comboBox_3.currentText() == "O'quvchilar" else "Ota" if data["sex"] == "male" else "Ona"
    ui.pushButton_2.clicked.connect(partial(edit_page_active, data["id"], data["sex"], kimligi, ui.label_8))


def get_users_thread_stop(event):
    # print("stop thread")
    database.is_get_users_thread = False



# pagega utish uchun
def get_page(button):
    if button.text() != "":
        ui.page_number_label.setText(button.text())
        ui.threadclass.start()


# barcha datalarni qayta yuklash butun maktab malumotlarini qayta yuklash
def all_data_refresh_maktab():
    refresh_kundalik_ui.label.setText(data["maktab_nomi"])
    login, parol = database.get_kundalik_profile()["login"], database.get_kundalik_profile()["parol"]
    # Thread(target=kundalikcom_func.get_users, args=[database.browser, database.get_kundalik_profile()["maktab_id"], refresh_kundalik_ui, database, login, parol]).start()
    worker_get_users = GetUsersWorker(database.get_kundalik_profile()["maktab_id"], login, parol)
    worker_get_users.end.connect(database.refresh)
    worker_get_users.start()
    RefreshKundalikFrame.exec_()


# narxi ko'rsatish funksiyalari tugma uchun
def add_one():
    try:
        num = int(ui.lineEdit_5.text())
    except:
        num = 0
    num+=1
    try:
        ui.label_21.setText(f"{'{:,}'.format(server.get_pc_months_price(num))} so'm")
        ui.lineEdit_5.setText(str(num))
    except requests.exceptions.ConnectionError:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()


def del_one():
    try:
        num = int(ui.lineEdit_5.text())
    except:
        num = 0
    if num <= 0:
        num = 0
    else:
        num-=1
    try:
        if num == 0:
            ui.label_21.setText(f"0 so'm")
            ui.lineEdit_5.setText("")
        else:
            ui.label_21.setText(f"{'{:,}'.format(server.get_pc_months_price(num))} so'm")
            ui.lineEdit_5.setText(str(num))
    except requests.exceptions.ConnectionError:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Internetga ulanmagansiz")
        msg.setInformativeText("Internetga ulaning")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()


def edit_page_active(user_id, sex, kimligi, label):
    edit_ui.lineEdit_20.clear()
    edit_ui.lineEdit_19.clear()
    user = database.get_user(user_id)
    
    if kimligi == "O'quvchi":
        if sex == "male":
            edit_ui.label_52.setPixmap(QtGui.QPixmap("icons/boy.png"))
        else:
            edit_ui.label_52.setPixmap(QtGui.QPixmap("icons/girl.png"))
    elif kimligi == "Ota":
        edit_ui.label_52.setPixmap(QtGui.QPixmap("icons/man.png"))
    else:
        edit_ui.label_52.setPixmap(QtGui.QPixmap("icons/woman.png"))
    edit_ui.lineEdit_21.setText(user["full_name"])
    # print(user)
    if user["login"] != None:
        edit_ui.lineEdit_20.setText(user["login"])
    if user["parol"] != None:
        edit_ui.lineEdit_19.setText(user["parol"])
    try:
        edit_ui.pushButton_13.clicked.disconnect()
    except:
        pass
    try:
        edit_ui.pushButton_12.clicked.disconnect()
    except:
        pass
    if kimligi == "O'quvchi" and user["sinf"] != "Aniqlanmagan":
        edit_ui.lineEdit_22.setText(user["sinf"]+" sinf o'quvchisi")
    else:
        edit_ui.lineEdit_22.setText(kimligi)
    edit_ui.pushButton_13.clicked.connect(partial(login_va_parol_tekshirish, user_id, label))
    edit_ui.pushButton_12.clicked.connect(partial(login_va_parol_saqlash, user_id, label))

    EditFrame.exec_()


def login_va_parol_tekshirish(user_id, label):
    login = edit_ui.lineEdit_20.text().strip()
    parol = edit_ui.lineEdit_19.text().strip()

    if login == "":
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Login bo'sh bo'lishi mumkin emas")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
        return
    elif parol == "":
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Parol bo'sh bo'lishi mumkin emas")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
        return
    how, data = kundalikcom_func.login_user(requests.session(), login, parol)
    edit_ui.pushButton_13.setStyleSheet("""QPushButton{
        border-radius: 10px;
        padding: 10px;
        font-size: 20px;
        color: white;
        }
        QPushButton:hover{
        border-color:  black;
            background-color: rgb(0,20,20);
        }""")
    if how:
        if user_id == data["user_id"]:
            if edit_ui.checkBox.isChecked():
                login_va_parol_saqlash(user_id, label)
            edit_ui.pushButton_13.setStyleSheet("""border-radius: 10px;
                padding: 10px;
                font-size: 20px;
                color: black; background-color: rgb(0,255,0);""")
        else:
            edit_ui.lineEdit_20.clear()
            edit_ui.lineEdit_19.clear()
            msg = QtWidgets.QMessageBox(EditFrame)
            msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
            msg.setText("Ushbu login parollar boshqa hisobga tegishli bo'lishi mumkin")
            msg.setInformativeText("Qayta kiriting")
            msg.setWindowTitle("Moslik mavjud emas!")
            msg.exec_()
    else:
        if data == "Login yoki parol xato":
            edit_ui.lineEdit_19.clear()
            edit_ui.pushButton_13.setStyleSheet("""border-radius: 10px;
                padding: 10px;
                font-size: 20px;
                color: black; background-color: rgb(255,0,0);""")
        elif data == "Internega ulanib bo'lmadi":
            msg = QtWidgets.QMessageBox(EditFrame)
            msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Internetga ulanmagansiz")
            msg.setInformativeText("Internetga ulaning")
            msg.setWindowTitle("Xatolik!")
            msg.exec_()
        else:
            msg = QtWidgets.QMessageBox(EditFrame)
            msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Nimadur xato ketdi")
            msg.setInformativeText("Qayta urinib ko'ring")
            msg.setWindowTitle("Xatolik!")
            msg.exec_()


def login_va_parol_saqlash(user_id, label):
    login = edit_ui.lineEdit_20.text().strip()
    parol = edit_ui.lineEdit_19.text().strip()
    if login == "" or parol == "":
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setText("login yoki parol bo'sh bo'lishi mumkin emas")
        msg.setInformativeText("Qatorlarni to'ldiring")
        msg.setWindowTitle("❌ Saqlanmadi")
        msg.exec_()
        return
    how, data = kundalikcom_func.login_user(requests.session(), login, parol)
    if not how:
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setText(data)
        msg.setInformativeText(" Qayta kiriting")
        msg.setWindowTitle("❌ Saqlanmadi")
        msg.exec_()
    elif "user_id" in data and data["user_id"] != user_id:
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setText("Ushbu login parollar boshqa hisobga tegishli bo'lishi mumkin")
        msg.setInformativeText("Qayta kiriting")
        msg.setWindowTitle("❌ Moslik mavjud emas!")
        msg.exec_()
    elif login == "":
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Login bo'sh bo'lishi mumkin emas")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    elif parol == "":
        msg = QtWidgets.QMessageBox(EditFrame)
        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Parol bo'sh bo'lishi mumkin emas")
        msg.setWindowTitle("Xatolik!")
        msg.exec_()
    else:
        database.set_user(user_id, login=login, parol=parol)
        label.setStyleSheet("background-color: none; color: rgb(0,255,0);")
        label.setText("Parol kiritilgan")
        if edit_ui.checkBox_2.isChecked():
            EditFrame.close()


def refresh_maktabni_tugatish_func():
    RefreshKundalikFrame.close()
    # AsosiyMenyuniOchish()


def set_today_func(value):
    database.set_today(value)
    if value==-1:
        ui.frame_13.setStyleSheet("""border-radius: 10px;
            font-size: 24px;
            background-color: rgb(48, 49, 49);""")
        ui.label_15.setText("0%")
    elif value<50:
        ui.frame_13.setStyleSheet("""
            font-size: 24px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 15, 0, 255), stop:0.517241 rgba(226, 136, 5, 255), stop:1 rgba(255, 114, 0, 255));
            """)
        ui.label_15.setText(f"{value}%")
    else:
        ui.frame_13.setStyleSheet("""
            font-size: 24px;
            border-radius: 10px;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0.409, stop:0 rgba(255, 241, 0), stop:0.517241 rgba(74, 255, 0), stop:1 rgba(0, 232, 255));
            """)
        ui.label_15.setText(f"{value}%")


class RunThreadClass(QtCore.QThread):
    get = QtCore.pyqtSignal(int)
    show_message = QtCore.pyqtSignal(str)
    def __init__(self, ui, database):
        super().__init__()
        self.ui = ui
        self.database = database


    def run(self):
        self.ui.pushButton_6.setEnabled(False)
        self.ui.admins_button.setEnabled(False)
        self.ui.admins_button_2.setEnabled(False)
        self.ui.hisob_button.setEnabled(False)
        # self.ui..setEnabled(False)
        all_data = database.get_logins()
        n, p_num = 0, 0
        for user_id in all_data.keys():
            # print(user_id)
            if all_data[user_id]["login"] != None and all_data[user_id]["parol"] != None:
                how = database.login_user(user_id)
                if how:
                    # print(all_data[user_id])
                    n+=1
                    self.ui.pushButton_6.setText(f"Jarayon ketmoqda ...\nActive: {n} / {len(all_data)}\nParoli xatolar: {p_num} ta")
                    self.get.emit(round((n*100)/len(all_data)))
                else:
                    p_num += 1
                    self.ui.pushButton_6.setText(f"Jarayon ketmoqda ...\nActive: {n} / {len(all_data)}\nParoli xatolar: {p_num} ta")
        self.get.emit(round((n*100)/len(all_data)))
        self.ui.pushButton_6.setEnabled(True)
        self.ui.pushButton_6.setText(f"BARCHA AKKOUNTLARNI\nLOGIN QILIB CHIQISH")
        self.ui.admins_button.setEnabled(True)
        self.ui.admins_button_2.setEnabled(True)
        self.ui.hisob_button.setEnabled(True)
        # Xabar QMessage chiqarish
        self.show_message.emit(f"Ko'rsatkich: {round((n*100)/len(all_data))}%\n{n} ta foydalanuvchilar muvaffaqiyatli kiritildi\nParoli xatolar: {p_num} ta")

def parol_kiritilmaganlar():
    loading()
    Thread(target=kundalikcom_func.no_parol_users, args=[database.get_logins(), loading_quit]).start()


def online_add():
    link = f'https://projectsplatform.uz/maktabga_login_parolni_tanitish/{database.get_profile()["id"]}'
    webbrowser.open(link)


class BuyThread(QtCore.QThread):
    get = QtCore.pyqtSignal(bool, str)
    def __init__(self, ui, server, database, loading_quit):
        super().__init__()
        self.ui = ui
        self.server = server
        self.database = database
        self.loading_quit = loading_quit

    def run(self):
        try:
            res = self.server.buy(self.database.get_profile()["token"], int(ui.lineEdit_5.text()))
            # print(res)
            self.get.emit(res["how"], res["message"])
        except requests.exceptions.ConnectionError:
            self.get.emit(False, "Internetga ulanib bo'lmadi")
        except Exception as e:
            # print(e)
            self.get.emit(False, "Nimadir xato ketdi keyinroq urinib ko'ring")
        self.loading_quit()
def buy_func():
    text = ui.lineEdit_5.text()
    if text == "":
        text = "0"
    months = int(text)
    if months == 0:
        return
    loading()
    narx = int(ui.label_21.text()[:-4].replace(",",""))
    buy_dialog_ui.textBrowser.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
    "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
    "p, li { white-space: pre-wrap; }\n"
    "</style></head><body style=\" font-family:\'Mongolian Baiti\'; font-size:30px; font-weight:400; font-style:normal;\">\n"
    f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:28pt;\">Miqdor: </span><span style=\" font-size:28pt; font-weight:600; color:#55ffff;\">{months} oy</span></p>\n"
    +("<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:28pt;\">Chegirma: </span><span style=\" font-size:28pt; font-weight:600; color:#ff0000;\">-20%</span></p>\n" if months >= 3 else "")
    +f"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:28pt;\">Umumiy narx: </span><span style=\" font-size:28pt; font-weight:600; color:#00ff80;\">{narx}</span><span style=\" font-size:28pt; font-weight:600;\"> so\'m</span></p></body></html>")
    BuyDialogFrame.exec_()

def buy_active():
    BuyDialogFrame.close()
    ui.buy.start()
def buy_how(how: bool, message: str):
    if how:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("border-radius: 5px; color: blue; font-size: 24px;")
        icon = QtGui.QPixmap("icons/active.png")
        msg.setIconPixmap(icon.scaled(32, 32, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        msg.setText(message)
        msg.setWindowTitle("To'lov!")
        msg.exec_()
        AsosiyMenyuniOchish()
    else:
        msg = QtWidgets.QMessageBox(MainWindow)
        msg.setStyleSheet("border-radius: 5px; color: blue; font-size: 24px;")
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("To'lov amalga oshirilmadi")
        msg.setInformativeText(message)
        msg.setWindowTitle("To'lov!")
        msg.exec_()

def copy_inputs(lineEdit):
    pyperclip.copy(lineEdit.text())

#####################################################################################################################

#######   #         #      #   #######  #######   #      #   #######  
#     ##  #         #      #  #            #      ##     #  #         
#######   #         #      #  #   ####     #      # #    #   ######   
#         #         #      #  #      #     #      #  #   #         #  
#         ########   ######    #######  #######   #   #  #  #######   


RefreshKundalikFrame.closeEvent = get_users_thread_stop

ui.login_check =  LoginsAddThreadClass(ui, database, loading, loading_quit)
ui.login_check.db_refresh.connect(database.refresh)

# tugmalarga ulash

login_ui.pushButton_2.clicked.connect(get_login_code)

login_ui.pushButton.clicked.connect(login_func)

ui.pushButton.clicked.connect(logout)

refresh_kundalik_ui.pushButton.clicked.connect(refresh_maktabni_tugatish_func)

kundalik_login_ui.pushButton.clicked.connect(kundalik_login_func)

ui.pushButton_9.clicked.connect(KundalikLoginFrame.exec_)

ui.pushButton_10.clicked.connect(buy_func)

ui.pushButton_3.clicked.connect(get_data_serach)
ui.pushButton_15.clicked.connect(all_data_refresh_maktab)

ui.pushButton_16.clicked.connect(parol_kiritilmaganlar)
ui.pushButton_17.clicked.connect(online_add)


ui.pushButton_11.clicked.connect(del_one)
ui.pushButton_8.clicked.connect(add_one)

ui.p1.clicked.connect(partial(get_page, ui.p1))
ui.p2.clicked.connect(partial(get_page, ui.p2))
ui.p3.clicked.connect(partial(get_page, ui.p3))
ui.p4.clicked.connect(partial(get_page, ui.p4))
ui.p5.clicked.connect(partial(get_page, ui.p5))
ui.p6.clicked.connect(partial(get_page, ui.p6))
ui.p7.clicked.connect(partial(get_page, ui.p7))

ui.admins_button_2.clicked.connect(show_home_page)

ui.hisob_button.clicked.connect(show_profile_page)

ui.admins_button.clicked.connect(show_data_page)

ui.threadclass = ThreadClass(ui, database, loading, loading_quit)
ui.threadclass.get.connect(add_user)
ui.threadclass.get2.connect(set_page_buttons)
def show_message(message: str):
    msg = QtWidgets.QMessageBox(MainWindow)
    msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText(message)
    msg.setWindowTitle("✅ Jarayon yakunlandi")
    msg.exec_()
ui.runThread = RunThreadClass(ui, database)
ui.runThread.get.connect(set_today_func)
ui.runThread.show_message.connect(show_message)

ui.pushButton_6.clicked.connect(ui.runThread.start)

# Comboboxlar changr bo'lganda
ui.comboBox.currentTextChanged.connect(changed_combobox)


# Inputlarda enter bosilganda
login_ui.lineEdit.returnPressed.connect(login_ui.lineEdit_2.setFocus)
login_ui.lineEdit_2.returnPressed.connect(get_login_code)
login_ui.lineEdit_3.returnPressed.connect(login_func)
login_ui.pushButton_4.released.connect(partial(password_toggle, login_ui.lineEdit_2, login_ui.pushButton_4))
kundalik_login_ui.lineEdit.returnPressed.connect(kundalik_login_ui.lineEdit_2.setFocus)
kundalik_login_ui.lineEdit_2.returnPressed.connect(kundalik_login_func)
kundalik_login_ui.pushButton_2.released.connect(partial(password_toggle, kundalik_login_ui.lineEdit_2, kundalik_login_ui.pushButton_2))
ui.lineEdit_4.returnPressed.connect(get_data_serach)

buy_dialog_ui.pushButton_2.clicked.connect(BuyDialogFrame.close)
buy_dialog_ui.pushButton_2.clicked.connect(loading_quit)

ui.buy = BuyThread(ui, server, database, loading_quit)
ui.buy.get.connect(buy_how)

buy_dialog_ui.pushButton.clicked.connect(buy_active)

edit_ui.copy_phone_9.clicked.connect(partial(copy_inputs, edit_ui.lineEdit_21))
edit_ui.copy_phone_12.clicked.connect(partial(copy_inputs, edit_ui.lineEdit_20))
edit_ui.copy_phone_11.clicked.connect(partial(copy_inputs, edit_ui.lineEdit_19))








################################################################################################################

#######   #      #  #      #  
#      #  #      #  # #    #  
#######   #      #  #  #   #  
#    #    #      #  #   #  #  
#     #    ######   #    # #  

# for user_id in datadatabase.get_logins()ata["all_data_logins"][user_id].pop("password")
# database.refresh()
if __name__ == "__main__":
    if database.isLogined():
        if database.isLoginedKundalik():
            try:
                kundalik_data = database.get_kundalik_profile()
                how, data = database.login_kundalik(kundalik_data["login"], kundalik_data["parol"])
                if how:
                    nat = AsosiyMenyuniOchish()
                    if nat != None:
                        msg = QtWidgets.QMessageBox(MainWindow)
                        msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
                        msg.setText(nat)
                        msg.setWindowTitle("Xatolik!")
                        msg.show()
                        LoginFrame.show()
                elif data == None:
                    msg = QtWidgets.QMessageBox(MainWindow)
                    msg.setStyleSheet("border-radius: 5px; padding: 4px; color: blue; font-size: 20px;")
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Internetga ulanmagansiz")
                    msg.setInformativeText("Internetga ulaning")
                    msg.setWindowTitle("Xatolik!")
                    msg.show()
                elif data:
                    KundalikLoginFrame.show()
                else:
                    msg = QtWidgets.QMessageBox(MainWindow)
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setText("Ayni paytda eMaktab.uz sayti ishlamayapti, keyinroq qata urinib kuring. Saytda profilaktika ishlari olib borilayotgan bo'lishi ham mumkin")
                    msg.setInformativeText("Keyinroq qayta kiring 7")
                    msg.setWindowTitle("Xatolik!")
                    msg.show()
            except requests.exceptions.ConnectionError as e:
                msg = QtWidgets.QMessageBox(MainWindow)
                msg.setStyleSheet("padding: 4px; font-size: 20px;")
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Internetga ulanmagansiz")
                msg.setInformativeText("Internetga ulaning")
                msg.setWindowTitle("Xatolik!")
                msg.show()
            except Exception as e:
                # print(type(e))
                # print(e)
                LoginFrame.show()
        else:
            KundalikLoginFrame.show()
    else:
        LoginFrame.show()
    sys.exit(app.exec_())