class EM(object):
    def __init__(self):
        self.connections = {}

    def connect(self, event, target):
        if not self.connections.get(event):
            self.connections[event] = []
        self.connections[event].append(target)

    def disconnect(self, event, target):
        while True:
            try:
                self.connections[event].remove(target)
            except ValueError:
                return

    def emit(self, event, *args, **kwargs):
        for target in self.connections[event]:
            target(*args, **kwargs)
