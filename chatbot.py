from flask import Flask, request, jsonify, render_template, session
from sentence_transformers import SentenceTransformer, util
from llama_cpp import Llama
import json
import os
from uuid import uuid4

app = Flask(__name__)
app.secret_key = 'rafa27'

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

SYSTEM_PROMPT = ("""Sen bir siber güvenlik asistanısın. Aşağıdaki kurallara uy:
1. Teknik sorulara detaylı cevap ver
2. "Detaylandırır mısın" gibi talepleri, önceki soruyla ilişkilendir
3. Kullanıcının son 3 mesajını dikkate al
4. cevap verirken şu formatta hareket et:
Cevaplarında aynı anlama gelen cümleleri kullanma.
Belirgin formatta cevap ver:
   - Tanım
   - Kullanım Amacı (madde işaretiyle)
   - Örnek Kullanım (kısa kod/komut)

Örnek Diyalog:
User: firewall nedir?
Assistant: Firewall, ağ trafiğini kontrol eden güvenlik sistemidir. 
Kullanım Alanları:
- Kurumsal ağlarda
- Bulut sunucularında
Örnek: Stateless firewall paketleri tek tek inceler."""
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

    GREETINGS = {"selam", "slm", "merhaba", "meraba", "s.a", "hello", "hey", "sa"}
    THANKS = {"teşekkür", "sağ ol", "sağol", "eyvallah", "thanks", "thank you"}
    BYE = {"görüşürüz", "bye", "hoşçakal", "güle güle"}
    DETAIL= {"detaylandır", "daha teknik anlat", "daha detaylı", "ayrıntılı açıkla", "detay ver", "aç detay", "daha ayrıntılı", "detay istiyorum"}

    for word in GREETINGS:
        if word in text:
            return "greeting"
    for word in THANKS:
        if word in text:
            return "thanks"
    for word in BYE:
        if word in text:
            return "farewell"
    for word in DETAIL:
        if word in text:
            return "detail_request"
    return "other"

def is_out_of_scope(user_input):
    user_input = user_input.lower()

    if any(word in user_input for word in ["spor", "yemek", "siyaset", "film"]):
        return True
    
    if any(phrase in user_input for phrase in ["başka soru", "başka bir şey", "farklı soru"]):
        return False
        
    security_keywords = [
        "firewall", "nmap", "port", "tarama", "siber", "güvenlik", 
        "ağ", "protokol", "zafiyet", "sızma", "pentest", "ddos"
    ]
    
    question_words = ["nedir", "nasıl", "detay", "açıkla", "nerede", "kullanılır"]
    
    if any(kw in user_input for kw in security_keywords):
        return False
        
    if any(qw in user_input for qw in question_words):
        return False
        
    return True

@app.route("/", methods=["GET"])
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())
        session['chat_history'] = []
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    chat_history = session['chat_history']

    intent = get_intent(user_input)

    if intent == "greeting":
        response = "Merhaba, siber güvenlikle ilgili nasıl yardımcı olabilirim?"
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": response})
        session['chat_history'] = chat_history
        return jsonify({"response": response})
    elif intent == "thanks":
        
        response = "Rica ederim! Yardımcı olabildiysem ne mutlu."
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": response})
        session['chat_history'] = chat_history
        return jsonify({"response": response})
    
    elif intent == "farewell":
        response = "Görüşmek üzere! Güvende kal."
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": response})
        session['chat_history'] = chat_history
        return jsonify({"response": response})

    elif intent == "detail_request":
        previous_bot_messages = [msg["content"] for msg in chat_history if msg["role"] == "bot"]
        if not previous_bot_messages:
            response = "Detaylandıracak bir önceki bilgiye ulaşamıyorum."
        else:
            last_response = previous_bot_messages[-1]
            detail_prompt = (
                SYSTEM_PROMPT +
                f"\nAşağıdaki açıklamayı teknik olarak detaylandır:\n\"{last_response}\"\n" +
                "Daha teknik, ayrıntılı, kod veya komut örnekli anlat:\nAssistant:"
            )
            try:
                output = llm(detail_prompt, max_tokens=256, temperature=0.5, stop=["Soru:", "User:", "###"])
                response = output.get("choices", [{}])[0].get("text", "Detaylı açıklama yapılamadı.").strip()
            except Exception as e:
                print("Detaylandırma hatası:", e)
                response = "Detaylı açıklama yapılırken bir hata oluştu."

    if is_out_of_scope(user_input):
        response = "Bu konuda yardımcı olamam. Siber güvenlikle ilgili bir soru sorabilirsin."
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": response})
        session['chat_history'] = chat_history
        return jsonify({"response": response})

    komut_cevap = handle_command(user_input)
    if komut_cevap:
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": komut_cevap})
        session['chat_history'] = chat_history
        return jsonify({"response": komut_cevap})

    input_embedding = model.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(input_embedding, faq_embeddings, top_k=1)
    hit = hits[0][0]

    context_info = ""
    if hit['score'] > 0.5:
        matched_question = list(faq_data.keys())[hit['corpus_id']]
        context_info = f"- Ek Bilgi: {faq_data[matched_question]}\n"

    chat_history.append({"role": "user", "content": user_input})

    history_prompt = ""
    for msg in chat_history[-6:]:
        role_prefix = "User" if msg["role"] == "user" else "Assistant"
        history_prompt += f"{role_prefix}: {msg['content']}\n"

    full_prompt = SYSTEM_PROMPT + "\n" + context_info + history_prompt + "Assistant:"

    try:
        output = llm(full_prompt, max_tokens=256, temperature=0.5, stop=["Soru:", "User:", "###"])
        answer = output.get("choices", [{}])[0].get("text", "Model cevap veremedi.").strip()
    except Exception as e:
        print("Model hatası:", e)
        answer = "Model cevap verirken bir hata oluştu."

    chat_history.append({"role": "bot", "content": answer})
    session['chat_history'] = chat_history

    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
