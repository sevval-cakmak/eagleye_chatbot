# 🦅 EagleEye Chatbot

EagleEye, Python, HuggingFace SentenceTransformer ve LLaMA tabanlı büyük dil modeli kullanılarak geliştirilmiş, Türkçe destekli ve siber güvenlik odaklı bir akıllı sohbet botudur. Anlamsal arama yeteneklerini LLaMA modeliyle birleştirerek güçlü ve esnek bir sohbet deneyimi sunar.

## Özellikler

LLaMA destekli güçlü yanıt motoru:
GGUF formatında optimize edilmiş Meta LLaMA 3 modeli ile doğal ve anlamlı yanıtlar üretir.

Çok dilli ve Türkçe desteği:
HuggingFace’in Distiluse-base-multilingual-cased-v2 modeli sayesinde Türkçe dahil birçok dili anlayabilir.

Siber güvenlik odaklı bilgi tabanı:
Önceden tanımlanmış soru-cevap veri kümesi ile siber güvenlik konularında hızlı ve alakalı cevaplar sunar.

Anlamsal benzerlik arama:
Kullanıcıdan gelen sorular embedding'e dönüştürülür, en yakın eşleşme veri.json üzerinden belirlenerek gerekirse LLaMA ile detaylandırılır.

Kolay genişletilebilir yapı:
veri.json dosyasına yeni soru-cevap çiftleri eklenerek bilgi tabanı zenginleştirilebilir.

Komut satırı veya web arayüzü desteği:
Terminal üzerinden sohbet edilebilir veya Flask tabanlı basit bir web arayüzü kullanılabilir.

## Klasör Yapısı

eagleye/
├── templates/
│   └── index.html
│
├── models/
│   └── Meta-Llama-3-8B.Q4_K_S.gguf
│
├── chatbot.py
├── veri.json
├── requirements.txt
├── README.md   

## Gereksinimler

Python 3.7 veya üzeri

Flask

sentence-transformers

llama-cpp-python

## Gerekli kütüphaneleri kurmak için:

pip install flask sentence-transformers llama-cpp-python

## Çalıştırma

python chatbot.py

## Notlar

models/ klasörü altındaki .gguf dosyası oldukça büyük olabilir. LLaMA modelinin çalışabilmesi için sisteminizde yeterli RAM ve CPU/GPU kaynakları bulunmalıdır.

LLaMA modeli ile entegrasyon, chatbot.py dosyasında llama-cpp-python üzerinden gerçekleştirilir.
