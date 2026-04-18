import os
import logging
from colorama import Fore

logger = logging.getLogger(__name__)


def _get_next_brackets(log_line, start_offset) -> "tuple[int, str]":
    start_index = log_line.index("[", start_offset)
    end_index = log_line.index("]", start_index)
    return end_index + 1, log_line[start_index + 1 : end_index].strip()


class OpenplanetLogMessage:
    def __init__(self, log_line: str) -> None:
        self.source = ""
        self.level = ""
        self.time = ""
        self.subject = ""
        self.text = ""

        index, self.source = _get_next_brackets(log_line, 0)
        if not log_line[index : index + 2] == "  ":
            index, self.level = _get_next_brackets(log_line, index)
            if not log_line[index : index + 2] == "  ":
                index, self.time = _get_next_brackets(log_line, index)
                if not log_line[index : index + 2] == "  ":
                    index, self.subject = _get_next_brackets(log_line, index)
        self.text = log_line[index + 2 :]


class OpenplanetLog:
    def __init__(self) -> None:
        self.file_path = ""
        self.last_len = 0

    def set_path(self, file_path) -> None:
        if os.path.isfile(file_path):
            logger.debug(f"Using {file_path} as log file")
            self.file_path = file_path
        else:
            logger.error(f"Log file not found at {file_path}")

    def start_monitor(self) -> None:
        if not os.path.isfile(self.file_path):
            self.last_len = 0
            return
        self.last_len = os.stat(self.file_path).st_size
        logger.debug(str(self.last_len))

    def end_monitor(self, print_msgs: bool = True) -> None:
        if not os.path.isfile(self.file_path):
            return []
        new_lines = []
        with open(self.file_path, "r") as log_file:
            log_file.seek(self.last_len)
            new_lines = log_file.read().splitlines()
            logger.debug(str(len(new_lines)) + " new lines found")
        if print_msgs:
            log_msgs: "list[OpenplanetLogMessage]" = [
                OpenplanetLogMessage(line) for line in new_lines
            ]
            for msg in log_msgs:
                if msg.source == "ScriptEngine":
                    if ":  ERR :" in msg.text or msg.level == "ERROR":
                        print(Fore.RED + msg.text + Fore.RESET)
                    elif ": WARN :" in msg.text or msg.level == "WARN":
                        print(Fore.YELLOW + msg.text + Fore.RESET)
                    else:
                        print(msg.text)
