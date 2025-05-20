# EagleEye Chatbot

EagleEye, Python ve HuggingFace SentenceTransformer modeli kullanarak geliştirilmiş, Türkçe destekli, siber güvenlik alanında soru-cevap yapabilen akıllı chatbot projesidir. İnternet bağlantısı gerektiren hazır modellerin embedding yeteneklerinden faydalanarak, basit ve genişletilebilir bir yapay zeka destekli sohbet asistanı sunar.

## Özellikler

-Çok dilli ve Türkçe destekli: Distiluse Base Multilingual cased v2 modeli kullanılır.
-Siber güvenlik odaklı soru-cevap: Önceden tanımlanmış soru-cevap verisi (veri.json) ile hızlı ve alakalı yanıtlar.
-Anlamsal benzerlik araması: Kullanıcı sorusunu embedding’e dönüştürerek en yakın soruyu bularak cevap verir.
-Konu ve seviye filtreleme: /konu <konu_adı> ve /seviye <başlangıç|orta|ileri> komutları ile içeriği filtreleme.
-Small talk desteği: Merhaba, teşekkür ederim, hoşça kal gibi temel sohbet ifadelerine yanıt verir.
-Kolay genişletilebilirlik: veri.json dosyasına yeni sorular ve cevaplar ekleyerek bilgi tabanı zenginleştirilebilir.
-Komut satırı arayüzü: Basit ve interaktif sohbet deneyimi.

## Gereksinimler

Python 3.7 ve üzeri
sentence-transformers kütüphanesi

## İleride Geliştirme Önerileri

-Web tabanlı arayüz eklemek
-Daha gelişmiş doğal dil işleme modelleri ile entegre etmek
-Kullanıcı sorularını kayıt edip analiz etmek
-Farklı dillerde destek artırmak
-Daha detaylı small talk ve doğal sohbet yetenekleri eklemek

## Çalıştırma
python chatbot.py
