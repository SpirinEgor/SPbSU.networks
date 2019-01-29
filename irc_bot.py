import socket
import threading
import time
import urllib3
import re
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
        self.http = urllib3.PoolManager()
        open(self.log_file_, 'w').close()

    def send_message(self, message, privmsg=True):
        if privmsg:
            message = 'PRIVMSG {} :{}\r\n'.format(self.channel_, message)
            print('<{}>: {}'.format(self.nickname_, message))
        self.irc.send(message.encode('utf-8'))


    def connect(self):
        self.irc.connect((self.server_, self.port_))
        self.send_message('USER {} * * : !\n'.format(self.nickname_), False)
        self.send_message('NICK {}\n'.format(self.nickname_), False)
        self.send_message('JOIN {}\n'.format(self.channel_), False)

        for msg in ['use this commands:', 'do some magic', 'bye bye']:
            self.send_message(msg)

    def get_message(self):
        result = self.irc.recv(1024).decode('utf-8')
        return result

    def listen(self):
        threads = []
        while True:
            recieve = self.get_message()
            with open(self.log_file_, 'a') as log:
                log.write(recieve + '\n')
            if 'PING' in recieve:
                response = recieve.split(' ')[1].replace('\n', '').replace('\r', '')
                print('PONG {}'.format(response))
                self.send_message('PONG {}\n'.format(response), False)
            else:
                if 'PRIVMSG' in recieve and 'VERSION' not in recieve:
                    author, message = self.parse_recieve_privmsg(recieve)
                    print('<{}>: {}'.format(author, message))
                    if self.nickname_ in message and self.MAGIC_MESSAGE in message:
                        thread = threading.Thread(target=self.do_some_quote)
                        thread.start()
                        threads.append(thread)                        
                    elif self.nickname_ in message and self.EXIT_MESSAGE in message:
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


    def do_some_quote(self):
        r = self.http.request('GET', 'http://finewords.ru/sluchajnaya')
        quote = r.data.decode('utf-8').replace('<p>', '').replace('</p>', '').replace('&quot', '"')
        quote = re.sub(r'<br( )*/>', '', quote)
        for q in quote.split('\n'):
            self.send_message(q)
