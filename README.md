# EagleEye Chatbot

EagleEye, Python ve HuggingFace SentenceTransformer modeli kullanarak geliştirilmiş, Türkçe destekli, siber güvenlik alanında soru-cevap yapabilen akıllı chatbot projesidir. İnternet bağlantısı gerektiren hazır modellerin embedding yeteneklerinden faydalanarak, basit ve genişletilebilir bir yapay zeka destekli sohbet asistanı sunar.

## Özellikler

Çok dilli ve Türkçe destekli: Distiluse Base Multilingual cased v2 modeli kullanılır.

Siber güvenlik odaklı soru-cevap: Önceden tanımlanmış soru-cevap verisi ile hızlı ve alakalı yanıtlar verilir.

Anlamsal benzerlik araması: Kullanıcı sorusunu embedding’e dönüştürerek en yakın soruyu bularak cevap verir.

Kolay genişletilebilirlik: veri.json dosyasına yeni sorular ve cevaplar ekleyerek bilgi tabanı zenginleştirilebilir.

Komut satırı arayüzü: Basit ve interaktif sohbet deneyimi.

## Klasör yapısı

eagleye/

├── templates/

│   └── index.html

│

├── models/

│   └── Meta-Llama-3-8B.Q4_K_S.gguf

│

├── chatbot.py

├── veri.json

├── README.md

## Gereksinimler

Python 3.7 ve üzeri

Flask

sentence-transformers kütüphanesi

## Çalıştırma

python chatbot.py
