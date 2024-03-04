# -*- coding: utf-8 -*-

from datetime import date, datetime

qtd_header_lines = 7
def extract_data_from_header(header):
    codigo_carga = None
    current_datetime = datetime.now()
    data = current_datetime.strftime("%Y%m%d")
    hora = current_datetime.strftime("%H%M%S")

    # Encontrar o número do CODIGO DE CARGA, a data e a hora no cabeçalho
    for i, line in enumerate(header):
        #procurando codigo de carga
        #carga_match = re.search(r'CODIGO DE CARGA:\s+(\d+)\s+', line)
        value = line.strip().split(':')
        #print(f"VALORES:{value}")
        
           
        if value[0] == 'DATA': 
            data = value[1].strip().split()[0] # Formato: YYYYMMDD
            dia, mes, ano = data.split('/')
            data = ano+mes+dia
            #print(f"DATA:{data}")
            hora = value[2].strip() + value[3].strip() + value[4].strip()  # Formato: HHMMSS

        if value[0] == 'CODIGO DE CARGA':
            codigo_carga = value[1].strip().split()[0]
            break
    return codigo_carga, data, hora, i

def read_header(lines):
    
    data_file_mount = []
    # with open(file_name, 'r', encoding='utf-8') as f:
    #     lines = f.readlines()
    
    # Definir as linhas onde começam os cabeçalhos
    header_starts = []  # Começa no início do arquivo
    for i, line in enumerate(lines):
        if line.strip().startswith('= = B A U M E R = ='):
            header_starts.append(i-1)
           
    # Adicionar a última linha do arquivo como uma referência final
    header_starts.append(len(lines))
    
        
    # Criar arquivos divididos com base nas linhas dos cabeçalhos
    for i in range(len(header_starts)-1):
        start_line = header_starts[i]
        end_line = header_starts[i + 1]
        #print(f"{start_line} ate {end_line}")
        #print(lines[start_line:start_line+qtd_header_lines])
        data_file_mount.append((start_line,end_line)+extract_data_from_header(lines[start_line:start_line+qtd_header_lines]))
    #enviando sempre o ultimo encontrado
    return data_file_mount

