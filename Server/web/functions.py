import socket
import threading
import json
from itertools import product
from time import sleep
from .sql import *



HEADER = 16
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "dc"
RDY_MESSAGE = "!OK"
DONE_MESSAGE = "!DONE"
COMPUTER_INFORMATION = "vm"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)






class Sock:

    def send(conn, addr, data):
        print("in send")
        data = json.dumps(data).encode(FORMAT)
        data_length = len(data)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        conn.send(send_length)
        conn.send(data)
        print("data sent")


        
    def handle_client(conn, addr):

        print(f'New Connection, {addr} connected.')
        connected = True
        try:
            while connected:


                data_length = conn.recv(HEADER).decode(FORMAT)
                if data_length:
                    print('data recieved')
                    data_length = int(data_length)
                    data = json.loads(conn.recv(data_length).decode(FORMAT))
                    task = data["header"]
                    print(task)
                    if task == DISCONNECT_MESSAGE:
                        print("DCed")
                        connected = False
                    elif task == "connect":   
                        gpu = ", ".join(data['ident'])
                        print(data['ident'])
                        Machines.ingest(addr, gpu)
                        any_queue(conn, addr)

                    elif task == "queue":
                        if data["ident"]:
                            Ongoing_job.task_done(data["ident"])

                        any_queue(conn, addr)

                    elif task == "decrypted":
                        Decrypted.ingest(data['hash_code'], data['attack_type'], data['password'])
                        Ongoing_job.cleanup()
                        Decrypt_queue.done(data["ident"])
                        any_queue(conn, addr)


                    print(f"{addr} {data}")
        except ConnectionResetError:
            print("force DCed")
        
        conn.close()
        Ongoing_job.revert(addr)
        Machines.dc(addr)
        


    def start_sock():

        server.listen()
        print(f"Server is listening on {SERVER}")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=Sock.handle_client, args=(conn, addr))
            thread.start()
            print(f'[New active connection]')

def any_queue(conn, addr):
    print('queueueueueue')
    
    try:
        
        task = Ongoing_job.get_next()
        print(task.task_nr)
            
        Ongoing_job.working(task.task_nr, addr)

        if task.attack_type == 'dict':
            job = []
            with open(task.job) as t:
                line = t.readline()
                while line:
                    print(line)
                    job.append(line[:-2])
                    line = t.readline()

        elif task.attack_type == 'mask':
            job = task.job
        data = pack("decrypt", task.task_nr, task.attack_type, task.algo, task.hash_code, job)
        task = task.task_nr
    except AttributeError or InvalidRequestError:
        data = pack("noq", "", "", "", "", "")
        completed = Ongoing_job.full_queue()
        task = 0
        if not completed:
            Decrypt_queue.done()
        else:
            print(completed)
    Sock.send(conn, addr, data)
    Machines.update(addr, task)

def pack(header, ident, attack_type, algo, hash_code, job):
     return {
        'header': header,
        'ident': ident,
        'attack_type' :attack_type,
        'algo': algo,
        'hash_code': hash_code,
        'job' : job,
                }
   

        
def mask_generator(settings):
    
    start = int(settings.setting1)
    stop = int(settings.setting2)
    stop += 1
    print(start, stop)
    mask_options = ["?l", "?u", "?d", "?s"]
    masks = []
    for i in range(start, stop):
        masks.extend("".join(prod) for prod in product(mask_options, repeat=i))
        
    for i in masks:
        print(i)
        Ongoing_job.ingest("mask", settings.hash_code, i, settings.algo)



def decrypt_work_queue(data):
 
    if data["decrypt_type"] == 'brute':
        if data["costum-length"] == 'no':
            setting1 = 8
            setting2 = 10
        else:
            setting1 = data['start']
            setting2 = data['stop']
        print(data['algo'], data['hash_input'], data["decrypt_type"],
                                    0, str(setting1), str(setting2))
        Decrypt_queue.ingest(data['algo'], data['hash_input'],
                                    data["decrypt_type"], 0, str(setting1), str(setting2))
    elif data["decrypt_type"] == 'dict':
        if data["costum-length"] == 'no':
            setting1 = 10000
        else:
            setting1 = setting1 = data['start']
        print(data['algo'], data['hash_input'], data["decrypt_type"], 0, str(setting1),
                                                    str(f"{data['selected_dict']}.txt"))
        Decrypt_queue.ingest(data['algo'], data['hash_input'], data["decrypt_type"], 0,
                                    str(setting1), str(f"{data['selected_dict']}.txt"))

def next_dectypt_queue():

    sleep(10)
    while True:
        try:
            print("queue check")
            queue = Decrypt_queue.queue()
            print(queue.ongoing)
            if not queue:
                print("no queue")
                sleep(30)  
            elif queue.ongoing:
                ("ongoing queue")
                sleep(30)
            else:
                Decrypt_queue.ongoing_task(queue.task_nr)
                
                if queue.decrypt_type == 'brute':
                    mask_generator(queue)
                elif queue.decrypt_type == 'dict':
                    dict_splitter(queue)

        except AttributeError:
            sleep(30)

def dict_splitter(settings):
    length = int(settings.setting1)
    cosen_dict = settings.setting2
    with open(f'./libs/{cosen_dict}') as d:
        line = d.readline()
        cnt = 1
        number = 1
        while line:
            job = f"./dict jobs/{number}job.txt"
            with open(job, 'w') as wj:
                write = True
                while write:
                    print(f"Line {cnt}: {line.strip()}")
                    wj.write(line)
                    line = d.readline()
                    cnt += 1
                    if cnt == length:
                        cnt = 1
                        number +=1
                        wj.close
                        write = False
                        Ongoing_job.ingest("dict", settings.hash_code,job , settings.algo)
