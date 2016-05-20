from threading import Thread
from select import select
import socket
from struct import pack, unpack
from custom_types import PacketType
from em import EM


class Packet(object):
    last_id = 1

    def __init__(self, type_, body, id_=None):
        self.type = type_
        self.body = body.strip('\x00')
        if id_ is not None:
            self.id = id_
        else:
            Packet.last_id += 1
            self.id = Packet.last_id

    def _get_size(self):
        return len(self.body) + 10

    def serialize(self):
        return ''.join([
            pack('<I', self._get_size()),
            pack('<I', self.id),
            pack('<I', self.type),
            self.body,
            '\x00\x00'
        ])

    @classmethod
    def unserialize(cls, raw):
        return Packet(
            id_=unpack('<I', raw[4:8])[0],
            type_=unpack('<I', raw[8:12])[0],
            body=raw[12:-1]
        )

    def __str__(self):
        return '<Packet size={} id={} type={} body={}>'.format(
            self._get_size(),
            self.id,
            self.type,
            ' '.join(['0x%02X' % ord(x) for x in self.body])
        )

    def __repr__(self):
        return self.__str__()


class RCONClient(Thread, EM):
    def __init__(self, host, port, rcon_password):
        Thread.__init__(self)
        EM.__init__(self)

        self.daemon = True

        self.alive = True

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = host
        self.port = port
        self.rcon_password = rcon_password

        self.first = True

    def _wait_for_read(self):
        return self.conn in select([self.conn], [], [], 0.25)[0]

    def send_packet(self, packet):
        self.conn.send(packet.serialize())

    def run(self):
        self.conn.connect((self.host, int(self.port)))
        self.send_packet(Packet(
            PacketType.SERVERDATA_AUTH,
            self.rcon_password
        ))

        while self.alive:
            if not self._wait_for_read():
                continue

            data = self.conn.recv(1024)
            if not len(data):
                self.alive = False
                self.emit('disconnect')
                return

            self.emit('packet', Packet.unserialize(data))

    def execute(self, cmd):
        self.send_packet(Packet(PacketType.SERVERDATA_EXECCOMMAND, cmd))

    def kill(self):
        self.alive = False
