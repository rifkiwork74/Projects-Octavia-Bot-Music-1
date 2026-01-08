# 1. Gunakan image Python 3.10 yang stabil
FROM python:3.10-slim

# 2. Instal FFmpeg dan tools pendukung (PENTING untuk audio)
# libopus-dev dkk ditambahkan untuk memastikan voice support Discord lancar
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libopus-dev \
    libffi-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Set direktori kerja di dalam container
WORKDIR /app

# 4. Copy requirements dulu agar build lebih cepat (cache layer)
COPY requirements.txt .

# 5. Instal library Python
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy seluruh file project ke dalam container
# Termasuk main.py, youtube_cookies.txt, dll.
COPY . .

# 7. Jalankan bot
CMD ["python", "main.py"]
