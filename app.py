from fastapi import FastAPI
from fastapi.responses import FileResponse
import yt_dlp
import os

app = FastAPI()

@app.get("/")
def home():
	return {"status": "ok", "message": "API YouTube Audio"}

@app.get("/download/")
def download_audio(url: str):
	output_file = "audio.mp3"
	if os.path.exists(output_file):
		os.remove(output_file)

	ydl_opts = {
		"format": "bestaudio/best",
		"extractaudio": True,
		"audioformat": "mp3",
		"outtmpl": output_file,
	}
	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])

	return FileResponse(output_file, media_type="audio/mpeg", filename="audio.mp3")