class Counter():
    def __init__(self):
        self.total = 0
        self.count = 0

    def add(self, new):
        self.total += new
    def reset(self):
        self.total = 0
        self.count = 0
    def inc(self):
        self.count += 1