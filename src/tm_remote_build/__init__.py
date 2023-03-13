import logging
from colorama import init, Fore

init(autoreset=True)


class ColorFormatter(logging.Formatter):
    level_colors = {
        "WARNING": Fore.YELLOW,
        "ERROR": Fore.RED,
        "DEBUG": Fore.BLUE,
        "INFO": Fore.WHITE,
        "CRITICAL": Fore.RED,
    }
    game_colors = {
        "TMNEXT": Fore.GREEN,
        "MP4": Fore.BLUE,
        "TURBO": Fore.YELLOW,
    }
    game_name = ""

    def format(self, record):
        color = self.level_colors.get(record.levelname, "")
        if color:
            record.levelname = color + record.levelname + Fore.RESET
            record.msg = color + record.msg
        if self.game_name:
            record.gamename = (
                self.game_colors.get(self.game_name, "") + self.game_name + Fore.RESET
            )
        return logging.Formatter.format(self, record)


class ColorLogger(logging.Logger):
    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.INFO)
        color_formatter = ColorFormatter("[%(levelname)-17s]  %(message)s")
        self.console = logging.StreamHandler()
        self.console.setFormatter(color_formatter)
        self.addHandler(self.console)

    def init_game_name(self, game_name="") -> None:
        color_formatter = ColorFormatter(
            "[%(gamename)-16s] [%(levelname)-17s]  %(message)s"
        )
        color_formatter.game_name = game_name
        self.console.setFormatter(color_formatter)


logging.setLoggerClass(ColorLogger)
