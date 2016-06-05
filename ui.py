# -*- coding: utf-8 -*-
from PyQt4.QtGui import *
from PyQt4.QtCore import *
import sys
import random
from datetime import datetime
import conn

time = datetime.now()

class StockDialog(QDialog):
    def __init__(self, parent=None):
        super(StockDialog, self).__init__(parent)
        self.setWindowTitle(self.tr("My Excel"))
        self.resize(770, 430)

        listWidget = QListWidget()
        listWidget.insertItem(0, self.tr("账目明细"))
        listWidget.insertItem(1, self.tr("每月总结"))

        stack = QStackedWidget()
        stack.setFrameStyle(QFrame.Panel | QFrame.Raised) # 边框样式
        everyone = Everyone()
        stack.addWidget(everyone)
        summary = Summary()
        stack.addWidget(summary)

        excel = QPushButton(self.tr("导出excel"))
        amend = QPushButton(self.tr("更新"))  
        close = QPushButton(self.tr("关闭"))
        buttonLayout=QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(excel)
        buttonLayout.addWidget(amend)
        buttonLayout.addWidget(close)

        layout = QVBoxLayout()
        layout.addWidget(stack)
        layout.addLayout(buttonLayout)


        mainLayout = QHBoxLayout(self)
        mainLayout.setMargin(10)
        mainLayout.setSpacing(6)
        mainLayout.addWidget(listWidget)
        mainLayout.addLayout(layout)
        mainLayout.setStretchFactor(listWidget, 1)
        mainLayout.setStretchFactor(layout, 7)


        self.connect(close, SIGNAL("clicked()"), self, SLOT("close()"))
        self.connect(listWidget, SIGNAL("currentRowChanged(int)"), \
                     stack, SLOT("setCurrentIndex(int)"))


class Everyone(QWidget):
    def __init__(self, parent=None):
        super(Everyone, self).__init__(parent)

        # 控件Label
        label1 = QLabel(self.tr("日期"))
        label2 = QLabel(self.tr("消费"))
        label3 = QLabel(self.tr("备注"))
        label4 = QLabel(self.tr("类型"))
        label5 = QLabel(self.tr("其他"))

        # 控件输入框
        self.daybox = QLineEdit(self.tr("%s") % time.day)
        self.spendbox = QLineEdit(self.tr("-100"))
        self.markbox = QLineEdit()
        self.formbox = QComboBox()
        self.formbox.insertItem(0, self.tr("现金"))
        self.formbox.insertItem(1, self.tr("借记卡"))
        self.otherbox = QComboBox()
        self.otherbox.insertItem(0, self.tr("False"))
        self.otherbox.insertItem(1, self.tr("True"))
        self.otherbox.insertItem(2, self.tr("None"))
        self.otherbox.insertItem(3, self.tr("Draw"))
        amend = QPushButton(self.tr("添加+同步"))
        close = QPushButton(self.tr("删除"))

        upLayout = QGridLayout()
        positions = [(i, j) for i in range(2) for j in range(6)]
        names = [label1, label2, label3, label4, label5, amend, \
                 self.daybox, self.spendbox, self.markbox, \
                 self.formbox, self.otherbox, close]
        for position, name in zip(positions, names):
            upLayout.addWidget(name, *position)

        # upLayout.addWidget(label1, 0, 0)
        # upLayout.addWidget(label2, 0, 1)
        # upLayout.addWidget(label3, 0, 2)
        # upLayout.addWidget(label4, 0, 3)
        # upLayout.addWidget(label5, 0, 4)
        # upLayout.addWidget(self.daybox, 1, 0)
        # upLayout.addWidget(self.spendbox, 1, 1)
        # upLayout.addWidget(self.markbox, 1, 2)
        # upLayout.addWidget(self.formbox, 1, 3)
        # upLayout.addWidget(self.otherbox, 1, 4)
        # upLayout.addWidget(amend, 0, 5)
        # upLayout.addWidget(close, 1, 5)


        # 表格
        self.rows, self.number = conn.read()  #读写表格，获得行数
        self.table = QTableWidget(self.number+2, 6)
        head = ['id', '日期', '消费', '备注', '类型', '其他']
        self.table.setHorizontalHeaderLabels(head)
        self.table.verticalHeader().setVisible(False)  # 关闭列标签
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows) # 整行选择


        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(15)
        mainLayout.setSpacing(10)
        mainLayout.addLayout(upLayout)
        mainLayout.addWidget(self.table)
        # mainLayout.setSizeConstraint(QLayout.SetFixedSize) # 固定大小

        # 第一次mysql读取表格
        self.tableupdate()

        
        self.connect(self.table, SIGNAL("itemClicked (QTableWidgetItem*)"), self.outSelect)
        self.connect(amend, SIGNAL("clicked()"), self.tableinsert)  # 添加
        self.connect(close, SIGNAL("clicked()"), self.tabledetele)  # 读取mysql

    # 随机颜色
    def randRGB1(self):
        return QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    # 读取mysql表格
    def tableupdate(self):
        self.rows, self.number = conn.read()
        
        positions = [(i, j) for i in range(self.number) for j in range(6)]
        a = 1
        cl = self.randRGB1()
        for position, row in zip(positions, self.rows):
            text = QTableWidgetItem('%s' % row)
            if position[1] == 1:
                if row == a:
                    text.setTextColor(cl)
                if row != a:
                    a = row
                    cl = self.randRGB1()
                    text.setTextColor(cl)
            self.table.setItem(position[0], position[1], text)


    # 鼠标选定的数据
    def outSelect(self, Item=None):
        if Item==None:
            return
        self.item = Item.text()
    # 删除
    def tabledetele(self):
        qtm=QMessageBox
        try:
            msg_box = qtm.question(self, "提示", "确定删除id='%s'的数据" % int(self.item), qtm.Yes,qtm.No)
            if msg_box == qtm.Yes:
                QTableWidget.clear(self.table) 
                conn.delete(self.item)
                self.tableupdate()
            else:   
                return
            msg_box.exec_()
        except:
            return
        
        

    # 添加&同步
    def tableinsert(self):
        raid = self.number
        day = self.daybox.text()
        spend = self.spendbox.text()
        mark = self.markbox.text()
        form = self.formbox.currentText()
        other = self.otherbox.currentText()

        #self.table.setItem(raid, 0, QTableWidgetItem('%s' % str(raid + 1)))
        #self.table.setItem(raid, 1, QTableWidgetItem('%s' % day))
        #self.table.setItem(raid, 2, QTableWidgetItem('%s' % spend))
        #self.table.setItem(raid, 3, QTableWidgetItem('%s' % mark))
        #self.table.setItem(raid, 4, QTableWidgetItem('%s' % form))
        #self.table.setItem(raid, 5, QTableWidgetItem('%s' % other))
        self.table.insertRow(raid+1)  # 插入行


        row = (str(raid+1),day , spend, mark, form, other)
        conn.insert(row)

        self.tableupdate()


class Summary(QWidget):
    def __init__(self, parent=None):
        super(Summary, self).__init__(parent)

        title = QLabel(self.tr("%s年%s月") % (time.year, time.month))

        self.rows, self.number = conn.read2()
        self.table2 = QTableWidget(self.number, 6)
        head = ['日期', '现金', '借记卡', '日均', '余额:现金', '余额:卡',]
        self.table2.setHorizontalHeaderLabels(head)
        self.table2.verticalHeader().setVisible(False)
        self.table2.setSelectionBehavior(QAbstractItemView.SelectRows) # 整行选择
        self.table2.setEditTriggers(QAbstractItemView.NoEditTriggers) # 禁止更改


        mainLayout = QVBoxLayout(self)
        mainLayout.setMargin(15)
        mainLayout.setSpacing(10)
        mainLayout.addWidget(title)
        mainLayout.addWidget(self.table2)


        self.tableread()

    def tableread(self):
        # self.rows, self.number = read2()
        positions = [(i, j) for i in range(self.number) for j in range(6)]

        for position, row in zip(positions, self.rows):

            text = QTableWidgetItem('%s' % row)
            if position[1] == 3:
                text.setTextColor(QColor(255, 0, 0))
            if position[1] == 4 or position[1] == 5:
                text.setTextColor(QColor(0, 0, 255))
            self.table2.setItem(position[0], position[1], text)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = StockDialog()
    demo.show()
    sys.exit(app.exec_())
