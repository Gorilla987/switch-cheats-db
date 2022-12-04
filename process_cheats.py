#!/usr/bin/env python3

from os import mkdir, listdir, path
from string import hexdigits
from pathlib import Path
import re
import subprocess
import json


class ProcessCheats:
    def __init__(self, in_path, out_path):
        self.out_path = Path(out_path)
        self.in_path = Path(in_path)
        self.parseCheats()

    def isHexAnd16Char(self, file_name):
        return (len(file_name) == 16) and (all(c in hexdigits for c in file_name[0:15]))

    def getCheatsPath(self, tid):
        for folder in tid.iterdir():
            if folder.name.lower() == "cheats":
                return folder
        return None

    def getAttribution(self, tid):
        attribution = {}
        for f in tid.iterdir():
            if f.suffix.lower() == ".txt":
                with open(f, "r") as attribution_file:
                    attribution[f.name] = attribution_file.read()
        return attribution

    def constructBidDict(self, sheet_path):
        out = []
        pos = []
        with open(sheet_path, 'r', encoding="utf-8", errors="ignore") as cheatSheet:
            lines = cheatSheet.readlines()

        for i in range(len(lines)):
            titles = re.search("(\[.+\]|\{.+\})", lines[i])
            if titles:
                pos.append(i)

        for i in range(len(pos)):
            try:
                codeLines = lines[pos[i]:pos[i + 1]]
            except IndexError:
                codeLines = lines[pos[i]:]
            if len(codeLines) > 1:
                code = "".join(codeLines)
                if re.search("[0-9a-fA-F]{8}", code):
                    out.append({"title": lines[pos[i]].strip(),
                                "content": code})
        return out

    def createJson(self, tid):
        out = {}
        cheats_dir = self.getCheatsPath(tid)
        try:
            for sheet in cheats_dir.iterdir():
                if self.isHexAnd16Char(sheet.stem):
                    out[sheet.stem.upper()] = self.constructBidDict(sheet)
        except FileNotFoundError:
            print(f"error: FileNotFoundError {folder_path}")
        attribution = self.getAttribution(tid)
        if attribution:
            out["attribution"] = self.getAttribution(tid)


        cheats_file = self.out_path.joinpath(f"{tid.name.upper()}.json")
        try:
            with open(cheats_file, 'r') as json_file:
                out |= json.load(json_file)
        except FileNotFoundError:
            pass

        with open(cheats_file, 'w') as json_file:
            json.dump(out, json_file, indent=4, sort_keys=True)

    def parseCheats(self):
        subprocess.call(['bash', '-c', f"chmod -R +rw {self.in_path}"])
        if not(self.out_path.exists()):
            self.out_path.mkdir()
        for tid in self.in_path.iterdir():
            if self.isHexAnd16Char(tid.name):
                self.createJson(tid)