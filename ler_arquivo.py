import yaml
import os
from lib.fitadigital import FileProcessor
from lib.logger import Logger
from datetime import datetime, timedelta
import time
import threading

CONFIG_FILE_NAME = "./config.yaml"

# Carregar configurações do arquivo YAML
with open(CONFIG_FILE_NAME, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

INPUT_DIR = config['input_dir'] 
PROCESSED_DIR = config['processed_dir'] 

# Criar diretórios se não existirem
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

file_thread = FileProcessor(INPUT_DIR, PROCESSED_DIR)
file_thread.start()