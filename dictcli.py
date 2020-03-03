from socket import *
import sys



def main():
	if len(sys.argv) < 3:
		print('argv is error')
		return
	HOST = sys.argv[1]
	PORT = int(sys.argv[2])
	s = socket()
	try:
		s.connect((HOST,PORT))
	except Exception as e:
		print(e)
		return

	while True:
		print('''
			=================================
			 -----1.註冊  2.登入  3.退出-----
			=================================
			''')
		try:
			cmd = int(input('輸入選項'))
		except Exception as e:
			print('error')
			continue

		if cmd not in [1,2,3]:
			print('error')
			sys.stdin.flush()#清除標準輸入
		elif cmd == 1:
			name = do_register(s)
			if name:
				print('ok')
				login(s,name)
			else:
				print('註冊失敗')
		elif cmd == 2:
			name = do_login(s)
			if name:
				print('登入成功')
				
				login(s,name)
			else:
				print('從新輸入')
		elif cmd == 3:
			s.send(b'E')
			sys.exit('E X I T')



def do_register(s):
	while True:
		name = input('User:')
		passwd = input('password:')
		password = input('enter password again:')

		if passwd != password:
			print('error')
			continue
		if (' ' in name) or (' ' in passwd):
			print('error')
			continue

		msg = 'R {} {}'.format(name,passwd)

		s.send(msg.encode())

		data = s.recv(128).decode()

		if data == 'ok':
			return name
		else:
			return



def do_login(s):
	name = input('user:')
	passwd = input('password:')
	msg = "L {} {}".format(name,passwd)
	
	s.send(msg.encode())

	data = s.recv(128).decode()

	if data == 'ok':
		return name
	else:
		return



def login(s,name):
	while True:
		print('''
		1.查詞 2.歷史紀錄 3.退出
		''')
		try:
			cmd = int(input('輸入選項:'))
		except Exception as e:
			print('enter again')
			continue
		if cmd not in [1,2,3]:
			print('請輸入正確選項')
			
			sys.stdin.flush()
			
			continue

		elif cmd == 1:
			
			do_query(s,name)

		elif cmd == 2:
			
			do_hist(s,name)

		elif cmd == 3:
			return

def do_query(s,name):
	while True:
		word = input("請輸入單詞:")
		if word == '##':
			break
		msg = 'Q {} {}'.format(name,word)

		s.send(msg.encode())

		data = s.recv(128).decode()

		if data == 'ok':
			data = s.recv(2048).decode()
			print(data)
		else:
			print("找無")

def do_hist(s,name):
	msg = 'H {}'.format(name)
	s.send(msg.encode())
	data = s.recv(128).decode()
	if data == 'ok':
		while True:
			data = s.recv(1024).decode()
			if data == '##':
				break
			print(data)
	else:
		print('no hits')

if __name__ == '__main__':
	main()