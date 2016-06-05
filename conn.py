# -*- coding: utf-8 -*-
import sys
from pymysql import connections
from datetime import datetime

time = datetime.now()

try:
    conn = connections.Connection(
                                  host='139.129.95.148', 
                                  port=3306,  
                                  user='root', 
                                  password='123456', 
                                  db='test',
                                  charset='utf8')
except Exception as e:
    print(e)
    sys.exit()

cursor = conn.cursor()
# 插入
def insert(number):
    sql_insert = """insert into \
                    everyone1606(id, day_id, spend, mark, form, other) \
                    values(%s, %s, %s, '%s', '%s', '%s')""" % number  # tuple(number)
    cursor.execute(sql_insert)
    conn.commit()  # 保存

# 删除
def delete(number):
    sql_delete = "delete from everyone1606 where id=%s" % number
    cursor.execute(sql_delete)
    conn.commit()

# 读取1
def read():
    sql_read = "select * from everyone1606"
    cursor.execute(sql_read)
    rows = cursor.fetchall()
    newrows = []
    for row in rows:
        for ra in row:
            newrows.append(ra)
    return newrows, cursor.rowcount

# 读取2
def read2():
    sql_read = "select * from summary1606"
    cursor.execute(sql_read)
    rows = cursor.fetchall()
    newrows = []
    for row in rows:
        for ra in row:
            newrows.append(ra)
    return newrows, cursor.rowcount

# 每日总结
def count(day, means, balance1, balance2):
    sql_read = """ select * from everyone1606 \
                  where day_id='%s' """ % day
    cursor.execute(sql_read)
    rows = cursor.fetchall()

    cash,card = 0, 0
    for row in rows:
        if row[1] == day:
            if row[5] == 'False':
                if row[4] == '现金':
                    cash = cash + row[2]
                if row[4] == '借记卡':
                    card = card + row[2]
            elif row[5] == 'None':
                balance2 = balance2 + row[2]
            elif row[5] == 'Draw':
                balance1 = balance1 - row[2]
                balance2 = balance2 + row[2]

    if day == 1:
        mean = cash + card
    elif day > 1:
        means = means*(day-1) + cash + card
        mean = round(means / day, 2)

    balance1 = round(balance1 + cash, 2)
    balance2 = round(balance2 + card, 2)
    return day, cash, card, mean, balance1, balance2

# 总结导入mysql数据库
def insert2(number):
    try:
        sql_insert = """INSERT INTO \
                        summary1606(id, cash, card, mean, balance1, balance2) \
                        values(%s, %s, %s, %s, %s, %s)""" % number
        cursor.execute(sql_insert)
    except:
        sql_update = """UPDATE summary1606 SET cash='%s',card='%s', \
                        mean='%s',balance1='%s',balance2='%s' where \
                        id='%s'""" % (number[1],number[2],number[3],number[4],number[5],number[0])
        cursor.execute(sql_update)
    conn.commit()  # 保存


def sd():
    balance1 = 140
    balance2 = 227.53
    mean = 0
    for day in range(1, time.day+1):
        summarys = count(day, mean, balance1, balance2)
        insert2(summarys)

        balance1 = summarys[4]
        balance2 = summarys[5]
        mean = summarys[3]


# sd()

# cursor.close()
# conn.close()

# conn.commit()  # 提交事务 保存
# conn.rollback()  #回滚事务