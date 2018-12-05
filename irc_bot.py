import socket
import threading
import time
from os.path import exists, join
from random import randint

class IrcBot:

    MAGIC_MESSAGE = 'do some magic'
    EXIT_MESSAGE = 'bye bye'

    def __init__(self, server, port, channel, nickname, log_file):
        self.server_ = server
        self.port_ = port
        self.channel_ = channel
        self.nickname_ = nickname
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.log_file_ = log_file
        open(self.log_file_, 'w').close()

    def send_message(self, message, privmsg=True):
        if privmsg:
            message = 'PRIVMSG {} :{}\r\n'.format(self.channel_, message)
        self.irc.send(message.encode('utf-8'))

    def connect(self):
        self.irc.connect((self.server_, self.port_))
        self.send_message('USER {} * * : !\n'.format(self.nickname_), False)
        self.send_message('NICK {}\n'.format(self.nickname_), False)
        self.send_message('JOIN {}\n'.format(self.channel_), False)

    def get_message(self):
        result = self.irc.recv(1024).decode('utf-8')
        return result

    def listen(self):
        threads = []
        while True:
            recieve = self.get_message()
            if 'PING' in recieve:
                response = recieve.split(' ')[1]
                if response == '001':
                    self.send_message('JOIN {}\n'.format(self.channel_), False)
                else:
                    self.send_message('PONG {}\n'.format(recieve.split(' ')[1]), False)
            else:
                with open(self.log_file_, 'a') as log:
                    log.write(recieve + '\n')
                if 'PRIVMSG' in recieve and 'VERSION' not in recieve:
                    author, message = self.parse_recieve_privmsg(recieve)
                    print('<{}>: {}'.format(author, message))
                    if '{}: {}'.format(self.nickname_, self.MAGIC_MESSAGE) == message:
                        thread = threading.Thread(target=self.do_some_magic)
                        thread.start()
                        threads.append(thread)
                    if '{}: {}'.format(self.nickname_, self.EXIT_MESSAGE) == message:
                        self.send_message(self.EXIT_MESSAGE)
                        break
        for thread in threads:
            thread.join()

    
    def parse_recieve_privmsg(self, recieve):
        author = recieve.split('!')[0][1:]
        message = ':'.join(recieve.split(':')[2:])
        if '\r\n' == message[-2:]:
            message = message[:-2]
        return author, message
            
    def do_some_magic(self):
        num = randint(0, 10)
        with open(join('memes', '{}.txt'.format(num)), 'r') as meme_in:
            for line in meme_in:
                self.send_message(line)
                time.sleep(0.5) 