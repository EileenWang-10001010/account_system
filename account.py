from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtGui import QImage,QPixmap
from PyQt5.QtWidgets import (QDialog, QApplication, QTableWidgetItem, QMainWindow, QMessageBox, )
import sqlite3
import numpy as np
import logging
import time
from datetime import datetime
import pandas as pd
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
        self.setupUi(self)

        # database
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        self.cursorObj.execute('create table if not exists user(id INTEGER PRIMARY KEY, name UNIQUE, ID_card, offeringID UNIQUE, phone, address)')
        self.cursorObj.execute('create table if not exists offering(id INTEGER PRIMARY KEY, offeringID, name, date, category, amount, note, receipt, payment_type) ')        
        self.con.commit() 
        
        # cursor = self.cursorObj.execute("SELECT * from offering").fetchall()
        # print(cursor)
        # cursor = self.cursorObj.execute("SELECT * from user").fetchall()
        # print(cursor)
        
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
                                                                                       datetime.strptime(self.Search_date_from.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date(), \
                                                                                       datetime.strptime(self.Search_date_end.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date() ))
        
        self.Search_table.cellChanged.connect(lambda row, col: self.Search_table_update_onchange(row, col))
        # self.Search_table.verticalHeader().sectionClicked.connect(lambda item: self.Search_table_delete_onchange(item))
        self.Search_table_delete_row.clicked.connect(self.Search_table_delete_onchange)
        self.Search_date_all.setChecked(False)

        # Weekly report 
        # self.WeeklyReport_wrap
        self.WeeklyReport_date_from.setDate(QtCore.QDate().currentDate())
        self.WeeklyReport_date_end.setDate(QtCore.QDate().currentDate())
        self.WeeklyReport_date_from.dateChanged.connect(self.WeeklyReport_date_onchange)
        self.WeeklyReport_date_end.dateChanged.connect(self.WeeklyReport_date_onchange)
        self.WeeklyReport_button.clicked.connect(self.WeeklyReport_date_onchange)

        # Analysis Search
        # self.Analysis_Search_wrap
        self.Analysis_name, self.Analysis_offeringID = "", ""
        self.Analysis_Search_date_from.setDate(QtCore.QDate().currentDate())
        self.Analysis_Search_date_end.setDate(QtCore.QDate().currentDate())
        self.Analysis_Search_ID_Name.textChanged.connect(lambda id_name: self.Analysis_Search_ID_Name_onchange(id_name,id_name))
        self.Analysis_ID_Name_list.clicked.connect(self.Analysis_ID_Name_list_onchange)
        self.Analysis_Search_pushButton.clicked.connect(lambda: self.Search_pushButton_onchange(self.Analysis_offeringID, \
                                                                                       "offering", \
                                                                                        str(self.Analysis_Search_category.text()), \
                                                                                       datetime.strptime(self.Analysis_Search_date_from.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date(), \
                                                                                       datetime.strptime(self.Analysis_Search_date_end.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date() ))

        self.Analysis_Search_show_download.clicked.connect(self.Analysis_Search_show_download_onchange)
        self.Analysis_Search_dataset_download.clicked.connect(self.Analysis_Search_dataset_download_onchange)


    def status_clear_onchange(self):
        self.status_note.setText("")

    def sql_operation(self, query):
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        cursor = self.cursorObj.execute(query).fetchall()
        self.con.commit()
        return cursor


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
            want_receipt = "No" if self.ADD_offering_receipt.isChecked() else "Yes"
            try:
                cursor = self.cursorObj.execute("insert into offering(offeringID ,name, date, category, amount, note, receipt, payment_type) VALUES (?,?,?,?,?,?,?,?)",\
                                                (str(self.ADD_offering_offeringID), str(self.ADD_offering_name), datetime.strptime(self.ADD_offering_date.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date(),str(self.ADD_offering_category.currentText()), str(self.ADD_offering_amount.text()),str(self.ADD_offering_note.toPlainText()), want_receipt, str(self.ADD_offering_paytype.currentText())))
                self.con.commit()

                cursor = self.cursorObj.execute("SELECT * FROM offering ORDER BY id DESC LIMIT 1")
                self.status_note.append(f"Success, 新增 {[row for row in cursor]}")
                self.con.commit()
                # update table
                self.Search_pushButton_onchange("", \
                                                "offering", \
                                                "", \
                                                "", \
                                                "")
                
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
        # self.ADD_offering_category.setCurrentIndex(0)
        self.ADD_offering_receipt.setChecked(False)

    '''
    Search and Update
    
    ID_Name_onchange (shared with analysis)
    Search_ID_Name_list_onchange
    Search_field_onchange
    Search_sql
    Search_pushButton_onchange
    Search_table_update_onchange: warning: date update!
    Search_table_delete_onchange
    '''
    def ID_Name_onchange(self, name, id):
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
            if offering_category: filter.append(f"(category LIKE '%{str(offering_category)}%' OR note LIKE '%{str(offering_category)}%')")
            
            # in which tab
            search_all_date = (not self.Analysis_date_all.isChecked()) if self.tabWidget.currentIndex() else (not self.Search_date_all.isChecked())
            if search_all_date:
                if date_from and date_end: filter.append(f"(date between '{datetime.strptime(str(date_from), '%Y-%m-%d').date()}' \
                                                            AND '{datetime.strptime(str(date_end), '%Y-%m-%d').date()}')")
        if filter:
            sql += " WHERE" + " AND ".join(filter)

        return sql
    
    def Search_pushButton_onchange(self, person = "", field = "offering", offering_category = "", date_from = "", date_end = ""):
        
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()

        sql = self.Search_sql(person, field, offering_category, date_from, date_end)
        cursor = self.cursorObj.execute(sql).fetchall()
        self.con.commit()

        which_table = self.Analysis_Search_table if self.tabWidget.currentIndex() else self.Search_table

        which_table.setRowCount(0)
        if len(cursor) > 0:
            which_table.setColumnCount(len(cursor[0]))      

        # Notice that col headers are manual
        if field == "user":
            which_table.setHorizontalHeaderLabels(('unique key', '姓名', '身分證', '奉獻編號', '電話', '地址'))
        else:
            which_table.setHorizontalHeaderLabels(('unique key', '奉獻編號', '姓名', '日期', '奉獻項目', '金額', '備註', '收據', '奉獻方式'))

        for row_number, row_data in enumerate(cursor):
            which_table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                if data == None:
                    data = ""
                    which_table.setItem(row_number,
                    column_number, QTableWidgetItem(str(data)))
                else:
                    item = QTableWidgetItem(str(data))
                    # https://blog.csdn.net/qq_41539778/article/details/119205439
                    item.setFlags(QtCore.Qt.ItemFlags(int("111111", 2))) # item.flags() ^ QtCore.Qt.ItemIsEditable
                    which_table.setItem(row_number, column_number, item)
        # tab 2
        if self.tabWidget.currentIndex():
            self.Analysis_Search_show.setText("")

            sumAmount = f"SUM(CASE WHEN `date` BETWEEN  '{datetime.strptime(str(date_from), '%Y-%m-%d').date()}' and '{datetime.strptime(str(date_end), '%Y-%m-%d').date()}' THEN amount ELSE 0 END) AS 'TOTAL'"
            
            if date_from == date_end:
                sum_up = f"SELECT `name`, {sumAmount}, `category` FROM offering GROUP BY `offeringID`"
                cursor = self.sql_operation(sum_up)
                self.Analysis_Search_show.append(f"從 {date_from} 到 {date_end}, 所有人當日奉獻收據")
                for row in cursor:
                    self.Analysis_Search_show.append(f"{row[0]}, {row[1]}, {row[2]} .等, {date_end}")

            # case all people
            elif ("category" not in sql) and ("offeringID" not in sql):

                sum_up = f"SELECT `name`, {sumAmount} FROM offering GROUP BY `offeringID`"
                cursor = self.sql_operation(sum_up)
                self.Analysis_Search_show.append(f"從 {date_from} 到 {date_end}, 所有人奉獻收據")
                for row in cursor:
                    self.Analysis_Search_show.append(f"{row[0]}, {row[1]}, 月定(什一)奉獻收入. 等, 自{date_from} 至 {date_end}")
                
            # case one person
            elif "category" not in sql:
                sum_up = f"SELECT `name`, {sumAmount} FROM offering WHERE offeringID = '{str(person)}'"
                cursor = self.sql_operation(sum_up)
                self.Analysis_Search_show.append(f"從 {date_from} 到 {date_end}, 個人奉獻收據")
                for row in cursor:
                    self.Analysis_Search_show.append(f"{row[0]}, {row[1]}, 月定(什一)奉獻收入. 等, 自{date_from} 至 {date_end}")
            # case category
            elif "offeringID" not in sql:
                sum_up = f"SELECT `category`, {sumAmount} FROM offering WHERE (category LIKE '%{str(offering_category)}%' OR note LIKE '%{str(offering_category)}%')"
                cursor = self.sql_operation(sum_up)
                self.Analysis_Search_show.append(f"從 {date_from} 到 {date_end}, 項目奉獻收據")
                for row in cursor:
                    self.Analysis_Search_show.append(f"{row[0]}, {row[1]}元, 自{date_from} 至 {date_end}")
            else:
                sum_up = f"SELECT `name`, `category`, {sumAmount} FROM offering WHERE (category LIKE '%{str(offering_category)}%' OR note LIKE '%{str(offering_category)}%') AND (offeringID = '{str(person)}')"
                cursor = self.sql_operation(sum_up)
                self.Analysis_Search_show.append(f"從 {date_from} 到 {date_end}, 個人項目奉獻收據")
                for row in cursor:
                    self.Analysis_Search_show.append(f"{row[0]}, {row[1]}, {row[2]}, 自{date_from} 至 {date_end}")


    
    def Search_table_update_onchange(self, row, col):
        # https://zhuanlan.zhihu.com/p/58619107
        if self.Search_table.currentItem():

            self.con = sqlite3.connect('database.db')
            self.cursorObj = self.con.cursor()
            cursor = self.cursorObj.execute(f"PRAGMA table_info({self.Search_table_type})") 
            header = [row[1] for row in cursor]
            self.con.commit()
            cursor = self.cursorObj.execute(f"UPDATE {self.Search_table_type} SET {header[col]} = '{self.Search_table.currentItem().text()}' WHERE id = '{self.Search_table.item(row,0).text()}'").fetchall()
            self.con.commit()
    
    def Search_table_delete_onchange(self):
        cur_row = self.Search_table.currentRow()
        # if row is selected
        if cur_row != -1:
            # reply = QMessageBox.question(self, 'warning', '確認刪除此筆資料?(刪除不可復原)',
            #     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            reply = QMessageBox(self)
            reply.setStyleSheet("QLabel{""min-width: 400px;""min-height: 120px;" "font-size: 20px" "}")
            reply.setText('確認刪除此筆資料? (刪除不可復原)')
            y = reply.addButton('yes',3)   
            n = reply.addButton('no',3)  
    
            reply.setDefaultButton(n)       
            res = reply.exec()

            # if reply == QMessageBox.Yes:
            if not res:
                query = f"DELETE FROM {self.Search_table_type} WHERE id = '{self.Search_table.item(cur_row,0).text()}'"
                cursor = self.sql_operation(query)

                # update table
                self.Search_pushButton_onchange(self.Search_offeringID, \
                                                self.Search_table_type, \
                                                "", \
                                                datetime.strptime(self.Search_date_from.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date(), \
                                                datetime.strptime(self.Search_date_end.date().toString("yyyy-MM-dd"), '%Y-%m-%d').date() )
        else:
            pass
            
    '''
    WeeklyReport
    '''

    def WeeklyReport_date_onchange(self):
        offering_category = {'什一奉獻':(self.WeeklyReport_tenth_ID_show, self.WeeklyReport_tenth_amount_show),
                             '主日奉獻':(self.WeeklyReport_sonday_ID_show, self.WeeklyReport_sonday_amount_show), 
                             '感恩奉獻':(self.WeeklyReport_thankful_ID_show, self.WeeklyReport_thankful_amount_show), 
                             '修繕奉獻':(self.WeeklyReport_repair_ID_show, self.WeeklyReport_repair_amount_show), 
                             '初熟奉獻':(self.WeeklyReport_firstfruit_ID_show, self.WeeklyReport_firstfruit_amount_show), 
                             '慈惠奉獻':(self.WeeklyReport_charity_ID_show, self.WeeklyReport_charity_amount_show), 
                             '宣教奉獻':(self.WeeklyReport_evangelist_ID_show, self.WeeklyReport_evangelist_amount_show), 
                             '搖籃奉獻':(self.WeeklyReport_cradle_ID_show, self.WeeklyReport_cradle_amount_show), 
                             '其他奉獻':(self.WeeklyReport_other_ID_show, self.WeeklyReport_other_amount_show), 
                             '個人奉獻':(self.WeeklyReport_person_ID_show, self.WeeklyReport_person_amount_show)}
        
        sumAmount = f"SUM(CASE WHEN `date` BETWEEN  '{datetime.strptime(self.WeeklyReport_date_from.date().toString('yyyy-MM-dd'), '%Y-%m-%d').date()}' and '{datetime.strptime(self.WeeklyReport_date_end.date().toString('yyyy-MM-dd'), '%Y-%m-%d').date()}' THEN amount ELSE 0 END) AS 'TOTAL' "
        total_sum = 0
        try:
            for category, (ID_show, amount_show)  in offering_category.items():
                query = f"SELECT `offeringID`, {sumAmount} FROM offering WHERE (category = '{str(category)}') GROUP BY `offeringID`"
                cursor = self.sql_operation(query)
                sum_up = 0
                id_show_str = ""
                ID_show.setText("")
                amount_show.setText("")

                for row in cursor:
                    if int(row[1]) > 0:
                        # ID_show.append(f"{row[0]}")
                        id_show_str += f"{row[0]},"
                        sum_up += int(row[1])

                amount_show.append(f"{sum_up}")
                ID_show.append(f"{id_show_str[:-1]}")
                total_sum += sum_up

            self.WeeklyReport_total.setText(f"{total_sum}")
        except:
            pass

    '''
    Analysis_Search
    '''
    def Analysis_Search_ID_Name_onchange(self, name, id):
        if name and id:
            try:
                self.con = sqlite3.connect('database.db')
                self.cursorObj = self.con.cursor()
                cursor = self.cursorObj.execute(f"SELECT name, offeringID FROM user WHERE  name LIKE '%{str(name)}%' OR offeringID LIKE '%{str(id)}%'")
                res = [f"姓名: {name}, 編號: {offeringID}" for name, offeringID in cursor]

                self.Analysis_ID_Name_list.clear()
                self.Analysis_ID_Name_list.addItems(res)

                self.con.commit()
            except:
                pass   
        else:
            self.Analysis_ID_Name_list.clear()
            self.Analysis_name, self.Analysis_offeringID = "", ""

    def Analysis_ID_Name_list_onchange(self):
        curr = np.char.split(self.Analysis_ID_Name_list.currentItem().text(), ' ').tolist()
        self.Analysis_name, self.Analysis_offeringID = curr[1], curr[3]

    def Analysis_Search_dataset_download_onchange(self):

        try:
            self.con = sqlite3.connect('database.db')
            self.cursorObj = self.con.cursor()
            cursor = self.cursorObj.execute("SELECT name FROM sqlite_master WHERE type ='table' AND name NOT LIKE 'sqlite_%'")
            filename = f"dataset_to_excel_{datetime.today().date()}.xlsx"
            writer= pd.ExcelWriter(filename, engine='xlsxwriter')
            for table_name in cursor:
                df = pd.read_sql(f"SELECT * FROM {table_name[0]}", self.con)
                df.to_excel(writer, sheet_name=f"{table_name[0]}", index=False)
            writer.close()
        except:
            pass

    def Analysis_Search_show_download_onchange(self):
        try:
            if self.Analysis_Search_show.toPlainText():
                lst = np.char.split(self.Analysis_Search_show.toPlainText(), '\n').tolist()
                sheetname = f"{lst[0].split(',')[1]}"
                data = [np.char.split(item, ',').tolist() for item in lst]
                df = pd.DataFrame(data)
                filename = f"browser_to_excel_{datetime.today().date()}.xlsx"
                df.to_excel(filename, sheet_name=sheetname, index=False)
        except:
            pass

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

    # paths = ['database.db']
    # fs_watcher = QtCore.QFileSystemWatcher(paths)
    # fs_watcher.fileChanged.connect(window.file_changed)

    window.show()
    sys.exit(app.exec_())
