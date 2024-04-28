from PyQt5.QtWidgets import QDialog
from PyQt5 import QtCore 
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import (QApplication, QTableWidgetItem, QMainWindow, QMessageBox, )
import sqlite3
import numpy as np
import logging
import time
from datetime import datetime
# import matplotlib.pyplot as plt
# import matplotlib.dates 
import math
import dialog_ui as ui

        # self.buttongroup = QtWidgets.QButtonGroup(self)
        # self.buttongroup.addButton(self.Search_offering_data_button,1)
        # self.buttongroup.addButton(self.Search_user_data_button,2)

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
        self.Search_name = ""
        self.Search_offeringID = ""
        self.Search_table_type = "offering"
        self.Search_ID_Name.setText("")
        self.Search_offering_data_button.setChecked(True)
        self.Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Search_date_end.setDate(QtCore.QDate().currentDate())

        self.Search_ID_Name.textChanged.connect(lambda id_name: self.ID_Name_onchange(id_name,id_name))
        self.Search_ID_Name_list.clicked.connect(self.Search_ID_Name_list_onchange)
        self.buttongroup.buttonClicked.connect(self.Search_field_onchange)
        self.Search_pushButton.clicked.connect(lambda: self.Search_pushButton_onchange(self.Search_offeringID, \
                                                                                       self.Search_table_type, \
                                                                                        "", \
                                                                                       str(datetime.strptime(self.Search_date_from.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date()), \
                                                                                       str(datetime.strptime(self.Search_date_end.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date()) ))
        
        self.Search_table.cellChanged.connect(lambda row, col: self.Search_table_onchange(row, col))


        # self.Search_table
        




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
            self.con.commit()

            res = [item for item in cursor]
            if len(res)>0:
                self.status_note.append(f"Fail, 名字 {self.ADD_user_name.text()} 已經存在於奉獻人名單: {res}")        
        except:
            pass

    def ADD_user_offeringID_onchange(self):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        try:
            cursor = self.cursorObj.execute("SELECT * from user WHERE offeringID = '%s'" %(self.ADD_user_offeringID.text()))
            self.con.commit()
            res = [item for item in cursor]
            if len(res)>0:
                self.status_note.append(f"Fail, 編號 {self.ADD_user_offeringID.text()} 已經存在於奉獻人名單: {res}")        
        except:
            pass

    def ADD_user_pushButton_onchange(self):
        if self.ADD_user_name.text() and self.ADD_user_offeringID.text():

            self.con = sqlite3.connect('database.db')
            self.cursorObj = self.con.cursor()
            try:
                cursor = self.cursorObj.execute("insert or ignore into user(name , ID_card, offeringID, phone, address) VALUES (?,?,?,?,?)" , \
                                                (str(self.ADD_user_name.text()), str(self.ADD_user_ID.text()), str(self.ADD_user_offeringID.text()), str(self.ADD_user_phone.text()), str(self.ADD_user_address.text())))
                cursor = self.cursorObj.execute("SELECT * FROM user ORDER BY id DESC LIMIT 1")
                self.status_note.append(f"Success, 新增 {[item for item in cursor]} 到奉獻人名單")
                self.con.commit()
            except:
                self.status_note.append(f"fail to add user, error message: {logging.CRITICAL}")
                pass
        else:
            self.status_note.append(f"fail to add user, 名字和奉獻編號不可為空")

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
                self.ADD_offering_person_show.setText("No user matched, 請新增奉獻人或重新搜尋")
            self.con.commit()
        except:
            pass
    
    def ADD_offering_pushButton_onchange(self):
        if str(self.ADD_offering_offeringID) and str(self.ADD_offering_amount.text()):
            self.con = sqlite3.connect('database.db')
            self.cursorObj = self.con.cursor()
            # maybe use 0/1
            want_receipt = "Yes" if self.ADD_offering_receipt.isChecked() else "No"
            try:
                cursor = self.cursorObj.execute("insert into offering(offeringID , date, category, amount, note, receipt, payment_type) VALUES (?,?,?,?,?,?,?)",\
                                                (str(self.ADD_offering_offeringID), str(datetime.strptime(self.ADD_offering_date.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date()),str(self.ADD_offering_category.currentText()), str(self.ADD_offering_amount.text()),str(self.ADD_offering_note.toPlainText()), want_receipt, str(self.ADD_offering_paytype.currentText())))
                self.con.commit()

                cursor = self.cursorObj.execute("SELECT * FROM offering ORDER BY id DESC LIMIT 1")
                self.status_note.append(f"Success, 新增 {[row for row in cursor]}")
                self.con.commit()
                
            except:
                pass
        else:
            self.status_note.append(f"fail, 奉獻人和奉獻金額不可為空, 或是奉獻人不存在")

        self.ADD_offering_offeringID = ""
        self.ADD_offering_name = ""
        self.ADD_offering_person.setText("")
        self.ADD_offering_date.setDate(QtCore.QDate().currentDate())
        self.ADD_offering_amount.setText("")
        self.ADD_offering_paytype.setCurrentIndex(0)
        self.ADD_offering_note.setText("")
        self.ADD_offering_category.setCurrentIndex(0)
        self.ADD_offering_receipt.setChecked(False)

    '''
    Search
    '''
    def ID_Name_onchange(self, name, id):
        # self.update_database()
        if name and id:
            try:
                self.con = sqlite3.connect('database.db')
                self.cursorObj = self.con.cursor()
                cursor = self.cursorObj.execute(f"SELECT name, offeringID FROM user WHERE  name LIKE '%{str(name)}%' OR offeringID LIKE '%{str(id)}%'")
                res = [f"姓名: {name}, 編號: {offeringID}" for name, offeringID in cursor]

                self.Search_ID_Name_list.clear()
                self.Search_ID_Name_list.addItems(res)

                self.con.commit()
            except:
                pass   
        else:
            self.Search_ID_Name_list.clear()
            self.Search_name, self.Search_offeringID = "", ""

    def Search_ID_Name_list_onchange(self):
        curr = np.char.split(self.Search_ID_Name_list.currentItem().text(), ' ').tolist()
        self.Search_name, self.Search_offeringID = curr[1], curr[3]
    
    def Search_field_onchange(self):
        if self.buttongroup.checkedId() == 1:
            self.Search_table_type = "offering"
        else:
            self.Search_table_type = "user"

    def Search_sql(self, person = "", field = "offering", offering_category = "", date_from = "", date_end = ""):
        sql = f"select * from {field}"
        filter = []
        if person: filter.append(f"(offeringID = '{str(person)}')")
        if field == "offering":
            if offering_category: filter.append(f"(category = '{str(offering_category)}' OR note LIKE '%{str(offering_category)}%')")
            if date_from and date_end: filter.append(f"(date between '{str(date_from)}' AND '{str(date_end)}')")

        if filter:
            sql += " WHERE" + " AND ".join(filter)
        # print(sql)
        return sql

    def Search_pushButton_onchange(self, person = "", field = "offering", offering_category = "", date_from = "", date_end = ""):
        
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()

        sql = self.Search_sql(person, field, offering_category, date_from, date_end)
        cursor = self.cursorObj.execute(sql).fetchall()
        self.con.commit()

        self.Search_table.setRowCount(0)
        if len(cursor) > 0:
            self.Search_table.setColumnCount(len(cursor[0]))      

        # Notice that col headers are manual
        if field == "user":
            self.Search_table.setHorizontalHeaderLabels(('unique key', '姓名', '身分證', '奉獻編號', '電話', '地址'))
        else:
            self.Search_table.setHorizontalHeaderLabels(('unique key', '奉獻編號', '日期', '奉獻項目', '金額', '備註', '收據', '奉獻方式'))

        for row_number, row_data in enumerate(cursor):
                self.Search_table.insertRow(row_number)
                for column_number, data in enumerate(row_data):
                    if data == None:
                        data = ""
                        self.Search_table.setItem(row_number,
                        column_number, QTableWidgetItem(str(data)))
                    else:
                        item = QTableWidgetItem(str(data))
                        # https://blog.csdn.net/qq_41539778/article/details/119205439
                        item.setFlags(QtCore.Qt.ItemFlags(int("111111", 2))) # item.flags() ^ QtCore.Qt.ItemIsEditable
                        self.Search_table.setItem(row_number, column_number, item)
    
    def Search_table_onchange(self, row, col):
        # https://zhuanlan.zhihu.com/p/58619107
        if self.Search_table.currentItem():
            # print(self.Search_table.currentItem().text(), self.Search_table.item(row,0).text())

            self.con = sqlite3.connect('database.db')
            self.cursorObj = self.con.cursor()
            cursor = self.cursorObj.execute(f"PRAGMA table_info({self.Search_table_type})") 
            header = [row[1] for row in cursor]
            self.con.commit()
            cursor = self.cursorObj.execute(f"UPDATE {self.Search_table_type} SET {header[col]} = '{self.Search_table.currentItem().text()}' WHERE id = '{self.Search_table.item(row,0).text()}'").fetchall()
            self.con.commit()
            
# np.char.split(np.char.strip(str(res), chars = "[]()"), ',') 



if __name__ == '__main__':
    # app = QApplication([])
    # #apply_stylesheet(app, theme='dark_blue.xml')
    # window = Window()
    # window.show()
    # app.exec()

    import sys
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    window = Window()
    window.show()
    sys.exit(app.exec_())
