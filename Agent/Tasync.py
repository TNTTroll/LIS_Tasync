# ----- Imports
import re
import json
import time
import ollama
from pathlib import Path

from Agent.Tools import Tools
from Agent.Memory import Memory
from Assets.Prompts import prompts


# ----- Class
class Tasync:
    colors = {
        "log": "90",
        "tool": "90;3",
        "err": "91",
        "ask": "92",
        "info": "94",
        "output": "95"
    }

    # Main
    def __init__(self):
        self.path = Path(Path().cwd())
        self.assetsPath = Path(self.path, "Assets")
        self.obsidian = Path(r'D:\GameDev\Obsidian\Notes')

        self.model = None
        self.permitFiles = []

        with open(Path(self.assetsPath, "Settings.json"), "r", encoding="utf-8") as file:
            self.settings = json.loads(file.read())

        self.tools = Tools(self.obsidian, self.permitFiles, self.colors)
        self.memory = Memory(self.path)

        self.load()
        self.talking()

    def load(self):
        try:
            self.model = self.settings["model"]
        except:
            self.model = "gemma4:31b-cloud"

        try:
            self.permitFiles = self.settings["permittedFiles"]
        except:
            self.permitFiles = [".obsidian"]

    def talking(self):
        while True:
            prompt = input(">>> ")
            if prompt == "0": break
            elif prompt == "/clear":
                self.memory.clear()
                self.tools.print("Память была очищена", "err")
            else:
                res = self.ask(f"{prompt}")
                self.tools.print(f"{res['text']} [{res['time']}]",
                                 "output" if res["code"] == "200" else "err")

    def ask(self, prompt):
        status = {
            "code": "200",
            "text": "",
            "time" : time.time()
        }

        p = [
            {
                "role": "system",
                "content": prompts["Initial"]
            },
            {
                "role": "user",
                "content": prompt
            },
            {
                "role": "assistant",
                "content": f"Прошлые запросы для понимания контекста: {str(self.memory.get)}"
            }
        ]

        self.memory.add(prompt)

        resp = self.use(p, useTools=False)
        resp = resp["message"]["content"]

        try:
            jsonMatch = re.search(r'(\[.*]|\{.*})', resp, re.DOTALL)
            jsonStr = jsonMatch.group()
            resp = json.loads(jsonStr)
        except:
            status["code"] = "400"
            status["text"] = "ERR. Agent return not in json format"

        if status["code"] == "200":
            if resp.get("action") and resp.get("text"):
                if resp["action"].lower() == "talk":
                    ans = resp["text"]
                    self.memory.add(ans, "assistant")

                    status["text"] = ans

                else:
                    plan = resp["text"].split("\n")
                    moves = {}

                    for step in plan:
                        self.tools.print(f" <<< {step}", "log")

                    for step in plan:
                        p = [
                            {
                                "role": "system",
                                "content": prompts["Step"]
                            },
                            {
                                "role": "user",
                                "content": step
                            },
                            {
                                "role": "assistant",
                                "content": f"Предыдущие действия: {str(moves)}"
                            }
                        ]

                        action = self.use(p)
                        action = action["message"]

                        if action.get("tool_calls"):
                            ret = self.tools.operate(action)
                            moves.update({step: ret})
                        else:
                            self.tools.print(action["content"], "info")
                            moves.update({step: f"Сообщил пользователю: {action['content']}"})

                        status["text"] = f"План выполнен"
            else:
                status["code"] = "400"
                status["text"] = "ERR. Agent created wrong format response"

        t = int(time.time() - status["time"])

        s = t % 60
        m = t % 3600 // 60
        h = t // 3600

        status["time"] = f"{h:02d}:{m:02d}:{s:02d}"

        return status

    def use(self, prompt, useTools=True):
        return ollama.chat(model=self.model,
                           messages=prompt,
                           tools=[v for v in self.tools.funcs.values()] if useTools else None)





