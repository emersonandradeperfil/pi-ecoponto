import json
from google.genai import types

from config.ambiente import obter_client_gemini, obter_client_groq

# ============================================================
#  [IA] PROMPTS E MAPEAMENTOS
# ============================================================

# Mapeamento de siglas/variações para o nome oficial da zona no banco
MAPA_ZONAS = {
    "zl": "Zona Leste", "zona leste": "Zona Leste", "leste": "Zona Leste",
    "zo": "Zona Oeste", "zona oeste": "Zona Oeste", "oeste": "Zona Oeste",
    "zn": "Zona Norte", "zona norte": "Zona Norte", "norte": "Zona Norte",
    "zs": "Zona Sul",   "zona sul": "Zona Sul",     "sul": "Zona Sul",
    "centro": "Centro", "região central": "Centro", "centro sp": "Centro",
}

# Prompt de sistema: extrai material, bairro/nome E zona separadamente
PROMPT_SISTEMA_EXTRACAO = """
Você é um assistente especialista em triagem de descarte de resíduos da cidade de São Paulo.
Sua única tarefa é ler a mensagem do usuário e extrair estruturadamente:
1. O MATERIAL ou objeto que ele deseja descartar (ex: entulho, sofá, lâmpada).
2. O BAIRRO ou nome de local específico mencionado (ex: Penha, Vila Esperança, Lapa).
3. A ZONA geográfica mencionada, se houver (ex: Zona Leste, ZL, ZO, Zona Sul, Centro).
   - Preencha 'zona' APENAS se o usuário mencionou explicitamente uma zona/região ampla.
   - Se mencionou bairro específico, deixe 'zona' como null.
   - Normalize siglas: ZL = Zona Leste, ZO = Zona Oeste, ZN = Zona Norte, ZS = Zona Sul.

Você DEVE responder única e exclusivamente com um objeto JSON válido contendo as chaves:
'material', 'bairro' e 'zona'.
Se não conseguir identificar alguma informação, preencha com null.
Não inclua nenhuma formatação markdown (como ```json) na resposta.
"""


# ============================================================
#  [IA] FUNÇÃO COM FALLBACK AUTOMÁTICO GEMINI → GROQ
# ============================================================
def chamar_ia_com_fallback(prompt_usuario: str, prompt_sistema: str) -> dict:
    """
    Tenta extrair material, bairro e zona via Gemini.
    Se falhar por qualquer motivo (cota, erro, etc.), usa Llama 3.1 (Groq) como fallback.
    Retorna sempre um dict com as chaves 'material', 'bairro' e 'zona'.
    """
    client_gemini = obter_client_gemini()
    client_groq = obter_client_groq()

    # ── Tentativa 1: Gemini ──
    try:
        config = types.GenerateContentConfig(
            system_instruction=prompt_sistema,
            response_mime_type="application/json",
            temperature=0.1
        )
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_usuario,
            config=config
        )
        dados = json.loads(response.text)
        dados["_modelo_usado"] = "Gemini 2.5 Flash"
        return dados

    except Exception as err_gemini:
        # ── Fallback: Llama 3.1 8B via Groq ──
        try:
            response_groq = client_groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.1,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user",   "content": prompt_usuario}
                ]
            )
            dados = json.loads(response_groq.choices[0].message.content)
            dados["_modelo_usado"] = "Llama 3.1 8B via Groq (fallback)"
            return dados

        except Exception as err_groq:
            raise RuntimeError(
                f"Ambas as IAs falharam.\nGemini: {err_gemini}\nGroq: {err_groq}"
            )


def normalizar_zona(zona_detectada):
    """Normaliza a zona pelo mapa de siglas (cobre casos que a IA não normalizou)."""
    if zona_detectada:
        return MAPA_ZONAS.get(zona_detectada.lower().strip(), zona_detectada)
    return zona_detectada
