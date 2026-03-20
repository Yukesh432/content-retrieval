class SessionMemory:

    def __init__(self):
        self.history = []

    def add_user(self, text):
        self.history.append({"role": "user", "content": text})

    def add_assistant(self, text):
        self.history.append({"role": "assistant", "content": text})

    def get_recent(self, n=6):
        return self.history[-n:]

    def export(self):
        return self.history