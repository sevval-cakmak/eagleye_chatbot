import subprocess
import json
import os
import re
from uuid import uuid4
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sentence_transformers import SentenceTransformer, util
from llama_cpp import Llama

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(BASE_DIR, "veri.json"), "r", encoding="utf-8") as f:
    data_list = json.load(f)

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
faq_data = {
    item['soru'].lower().strip(): item['cevap']
    for item in data_list
    if 'soru' in item and 'cevap' in item
}
faq_embeddings = model.encode(list(faq_data.keys()), convert_to_tensor=True)

llama_path = r"LLAMA_MODELİNİN_YOLU"
llm = Llama(model_path=llama_path, n_ctx=2048, n_threads=4, n_gpu_layers=30)

SYSTEM_PROMPT = ("""Sen bir siber güvenlik asistanısın. Aşağıdaki kurallara uy:
1. Teknik sorulara detaylı cevap ver
2. "Detaylandırır mısın","Ayrıntılı anlatır mısın","Detaylı anlatır mısın" gibi talepleri, önceki soruyla ilişkilendir.
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
Örnek: Stateless firewall paketleri tek tek inceler.""")

def extract_ip(text):
    match = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', text)
    return match.group(1) if match else None

def extract_interface(text):
    match = re.search(r"trafiğini izle\s+([\w-]+)", text.lower())
    return match.group(1) if match else None

def run_nmap_scan(user_input):
    ip = extract_ip(user_input)
    if not ip:
        return "Lütfen nmap taraması için geçerli bir IP adresi belirtin. Örnek: 'nmap tara 192.168.1.5'"
    try:
        result = subprocess.check_output(
            ["nmap", "-sV", ip],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=20
        )
        return f"Nmap tarama ({ip}) tamamlandı:\n\n{result[:700]}..."
    except subprocess.TimeoutExpired:
        return "Nmap taraması zaman aşımına uğradı."
    except Exception as e:
        return f"Nmap hatası: {e}"

def run_tshark_capture(user_input, duration=10):
    interface = extract_interface(user_input)
    if not interface:
        return "Lütfen tshark için izlemek istediğiniz arayüzü belirtin. Örnek: 'ağ trafiğini izle Wi-Fi'"
    try:
        result = subprocess.check_output(
            ["tshark", "-i", interface, "-a", f"duration:{duration}", "-c", "10"],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return f"Tshark ({interface}) ile trafik izlendi:\n\n{result}"
    except Exception as e:
        return f"Tshark hatası: {e}"

def handle_command(command, session):
    command = command.lower()

    if not session.get("user_consent", False):
        return "Lütfen devam etmeden önce ağ taraması ve trafik izlemeye açık rıza verdiğinizi belirtin. 'Tarama için onay veriyorum' yazmanız yeterlidir."

    if "nmap" in command or "tara" in command:
        return run_nmap_scan(command)
    elif "tshark" in command or "ağ trafiğini izle" in command or "trafiği izle" in command:
        return run_tshark_capture(command)
    return None

def get_intent(text):
    text = text.lower().strip()

    GREETINGS = {"selam", "slm", "merhaba", "meraba", "s.a", "hello", "hey", "sa"}
    THANKS = {"teşekkür", "sağ ol", "sağol", "eyvallah", "thanks", "thank you"}
    BYE = {"görüşürüz", "bye", "hoşçakal", "güle güle"}
    DETAIL = {"detaylandır", "daha teknik anlat", "daha detaylı", "ayrıntılı açıkla", "detay ver", "aç detay", "daha ayrıntılı", "detay istiyorum"}

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

def home(request):
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid4())
        request.session['chat_history'] = []
    return render(request, "index.html")

@csrf_exempt
def chat(request):
    if request.method != "POST":
        return JsonResponse({"response": "Invalid request method."}, status=405)

    data = json.loads(request.body)
    user_input = data.get("message", "").strip()
    session = request.session
    chat_history = session.get("chat_history", [])

    if "tarama için onay veriyorum" in user_input.lower():
        session["user_consent"] = True
        response = "Teşekkürler, onayınız alındı. Artık tarama ve ağ trafiği işlemlerine devam edebilirim. Hangi taramayı yapmak istediğinizi bir kez daha belirtir misiniz?"
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "bot", "content": response})
        session['chat_history'] = chat_history
        return JsonResponse({"response": response})

    intent = get_intent(user_input)

    if intent == "greeting":
        response = "Merhaba, siber güvenlikle ilgili nasıl yardımcı olabilirim?"
    elif intent == "thanks":
        response = "Rica ederim! Yardımcı olabildiysem ne mutlu."
    elif intent == "farewell":
        response = "Görüşmek üzere! Güvende kal."
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
    elif is_out_of_scope(user_input):
        response = "Bu konuda yardımcı olamam. Siber güvenlikle ilgili bir soru sorabilirsin."
    else:
        komut_cevap = handle_command(user_input)

        if not komut_cevap:
            input_embedding = model.encode(user_input, convert_to_tensor=True)
            hits = util.semantic_search(input_embedding, faq_embeddings, top_k=1)
            hit = hits[0][0]
            context_info = ""
            if hit['score'] > 0.5:
                matched_question = list(faq_data.keys())[hit['corpus_id']]
                context_info = f"- Ek Bilgi: {faq_data[matched_question]}\n"

            history_prompt = ""
            for msg in chat_history[-6:]:
                role_prefix = "User" if msg["role"] == "user" else "Assistant"
                history_prompt += f"{role_prefix}: {msg['content']}\n"

            full_prompt = SYSTEM_PROMPT + "\n" + context_info + history_prompt + f"User: {user_input}\nAssistant:"
            try:
                output = llm(full_prompt, max_tokens=256, temperature=0.5, stop=["Soru:", "User:", "###"])
                response = output.get("choices", [{}])[0].get("text", "Model cevap veremedi.").strip()
            except Exception as e:
                print("Model hatası:", e)
                response = "Model cevap verirken bir hata oluştu."
        else:
            response = komut_cevap

    chat_history.append({"role": "user", "content": user_input})
    chat_history.append({"role": "bot", "content": response})
    session['chat_history'] = chat_history
    return JsonResponse({"response": response})
    
