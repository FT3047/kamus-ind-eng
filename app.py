from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/api/kbbi')
def kbbi():
    word = request.args.get('word', '')
    if not word:
        return jsonify({'error': 'Parameter word kosong'}), 400
    url = f"https://kbbi.kemdikbud.go.id/entri/{word}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return jsonify({'word': word, 'definition': 'Tidak ditemukan di KBBI.'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        desc = soup.find('div', class_='desc')
        if desc:
            definition = desc.get_text(separator=" ", strip=True)
            return jsonify({'word': word, 'definition': definition})
        else:
            return jsonify({'word': word, 'definition': 'Tidak ditemukan di KBBI.'})
    except Exception as e:
        return jsonify({'word': word, 'definition': f'Error: {str(e)}'})

@app.route('/api/babla')
def babla():
    word = request.args.get('word', '')
    if not word:
        return jsonify({'error': 'Parameter word kosong'}), 400
    url = f"https://id.bab.la/kamus/inggris-indonesia/{word}"
    try:
        # Tambahkan header User-Agent agar request tidak diblokir Babla
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return jsonify({'eng': word, 'indo': 'Tidak ditemukan di Babla.'})

        soup = BeautifulSoup(resp.text, 'html.parser')
        # ...lanjutkan kode scraping sesuai kebutuhan...

    except Exception as e:
        return jsonify({'eng': word, 'indo': f'Error: {str(e)}'})
        
        # DEBUG (sementara): Lihat hasil HTML jika ingin inspeksi
        # print(resp.text)  # aktifkan ini jika ingin debug HTML

        # Ambil hasil utama "water = air"
        main_translation = None
        content_col = soup.find('div', class_='content-column')
        if content_col:
            spans = content_col.find_all('span')
            for i, span in enumerate(spans):
                if span.get_text(strip=True).lower() == word.lower() and i+2 < len(spans):
                    if spans[i+1].get_text(strip=True) == '=':
                        main_translation = spans[i+2].get_text(strip=True)
                        break

        # Ambil daftar terjemahan lain dari <span class="sense-group-results">
        translations = []
        sense_groups = soup.find_all('span', class_='sense-group-results')
        for sense_group in sense_groups:
            translations.extend([a.get_text(strip=True) for a in sense_group.find_all('a', class_='result-link')])

        # Jika hasil utama tidak ditemukan, coba <a class="result-link"> di seluruh page
        if not main_translation and not translations:
            links = soup.find_all('a', class_='result-link')
            translations = [l.get_text(strip=True) for l in links if l.get_text(strip=True)]

        # Gabungkan hasil utama dan daftar lain (hindari duplikat)
        result = []
        if main_translation:
            result.append(main_translation)
        for t in translations:
            if t and t not in result:
                result.append(t)

        if result:
            return jsonify({'eng': word, 'indo': ', '.join(result)})
        else:
            return jsonify({'eng': word, 'indo': 'Tidak ditemukan di Babla.'})
    except Exception as e:
        return jsonify({'eng': word, 'indo': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)