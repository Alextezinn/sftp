import sys

import constants


config = {
    "handlers": [
        {"sink": sys.stdout, "colorize": True, "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | {level} | <red>{message}</red>"},
        {"sink": constants.PATH_LOG_FILE, "level": "DEBUG", "rotation": "10 MB",
         "compression": "zip", "serialize": True},
    ]
}