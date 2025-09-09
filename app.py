from fastapi import FastAPI
from fastapi.responses import FileResponse
import yt_dlp
import re
import tempfile
import os

app = FastAPI()

def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo"""
    return re.sub(r'[\\/*?:"<>|]', "", name)

@app.get("/")
def home():
    return {"status": "ok", "message": "API YouTube Audio"}

@app.get("/v1/download/")
def download_audio_v1(url: str):
    """
    Baixa o áudio no formato original do YouTube (m4a/webm).
    """
    # Extrai informações do vídeo
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info.get("title", "audio"))

    # Seleciona melhor stream de áudio
    audio_stream = next((f for f in info['formats'] if f['acodec'] != 'none' and f['vcodec'] == 'none'), None)
    ext = audio_stream['ext'] if audio_stream else "m4a"

    # Arquivo temporário
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}")
    tmp_file_path = tmp_file.name
    tmp_file.close()

    # Baixa áudio para arquivo temporário
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_file_path
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Retorna arquivo e deleta depois
    response = FileResponse(
        tmp_file_path,
        media_type=f"audio/{ext}",
        filename=f"{title}.{ext}"
    )
    response.background = lambda: os.remove(tmp_file_path)
    return response

@app.get("/v2/download/")
def download_audio_v2(url: str):
    """
    Baixa o áudio e converte para MP3.
    Precisa de ffmpeg instalado para a conversão.
    """
    # Extrai informações do vídeo
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)
        title = sanitize_filename(info.get("title", "audio"))

    # Arquivo temporário
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_file_path = tmp_file.name
    tmp_file.close()

    # Baixa e converte para MP3
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_file_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # Retorna arquivo MP3 e deleta depois
    response = FileResponse(
        tmp_file_path,
        media_type="audio/mpeg",
        filename=f"{title}.mp3"
    )
    response.background = lambda: os.remove(tmp_file_path)
    return response

@app.get("/debug/")
def debug_video(url: str):
    """
    Retorna dados do vídeo e streams de áudio disponíveis.
    """
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(url, download=False)

    audio_formats = [f for f in info['formats'] if 'audio' in f['acodec']]

    return {
        "title": info.get("title"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "view_count": info.get("view_count"),
        "audio_formats": audio_formats
    }
