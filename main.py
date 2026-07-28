import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Token de verificação da Meta (usado na hora de configurar o Webhook)
VERIFY_TOKEN = "meu_token_seguro_123"

# Credenciais da API do WhatsApp (puxadas do Render ou colocadas diretamente aqui)
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "EAAOdvT7JOkgBSP3w3WFTr4NWQlg4OIum8nBtQIa1NAVqFSql8rJMQobZCBsGtbwRZChby4oPR3uuFz61hvataKLENS6FJamLBuh8CgP9JSHhrNZAngZAfZBA5j2AbSzugRdXMTDWsmxC8ZAIJa2fChFm2ZCfTSLFaGTkzpAdIMECa9ZBdegJ2Q1Gh809vsZC4dxwjDJ9jkWdpSewkELJ4PtbycBqOrhG1bH7mPXdt")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID", "1187365107801291")

# Credenciais da Shopee (puxadas do Render)
SHOPEE_API_KEY = os.environ.get("1187365107801291")
SHOPEE_PARTNER_ID = os.environ.get("R7NZNY7PZWRLB5FOSUFL24MP3DOBJP2E")

@app.route("/", methods=["GET"])
def home():
    return "Bot de Achadinhos da Shopee está online e rodando 24h na nuvem!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Validação exigida pela Meta (Facebook / WhatsApp)
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode and token:
            if mode == "subscribe" and token == VERIFY_TOKEN:
                print("Webhook verificado com sucesso pela Meta!")
                return challenge, 200
            else:
                return "Token de verificação inválido", 403
        return "Parâmetros ausentes", 400

    elif request.method == "POST":
        # Recebendo as mensagens enviadas pelos usuários no WhatsApp
        data = request.json
        print("Mensagem recebida do WhatsApp:", data)

        try:
            entry = data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            messages = value.get("messages")

            if messages:
                msg = messages[0]
                sender_phone = msg.get("from") # Número do usuário que mandou a mensagem
                msg_body = msg.get("text", {}).get("body", "").strip() # Texto enviado
                
                print(f"Mensagem de {sender_phone}: {msg_body}")

                # Exemplo de resposta automática usando a API do WhatsApp configurada acima:
                # enviar_mensagem_whatsapp(sender_phone, f"Olá! Vi que você mandou: '{msg_body}'. Em breve mandarei os achadinhos!")

        except Exception as e:
            print("Erro ao processar a mensagem:", e)

        return "EVENT_RECEIVED", 200

# Função oficial para enviar mensagens de volta pelo WhatsApp
def enviar_mensagem_whatsapp(numero_destino, texto_resposta):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto_resposta}
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
