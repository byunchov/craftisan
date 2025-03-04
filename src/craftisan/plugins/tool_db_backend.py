#!/usr/bin/env python3

import os
import sys
import traceback
from craftisan.tool_db.base import Session
from craftisan.tool_db.model import Tool, Pocket


class ToolDatabaseManager:
    DB_VERSION = 'v2.1'
    COLUMNS = 'TPXYZCB'
    FINISH_MSG = 'FINI'
    EMPTY_LINE = 'empty_line'

    def __init__(self):
        self.debug: bool = False
        self.last_line: str = ""
        self.cmd_switcher = {
            "g": self.get_tools,
            "p": self.put_tool,
            "u": self.load_spindle,
            "l": self.unload_spindle,
        }

        if len(sys.argv) > 1 and sys.argv[1] in ('debug', '--debug', '-d'):
            self.debug = True

    def reply(self, msg):
        try:
            sys.stdout.write(f"{msg}\n")
            sys.stdout.flush()
        except BrokenPipeError as e:
            raise ConnectionAbortedError from e

    def nak_reply(self, msg):
        if msg != self.EMPTY_LINE:
            sys.stderr.write(f"{traceback.format_exc()}\n")
        self.reply(f"NAK {msg} <{self.last_line}>")

    def get_tools(self, *args) -> None:
        if self.debug:
            sys.stderr.write(f"!!get_tools()=<{args}>\n")
        
        with Session() as session:
            non_empty_pockets = session.query(Pocket).filter(Pocket.toolId.isnot(None)).all()

            for pocket in non_empty_pockets:
                if pocket.tool is not None:
                    self.reply(pocket.tool.toToolString())
        
        self.reply(self.FINISH_MSG)

    def put_tool(self, params: dict) -> None:
        with Session() as session:
            tool = session.get(Tool, params.get('T'))

            if tool:
                tool.updateFromDict(params)
                session.add(tool)
                session.commit()
        
        self.reply(self.FINISH_MSG)

    def load_spindle(self, params: dict) -> None:
        # Do something
        self.reply(self.FINISH_MSG)

    def unload_spindle(self, params: dict) -> None:
        # Do something
        self.reply(self.FINISH_MSG)

    def unknown_cmd(self, *args):
        self.nak_reply("Unknown command recieved")

    def fetch_line(self):
        if self.debug:
            sys.stderr.write(f"!!line=<{self.last_line}>\n")
        
        tokens = self.last_line.upper().split()
        cmd = tokens[0].lower()
        params = {}
        if len(tokens) > 1:
            params = {token[0]: token[1:] for token in tokens}
        
        callback = self.cmd_switcher.get(cmd, self.unknown_cmd)
        callback(params)

    def startup_ack(self):
        self.reply(self.DB_VERSION)

    def run(self):
        self.startup_ack()
        while True:
            try:
                self.last_line = sys.stdin.readline().strip()
                if self.last_line:
                    self.fetch_line()
                else:
                    self.nak_reply(self.EMPTY_LINE)
            except (ConnectionAbortedError, KeyboardInterrupt) as e:
                sys.stdout = open(os.devnull, 'w')                
                if self.debug:
                    sys.stderr.write(f"!!{e.__class__.__name__}: Quitting DB backend...\n"
                                     f"Redirecting stdout > {sys.stdout.name}\n")
                break
            except Exception as e:
                self.nak_reply(f"[{self.__class__.__name__}]_exception={e}")


def main():
    tool_db = ToolDatabaseManager()
    tool_db.run()


if __name__ == "__main__":
    main()
