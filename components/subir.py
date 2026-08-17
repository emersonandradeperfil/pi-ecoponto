import pandas as pd
from pymongo import MongoClient

# 1. Cole aqui a sua URI de conexão oficial do MongoDB Atlas
# (Exemplo: "mongodb+srv://usuario:senha@cluster.mongodb.net/?retryWrites=true&w=majority")
uri = "mongodb+srv://ecoponto:emerson@ecoponto.qozypnw.mongodb.net/?appName=ecoponto"

client = MongoClient(uri)
db = client["pi_ecoponto"]         # Nome do banco que aparece na sua tela
collection = db["ecopontos"]       # Nome da collection

# 2. Lê o CSV que geramos antes
df = pd.read_csv("ecopontos_processado.csv")

# 3. Converte o DataFrame para formato de dicionário e insere no banco
registros = df.to_dict(orient="records")
collection.insert_many(registros)

print(f"Sucesso! {len(registros)} ecopontos inseridos no MongoDB Atlas.")