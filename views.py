from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json, os

# AI model kütüphaneleri
from sentence_transformers import SentenceTransformer, util
from llama_cpp import Llama

# 🧠 Modeli baştan yükleyelim (1 kez):
llama_path = r"C:\Users\Feriha\Desktop\EagleEye\eagle_eye\chat\models\Meta-Llama-3-8B.Q4_K_S.gguf"

llm = Llama(model_path=llama_path, n_ctx=2048, n_threads=4, n_gpu_layers=30)

# 🧠 Embedding modelini de 1 kez yükle:
model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')


def get_llama_response(prompt):
    full_prompt = prompt + "\nCevap:"
    output = llm(full_prompt, max_tokens=256, temperature=0.5, stop=["User:", "###"])
    return output.get("choices", [{}])[0].get("text", "Model cevap veremedi.").strip()


@login_required(login_url='index')
def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message', '').strip()

        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            veri_path = os.path.join(dir_path, "veri.json")
            with open(veri_path, "r", encoding="utf-8") as f:
                data_list = json.load(f)

            # Soru-cevap verisini ayıkla
            faq_data = {
                item['soru'].lower().strip(): item['cevap']
                for item in data_list
                if 'soru' in item and 'cevap' in item
            }

            # Soru embedding'lerini oluştur
            faq_embeddings = model.encode(list(faq_data.keys()), convert_to_tensor=True)
            user_embedding = model.encode(user_message, convert_to_tensor=True)

            # En yakın eşleşmeyi bul
            similarities = util.cos_sim(user_embedding, faq_embeddings)[0]
            best_score = float(similarities.max())
            best_match_idx = int(similarities.argmax())

            matched_question = list(faq_data.keys())[best_match_idx]

            # Eğer benzerlik yüksekse hazır cevabı ver, değilse Llama kullan
            if best_score > 0.7:
                bot_response = faq_data[matched_question]
            else:
                bot_response = get_llama_response(user_message)

        except Exception as e:
            bot_response = f"Hata oluştu: {str(e)}"

        return render(request, 'chat/chatbot.html', {
            'bot_response': bot_response,
            'user_message': user_message,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name
        })

    # GET request için boş sayfa
    return render(request, 'chat/chatbot.html', {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name
    })
