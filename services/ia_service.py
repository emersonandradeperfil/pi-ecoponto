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

# ------------------------------------------------------------
# Prompt de sistema: agora define uma persona de CONSULTOR
# ambiental humanizado, que também extrai dados a partir de
# TODO o histórico da conversa (não só da última mensagem).
# ------------------------------------------------------------
PROMPT_SISTEMA_CONSULTOR = """
Você é o assistente virtual do Ecoponto SP: um consultor ambiental humanizado, não um robô
de extração de dados. Fale de forma simpática, natural e educada, como um atendente real.

SEU PAPEL:
1. Se o usuário parecer não saber o que é um ecoponto, ou fizer perguntas gerais sobre o
   serviço, explique com clareza (ex.: o que é, que é gratuito, o limite de descarte de até
   1m³ por vez por pessoa, que aceita entulho, móveis, eletrônicos, poda, etc.) e tire as
   dúvidas antes de avançar.
2. Só depois de esclarecer dúvidas (ou se o usuário já não tiver nenhuma), conduza a conversa
   para coletar as duas informações necessárias para localizar ecopontos:
   - o MATERIAL que a pessoa deseja descartar;
   - a LOCALIZAÇÃO: um bairro/local específico OU uma zona ampla (Zona Leste, Zona Oeste,
     Zona Norte, Zona Sul, Centro).
3. Você recebe o HISTÓRICO COMPLETO da conversa (não apenas a última mensagem). Use-o para
   lembrar informações já ditas antes. Se o material foi dito em uma mensagem e o bairro em
   outra mensagem posterior (mesmo sem relação textual aparente), você deve unir as duas
   informações. Nunca "esqueça" um dado já informado anteriormente na conversa.
4. Normalize siglas de zona: ZL = Zona Leste, ZO = Zona Oeste, ZN = Zona Norte, ZS = Zona Sul.
   Se o usuário mencionou um bairro específico, deixe "zona" como null (bairro tem prioridade).

FORMATO DE SAÍDA (OBRIGATÓRIO E ÚNICO):
Responda SEMPRE e SOMENTE com um objeto JSON válido (sem markdown, sem ```), com exatamente
estas chaves:
- "resposta_ao_usuario": (string) o texto humanizado a ser exibido no chat — pode ser uma
  explicação, resposta a uma dúvida, ou uma pergunta conduzindo para o próximo dado que falta.
- "material": (string ou null) material identificado até agora, considerando toda a conversa.
- "bairro": (string ou null) bairro/local específico identificado, se houver.
- "zona": (string ou null) zona ampla identificada, se houver (só quando não há bairro específico).
- "pronto_para_buscar": (boolean) true SOMENTE quando já houver material E (bairro OU zona)

Nunca inclua texto fora do JSON.
"""

# Mantido por compatibilidade/retrocompatibilidade com outras partes do código
PROMPT_SISTEMA_EXTRACAO = PROMPT_SISTEMA_CONSULTOR


# ============================================================
#  [IA] HELPERS DE CONSTRUÇÃO DE HISTÓRICO POR PROVEDOR
# ============================================================
def _construir_historico_gemini(historico_mensagens: list[dict]) -> list:
    """Converte [{'role': 'user'/'assistant', 'content': str}, ...] no formato
    de turnos esperado pela API do Gemini ('user' / 'model')."""
    turnos = []
    for msg in historico_mensagens:
        papel_gemini = "model" if msg["role"] == "assistant" else "user"
        turnos.append(types.Content(role=papel_gemini, parts=[types.Part(text=msg["content"])]))
    return turnos


def _construir_historico_groq(historico_mensagens: list[dict], prompt_sistema: str) -> list[dict]:
    """Monta a lista de mensagens no formato OpenAI-compatible usado pela Groq."""
    mensagens = [{"role": "system", "content": prompt_sistema}]
    for msg in historico_mensagens:
        mensagens.append({"role": msg["role"], "content": msg["content"]})
    return mensagens


# ============================================================
#  [IA] FUNÇÃO COM FALLBACK AUTOMÁTICO GEMINI → GROQ
# ============================================================
def chamar_ia_com_fallback(historico_mensagens: list[dict], prompt_sistema: str = PROMPT_SISTEMA_CONSULTOR) -> dict:
    """
    Envia o HISTÓRICO da conversa (lista de {'role', 'content'}) para a IA, para que ela
    tenha memória de curto prazo dentro da sessão. Tenta Gemini primeiro; se falhar por
    qualquer motivo (cota, erro, etc.), usa Llama 3.1 (Groq) como fallback.

    Retorna sempre um dict com as chaves:
    'resposta_ao_usuario', 'material', 'bairro', 'zona', 'pronto_para_buscar', '_modelo_usado'.
    """
    client_gemini = obter_client_gemini()
    client_groq = obter_client_groq()

    # ── Tentativa 1: Gemini ──
    try:
        config = types.GenerateContentConfig(
            system_instruction=prompt_sistema,
            response_mime_type="application/json",
            temperature=0.2
        )
        contents = _construir_historico_gemini(historico_mensagens)
        response = client_gemini.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=config
        )
        dados = json.loads(response.text)
        dados["_modelo_usado"] = "Gemini 2.5 Flash"
        return dados

    except Exception as err_gemini:
        # ── Fallback: Llama 3.1 8B via Groq ──
        try:
            mensagens = _construir_historico_groq(historico_mensagens, prompt_sistema)
            response_groq = client_groq.chat.completions.create(
                model="llama-3.1-8b-instant",
                temperature=0.2,
                response_format={"type": "json_object"},
                messages=mensagens
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
