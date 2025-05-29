from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer, util
from llama_cpp import Llama
import json
import os

app = Flask(__name__)

# Veri dosyasını oku
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "veri.json"), "r", encoding="utf-8") as f:
    data_list = json.load(f)

# Embedding modeli
model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')
faq_data = {
    item['soru'].lower().strip(): item['cevap']
    for item in data_list
    if 'soru' in item and 'cevap' in item
}
faq_embeddings = model.encode(list(faq_data.keys()), convert_to_tensor=True)

# LLaMA modelini yükle
llama_path = r"C:\Users\Elif\Desktop\rafa\models\Meta-Llama-3-8B.Q4_K_S.gguf"
llm = Llama(model_path=llama_path, n_ctx=2048, n_threads=4, n_gpu_layers=30)

# Sistem promptu: sadece siber güvenlik sorularına yanıt ver
SYSTEM_PROMPT = (
    "Sen bir siber güvenlik uzmanısın. Yalnızca ağ güvenliği, port tarama, protokoller, zafiyet analizleri gibi konularda cevap ver. "
    "Konu dışı bir şey sorulursa 'Bu konuda yardımcı olamam. Siber güvenlikle ilgili bir soru sorabilirsin.' de.\n"
)

def get_llama_response(prompt):
    full_prompt = SYSTEM_PROMPT + "\nSoru: " + prompt + "\nCevap:"
    output = llm(full_prompt, max_tokens=512, temperature=0.7, stop=["Soru:", "User:", "###"])
    return output["choices"][0]["text"].strip()

# Komut işleyici (nmap/tshark gibi)
def handle_command(command):
    if "tara" in command:
        return "Nmap taraması başlatılıyor... (Bu sadece örnek bir çıktı!)"
    elif "ağ trafiğini izle" in command or "trafiği izle" in command:
        return "Tshark ile ağ trafiği izleniyor... (Bu sadece örnek bir çıktı!)"
    return None

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").lower().strip()

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

    # LLaMA'dan cevap al
    full_prompt = context_info + user_input
    answer = get_llama_response(full_prompt)
    return jsonify({"response": answer})

if __name__ == "__main__":
    app.run(debug=True)
