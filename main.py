import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

# Inisialisasi aplikasi Flask
app = Flask(__name__)
# Izinkan akses dari semua domain (penting agar front-end bisa mengambil data)
CORS(app)

# URL target untuk scraping
TARGET_URL = "https://tradingeconomics.com/stream?i=currency"

def scrape_news():
    """
    Fungsi untuk melakukan scraping judul dan deskripsi berita.
    """
    try:
        # Header untuk meniru browser biasa agar tidak diblokir
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Mengambil konten HTML dari URL target
        response = requests.get(TARGET_URL, headers=headers)
        # Cek jika permintaan gagal
        response.raise_for_status()

        # Parsing HTML menggunakan BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Siapkan list untuk menampung hasil scraping
        news_items = []

        # Cari semua tag <li> dengan class 'te-stream-item'
        stream_items = soup.find_all('li', class_='te-stream-item')

        for item in stream_items:
            # Cari judul di dalam tag <b>
            title_tag = item.find('b')
            # Cari deskripsi di dalam tag <span> dengan class yang spesifik
            description_tag = item.find('span', class_='te-stream-item-description')

            # Pastikan kedua tag ditemukan sebelum mengambil teksnya
            if title_tag and description_tag:
                title = title_tag.get_text(strip=True)
                description = description_tag.get_text(strip=True)
                
                news_items.append({
                    'title': title,
                    'description': description
                })

        return {
            "source": TARGET_URL,
            "scrapedAt":  __import__('datetime').datetime.now().isoformat(),
            "newsCount": len(news_items),
            "newsItems": news_items
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Gagal mengambil URL: {e}"}
    except Exception as e:
        return {"error": f"Terjadi kesalahan saat parsing: {e}"}

@app.route('/')
def get_news():
    """
    Endpoint utama yang akan dipanggil untuk mendapatkan data berita.
    """
    data = scrape_news()
    # Kembalikan data dalam format JSON
    return jsonify(data)

if __name__ == "__main__":
    # Jalankan server. Railway akan menyediakan port secara otomatis.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
