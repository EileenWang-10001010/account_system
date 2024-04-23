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
        self.cursorObj.execute('create table if not exists user(id INTEGER PRIMARY KEY, name UNIQUE, ID_card, offeringID UNIQUE, phone, address)')
        self.cursorObj.execute('create table if not exists offering(id INTEGER PRIMARY KEY, offeringID, date, category, amount, note, receipt, payment_type) ')        
        self.con.commit() 
        
        cursor = self.cursorObj.execute("SELECT * from offering").fetchall()
        print(cursor)
        cursor = self.cursorObj.execute("SELECT * from user").fetchall()
        print(cursor)
        # status clear
        self.status_clear.clicked.connect(self.status_clear_onchange)

        # ADD user
        # self.ADD_user_wrap
        self.ADD_user_name.textChanged.connect(self.ADD_user_name_onchange)
        # self.ADD_user_ID
        self.ADD_user_offeringID.textChanged.connect(self.ADD_user_offeringID_onchange)
        # self.ADD_user_phone
        # self.ADD_user_address
        self.ADD_user_pushButton.clicked.connect(self.ADD_user_pushButton_onchange)

        # ADD offering
        # self.ADD_offering_wrap
        self.ADD_offering_offeringID = ""
        self.ADD_offering_name = ""
        self.ADD_offering_person.textChanged.connect(self.ADD_offering_person_onchange)
        self.ADD_offering_pushButton.clicked.connect(self.ADD_offering_pushButton_onchange)

        self.ADD_offering_person.setText("")
        self.ADD_offering_date.setDate(QtCore.QDate().currentDate())
        self.ADD_offering_amount.setText("")
        self.ADD_offering_paytype.setCurrentIndex(0)
        self.ADD_offering_note.setText("")
        self.ADD_offering_category.setCurrentIndex(0)
        self.ADD_offering_receipt.setChecked(False)

        # Search
        self.Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Search_date_end.setDate(QtCore.QDate().currentDate())

        # Weekly report 
        # self.WeeklyReport_wrap
        self.WeeklyReport_date.setDate(QtCore.QDate().currentDate())
        # WeeklyReport_tenth_ID_show
        # WeeklyReport_tenth_amount_show
        # WeeklyReport_sonday_ID_show

        # WeeklyReport_firstfruit_ID_show

        # WeeklyReport_thanks_ID_show

        # WeeklyReport_special_ID_show

        # WeeklyReport_repair_ID_show

        # WeeklyReport_specific_ID_show

        # WeeklyReport_others_ID_show

        # Analysis Search
        # self.Analysis_Search_wrap
        self.Analysis_Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Analysis_Search_date_to.setDate(QtCore.QDate().currentDate())

        # self.user_list.addItem(row[0])

    def status_clear_onchange(self):
        self.status_note.setText("")

    '''
    ADD USER

    ADD_user_name_onchange: name is UNIQUE
    ADD_user_offeringID_onchange: offeringID is UNIQUE
    ADD_user_pushButton_onchange: Add user to database - user table, and clear the blanks
    '''
    def ADD_user_name_onchange(self):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        try:
            cursor = self.cursorObj.execute("SELECT * from user WHERE name = '%s'" %(self.ADD_user_name.text()))
            res = [item for item in cursor]
            if len(res)>0:
                self.status_note.append(f"Fail, name {self.ADD_user_name.text()} already exists in the user table. Person {res} is in the table.")        
        except:
            pass

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
            cursor = self.cursorObj.execute("insert or ignore into user(name , ID_card, offeringID, phone, address) VALUES (?,?,?,?,?)" , \
                                            (str(self.ADD_user_name.text()), str(self.ADD_user_ID.text()), str(self.ADD_user_offeringID.text()), str(self.ADD_user_phone.text()), str(self.ADD_user_address.text())))
            cursor = self.cursorObj.execute("SELECT * FROM user ORDER BY id DESC LIMIT 1")
            self.status_note.append(f"Success, add {[item for item in cursor]} to the user table")
            self.con.commit()
        except:
            self.status_note.append(f"fail to add user, error message: {logging.CRITICAL}")
            pass
        
        self.ADD_user_name.setText("")
        self.ADD_user_ID.setText("")
        self.ADD_user_offeringID.setText("")
        self.ADD_user_phone.setText("")
        self.ADD_user_address.setText("")

    '''
    ADD OFFERING

    ADD_offering_person_onchange: find the right person
    ADD_offering_pushButton_onchange: add offering to database - offering, and clear the blanks
    '''
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
    
    def ADD_offering_pushButton_onchange(self):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        # maybe use 0/1
        want_receipt = "Yes" if self.ADD_offering_receipt.isChecked() else "No"
        try:
            cursor = self.cursorObj.execute("insert into offering(offeringID , date, category, amount, note, receipt, payment_type) VALUES (?,?,?,?,?,?,?)",\
                                            (str(self.ADD_offering_offeringID), datetime.strptime(self.ADD_offering_date.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date(),str(self.ADD_offering_category.currentText()), str(self.ADD_offering_amount.text()),str(self.ADD_offering_note.toPlainText()), want_receipt, str(self.ADD_offering_paytype.currentText())))
            
            cursor = self.cursorObj.execute("SELECT * FROM offering ORDER BY id DESC LIMIT 1")
            self.status_note.append(f"Success, add {[row for row in cursor]}")
            self.con.commit()
            
        except:
            pass

        self.ADD_offering_offeringID = ""
        self.ADD_offering_name = ""
        self.ADD_offering_person.setText("")
        self.ADD_offering_date.setDate(QtCore.QDate().currentDate())
        self.ADD_offering_amount.setText("")
        self.ADD_offering_paytype.setCurrentIndex(0)
        self.ADD_offering_note.setText("")
        self.ADD_offering_category.setCurrentIndex(0)
        self.ADD_offering_receipt.setChecked(False)


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
