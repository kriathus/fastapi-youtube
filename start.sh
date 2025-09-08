#!/bin/bash
apt-get update && apt-get install -y ffmpeg
uvicorn app:app --host 0.0.0.0 --port 10000