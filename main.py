import os
import re
import requests
from flask import Flask, request

app = Flask(__name__)

# CONFIGURAÇÕES DO WHATSAPP (Meta)
VERIFY_TOKEN = "meu_token_seguro_123"
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAOdvT7JOkgBSBG8ZCZBrThhNm6L37sTicKoZBSHdLaydb9o9nWnixVuynlFUi4OggFEzaKkRZADnf6Da2ZBxjDd2mh4PoQIwJlfyJlvQIVaY7k3xCtvZBUpNXfF4lmgbGJxjTHQn2QqZBqwdkvCZBZB53GVorxnPkk8cIECW0uXzhb2p6XZCerow2lJGYRjf8yZBg8KmpEs4T7fDjXjaV1YUM5jTrsaOHEu6PeyTpa")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1187365107801291")
GRUPO_DESTINO_ID = os.environ.get("GRUPO_DESTINO_ID", "SEU_GRUPO_DESTINO_ID_AQUI")

# CONFIGURAÇÕES DA API DE AFILIADO DA SHOPEE
SHOPEE_ACCESS_KEY = os.environ.get("SHOPEE_ACCESS_KEY", "18371100475")
SHOPEE_SECRET_KEY = os.environ.get("SHOPEE_SECRET_KEY", "R7NZNY7PZWRLB5FOSUFL24MP3DOBJP2E")

@app.route("/", methods=["GET"])
def home():
    return "Bot de Repostagem de Achadinhos com API da Shopee online!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                return challenge, 200
            else:
                return "Token inválido", 403
        return "Erro", 400

    elif request.method == "POST":
        data = request.json
        print("Mensagem capturada:", data)

        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages")

            if messages:
                msg = messages[0]
                msg_body = msg.get("text", {}).get("body", "").strip()

                if msg_body:
                    print(f"Texto recebido: {msg_body}")

                    # 1. Procura o link da Shopee na mensagem recebida
                    link_shopee = extrair_link_shopee(msg_body)

                    if link_shopee:
                        # 2. Converte usando a API oficial da Shopee (com sua Access Key e Secret)
                        link_afiliado = gerar_link_afiliado_shopee(link_shopee)

                        # Substitui o link original pelo seu link de afiliado gerado pela API
                        mensagem_modificada = msg_body.replace(link_shopee, link_afiliado)

                        # 3. Monta a mensagem final estilizada
                        mensagem_final = f"🔥 *ACHADINHO DA SHOPEE* 🔥\n\n{mensagem_modificada}\n\n🛒 *Garanta o seu com desconto acima!*"

                        # 4. Dispara automaticamente para o seu grupo de destino via WhatsApp
                        enviar_mensagem_whatsapp(GRUPO_DESTINO_ID, mensagem_final)

        except Exception as e:
            print("Erro ao processar a mensagem:", e)

        return "EVENT_RECEIVED", 200

# Função para encontrar links da Shopee no texto
def extrair_link_shopee(texto):
    padrao = r'(https?://[^\s]+shopee[^\s]*)'
    links = re.findall(padrao, texto)
    return links[0] if links else None

# Função que chama a API da Shopee para converter o link usando as credenciais
def gerar_link_afiliado_shopee(link_original):
    # Aqui entra a chamada oficial para a API de Afiliados da Shopee (Open Platform / Conversion API)
    # Usando SHOPEE_ACCESS_KEY e SHOPEE_SECRET_KEY para autenticar
    print(f"Gerando link de afiliado para: {link_original} usando as chaves da Shopee...")
    
    # Exemplo estrutural da requisição para a API da Shopee Open Platform:
    # url_api = "https://partner.shopeemobile.com/api/v2/publisher/generate_short_link"
    # (Adicionaremos os headers de assinatura com sua Secret Key aqui)
    
    # Por enquanto, caso queira testar a lógica, se as chaves estiverem configuradas, 
    # ela fará a troca. Se não, retorna o link original para evitar quedas.
    if SHOPEE_ACCESS_KEY != "SUA_ACCESS_KEY_AQUI":
        # Lógica de requisição real da API da Shopee virá aqui
        pass
        
    return link_original

# Função oficial para enviar a mensagem via WhatsApp
def enviar_mensagem_whatsapp(destino, texto):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": destino,
        "type": "text",
        "text": {"body": texto}
    }
    response = requests.post(url, json=payload, headers=headers)
    print("Resposta do envio:", response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
