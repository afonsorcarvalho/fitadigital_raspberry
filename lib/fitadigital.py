"""
FITADIGITAL 
Ler Serial 

Autor: AFONSO CARVALHO

Este script consiste em duas classes principais, SerialReader e FileProcessor, que são executadas em threads separadas para ler dados da porta serial e processar arquivos, respectivamente.

Para funcionar corretamente, o script depende de um arquivo de configuração YAML chamado 'config.yaml' que deve estar presente no mesmo diretório do script. Este arquivo contém as configurações necessárias para o script, como o nome da porta serial, diretórios de entrada e saída, entre outros.

O script segue o seguinte fluxo de execução:
1. Carregar as configurações do arquivo YAML.
2. Inicializar a leitura serial em uma thread separada (SerialReader).
3. Inicializar o processamento de arquivos em outra thread separada (FileProcessor).
4. As threads executam suas tarefas de forma assíncrona, lendo dados da porta serial e processando arquivos conforme necessário.
5. O script registra eventos importantes no arquivo de log especificado no arquivo de configuração.

Classes:
- SerialReader: Classe para leitura assíncrona da porta serial.
- FileProcessor: Classe para processamento assíncrono de arquivos.

Métodos importantes:
- SerialReader.update_config(): Atualiza o arquivo de configuração com o nome do arquivo atual.
- FileProcessor.update_config(): Atualiza o arquivo de configuração com o nome do arquivo atual e o ponteiro de arquivo.
"""

import serial
import  yaml
import os
from lib.logger import Logger
from datetime import datetime, timedelta
import time
import threading

import importlib.util


CONFIG_FILE_NAME = "config.yaml"

# Carregar configurações do arquivo YAML
with open(CONFIG_FILE_NAME, 'r') as stream:
    config = yaml.load(stream, Loader=yaml.FullLoader)

# Define o diretorio dos logs
path_log = config['path_log']
_loggin = Logger(diretorio_logs=path_log)
_loggin.log("info", 'Iniciou Leitura da serial')
module_name = config['header_processor']
module_path = os.path.join("lib", f"{module_name}.py")


# Define o manipulador de arquivo para o logger
# Carregar o arquivo do módulo
spec = importlib.util.spec_from_file_location(module_name, module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Acessar a função desejada do módulo importado
header_processor = getattr(module, 'read_header')

# Configurações
SERIAL_PORT = config['serial_port']  # Altere para a porta serial que você está usando
INPUT_DIR = config['input_dir'] 
PROCESSED_DIR = config['processed_dir'] 

class SerialReader(threading.Thread):
    def __init__(self, serial_port, output_dir):
        super().__init__()
        self.serial_port = serial_port
        self.output_dir = output_dir

    def update_config(self,filename):
        update = False
        with threading.Lock():
            
            # Carregar configurações do arquivo YAML
            with open(CONFIG_FILE_NAME, 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)

            if config['current_file_input'] != filename:
                update = True
                config['current_file_input'] = filename
            if config['current_file_processor'] != filename:
                update = True
                config['current_file_processor'] = filename
            if update:
                try:
                    with open(CONFIG_FILE_NAME, 'w') as stream:
                        yaml.dump(config, stream)
                except FileNotFoundError:
                    _loggin.log("error",f"Erro na gravação da configuração. Arquivo {CONFIG_FILE_NAME} nao encontrado")
                except Exception as e:
                    _loggin.log("error",f"Erro ao ler {CONFIG_FILE_NAME}: {e}")

    def run(self):
        
        _loggin.log("info",f"Iniciado leitura na {self.serial_port} ")

        while True:
            # Ler dados da porta serial
            try:
                data = self.serial_port.readline().decode()
            except Exception as e:
                _loggin.log("error",f"Ler linha da serial: {e}")
            #print(data)

            # Obter a data atual
            today = datetime.now().strftime("%Y-%m-%d")

            # Nome do arquivo de saída com base na data atual
            filename = f"output_{today}.txt"
            self.update_config(filename)
            filepath = os.path.join(self.output_dir, filename)

            # Escrever os dados no arquivo
            with open(filepath, "a") as file:
                file.write(data)


class FileProcessor(threading.Thread):
    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir

    
    def update_config(self,filename,pointer_file):
        update = False
        with threading.Lock():
            # Carregar configurações do arquivo YAML
            with open(CONFIG_FILE_NAME, 'r') as stream:
                config = yaml.load(stream, Loader=yaml.FullLoader)

            if config['current_file_processor'] != filename:
                # Modificar configurações
                config['current_file_processor'] = filename
                update = True
            
            if config['pointer_file'] != pointer_file:
                config['pointer_file'] = pointer_file
                update = True

            if update:
                # Salvar configurações de volta para o arquivo YAML
                try:
                    with open(CONFIG_FILE_NAME, 'w') as stream:
                        yaml.dump(config, stream)
                except FileNotFoundError:
                    _loggin.log("error",f"Erro na gravação da configuração. Arquivo {CONFIG_FILE_NAME} nao encontrado")

                except Exception as e:
                    _loggin.log("error",f"Erro ao ler {CONFIG_FILE_NAME}: {e}")
    
    def add_files_cycle(self, lines, cycles_print):

        #lendo file_in
        #with open(filepath_in, "r") as file_in:
        #    lines_in = file_in.readlines()
        
        for cycles in cycles_print:
            name_file = f"{cycles[2]}_{cycles[3]}_{cycles[4]}.txt"

            # Criar o diretório
            output_dir =f"{self.output_dir}/{cycles[2]}"
            if not os.path.exists(output_dir):
                _loggin.log("info",f"Criando o diretório '{output_dir}'...")
                os.makedirs(output_dir)
            
            path_file = os.path.join(output_dir,name_file)
            #print(path_file)

            # Criar o arquivo dentro do diretório
            lines_write = lines[cycles[0]: cycles[1]]
            if os.path.exists(path_file):
                
                with open(path_file, "r") as file_out:
                    file_out_lines = len(file_out.readlines())
                #print(f'Tamanho arquivo fileout {file_out_lines}, lines in: {len(lines_write)}')
                if file_out_lines != len(lines_write):
                    with open(path_file, "w") as file_out:
                        _loggin.log("info",f"O arquivo '{path_file}' já modificado. Atualizando")
                        file_out.writelines(lines_write)
            else:
                _loggin.log("info",f"O arquivo '{path_file}' não existe. Criando-o")
                with open(path_file, "w") as file_out:
                    file_out.writelines(lines_write)

    def file_processor_yesterday(self, file_name):
        # Extrair a data do nome do arquivo
        partes = file_name.split('_')[-1].split('.')[0]  # Extrai YYYY-MM-DD da string
        data_arquivo = datetime.strptime(partes, '%Y-%m-%d').date()

        # Subtrair um dia da data do arquivo para obter a data do dia anterior
        data_ontem = data_arquivo - timedelta(days=1)

        # Formatar a data do dia anterior como YYYY-MM-DD
        nome_arquivo_ontem = f"output_{data_ontem.strftime('%Y-%m-%d')}.txt"
        
        return nome_arquivo_ontem

    def run(self):
        _loggin.log("info","Iniciado file processor")
        
        while True:
            #print("procurando mudanca do no arquivo")
            # Pega da configuração o arquivo para ser processado
            file_processor = config['current_file_processor']
            
            file_processor_yesterday = self.file_processor_yesterday(file_processor)
            
            # Verificar se existem arquivos no diretório de entrada
            files = os.listdir(self.input_dir)
            _loggin.log("debug",f"Arquivos encontrados:{files}")
            
        
            # Processar apenas  
            lines_file_yesterday = []
            lines_file_current =[]
            lines_concatenada = []
            for file in files:
                filepath = os.path.join(self.input_dir, file)   
                if file == file_processor_yesterday:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    lines_file_yesterday = lines
                    #_loggin.log("info",f"Linhas_yesterday: {lines_file_yesterday}")
                    
                    
            for file in files:
                filepath = os.path.join(self.input_dir, file)   
                if file == file_processor:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    lines_file_current = lines
                    #_loggin.log("info",f"Linhas_hoje: {lines_file_current}")
                    
                    
            lines_concatenada =  lines_file_yesterday + lines_file_current
            #_loggin.log("info",f"concatenhada: {lines_concatenada}")
            cycles_header = header_processor(lines_concatenada) # Ler o cabeçalho do arquivo achando os ciclos
            #_loggin.log("info",f"Ciclos index: {cycles_header}")
            self.add_files_cycle(lines_concatenada,cycles_header)
               
            time.sleep(1)




