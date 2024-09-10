import psycopg2
import googlemaps

# Configurações do banco de dados PostgreSQL
db_config = {
    'dbname': 'auctions_dev',
    'user': 'postgres',
    'password': 'Last$1981',
    'host': '94.130.107.131',
    'port': 5432
}

# Configuração da API do Google Places
gmaps = googlemaps.Client(key='SUA_CHAVE_DE_API_GOOGLE_PLACES')

def buscar_enderecos():
    # Conectar ao banco de dados PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Consultar a tabela "leiloes" para obter os endereços
    cursor.execute("SELECT i.'Endereço' as endereco FROM tbl_imoveis i")
    enderecos = cursor.fetchall()

    # Fechar a conexão com o banco de dados
    cursor.close()
    conn.close()

    return enderecos

def buscar_dados_proximos(endereco):
    # Geocodificar o endereço para obter latitude e longitude
    geocode_result = gmaps.geocode(endereco)
    
    if not geocode_result:
        print(f"Não foi possível geocodificar o endereço: {endereco}")
        return

    location = geocode_result[0]['geometry']['location']
    latitude, longitude = location['lat'], location['lng']

    # Fazer uma busca por estabelecimentos próximos
    places_result = gmaps.places_nearby(location=(latitude, longitude), radius=1000)

    return places_result.get('results', [])

def main():
    enderecos = buscar_enderecos()

    for endereco in enderecos:
        endereco_str = endereco[0]  # Desempacotar a tupla
        print(f"Buscando dados próximos para o endereço: {endereco_str}")

        lugares_proximos = buscar_dados_proximos(endereco_str)
        
        for lugar in lugares_proximos:
            print(f"Nome: {lugar['name']}, Endereço: {lugar['vicinity']}")

if __name__ == "__main__":
    main()
