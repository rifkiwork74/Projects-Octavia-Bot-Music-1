# 💿 Angelss Music Bot • V17 FINAL FIX
<p align="center">
  <img src="https://github.com/rifkiwork74/Projects-Octavia-Bot-Music-1/blob/main/Angels-Banner-Bot-1.png" width=720x50" alt="Angelss Logo">
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Version-V17--Final--Fix-red?style=for-the-badge&logo=github" alt="Version"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10-red?style=for-the-badge&logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Infrastructure-Octavia--Cloud-black?style=for-the-badge&logo=linux" alt="Infrastructure"></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-Production--Ready-green?style=for-the-badge" alt="Status"></a>
</p>

---

## 🚀 Overview
**Angelss Music Bot** adalah solusi audio Discord kelas industri yang dirancang untuk performa maksimal pada **Python 3.10**. Menggunakan engine `yt-dlp` yang dikombinasikan dengan `static-ffmpeg` untuk menghasilkan kualitas suara *High-Fidelity* tanpa memerlukan instalasi manual pada environment hosting.

> **Project Update V17:** Sinkronisasi total antara Dashboard UI, Volume Control, dan Session Memory Management.

---

## ⚡ Key Technical Features
* **High-Performance Audio Engine**: Dioptimalkan untuk **2vCPU / 2GB RAM** (Octavia Specs).
* **Interactive Mixer Console**: Dashboard real-time dengan tombol kendali dinamis.
* **Smart Queue System**: Menggunakan `collections.deque` untuk manajemen antrean yang ringan.
* **Bypass YouTube Restriction**: Dilengkapi dengan sistem sinkronisasi `youtube_cookies.txt` untuk mencegah Error 403.
* **Auto-Cleaning Session**: Menghapus log dan dashboard lama secara otomatis untuk menjaga kebersihan channel.

---

## 🏗️ Project Architecture
```text
📁 Angelss-Project-V17/
├── 📄 main.py               # Core Bot Logic (Discord API & Audio Engine)
├── 📄 .env                  # Environment Variables (Sensitive Data)
├── 📄 .gitignore            # Security filters for Git
├── 📄 requirements.txt      # Dependency manifest
└── 📄 youtube_cookies.txt   # YouTube Auth Session
