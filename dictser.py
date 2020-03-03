from socket import *
import os
import time
import signal
import pymysql
import sys

DICT_TXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST,PORT)


def main():
	
	db = pymysql.connect('localhost','root','a123456','dict')

	s = socket()
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s.bind(ADDR)
	s.listen(5)

	#忽略子進程信號
	signal.signal(signal.SIGCHLD,signal.SIG_IGN)

	while True:
		try:
			c,addr = s.accept()
			print("connect from",addr)
		except KeyboardInterrupt:
			s.close()
			sys.exit("服務端退出")
		except Exception as e:
			print(e)
			continue

		pid = os.fork()
		if pid == 0:
			s.close()
			do_child(c,db)
			sys.exit(0)
		else:
			c.close()
			continue


def do_child(c,db):
	while True:
		data = c.recv(128).decode()
		print(c.getpeername(),':',data)
		if (not data) or data[0] == 'E':
			
			c.close()
			#子進程退出
			sys.exit(0)

		elif data[0] == 'R':
			do_register(c,db,data)
		elif data[0] == 'L':
			do_login(c,db,data)
		elif data[0] == 'Q':
			do_query(c,db,data)
		elif data[0] == 'H':
			do_hist(c,db,data)




def do_login(c,db,data):
	print('登入操作')
	l = data.split(' ')
	name = l[1]
	passwd = l[2]
	
	cursor = db.cursor()

	sql = "select * from user where name='%s' and passwd='%s'"%(name,passwd)
	cursor.execute(sql)
	r = cursor.fetchone()

	if r == None:
		c.send(b'fall')
	else:
		print("%s登入成功"%name)
		c.send(b'ok')


def do_register(c,db,data):
	print('註冊操作')
	l = data.split(' ')
	name = l[1]
	passwd = l[2]
	cursor = db.cursor()
	print(l[1],l[2])

	sql = "select * from user where name='%s'"%name
	cursor.execute(sql)
	r = cursor.fetchone()

	if r != None:
		c.send(b' ')
		return

	sql = "insert into user (name,passwd) values ('%s','%s')"%(name,passwd)
	try:
		cursor.execute(sql)
		db.commit()
		c.send(b'ok')
	except:
		db.rollback()
		c.send(b'fall')
	else:
		print("%s註冊成功"%name)	

def do_query(c,db,data):
	print('找找')
	l = data.split(' ')
	name = l[1]
	word = l[2]
	cursor = db.cursor()

	def insert_history():
		tm = time.ctime()
		sql = "insert into hist (name,word,time) values('%s','%s','%s')"%(name,word,tm)
		try:
			cursor.execute(sql)
			db.commit()
		except:
			db.rollback()

	try:
		f = open(DICT_TXT)
	except:
		c.send(b'fall')
		return

	for line in f:
		tmp = line.split(' ')[0]
		if tmp > word:
			c.send(b'fall')
			f.close()
			return
		elif tmp == word:
			c.send(b'ok')
			time.sleep(0.1)
			c.send(line.encode())
			f.close()
			insert_history()
			return

	c.send(b'fall')

def do_hist(c,db,data):
	print("操作歷史紀錄")
	l = data.split(' ')
	name = l[1]

	cursor = db.cursor()
	
	sql = 'select * from hist where name ="%s"'%name
	cursor.execute(sql)
	r = cursor.fetchall()
	if not r:
		c.send(b'fall')
		return
	else:
		c.send(b'ok')
		for i in r:
			time.sleep(0.1)
			msg = "%s   %s   %s"%(i[1],i[2],i[3])
			c.send(msg.encode())
		time.sleep(0.1)
		c.send(b'##')




if __name__ == '__main__':
	main()