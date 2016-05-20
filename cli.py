from sys import stdin, stdout
from threading import Thread
from custom_types import PacketType
from select import select
from em import EM


class Application(Thread, EM):
    def __init__(self):
        Thread.__init__(self)
        EM.__init__(self)

        self.daemon = True

        self.alive = True

        self.first = True

    def kill(self):
        self.alive = False

    def run(self):
        while self.alive:
            if stdin in select([stdin], [], [], 0.25)[0]:
                cmd = stdin.readline().strip()
                if not cmd:
                    continue
                if cmd.lower() in ('q', 'quit'):
                    self.alive = False
                    self.emit('quit')
                    return
                self.emit('command', cmd)

    def process(self, packet):
        if self.first and packet.type == PacketType.SERVERDATA_AUTH_RESPONSE:
            # Auth response
            if packet.id == 0xFFFFFFFF:
                stdout.write('Auth failed. Bad RCON password?\n')
                stdout.flush()
                self.alive = False
                self.on_quit_cb()
            else:
                stdout.write('Auth succeeded!\n')
                stdout.flush()
            self.first = False
        else:
            data = packet.body.strip('\r\n\x00\t')
            if packet.type == PacketType.SERVERDATA_RESPONSE_VALUE and data:
                stdout.write('<< ' + data + '\n')
