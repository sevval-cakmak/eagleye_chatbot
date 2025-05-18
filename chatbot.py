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

def chatbot_response(user_input):
    user_input = user_input.lower().strip()

    # Small talk kontrolü
    if user_input in small_talk:
        return small_talk[user_input]

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
