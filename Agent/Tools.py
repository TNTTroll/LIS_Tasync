# ----- Imports
import os
import sys
import inspect
import subprocess
from pathlib import Path

from Assets.Prompts import prompts


# ----- Class
class Tools:
    # Main
    def __init__(self, _path, _permitFiles, _colors):
        self.path = _path
        self.permitFiles = _permitFiles
        self.colors = _colors

        self.funcs = {}

        self.settings()

    def settings(self):
        self.funcs = {}
        for name in [[k, v] for k, v in inspect.getmembers(self, predicate=inspect.ismethod)
                     if k.startswith('tool')]:
            self.funcs.update({name[0]: name[1]})

    def operate(self, response):
        res = []
        for tool in response['tool_calls']:
            self.print(f" <<< Использую tool: {tool}", "tool")

            function_name = tool['function']['name']
            function_args = tool['function']['arguments']

            if function_name in self.funcs:
                function_to_call = self.funcs[function_name]
                res.append({
                    "Действие": tool['function']['name'],
                    "Результат": function_to_call(**function_args)
                })
        return res

    def print(self, text, color="info"):
        print(f"\033[{self.colors[color]}m{text}\033[0m")

    # Tools
    def toolCreateDir(self, dir: str):
        """
        Function only for creating a folder
        :param dir: Path to the place where you want to create a new folder
        """

        try:
            os.mkdir(Path(self.path, dir))
        except: pass

        return f"Dir name: {dir}"

    def toolDeleteDir(self, dir: str):
        """
        Function only for removing a folder
        :param dir: Path to the place where you want to remove a new folder
        """

        try:
            if dir not in self.permitFiles:
                os.rmdir(Path(self.path, dir))
        except: pass

        return f"Dir name: {dir}"

    def toolCreateFile(self, file: str):
        """
        Function for creating a file in ONLY MD format. NEVER use others format

        :param file: ONLY file's name to create
        """

        try:
            if file.find(".") != -1:
                file = file[:file.find(".")]
            if not file.endswith(".md"): file += ".md"
            with open(Path(self.path, file), "w", encoding="utf-8"): pass
        except: pass

        return f"File name: {file}"

    def toolDeleteFile(self, file: str):
        """
        Function only for removing a file
        :param file: Name of the file
        """

        try:
            if dir not in self.permitFiles:
                os.remove(Path(self.path, file))
        except: pass

        return f"File name: {file}"

    def toolWriteFile(self, file: str, data: str, mode: str):
        """
        Function to write data to md file in md format in on of two modes:
        W - Rewrite full file, open it clear and write down the data
        A - Append data to the file

        :param file: Name of the file where data has to be written to
        :param data: String of data to write in to the file
        :param mode: Mode with open the file. Must be "w" or "a"
        """

        try:
            with open(Path(self.path, file), mode, encoding="utf-8") as file:
                file.write(data)
        except: pass

        return f"File name: {file}"

    def toolReadFile(self, file: str) -> str:
        """
        Function to read data from md file

        :param file: Name of the file where data has to be written to
        :return str: Data from the file
        """

        try:
            with open(Path(self.path, file), "r", encoding="utf-8") as file:
                return file.read()
        except: return ""

    def toolGetDirs(self) -> dict:
        """
        Function to see all files in root folder, including all files in all folders inside of this

        :return: Dict with all folders and files in selected folder
        """

        def getFiles(path):
            files = []
            folders = {}
            root = Path(path)

            for item in [Path(root, file) for file in os.listdir(root)]:
                file = item.relative_to(root)
                if str(file.parent) in self.permitFiles or str(file.name) in self.permitFiles: continue

                if item.is_dir():
                    folders.update({file.name: getFiles(Path(path, file))})
                else:
                    files.append(file.name)

            return {
                "folders": folders,
                "files": files
            }

        return getFiles(self.path)

    def toolAskUser(self, query: str) -> str:
        """
        Function to ask user anything necessary

        :param query: Text that user will see to know the question
        :return: User's answer
        """

        self.print(query, "ask")
        return input("   >>> ")

    def toolTextUser(self, text: str):
        """
        Function to show text to user

        :param text: Text to be shown to user
        """

        self.print(text, "info")

    # def toolExecutePython(self, script: str) -> str:
    #     """
    #     Executes a standalone Python script in a separate subprocess and returns its terminal output (stdout and stderr combined).
    #     Before running, the script is displayed to the user for manual review and confirmation.
    #     If the user rejects the execution, the function returns 'Отменено.'.
    #
    #     :params script: The complete, valid Python code to be executed.
    #     :return str: The combined stdout and stderr produced by the script, or a cancellation notice.
    #     """
    #
    #     key = input(f"{script}\n\nAccept? [Y/N]: ")
    #
    #     if key not in ("y", "д"):
    #         print("Canceled")
    #         return ""
    #
    #     res = subprocess.run([sys.executable, "-c", script],
    #                          capture_output=True,
    #                          text=True,
    #                          encoding="utf-8")
    #     print(res.stdout)
    #     return res.stdout + res.stderr