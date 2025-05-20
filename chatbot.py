from sentence_transformers import SentenceTransformer, util
import json

model = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased-v2')

with open("veri.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

faq_data = {item['soru'].lower().strip(): item['cevap'] for item in data_list}
faq_embeddings = model.encode(list(faq_data.keys()), convert_to_tensor=True)

# Small talk sözlüğü
small_talk = {
    "merhaba": "Merhaba! Size nasıl yardımcı olabilirim?",
    "selam": "Selam! Siber güvenlikle ilgili ne öğrenmek istersiniz?",
    "teşekkürler": "Rica ederim, yardımcı olabildiysem ne mutlu!",
    "teşekkür ederim": "Ne demek, her zaman buradayım!",
    "görüşürüz": "Görüşmek üzere, kendinize dikkat edin!",
    "hoşça kal": "Hoşça kal! Güvende kalın!"
}

# Global değişken: Son quiz soruları ve cevapları burada tutulacak
last_quiz_answers = []

def filter_by_topic_or_level(user_input):
    if user_input.startswith("/konu"):
        topic = user_input.replace("/konu", "").strip().lower()
        filtered = [f"- {item['soru']} → {item['cevap']}" for item in data_list if item['konu'].lower() == topic]
        return "\n".join(filtered) if filtered else "Bu konuyla ilgili bir içerik bulunamadı."

    elif user_input.startswith("/seviye"):
        level = user_input.replace("/seviye", "").strip().lower()
        filtered = [f"- {item['soru']} → {item['cevap']}" for item in data_list if item['seviye'].lower() == level]
        return "\n".join(filtered) if filtered else "Bu seviyeye uygun bir içerik bulunamadı."

    return None

def parse_quiz_command(command):
    topic = None
    level = None

    if "konu=" in command:
        topic = command.split("konu=")[1].split()[0].strip().lower()
    if "seviye=" in command:
        level = command.split("seviye=")[1].split()[0].strip().lower()

    return topic, level

def generate_quiz(topic=None, level=None, num_questions=3):
    filtered = data_list

    if topic:
        filtered = [item for item in filtered if item['konu'].lower() == topic]
    if level:
        filtered = [item for item in filtered if item['seviye'].lower() == level]

    if not filtered:
        return "Bu kriterlere uygun soru bulunamadı."

    selected = filtered[:num_questions]
    quiz_text = "Mini Quiz:\n"
    for i, item in enumerate(selected, 1):
        quiz_text += f"{i}. {item['soru']}\n"

    quiz_text += "\nCevapları görmek için '/cevaplar' yazabilirsin."
    global last_quiz_answers
    last_quiz_answers = selected
    return quiz_text

def chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # Small talk kontrolü
    if user_input in small_talk:
        return small_talk[user_input]

    # Quiz komutu kontrolü
    if user_input.startswith("/quiz"):
        topic, level = parse_quiz_command(user_input)
        return generate_quiz(topic, level)

    if user_input == "/cevaplar":
        if not last_quiz_answers:
            return "Henüz bir quiz yapılmadı."
        return "\n".join([f"{i+1}. {item['cevap']}" for i, item in enumerate(last_quiz_answers)])

    # Komut kontrolü
    komut_cevap = filter_by_topic_or_level(user_input)
    if komut_cevap:
        return komut_cevap

    # Anlamsal arama
    input_embedding = model.encode(user_input, convert_to_tensor=True)
    hits = util.semantic_search(input_embedding, faq_embeddings, top_k=1)
    hit = hits[0][0]

    if hit['score'] > 0.7:
        matched_question = list(faq_data.keys())[hit['corpus_id']]
        return faq_data[matched_question]
    else:
        return "Üzgünüm, bunu anlayamadım. Başka bir soru sorabilir misiniz?"

def main():
    print("Siber Güvenlik Chatbot'a Hoşgeldiniz! Çıkmak için 'exit' yazınız.")
    while True:
        user_input = input("Sen: ")
        if user_input.lower().strip() == "exit":
            print("Chatbot: Görüşürüz!")
            break
        response = chatbot_response(user_input)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    main()
