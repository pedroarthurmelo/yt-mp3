from flask import Flask, request, jsonify, send_from_directory, render_template
import yt_dlp
import os
from pathlib import Path

app = Flask(__name__)

# Usando a biblioteca pathlib para buscar a pasta Downloads
DOWNLOAD_FOLDER = str(Path.home() / "Downloads")

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')  # Certifique-se de ter o arquivo 'index.html' no diretório 'templates'

@app.route('/download', methods=['POST'])
def download_video():
    data = request.json
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL inválida"}), 400

    ydl_opts = {
        'format': 'bestaudio/best',  # Baixar o melhor áudio disponível
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),  # Caminho de saída
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',  # Corrigido para o nome correto do postprocessador
            'preferredcodec': 'mp3'  # Salvar em formato MP3
        }],
        'noplaylist': True,  # Não baixar playlists, apenas o vídeo/áudio individual
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info) # yt-dlp já adiciona a extensão correta
            file_path = os.path.basename(file_name)


        return jsonify({"message": "Download concluído!", "file": file_path, "download_url": f"/downloads/{file_path}"})

    except Exception as e:
        print(f"Ocorreu um erro durante o download: {e}")
        return jsonify({"error": f"Ocorreu um erro durante o download: {str(e)}"}), 500



@app.route('/downloads/<filename>')
def get_video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)