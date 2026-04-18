import os
import logging
from pathlib import Path
import time
from colorama import Fore

logger = logging.getLogger(__name__)
PLUGIN_ID = "unk"


def _get_next_brackets(log_line: str, start_offset) -> "tuple[int, str]":
    if "[" not in log_line[start_offset:]:
        return len(log_line)-1, log_line
    start_index = log_line.index("[", start_offset)
    if "]" not in log_line[start_index:]:
        return len(log_line)-1, log_line
        # return start_index, ""
    end_index = log_line.index("]", start_index)
    return end_index + 1, log_line[start_index + 1 : end_index].strip()


class OpenplanetLogMessage:
    def __init__(self, log_line: str) -> None:
        self.source = ""
        self.time = ""
        self.subject = ""
        self._text = ""
        self.detected_plugin = ""

        index, self.source = _get_next_brackets(log_line, 0)
        if not log_line[index : index + 2] == "  ":
            index, self.time = _get_next_brackets(log_line, index)
            if not log_line[index : index + 2] == "  ":
                index, self.subject = _get_next_brackets(log_line, index)
                if not log_line[index : index + 2] == "  ":
                    index, self.detected_plugin = _get_next_brackets(log_line, index)
        self._text = log_line[index + 2 :]

    @property
    def text(self) -> str:
        global PLUGIN_ID
        if "/OpenplanetNext/Plugins/" in self._text and self._text[1] == ":":
            self._text = self._text.split("/OpenplanetNext/Plugins/", 1)[1]
            self._text = self._text.split("/", 1)[1] # could add "./" at the start here but ctrl+click doesn't work for me in vscode (but `/` would)
        return self._text

    def print(self) -> None:
        if ":  ERR :" in self.text:
            print(Fore.RED + self.text + Fore.RESET)
        elif ": WARN :" in self.text:
            print(Fore.YELLOW + self.text + Fore.RESET)
        else:
            print(self.text)


class OpenplanetLog:
    def __init__(self) -> None:
        self.file_path = ""
        self.last_len = 0
        self.last_checked_len = 0
        self.check_after_hit_count = -1

    def set_path(self, file_path) -> None:
        if os.path.isfile(file_path):
            self.file_path = file_path

    def seek_back(self, offset: int) -> None:
        self.last_len = max(0, self.last_len - offset)
        self.last_checked_len = max(0, self.last_checked_len - offset)

    def __enter__(self):
        self.start_monitor()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_monitor()

    # return true if we are done; sleep between calls
    def check_if_log_done(self, log_done_limit: int) -> bool:
        slice, s_len, new_len = self.get_log_slice(self.last_checked_len, -1)
        self.last_checked_len = new_len
        filtered_msgs = [msg for msg in slice if msg.source == "ScriptEngine" or PLUGIN_ID == msg.detected_plugin]
        if len(filtered_msgs) > 0:
            self.check_after_hit_count = 0
            for msg in filtered_msgs:
                msg.print()
        else:
            if self.check_after_hit_count >= 0:
                self.check_after_hit_count += 1
            # if has_hit=true => done since no more msgs are found after finding some
            return self.check_after_hit_count >= log_done_limit
        return False

    def start_monitor(self) -> None:
        self.last_len = 0
        self.last_checked_len = 0
        self.check_after_hit_count = -1

        if not os.path.isfile(self.file_path):
            return

        self.last_len = os.stat(self.file_path).st_size
        self.last_checked_len = self.last_len
        logger.debug(f"last line len: {self.last_len}")

    def get_log_slice(self, start: int, end: int) -> "tuple[list[OpenplanetLogMessage], int, int]":
        if not os.path.isfile(self.file_path):
            return []
        new_lines = []
        bytes_read = 0
        end_offset = 0
        with open(self.file_path, "r") as log_file:
            log_file.seek(start)
            raw_lines = log_file.read(-1 if end < 0 else end - start)
            bytes_read = len(raw_lines)
            new_lines = raw_lines.splitlines()
            end_offset = start + bytes_read
            logger.debug(f"{len(new_lines)} new lines found")
        log_msgs: "list[OpenplanetLogMessage]" = [
            OpenplanetLogMessage(line) for line in new_lines
        ]
        return log_msgs, bytes_read, end_offset


    def end_monitor(self, print_msgs: bool = True) -> None:
        # if not os.path.isfile(self.file_path):
        #     return []
        # new_lines = []
        # with open(self.file_path, "r") as log_file:
        #     log_file.seek(self.last_len)
        #     new_lines = log_file.read().splitlines()
            # logger.debug(str(len(new_lines)) + " new lines found")
        log_msgs, _, _ = self.get_log_slice(self.last_len, -1)
        errors = [msg for msg in log_msgs if ":  ERR :" in msg.text and msg.source == "ScriptEngine"]
        if print_msgs:
            for msg in log_msgs:
                if msg.source == "ScriptEngine":
                    msg.print()
            if len(errors) > 0:
                print(f"------------ ERRORS ------------")
                print(Fore.RED + str(len(errors)) + " errors found" + Fore.RESET)
                for msg in errors:
                    msg.print()
        self.last_len = 0

    def watch_and_print_log_updates(
        self, log_done_limit: int = 3, log_check_interval: int = 0.5
    ) -> None:
        with self as opl:
            while not opl.check_if_log_done(log_done_limit):
                time.sleep(log_check_interval)
