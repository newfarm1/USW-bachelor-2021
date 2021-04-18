import os, threading, sys
from multiprocessing import Process
from web.functions import *
from web.web import app
from web.sql import table_check, Hashes


hashes = [
    {'hash_mode': 0, 'hash_name': 'MD5'},
    {'hash_mode': 10, 'hash_name': 'md5($pass.$salt)'},
    {'hash_mode': 20, 'hash_name': 'md5($salt.$pass)'},
    {'hash_mode': 30, 'hash_name': 'md5(utf16le($pass).$salt)'},
    {'hash_mode': 40, 'hash_name': 'md5($salt.utf16le($pass))'},
    {'hash_mode': 1400, 'hash_name': 'SHA 256'},
    {'hash_mode': 1700, 'hash_name': 'SHA 512'},
]


def test_menu():
 
    print("press 1 to add to basic MD5 to database for test purposes")
    print("press 2 to quit")
    task = int(input())

    if task == 1:
        for i in hashes:
            Hashes.ingest(i['hash_mode'], i['hash_name'])
        test_menu()

        print("goofball")
        test_menu()





if __name__ == "__main__":
    print("Starting server")
    table_check()

    thread1 = threading.Thread(target=test_menu)
    thread1.start()
    socktprocess = Process(target=Sock.start_sock)
    socktprocess.start()
    queueprocess = Process(target=next_dectypt_queue)
    queueprocess.start()
    app.run()
    


