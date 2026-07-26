# UNEX (United Exploit Toolkit)

UNEX, Termux (Android) ve Linux ortamları için geliştirilmiş modern, modüler ve kullanımı kolay bir araç yöneticisi ve yükleyicisidir.

## 🚀 Özellikler
- **Modüler Mimari:** Kolayca yeni araçlar ve kategoriler eklenebilir.
- **SQLite Entegrasyonu:** Yüklü araçları ve veritabanı durumunu takip eder.
- **Toplu Kurulum:** Aynı anda birden fazla aracı veya tüm kategoriyi seçerek kurma imkanı.
- **Renkli Arayüz:** Colorama tabanlı modern ve şık CLI tasarımı.

## 👥 Takım (Team Unex)
- UNEX-project 
- ZelderSlaw 
## 🛠️ Kurulum

```bash
pkg update && pkg upgrade -y
pkg install git python -y
git clone https://github.com/team-unex/unex.git
cd unex
pip install -r requirements.txt
python unex.py
```

## 📖 Kullanım
1. Ana menüden bir kategori numarası seçin.
2. Açılan alt menüden kurmak istediğiniz araç veya araçların numaralarını aralarında boşluk bırakarak yazın (örneğin: `1 3 5`).
3. Kategorideki tüm araçları yüklemek için `@` yazabilirsiniz.

## ⚠️ Sorumluluk Reddi (Disclaimer)
Bu araç yalnızca **eğitim**, **güvenlik araştırmaları** ve **yetkili sızma testleri** amacıyla geliştirilmiştir. İzinsiz sistemlerde kullanılması yasadışıdır. Geliştirici ekip, oluşabilecek olumsuz durumlardan sorumlu tutulamaz.

## 📜 Lisans
MIT License
