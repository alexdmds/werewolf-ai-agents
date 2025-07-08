class AgentMemory:
    def __init__(self):
        self.log = []

    def add(self, message: str):
        self.log.append(message)

    def get_recent(self, n: int):
        return self.log[-n:]

    def get_summary(self):
        # Version minimale : concatène les messages
        return " ".join(self.log)
