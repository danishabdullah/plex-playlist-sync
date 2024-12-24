import logging


class ColoredFormatter(logging.Formatter):
    """
    A formatter that adds color to the log output.
    """

    def format(self, record):
        if record.levelno == logging.DEBUG:
            record.levelname = f"\033[34m{record.levelname}\033[0m"
        elif record.levelno == logging.INFO:
            record.levelname = f"\033[32m{record.levelname}\033[0m"
        elif record.levelno == logging.WARNING:
            record.levelname = f"\033[33m{record.levelname}\033[0m"
        elif record.levelno == logging.ERROR:
            record.levelname = f"\033[31m{record.levelname}\033[0m"
        elif record.levelno == logging.CRITICAL:
            record.levelname = f"\033[35m{record.levelname}\033[0m"
        return super().format(record)


class ColorHandler(logging.StreamHandler):
    # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    GRAY8 = "38;5;8"
    GRAY7 = "38;5;7"
    ORANGE = "33"
    RED = "31"
    WHITE = "0"

    def emit(self, record):
        # Don't use white for any logging, to help distinguish from user print statements
        level_color_map = {
            logging.DEBUG: self.GRAY8,
            logging.INFO: self.GRAY7,
            logging.WARNING: self.ORANGE,
            logging.ERROR: self.RED,
        }

        csi = f"{chr(27)}["  # control sequence introducer
        color = level_color_map.get(record.levelno, self.WHITE)

        print(f"{csi}{color}m{self.format(record)}{csi}m")


def setup_logging():
    # Set up logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a formatter
    c_formatter = ColoredFormatter('%(asctime)s - %(module)s - %(levelname)s - %(message)s')

    # Create a console handler and set the formatter
    console_handler = ColorHandler()
    console_handler.setFormatter(c_formatter)

    # Add both handlers to the logger
    logger.addHandler(console_handler)
