
import logging
import os
from datetime import datetime, timedelta

class Logger:
    def __init__(self, diretorio_logs="logs"):
        self.diretorio_logs = diretorio_logs
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.configurar_logger()

    def configurar_logger(self):
        os.makedirs(self.diretorio_logs, exist_ok=True)
        data_atual = datetime.now().strftime("%Y-%m-%d")
        nome_arquivo = os.path.join(self.diretorio_logs, f"log_{data_atual}.txt")
        file_handler = logging.FileHandler(nome_arquivo)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)

    def log(self, level, mensagem):
        if level == "debug":
            self.logger.debug(mensagem)
        elif level == "info":
            self.logger.info(mensagem)
        elif level == "warning":
            self.logger.warning(mensagem)
        elif level == "error":
            self.logger.error(mensagem)
        elif level == "critical":
            self.logger.critical(mensagem)