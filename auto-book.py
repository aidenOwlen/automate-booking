import sys
import threading

from PyQt5.QtWidgets import (QWidget, QPushButton,
                             QHBoxLayout, QVBoxLayout, QApplication,QDateTimeEdit, QTimeEdit,QGridLayout,QLabel,QLineEdit)
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

from datetime import datetime
import datetime as dt

from time import sleep
#import winsound

from selenium import webdriver
#from chromedriver_py import binary_path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys



global START,TIME2,TIME1, RUNNING, datetimeFormat, BOOKED

duration = 3000  # milliseconds / sound
freq = 440  # Hz / sound 
# To play a beep to notify to complete captcha

datetimeFormat = '%H:%M'
RUNNING = True
BOOKED = False
repeat = True


def main_bot(username,password,time1,time2): #BOT PART
    global BOOKED, TIME1,TIME2, repeat
    driver = webdriver.Chrome()
    driver.get("https://foreupsoftware.com/index.php/booking/20290#/teetimes")
    driver.maximize_window()
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".login")))
    element.click() 

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email")))
    element.send_keys(username)

    driver.find_element_by_name("password").send_keys(password)
    driver.find_element_by_xpath("""//*[@id="login"]/div/div[3]/div[1]/button[1]""").click()

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, """//*[@id="profile-main"]/div/ul/li/a""")))
    element.click() 
    
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, """//*[@id="content"]/div/button[1]""")))
    element.click()

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, """//*[@id="nav"]/div/div[3]/div/div/a[4]""")))
    element.click()

    d = dt.date.today()
    d2 = dt.date.today()

    the_value = 6
    opp = open("day.txt","r")
    r = opp.read()
    opp.close()
    try:
        the_value = int(r)
    except:
        pass

    while d.weekday() != the_value:
        d += dt.timedelta(1)

    if d2 == d:
        d+= dt.timedelta(7)

    d = str(d).split("-")
    new_d = d[1] + "-" + d[2] + "-" + d[0]
    cx = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "date")))
    cx.send_keys(Keys.CONTROL + "a")

    diff = 1
    while str(diff) != "0:01:00":
            now = datetime.now()
            current = now.strftime("%H:%M")

            diff = datetime.strptime(START, datetimeFormat)\
    - datetime.strptime(current, datetimeFormat)
            
    sleep(50)
    

    cx.send_keys(new_d)
    cx.send_keys(Keys.ENTER)
   

    time_not_released = True
       
    while time_not_released and repeat:
        cx.send_keys(Keys.ENTER)
        x = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, "times")))
        items = x.find_elements_by_tag_name("li")
        for item in items:

            try:
                print(item.text)
                hour = item.text.replace("pm", " PM").replace("am"," AM").replace("\n","")
                hour = hour.split(":")
                if len(hour[0]) == 1:
                    hour[0] = "0" + hour[0]
                hour = ":".join(hour)
                if "PM" in hour or "AM" in hour:
                    hour_to_book = hour[0:8]
                 
                    try:
                        hour_to_book = datetime.strptime(hour_to_book,"%H:%M %p")
                        hour_to_book = str(hour_to_book)[-8:]
                        hour_to_book = hour_to_book[0:5]
                        hour_to_book = datetime.strptime(str(hour_to_book), "%H:%M")
                        
                    except Exception as er:
                        print("error " + str(er))

                    if hour_to_book > time1 and hour_to_book < time2:
                        try:
                            print(str(hour_to_book) + str( "BOOKED"))
                            item.click()
                            time_not_released = False
                            print("BOOKED")
                            
                            repeat = False
                            break
                        except Exception as C:
                            print("Exception : " + str(C))
                            repeat = True
                            
                        
                        # You have 5 minutes to solve captcha manually
            except:
                pass
        

    sleep(3600)



class SeleniumWorker(QtCore.QObject): # MULTITHREAD LAUNCHER BOT
   
    progressChanged = QtCore.pyqtSignal(str)
    def doWork(self):
        global TIME1,TIME2
        
        diff = 1
        
        while str(diff) != "0:02:00" and str(diff) != "0:01:00" and str(diff) != "0:00:00":
            now = datetime.now()
            current = now.strftime("%H:%M")

            diff = datetime.strptime(START, datetimeFormat)\
    - datetime.strptime(current, datetimeFormat)
            
            sleep(1)
            self.progressChanged.emit(str(diff))
            print(diff)

        TIME1 = datetime.strptime(TIME1, "%H:%M %p")
        TIME2 = datetime.strptime(TIME2, "%H:%M %p")
        self.progressChanged.emit("RUNNING")
        main_bot(USERNAME,PASSWORD,TIME1,TIME2)
        



class Interface(QWidget): # GUI

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        
        self.running = False
   
        self.setStyleSheet("background-color:lightblue")
        self.hbox = QGridLayout()

        self.thread = QtCore.QThread()
        self.worker = SeleniumWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.doWork)

        self.startTime = QTimeEdit()
        self.startTime.setStyleSheet("background-color:dodgerblue")
        self.label1 = QLabel("Run at : ")
        self.label1.setStyleSheet("color:red;font:bold")

        self.nb_instances = QLabel("Nb of instances : ")
        self.nb_instances.setStyleSheet("color:red;font:bold")

        self.fromm = QLabel("From")
        self.fromm.setStyleSheet("color:red;font:bold")

        self.to = QLabel("To")
        self.to.setStyleSheet("color:red;font:bold")
        self.to.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.to.setAlignment(Qt.AlignCenter)

        self.name = QLabel("Username")
        self.name.setStyleSheet("color:red;font:bold")

        self.passs = QLabel("Password")
        self.passs.setStyleSheet("color:red;font:bold")
        self.passs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.passs.setAlignment(Qt.AlignCenter)

        self.time1 = QTimeEdit()
        self.time1.setStyleSheet("background-color:dodgerblue")
        self.time2 = QTimeEdit() 
        self.time2.setStyleSheet("background-color:dodgerblue")
        self.start = QPushButton("Run")
        self.start.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.start.setStyleSheet("font:bold;background-color:dodgerblue")

        self.countdown = QTextEdit()
        self.countdown.setReadOnly(True)

        self.countdown.setText("State : Not running")
        self.countdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.countdown.setAlignment(Qt.AlignCenter)
        self.countdown.setStyleSheet("font:bold")

        self.input1 = QLineEdit("jackbij@gmail.com")
        self.input1.setStyleSheet("background-color:dodgerblue")
        self.input2 = QLineEdit("Jackiebijou3")
        self.input2.setStyleSheet("background-color:dodgerblue")
        self.input2.setEchoMode(QLineEdit.Password)

        self.instances = QLineEdit("5")
    
        self.hbox.addWidget(self.label1,0,0)
        #self.hbox.addWidget(self.nb_instances,0,2)

        #self.hbox.addWidget(self.instances,0,3)

        self.hbox.addWidget(self.startTime,0,1)

        self.hbox.addWidget(self.fromm,1,0)
        self.hbox.addWidget(self.time1,1,1)

        self.hbox.addWidget(self.to,1,2)
        self.hbox.addWidget(self.time2,1,3)

        self.hbox.addWidget(self.start,3,0,1,4)

        self.hbox.addWidget(self.name,2,0)
        self.hbox.addWidget(self.input1,2,1)

        self.hbox.addWidget(self.passs,2,2)
        self.hbox.addWidget(self.input2,2,3)
        self.hbox.addWidget(self.countdown,4,0,1,4)

      
        self.worker.progressChanged.connect(self.progressing)
        self.start.clicked.connect(self.run)
        self.setLayout(self.hbox)
        self.setGeometry(300, 300, 500, 150)
        self.setWindowTitle('Feldm')
        self.show()

    def progressing(self,value):
         if value != "RUNNING":
            self.countdown.setText("Will run at time : " + str(START) + "\n" + "For time interval between : " + str(TIME1) + " and " + str(TIME2) + "\n" + "Countdown before running the bot : " + str(value))
         else:
            self.countdown.setText("RUNNING NOW")
    def run (self):
       global START,TIME1,TIME2, RUNNING, USERNAME, PASSWORD
       now = datetime.now()
       current = now.strftime("%H:%M")
       start_time = datetime.strptime(self.startTime.text(), "%I:%M %p")
       start_time = datetime.strftime(start_time, "%H:%M")

       TIME1 = self.time1.text()
       TIME2 = self.time2.text()

       diff = datetime.strptime(start_time, datetimeFormat)\
    - datetime.strptime(current, datetimeFormat)
     
       if self.running == False:
      
           self.start.setText("Stop")
           self.countdown.setText("Will run at time : " + str(start_time) + "\n" + "For time interval between : " + self.time1.text() + " and " + self.time2.text() + "\n" + "Countdown before running the bot : " + str(diff))
           self.running = True
           self.thread.start()
           START = str(start_time)
           USERNAME = self.input1.text()
           PASSWORD = self.input2.text()
     
       else:
            
            self.start.setText("Run")
            self.countdown.setText("State : Not running")
            self.running = False
            self.close()

            

        
        
def main():
    app = QApplication(sys.argv)
    interface = Interface()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    win.show()
    sys.exit(app.exec_())

