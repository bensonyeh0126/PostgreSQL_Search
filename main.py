# 固定碼(738)+產品別 + 流水碼 + 下拉選擇(SAS/方向1/方向2) + 流水號:00000-99999 - 客戶別

# Written by Benson Yeh, 1/10/2022,

import sys
import psycopg2

import os
import datetime
from ui import Ui_MainWindow
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore
from PyQt5.QtCore import QStringListModel ,Qt
from PyQt5.QtGui import QPixmap, QStandardItemModel, QFont, QStandardItem, QIcon
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QPushButton, QVBoxLayout, QLabel, QToolBar, QStatusBar, \
    QHBoxLayout, QGroupBox, QComboBox, QCheckBox, QListView, QTabWidget, QPlainTextEdit, QProgressBar, QFileDialog, \
    QMessageBox, \
    QAction ,QListWidget,QTableWidgetItem

class Controller(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(QMainWindow, self).__init__(parent)
        self.setupUi(self)
       
        self.create_comboBox()
        self.pushButton_2.clicked.connect(self.insert_to_sql)
        self.create_btn.clicked.connect(self.create_new_item)
        self.display_five_data()
        

        self.show()
    
    def connect_db(self):
        '''
        連線資料庫
        '''
        self.conn = psycopg2.connect(database = "Hight_speed_db", user = "postgres", password = "a@00", 
                                     host =  "127.0.0.1", port = "5432")
        # # 設置自動提交
        self.conn.autocommit = True
        # 使用cursor()方法創建游標對象
        self.cursor = self.conn.cursor()

    def close_db(self) :
        '''
        關閉資料庫
        '''
        self.cursor.close()
        self.conn.close()


    def create_comboBox(self):
        '''
        產生介面上所有的combobox
        '''
        self.product.clear()
        self.SAS.clear()
        self.direction_1.clear()
        self.direction_2.clear()
        self.customer.clear()
        ## 生產
        # 產品別
        self.connect_db()
        element_product = []
        self.cursor.execute ( "SELECT * FROM product")
        ans = self.cursor. fetchall ()
        for i in range(0,len(ans)):
            for j in range(0,1):
               element_product.append(str(ans[i][j]))
        self.product.addItems(element_product)  

        # SAS
        element_SAS = []
        self.cursor.execute ( "SELECT * FROM sas")
        ans = self.cursor. fetchall ()
        for i in range(0,len(ans)):
            for j in range(0,1):
               element_SAS.append(str(ans[i][j]))       
        self.SAS.addItems(element_SAS)  

        # 方向
        element_direction = []
        self.cursor.execute ( "SELECT * FROM direction")
        ans = self.cursor. fetchall ()
        for i in range(0,len(ans)):
            for j in range(0,1):
               element_direction.append(str(ans[i][j]))
        self.direction_1.addItems(element_direction)  
        self.direction_2.addItems(element_direction)  
        # 客戶別

        element_customer = []
        self.cursor.execute ( "SELECT * FROM customer ORDER BY item ASC")
        ans = self.cursor. fetchall ()
        for i in range(0,len(ans)):
            for j in range(0,1):
               element_customer.append(str(ans[i][j]))       
        self.customer.addItems(element_customer) 


        ##新增類別 (固定)
        items = ['產品別','SAS','方向','客戶別']
        self.combobox_create.addItems(items)
        self.close_db()

    def insert_to_sql(self):
        '''
        接收介面資料並用子程式 ask_to_insert 新增至資料庫
        '''
        table = 'items'
        product = self.product.currentText()
        SAS = self.SAS.currentText()
        direction_1 = self.direction_1.currentText()
        direction_2 = self.direction_2.currentText()
        customer = self.customer.currentText()
        remark = self.remark.text()
        product = product.split('_')[0]
        customer = customer.split('_')[0]
        self.ask_to_insert(table, product, SAS, direction_1, direction_2, remark, customer)
        print('finish')  

        

         
    def ask_to_insert(self,table, product, SAS, direction_1, direction_2, remark, customer):
        '''
        判斷有無與資料庫重複
        '''
        try:
            self.connect_db()
            # print(table, product, SAS, direction_1, direction_2,customer)
            self.cursor.execute("SELECT * FROM {} WHERE item_id = '{}' and SAS  = '{}' and direction1 = '{}' and direction2 = '{}' and customer = '{}' ".format(table, product, SAS, direction_1, direction_2,customer))
            ans = self.cursor. fetchone()
            print('第一次查詢:{}' .format(ans))
            self.cursor.execute("SELECT * FROM {} WHERE item_id = '{}' and SAS  = '{}' and direction1 = '{}' and direction2 = '{}' and customer = '{}' ".format(table, product, SAS, direction_2, direction_1,customer))
            ans1 = self.cursor. fetchone()
            print('第二次查詢:{}'.format(ans1))
            self.close_db()

            if ans or ans1 != None:
                # 判斷有無使用過
                if ans == None and ans1 != None:
                    self.status_2.setText('已使用過: {}-{}-{}'.format(ans1[0],ans1[1],ans1[5]))
                elif ans1 == None and ans != None:
                    self.status_2.setText('已使用過: {}-{}-{}'.format(ans[0],ans[1],ans[5]))
                else:
                    self.status_2.setText('已使用過: {}-{}-{}'.format(ans[0],ans[1],ans[5]))    
            else:
                self.connect_db()

                product = product.split('_')[0]
                customer = customer.split('_')[0]
                self.cursor.execute("select  COUNT(*) from  {} WHERE item_id = '{}'".format(table, product))
                result = self.cursor. fetchone()
                print('已新增流水碼:%02d'%result[0])
                self.serial_code.setText('%02d'%result[0])
                serial_code = '%02d'%result[0]
                datetime_dt = datetime.datetime.today()
                datetime_str = datetime_dt.strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute("INSERT INTO {} (item_id,serial_code, sas,direction1,direction2,customer, remark, create_time) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')".format(table, product, serial_code, SAS, direction_1, direction_2,customer,remark,datetime_str)) 
                self.status_2.setText('已新增:{}-{}-{}-{}-{}-{}'.format( product, serial_code, SAS, direction_1, direction_2,customer)) 
                self.close_db() 

                # 新增完更新顯示
                self.display_five_data()

        
        except psycopg2.Error as e:
            print(e)


    def display_five_data(self):
        '''
        顯示五個最近新增
        '''
        self.connect_db()
        self.cursor.execute("SELECT * FROM items ORDER BY create_time DESC ")
        result = self.cursor. fetchmany(10)
        self.close_db() 
        self.tableWidget.clear()
                
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setHorizontalHeaderLabels(['類別','流水號','SAS','方向1','方向2','客戶別','備註','產生時間'])
        i=0
        for row in result:
            
            self.tableWidget.setItem(i, 0, QTableWidgetItem(row[0])) 
            self.tableWidget.setItem(i, 1, QTableWidgetItem(row[1]))  
            self.tableWidget.setItem(i, 2, QTableWidgetItem(row[2])) 
            self.tableWidget.setItem(i, 3, QTableWidgetItem(row[3]))  
            self.tableWidget.setItem(i, 4, QTableWidgetItem(row[4])) 
            self.tableWidget.setItem(i, 5, QTableWidgetItem(row[5]))  
            self.tableWidget.setItem(i, 6, QTableWidgetItem(row[6])) 
            self.tableWidget.setItem(i, 7, QTableWidgetItem(row[7])) 
                # print(i)
            i+=1    

            print(row)

    def create_new_item(self):
        ''' 
        新增類別 子程式 insert_item_to_sql
        '''
        result = self.combobox_create.currentText()
        sql_input = self.create_input.text()
        items = ['產品別','SAS','方向','客戶別']
        if result == items[0]:
            table = 'product'
        elif result == items[1]:
            table = 'sas'    
        elif result == items[2]:
            table = 'direction' 

        elif result == items[3]:   
            table = 'customer' 

        if sql_input == '':
            self.status_3.setText('輸入欄位為空')

        else:
            self.insert_item_to_sql(table,sql_input)       
    def insert_item_to_sql(self, table, sql_input):
        self.connect_db()
        self.cursor.execute("SELECT * FROM {} WHERE item = '{}' ".format(table, sql_input))
        ans = self.cursor. fetchone() 
        print(ans)
        if ans == None:
            self.cursor.execute("INSERT INTO {} (item) VALUES ('{}')".format(table, sql_input)) 
            print('已新增{}:{}'.format(table,sql_input))
            self.status_3.setText('已新增{}:{}'.format(table,sql_input))
            self.create_comboBox()
        else:
            print('失敗')
            self.status_3.setText('失敗')
            
        self.close_db() 




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Controller()
    sys.exit(app.exec_())
    
