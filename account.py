from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore 
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import (QApplication, QMessageBox, )
import sqlite3
import numpy as np
import logging
import time
from datetime import datetime
# import matplotlib.pyplot as plt
# import matplotlib.dates 
import math
import dialog_ui as ui

class Window(QDialog, ui.Ui_Dialog):
    def __init__(self):
        super().__init__()
        # QtWidgets
        self.setupUi(self)

        # database
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        self.cursorObj.execute('create table if not exists user(name , ID, offeringID UNIQUE, phone, address)')
        self.cursorObj.execute('create table if not exists offering(offeringID, date, category, amount, note, receipt, payment_type) ')        
        self.con.commit() 
        
        cursor = self.cursorObj.execute("SELECT * from offering").fetchall()
        print(cursor)
        cursor = self.cursorObj.execute("SELECT * from user").fetchall()
        print(cursor)

        # ADD user
        # self.ADD_user_name
        # self.ADD_user_ID
        self.ADD_user_offeringID.textChanged.connect(self.ADD_user_offeringID_onchange)
        # self.ADD_user_phone
        # self.ADD_user_address
        self.ADD_user_pushButton.clicked.connect(self.ADD_user_pushButton_onchange)

        # ADD offering
        self.ADD_offering_offeringID = ""
        self.ADD_offering_name = ""
        self.ADD_offering_person.textChanged.connect(self.ADD_offering_person_onchange)
        self.ADD_offering_date.setDate(QtCore.QDate().currentDate())


        # self.ADD_offering_paytype
        # self.ADD_offering_note
        # self.ADD_offering_category
        # self.ADD_offering_receipt
        # self.ADD_offering_pushButton.clicked.connect(self.ADD_offering_pushButton_onchange)




        # Search
        self.Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Search_date_end.setDate(QtCore.QDate().currentDate())

        # Weekly report 
        self.WeeklyReport_date.setDate(QtCore.QDate().currentDate())

        # Analysis Search
        self.Analysis_Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Analysis_Search_date_to.setDate(QtCore.QDate().currentDate())

        # self.user_list.addItem(row[0])

    '''ADD USER'''
    def ADD_user_offeringID_onchange(self):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        try:
            cursor = self.cursorObj.execute("SELECT * from user WHERE offeringID = '%s'" %(self.ADD_user_offeringID.text()))
            res = [item for item in cursor]
            if len(res)>0:
                self.status_note.append(f"Fail, OfferingID {self.ADD_user_offeringID.text()} already exists in the user table. Person {res} is in the table.")        
        except:
            pass

    def ADD_user_pushButton_onchange(self):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        try:
            cursor = self.cursorObj.execute("insert or ignore into user(name , ID, offeringID, phone, address) VALUES (?,?,?,?,?)" , (str(self.ADD_user_name.text()), str(self.ADD_user_ID.text()), str(self.ADD_user_offeringID.text()), str(self.ADD_user_phone.text()), str(self.ADD_user_address.text())))
        
            cursor = self.cursorObj.execute("SELECT * from user WHERE offeringID = '%s'" %(self.ADD_user_offeringID.text()))
            self.status_note.append(f"Success, append {str([item for item in cursor])} to the user table")
            self.con.commit()
        except:
            self.status_note.append(f"fail to append user, error message: {logging.CRITICAL}")
            pass
        
        self.ADD_user_name.setText("")
        self.ADD_user_ID.setText("")
        self.ADD_user_offeringID.setText("")
        self.ADD_user_phone.setText("")
        self.ADD_user_address.setText("")

    '''ADD OFFERING'''
    def ADD_offering_person_onchange(self):
        # self.update_database()
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        try:
            cursor = self.cursorObj.execute(f"SELECT name, offeringID FROM user WHERE offeringID = '%s' OR name = '%s'" %(str(self.ADD_offering_person.text()), str(self.ADD_offering_person.text())))
            res = [item for item in cursor]
            if len(res) > 0:
                # res =  np.char.split(np.char.strip(str(res), chars = "[]()"), ',') 
                self.ADD_offering_name = res[0][0]
                self.ADD_offering_offeringID = res[0][1]
                self.ADD_offering_person_show.setText(f"name: {self.ADD_offering_name}, offeringID: {self.ADD_offering_offeringID}")
            else:
                self.ADD_offering_person_show.setText("No user matched, please append the user or search another name/offeringID")
            self.con.commit()
        except:
            pass
          
    
    # def ADD_offering_pushButton_onchange(self):
    #     self.con = sqlite3.connect('database.db')
    #     self.cursorObj = self.con.cursor()

    #     cursor = self.cursorObj.execute("insert or ignore into offering(offeringID , date, category, amount, note, receipt, payment_type) VALUES (?,?,?,?,?,?,?)" ,('E00','2024-04-21','什一奉獻',1000,"",0, "cash"))



    # def update_database(self):
    #     self.cursorObj.execute("UPDATE threshold SET distance_area = %s, distance_ratio = %s ,  brightness= %s , blink=%s  WHERE user='%s'" %(self.eye_area, self.distance_threshold.value(),self.bright_threshold.value(),self.blink_threshold.value(),self.current_user))
    #     self.con.commit()   


    # def user_list_onchange(self,user = 1):
    #     self.update_database()
    #     self.current_user  = str(self.user_list.currentText())
    #     if user ==2 :
    #         self.current_user  = str(self.user_list_2.currentText())
    #         self.calendar()
    #     self.con = sqlite3.connect('database.db')
    #     self.cursorObj = self.con.cursor()
    #     cursor = self.cursorObj.execute("SELECT user,line_token, distance_area,distance_ratio, brightness, blink  from threshold  WHERE user = '%s'" %(self.current_user,))
    #     self.con.commit() 
    #     for row in cursor:
    #         self.blink_threshold.setValue(float(row[5]))
    #         self.bright_threshold.setValue(float(row[4]))
    #         self.distance_threshold.setValue(float(row[3]))
    #         self.eye_area_record = (float(row[2]))
    #         self.token = row[1]
    #     self.con.commit() 


if __name__ == '__main__':
    app = QApplication([])
    #apply_stylesheet(app, theme='dark_blue.xml')
    window = Window()
    window.show()
    app.exec()
