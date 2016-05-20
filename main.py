#!/usr/bin/env python2

from rcon import RCONClient
from cli import Application
import sys


def main():
    if len(sys.argv) != 3:
        sys.stdout.write(
            'Usage:\n'
            '  rkon HOST RCON_PASSWORD\n'
            '  rkon HOST:PORT RCON_PASSWORD\n'
        )
        sys.stdout.flush()
        sys.exit(1)

    parts = sys.argv[1].split(':')
    if len(parts) == 1:
        parts.append(27015)
    host, port = parts

    rcon_password = sys.argv[2]

    # def on_command_cb(cmd):
    #     client.execute(cmd)

    # def on_data_cb(data):
    #     app.process(data)

    def disconnect():
        sys.stdout.write('Connection dropped.\n')
        quit()

    def quit():
        app.kill()
        client.kill()

    app = Application()
    client = RCONClient(host, port, rcon_password)

    app.connect('command', client.execute)
    app.connect('quit', client.kill)
    client.connect('packet', app.process)

    app.connect('quit', quit)
    client.connect('disconnect', disconnect)

    app.start()
    client.start()

    app.join()
    client.join()

if __name__ == '__main__':
    # try:
    main()
    # except KeyboardInterrupt:
        # sys.stdout.write('CTRL-C hit, terminating.\n')
        # sys.exit(130)
