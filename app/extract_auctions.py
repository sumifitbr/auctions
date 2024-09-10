import requests
import os

# Lista de estados brasileiros e suas siglas
estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 
           'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 
           'RR', 'SC', 'SP', 'SE', 'TO']

# URL padrão (modificamos a sigla do estado)
url_template = "https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{}.csv"

# Diretório para salvar os arquivos CSV
output_dir = "./app/files"
os.makedirs(output_dir, exist_ok=True)

for estado in estados:
    # Gerar a URL com a sigla do estado
    url = url_template.format(estado)
    
    try:
        print(f"Baixando arquivo para o estado: {estado}...")
        response = requests.get(url)
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Caminho do arquivo de saída
            file_path = os.path.join(output_dir, f"Lista_imoveis_{estado}.csv")
            
            # Salvar o conteúdo do CSV no arquivo
            with open(file_path, 'wb') as file:
                file.write(response.content)
                
            print(f"Download concluído: {file_path}")
        else:
            print(f"Erro ao baixar o arquivo para o estado: {estado}")
    
    except Exception as e:
        print(f"Erro ao processar o estado {estado}: {e}")