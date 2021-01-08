from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from functools import partial
# from analytics import  AnalyticsWidget

import os
import sys
import time

import math
import requests
import datetime
import json
import random


import pyautogui
import pywinauto.mouse as mouse
import pywinauto.keyboard as keyboard
import webbrowser
from pywinauto import Desktop, Application

import pytesseract
from PIL import Image
from zipfile import ZipFile   

# ============= Const variables define part =============

FROM_RESET, _ = loadUiType(os.path.join(os.path.dirname(__file__), "./UI/reset.ui"))
FROM_SETTINGSDLG, _ = loadUiType(os.path.join(os.path.dirname(__file__), "./UI/settingsDlg.ui"))
is_auth = False

# =============
def get_curtime():
    curtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')       
    return curtime

def get_response_for_license(username,license_key):    
    url = f"http://localhost:8002/ischecklicense?username={username}&license={license_key}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_response_for_stake(stake):    
    url = f"http://localhost:8002/get_stake?stake={stake}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def check_auth(username,license_key):    
    response = get_response_for_license(username,license_key)
    results=json.dumps(response) 
    results=json.loads(results)
    print(results)
    print(results['results'])

    print(results['username'])
    print(results['license'])

    
    if results['results']:
        global is_auth
        is_auth = True  

    print(is_auth)

def get_stake_text():
    stake = '1'
    response = get_response_for_stake(stake)
    results=json.dumps(response) 
    results=json.loads(results)
    print(results)
    print(results['results'])
    print(results['targetvalue'])
    print(results['odds'])


zip_name = "Tesseract-OCR2.zip"

def unzip(filename):
    with ZipFile(filename, 'r') as zip:         
        zip.printdir()          
        print('Extracting all the files now...') 
        zip.extractall() 

def _getText(imgname):
    pytesseract.pytesseract.tesseract_cmd = r"Tesseract-OCR2\\tesseract.exe"
    image = Image.open(str(imgname))    
    #im = image.convert('p')
    custom_config = r'--psm 6 --oem 3' 
    st = pytesseract.image_to_string(image, lang='eng',config=custom_config)    
    # print(image_to_text)
    if '.' not in st :
        st2 = st[0]+'.'+st[1:len(st)]
    else:
        st2 = st
    return st2

def start(searchwords,odds,stake):
    # try:
    url = f"http://localhost:8002/start?searchwords={searchwords}&odds={odds}&stake={stake}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
    # except:        
    #     return False
    

# ============= SettingsDlg define part =============

class SettingsDlg(QMainWindow, FROM_SETTINGSDLG) :
    
    def __init__(self, parent = None) :
        super(SettingsDlg, self).__init__(parent)
        self.setupUi(self)
        
        px = QPixmap("./images/backDlg.png")
        px = px.scaled(self.back.size(), Qt.IgnoreAspectRatio)
        self.back.setPixmap(px)
        
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.btnClose.setIcon(QIcon(QPixmap("./images/icon_window_close.png")))
        
        self.btnClose.clicked.connect(self.close)
        self.cancelBtn.clicked.connect(self.close)
        self.okBtn.clicked.connect(self.saveData)
    
    def saveData(self) :
        fn = open("./data.txt", "w")
        
        fn.write(self.user.text() + '\n')
        fn.write(self.licKey.text() + '\n')
        fn.write(str(self.flatSpin.value()) + '\n')
        fn.write("True" + '\n' if self.flatChk.isChecked() else "False" + '\n')
        fn.write(self.domain.text() + '\n')
        fn.write(str(self.runMinSpin.value()) + '\n')
        fn.write(str(self.stopMinSpin.value()) + '\n')
        fn.write(self.username.text() + '\n')
        fn.write(self.pwd.text() + '\n')
        
        # check_auth(self.user.text(),self.licKey.text())

        self.close()

# ============= MainWindow define part =============

class MainWindow(QMainWindow, FROM_RESET) :
    def __init__(self, parent = None) :
        QMainWindow.__init__(self)
        self.setupUi(self)
        
        px = QPixmap("./images/back.png")
        px = px.scaled(self.back.size(), Qt.IgnoreAspectRatio)
        self.back.setPixmap(px)
        
        self.setWindowIcon(QIcon('./images/icon.png'))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.iconLabel.setPixmap(QPixmap("./images/icon.png"))
        self.btnMinimize.setIcon(QIcon(QPixmap("./images/icon_window_minimize.png")))
        self.btnClose.setIcon(QIcon(QPixmap("./images/icon_window_close.png")))

        self.btnClose.clicked.connect(self.close)
        self.btnMinimize.clicked.connect(self.showMinimized)

        self.startBtn.clicked.connect(self.startProg)
        self.stopBtn.clicked.connect(self.stopProg)
        self.settingBtn.clicked.connect(self.showSettingDlg)

        if os.path.exists('Tesseract-OCR2'):
            print(' ! It exists tesseract-ocr directory.')
        else:
            unzip(zip_name)

    def startProg(self) :   
        curtime = get_curtime()     
        self.logText.append(curtime + ":" + "Data processing is started!")
        f = open("./data.txt", "r")
        data = f.read()
        data = data.split('\n')
        username = data[0]
        license_key = data[1]
        stake = data[2]

        print(username)
        print(license_key)
        print(stake)

        global is_auth
        is_auth = False  
        if username and license_key:
            check_auth(username,license_key)
        

        if is_auth:
            curtime = get_curtime()   
            self.logText.append(curtime + ": " + "Login success!")
            self.account.setText(username)
            response = get_response_for_stake(stake)
            results=json.dumps(response) 
            results=json.loads(results)
            data = results['data']
            print(data)
            time.sleep(1)
            if data:
                for item in data:                
                    self.logText.append("Targetvalue:"+item['targetvalue'])
                    self.logText.append("Odds:"+item['odds'])
                    self.logText.append("Stake:"+item['stake'])
            
                    # searchwords = results['targetvalue']
                    # odds = results['odds']
                    # stake = results['stake']
                    time.sleep(1)
                    # if searchwords:      
                    #       
                    # searchwords = 'foot'
                    # odds = '1.98'
                    # stake = '1'
                    result = start(item['targetvalue'],item['odds'],item['stake'])
                    self.logText.append("Bet Result:"+str(result['results']))
                    print(result)
            else:
                self.logText.append("--------"+"No result"+"--------")

            # searchwords = "foot"
            # odds = "2.2"
            # stake = "2.5"
            # result = start(searchwords,odds,stake)
            

        else:
            curtime = get_curtime()   
            self.logText.append(curtime + ": " + "Login faild.Please confirm login info again!")

        

    def stopProg(self) :
        self.logText.append(get_curtime() + ":" + "Data processing is stopped!")

    def showSettingDlg(self) :
        
        
        stgDlg = SettingsDlg(self)
        stgDlg.setWindowModality(Qt.ApplicationModal)  
        
        try:
            f = open("./data.txt", "r")    
            data = f.read()
            data = data.split('\n')
            username = data[0]
            license_key = data[1]
            stake = data[2]
            checked = data[3]
            domain = data[4]
            runmin = data[5]
            runmax = data[6]
            clientname = data[7]
            clientpwd = data[8]      

            stgDlg.user.setText(username)
            stgDlg.licKey.setText(license_key)
            if stake:
                stgDlg.flatSpin.setValue(float(stake))
            if checked == "True":
                stgDlg.flatChk.setChecked(True)
            stgDlg.domain.setText(domain)
            if runmin:
                stgDlg.runMinSpin.setValue(float(runmin))
            if runmax:
                stgDlg.stopMinSpin.setValue(float(runmax))
            stgDlg.username.setText(clientname)
            stgDlg.pwd.setText(clientpwd)
        except:
            pass
        
        stgDlg.show()

    def closeEvent(self, event) :
        reply = QMessageBox.question(self, 'Application Close', 'Are you sure you want to close the application?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes :
            self.close()
        else :
            event.ignore()


# ============= Application Start Point =============

def main() :
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    app.exec()

if __name__ == '__main__' :
    try :
        main()
    except Exception as why :
        print(why)
