import os
import time
import hashlib
import hmac
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==============================================================================
# 1. CONFIGURAÇÕES DA API DA META (WHATSAPP)
# ==============================================================================
# Token de acesso copiado do Graph API Explorer / Painel da Meta
META_ACCESS_TOKEN = "EAAOdvT7JOkgBSP3w3WFTr4NWQlg4OIum8nBtQIa1NAVqFSql8rJMQobZCBsGtbwRZChby4oPR3uuFz61hvataKLENS6FJamLBuh8CgP9JSHhrNZAngZAfZBA5j2AbSzugRdXMTDWsmxC8ZAIJa2fChFm2ZCfTSLFaGTkzpAdIMECa9ZBdegJ2Q1Gh809vsZC4dxwjDJ9jkWdpSewkELJ4PtbycBqOrhG1bH7mPXdt"

# ID do Número de Telefone (Phone Number ID)
META_PHONE_NUMBER_ID = "1187365107801291"

# Senha de verificação criada por você para validar a URL do Webhook com a Meta
VERIFY_TOKEN = "meu_token_seguro_123"

# Versão da API da Meta
API_VERSION = "v25.0"


# ==============================================================================
# 2. CONFIGURAÇÕES DA API DE AFILIADOS DA SHOPEE
# ==============================================================================
# Pegue no painel de Afiliados Shopee > Configurações da Conta > Open API
SHOPEE_APP_KEY = "18371100475"
SHOPEE_APP_SECRET = "R7NZNY7PZWRLB5FOSUFL24MP3DOBJP2E"


# ==============================================================================
# 3. FUNÇÕES AUXILIARES DA SHOPEE
# ==============================================================================
def gerar_link_afiliado_shopee(original_url):
    """
    Gera um link de afiliado rastreável usando a API de Afiliados da Shopee (GraphQL Open API).
    Se as credenciais não estiverem configuradas, retorna o link original.
    """
    if SHOPEE_APP_KEY == "SUA_SHOPEE_APP_KEY_AQUI" or SHOPEE_APP_SECRET == "SEU_SHOPEE_APP_SECRET_AQUI":
        print("[AVISO Shopee] Credenciais da Shopee não preenchidas. Retornando link padrão.")
        return original_url

    timestamp = int(time.time())
    
    # Query GraphQL para conversão de link
    query = """
    mutation {
        generateCustomUrl(originUrl: "%s") {
            shortUrl
        }
    }
    """ % original_url

    # Assinatura HMAC-SHA256 exigida pela Shopee
    base_string = f"{SHOPEE_APP_KEY}{timestamp}{query}{SHOPEE_APP_SECRET}"
    signature = hmac.new(
        SHOPEE_APP_SECRET.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"SHA256 Credential={SHOPEE_APP_KEY}, Timestamp={timestamp}, Signature={signature}"
    }

    payload = {"query": query}
    shopee_endpoint = "https://open-api.affiliate.shopee.com.br/graphql"

    try:
        res = requests.post(shopee_endpoint, json=payload, headers=headers, timeout=10)
        data = res.json()
        short_url = data.get("data", {}).get("generateCustomUrl", {}).get("shortUrl")
        if short_url:
            return short_url
    except Exception as e:
        print(f"[ERRO Shopee API] {e}")

    return original_url


# ==============================================================================
# 4. FUNÇÕES AUXILIARES DA META (WHATSAPP)
# ==============================================================================
def send_whatsapp_message(to_phone_number, text_message):
    """
    Envia mensagens de texto via API Oficial do WhatsApp Cloud.
    """
    url = f"https://graph.facebook.com/{API_VERSION}/{META_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone_number,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": text_message
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response_data = response.json()
        print(f"[LOG] Resposta da Meta: {response_data}")
        return response_data
    except Exception as e:
        print(f"[ERRO WhatsApp Send] {e}")
        return None


# ==============================================================================
# 5. ROTAS DO WEBHOOK (FLASK)
# ==============================================================================
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Validação inicial exigida pela Meta para conectar o Ngrok ao painel Developer.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("[LOG] Webhook verificado com sucesso pela Meta!")
            return challenge, 200
        else:
            print("[ERRO] Falha na verificação. Token incorreto.")
            return "Forbidden", 403
            
    return "Requisição inválida", 400


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Recebe as mensagens do WhatsApp e processa as respostas automáticas.
    """
    data = request.get_json()
    print(f"[LOG] Evento recebido: {data}")

    try:
        if data.get("entry"):
            for entry in data["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            from_number = message["from"]
                            msg_type = message.get("type")

                            if msg_type == "text":
                                user_text = message["text"]["body"].strip().lower()
                                print(f"[LOG] Mensagem de {from_number}: {user_text}")

                                # Lógica de resposta do Bot de Achadinhos
                                if any(kw in user_text for kw in ["oi", "ola", "olá", "iniciar", "menu"]):
                                    reply = (
                                        "👋 *Olá! Bem-vindo ao Bot de Achadinhos Shopee!*\n\n"
                                        "Escolha uma opção digitando o número desejado:\n"
                                        "1️⃣ *Promos* - Ver ofertas em destaque hoje\n"
                                        "2️⃣ *Grupos* - Entrar nos grupos VIP de achadinhos\n"
                                        "3️⃣ *Ajuda* - Como funciona"
                                    )
                                elif "1" in user_text or "promos" in user_text:
                                    # Gera links de afiliado dinâmicos via API Shopee
                                    link_item1 = gerar_link_afiliado_shopee("https://shopee.com.br")
                                    link_item2 = gerar_link_afiliado_shopee("https://shopee.com.br")

                                    reply = (
                                        "🔥 *ACHADINHOS EM DESTAQUE HOJE:*\n\n"
                                        "🎧 *Fone Bluetooth Sem Fio*\n"
                                        "De R$ 89,90 por R$ 29,90!\n"
                                        f"🔗 Compre aqui: {link_item1}\n\n"
                                        "👕 *Kit 3 Camisas Masculinas*\n"
                                        "Com até 50% OFF!\n"
                                        f"🔗 Compre aqui: {link_item2}\n\n"
                                        "💡 _Responda *1* a qualquer momento para ver mais._"
                                    )
                                elif "2" in user_text or "grupos" in user_text:
                                    reply = (
                                        "📢 *Entre no nosso Canal/Grupo VIP:*\n\n"
                                        "Receba achadinhos e cupons exclusivos diariamente em primeira mão!\n"
                                        "🔗 Clique aqui para entrar: https://chat.whatsapp.com/seu-grupo-aqui"
                                    )
                                elif "3" in user_text or "ajuda" in user_text:
                                    reply = (
                                        "❓ *Como funciona?*\n\n"
                                        "Nós garimpamos os melhores cupons e ofertas com desconto real na Shopee e enviamos aqui pra você economizar!\n\n"
                                        "Digite *1* para ver as ofertas de hoje."
                                    )
                                else:
                                    reply = (
                                        "Desculpe, não entendi. 😅\n\n"
                                        "Digite *1* para ver ofertas ou *2* para entrar no grupo VIP."
                                    )

                                # Envia a resposta de volta ao usuário no WhatsApp
                                send_whatsapp_message(from_number, reply)

    except Exception as e:
        print(f"[ERRO Processamento Webhook] {e}")

    return jsonify({"status": "success"}), 200


# ==============================================================================
# 6. EXECUÇÃO DO SERVIDOR (PYDROID 3)
# ==============================================================================
if __name__ == "__main__":
    print("🚀 Servidor de Achadinhos rodando na porta 5000...")
    app.run(host="0.0.0.0", port=5000)
