from typing import Optional

class AgentAction:
    def __init__(self, actor: str, type: str, target: str, reason: Optional[str] = None):
        self.actor = actor
        self.type = type  # "VOTE", "KILL", "PEEK", etc.
        self.target = target
        self.reason = reason
