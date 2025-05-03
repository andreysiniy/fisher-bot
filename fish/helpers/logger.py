import datetime
import logging
import os
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')

def get_logger(name: str = "fish_log") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:  
        logger.setLevel(logging.INFO)
        formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')

        file_handler = RotatingFileHandler(
            os.path.join("logs", f"{name}.log"),          
            maxBytes=1_000_000,  
            backupCount=10      
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    return logger
