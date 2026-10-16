# ----- Imports
import json
from pathlib import Path


# ----- Class
class Memory:
    # Main
    def __init__(self, _path):
        self.path = Path(_path, "Assets")

        self.memory = None

        self.getMemory()

    def clear(self):
        with open(Path(self.path, "Memory.json"), "w", encoding="utf-8") as file:
            file.write(json.dumps([], ensure_ascii=False, indent=4))
        self.memory = []

    # Input
    @property
    def get(self):
        pack = []

        for i in range(len(self.memory)-1, -1, -1):
            pack.append(self.memory[i])
            if len(pack) >= 3: break
        pack.reverse()

        return pack

    def getMemory(self):
        with open(Path(self.path, "Memory.json"), "r", encoding="utf-8") as file:
            self.memory = json.loads(file.read())

    # Output
    def add(self, data, role="user"):
        self.memory.append({"role": role, "content": data})

        self.saveMemory()

    def saveMemory(self):
        with open(Path(self.path, "Memory.json"), "w", encoding="utf-8") as file:
            file.write(json.dumps(self.memory, indent=4, ensure_ascii=False))
