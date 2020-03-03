import re
import pymysql
import sys
import socket


f = open("dict.txt")

db = pymysql.connect('localhost','root','a123456','dict')

cursor = db.cursor()

for i in f:
	l = re.split(r'\s+',i)
	word = l[0]
	interpret = ' '.join(l[1:])
	sql = "insert into words (word,interpret) values('%s','%s')"%(word,interpret)

	try:
		cursor.execute(sql)
		db.commit()
	except:
		db.rollback()
f.close()