import os
import logging
import itertools

logger = logging.getLogger(__name__)


class OpenplanetLogMessage:
    def __init__(self, log_line: str) -> None:
        self.source = ''
        self.time = ''
        self.subject = ''
        self.text = ''

        index, self.source = OpenplanetLogMessage.__get_next_brackets(log_line, 0)
        if not log_line[index:index+2] == '  ':
            index, self.time = OpenplanetLogMessage.__get_next_brackets(log_line, index)
            if not log_line[index:index+2] == '  ':
                index, self.subject = OpenplanetLogMessage.__get_next_brackets(log_line, index)
        self.text = log_line[index+2:]

    @staticmethod
    def __get_next_brackets(log_line, start_offset) -> 'tuple[int, str]':
        start_index = log_line.index('[', start_offset)
        end_index = log_line.index(']', start_index)
        return end_index+1, log_line[start_index+1:end_index].strip()

class OpenplanetLog:
    def __init__(self) -> None:
        self.file_path = ''
        self.last_len = 0

    def set_path(self, file_path) -> None:
        if os.path.isfile(file_path):
            self.file_path = file_path

    def start_monitor(self) -> None:
        if not os.path.isfile(self.file_path):
            self.last_len = 0
            return
        with open(self.file_path, 'r') as log_file:
            self.last_len = len(log_file.read())
            logger.debug(str(self.last_len))

    def end_monitor(self) -> 'list[OpenplanetLogMessage]':
        if not os.path.isfile(self.file_path):
            return []
        new_lines = []
        with open(self.file_path, 'r') as log_file:
            new_lines = log_file.read()[self.last_len:].splitlines()
            logger.debug(str(len(new_lines)) + " new lines found")
        return [OpenplanetLogMessage(line) for line in new_lines]
