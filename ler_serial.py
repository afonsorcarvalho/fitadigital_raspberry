import serial
import yaml
import os
from lib.fitadigital import SerialReader
from lib.logger import Logger
from datetime import datetime, timedelta
import time
import threading

CONFIG_FILE_NAME = "./config.yaml"

# Carregar configurações do arquivo YAML
with open(CONFIG_FILE_NAME, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)
    
SERIAL_PORT = config['serial_port']  # Altere para a porta serial que você está usando
INPUT_DIR = config['input_dir'] 
PROCESSED_DIR = config['processed_dir'] 

# Criar diretórios se não existirem
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(INPUT_DIR, exist_ok=True)

# Iniciar threads
ser = serial.Serial(SERIAL_PORT, baudrate=9600)  # Configurar a porta serial
serial_thread = SerialReader(ser, INPUT_DIR)


serial_thread.start()

