from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
from llama_cpp import Llama
import json
import os

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "veri.json"), "r", encoding="utf-8") as f:
    data_list = json.load(f)

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
faq_data = {
    item['soru'].lower().strip(): item['cevap']
    for item in data_list
    if 'soru' in item and 'cevap' in item
}
faq_embeddings = model.encode(list(faq_data.keys()), convert_to_tensor=True)

llama_path = r"C:\Users\Elif\Desktop\rafa\models\Meta-Llama-3-8B.Q4_K_S.gguf"
llm = Llama(model_path=llama_path, n_ctx=2048, n_threads=4, n_gpu_layers=30)

SYSTEM_PROMPT = (
    "Sen bir siber güvenlik uzmanısın. Yalnızca ağ güvenliği, port tarama, protokoller, zafiyet analizleri gibi konularda cevap ver. "
    "Konu dışı bir şey sorulursa 'Bu konuda yardımcı olamam. Siber güvenlikle ilgili bir soru sorabilirsin.' de.\n"
    "User: Merhaba!\nAssistant: Merhaba, siber güvenlikle ilgili nasıl yardımcı olabilirim?\n"
)

def get_llama_response(prompt):
    try:
        full_prompt = SYSTEM_PROMPT + "\nSoru: " + prompt + "\nCevap:"
        output = llm(full_prompt, max_tokens=256, temperature=0.5, stop=["Soru:", "User:", "###"])
        return output.get("choices", [{}])[0].get("text", "Model cevap veremedi.").strip()
    except Exception as e:
        print("Modelden cevap alınamadı:", e)
        return "Model cevap verirken bir hata oluştu."

def handle_command(command):
    if "tara" in command:
        return "Nmap taraması başlatılıyor... (Bu sadece örnek bir çıktı!)"
    elif "ağ trafiğini izle" in command or "trafiği izle" in command:
        return "Tshark ile ağ trafiği izleniyor... (Bu sadece örnek bir çıktı!)"
    return None

def get_intent(text):
    text = text.lower().strip()

    GREETINGS = {"selam", "slm", "merhaba", "s.a", "hey", "sa"}
    THANKS = {"teşekkür", "sağ ol", "eyvallah", "thanks", "thank you"}
    BYE = {"görüşürüz", "bye", "hoşçakal"}

    for word in GREETINGS:
        if word in text:
            return "greeting"
    for word in THANKS:
        if word in text:
            return "thanks"
    for word in BYE:
        if word in text:
            return "farewell"
    return "other"

def is_out_of_scope(user_input):
    allowed_keywords = [
        "siber", "güvenlik", "ağ", "nmap", "tshark", "port", "firewall",
        "zararlı yazılım", "scan", "exploit", "ddos", "vpn", "phishing"
    ]
    return not any(keyword in user_input.lower() for keyword in allowed_keywords)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

chat_history = []  # Basit senaryo için global mesaj geçmişi (tek kullanıcı)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()

    # Intent belirle
    intent = get_intent(user_input)

    # Selamlaşma / Teşekkür / Veda
    if intent == "greeting":
        return jsonify({"response": "Merhaba, siber güvenlikle ilgili nasıl yardımcı olabilirim?"})
    elif intent == "thanks":
        return jsonify({"response": "Rica ederim! Yardımcı olabildiysem ne mutlu."})
    elif intent == "farewell":
        return jsonify({"response": "Görüşmek üzere! Güvende kal."})

    # Bağlam dışı kontrol
    if is_out_of_scope(user_input):
        return jsonify({"response": "Bu konuda yardımcı olamam. Siber güvenlikle ilgili bir soru sorabilirsin."})

    # Komut algılama
    komut_cevap = handle_command(user_input)
    if komut_cevap:
        return jsonify({"response": komut_cevap})

    # Embedding ile veri.json'dan yakın cevap çek (RAG)
    input_embedding = model.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(input_embedding, faq_embeddings, top_k=1)
    hit = hits[0][0]

    context_info = ""
    if hit['score'] > 0.5:
        matched_question = list(faq_data.keys())[hit['corpus_id']]
        context_info = f"- Ek Bilgi: {faq_data[matched_question]}\n"

    if len(chat_history) == 0 or chat_history[-1]['content'] != user_input:
        chat_history.append({"role": "user", "content": user_input})

    # Son 3 tur geçmişten bağlam oluştur (user + bot)
    history_prompt = ""
    for msg in chat_history[-6:]:
        role_prefix = "User" if msg["role"] == "user" else "Assistant"
        history_prompt += f"{role_prefix}: {msg['content']}\n"

    # LLaMA'dan cevap al
    full_prompt = SYSTEM_PROMPT + "\n" + context_info + history_prompt + "Assistant:"

    try:
        output = llm(full_prompt, max_tokens=256, temperature=0.5, stop=["Soru:", "User:", "###"])
        answer = output.get("choices", [{}])[0].get("text", "Model cevap veremedi.").strip()
    except Exception as e:
        print("Model hatası:", e)
        answer = "Model cevap verirken bir hata oluştu."

    # Bot cevabını da geçmişe ekle
    if len(chat_history) == 0 or chat_history[-1]['content'] != answer:
        chat_history.append({"role": "bot", "content": answer})

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
