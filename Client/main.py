import socket
import os
import json
import GPUtil
from time import sleep

HEADER = 16
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE =  "dc"




SERVER = '10.0.0.34'
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

class Sock:

    def __init__(self):
        self.HEADER = HEADER
        self.FORMAT = FORMAT
        self.DISCONNECT_MESSAGE = DISCONNECT_MESSAGE
        self.COMPUTER_INFORMATION = COMPUTER_INFORMATION


    def send(data):

        data = json.dumps(data).encode(FORMAT)
        data_length = len(data)
        print(data_length)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(data)
        print("data sent")


    def recv():

        connected = True
        while connected:
            data_length = client.recv(HEADER).decode(FORMAT)

            if data_length:
                print('data recieved')
                data_length = int(data_length)
                data = json.loads(client.recv(data_length))
                task = data["header"]
                print(task)
                if task == DISCONNECT_MESSAGE:
                    send = pack(DISCONNECT_MESSAGE, "", "", "", "")
                    Sock.send(send)
                    connected = False

                elif task == "noq":
                    sleep(10)
                    queue = pack("queue", "", "", "","")
                    Sock.send(queue)

                elif task == 'decrypt':
                    sleep(1)
                    decrypt(data)
                    try:
                        with open("pw.txt") as f:
                            pw = f.read()
                        pw = pw.split(':')
                        decrypted = pack("decrypted", data["ident"], data['algo'], pw[0], pw[1])
                        print(decrypted)
                        Sock.send(decrypted)
                        data = ""
                    except FileNotFoundError:

                        queue = pack("queue", data['ident'], "", "","")
                        Sock.send(queue)




def decrypt(data):
    if data["attack_type"] == 'dict':
        with open('task.txt', 'w') as w: 
           for d in data['job']:
                w.write(f'{d}\n')
                print(d)

        amode = '0'
        job = 'task.txt'

    elif data["attack_type"] == 'mask':
        print(data)
        amode = '3'
        job = data["job"]
    attak = f'hashcat.exe -m {data["algo"]} -a {amode} {data["hash_code"]} {job} -o pw.txt'
    print(attak)
    read = os.popen(attak)
    for line in read:
        print(read.readline())

def pack(header, ident, comp_info, hash_code, password):

    return {
        'header': header,
        'ident': ident,
        'attack_type' :comp_info,
        'hash_code': hash_code,
        'password': password
                }

def gpu_name():
    gpus = GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        gpu_name = gpu.name
        list_gpus.append(gpu_name)
    return list_gpus

print(gpu_name())
gpus = gpu_name()

start = pack("connect", gpus, "", "", "")

print(start)

Sock.send(start)
Sock.recv()


