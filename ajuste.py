from pymongo import MongoClient
import re

# ============================================================
# CONEXÃO COM O MONGODB ATLAS
# ============================================================

uri = "mongodb+srv://ecoponto:emerson@ecoponto.qozypnw.mongodb.net/?appName=ecoponto"

client = MongoClient(uri)

db = client["pi_ecoponto"]
collection = db["ecopontos"]


# ============================================================
# BUSCA REGISTROS QUE POSSUEM "PODA"
# ============================================================

ecopontos = collection.find({
    "materiais_aceitos": {
        "$regex": r"\bpoda\b",
        "$options": "i"
    }
})


contador = 0


# ============================================================
# NORMALIZAÇÃO
# ============================================================

for doc in ecopontos:

    material_atual = doc.get("materiais_aceitos", "")

    if not isinstance(material_atual, str):
        continue

    # "poda de árvore" OU "poda" → "poda de árvores"
    novo_material = re.sub(
        r"\bpoda(?:\s+de\s+árvore)?\b",
        "poda de árvores",
        material_atual,
        flags=re.IGNORECASE
    )

    # Atualiza somente se realmente houve alteração
    if novo_material != material_atual:

        collection.update_one(
            {"_id": doc["_id"]},
            {
                "$set": {
                    "materiais_aceitos": novo_material
                }
            }
        )

        contador += 1


# ============================================================
# FINALIZAÇÃO
# ============================================================

print(
    f"Atualização concluída com sucesso! "
    f"{contador} registros foram atualizados."
)

client.close()