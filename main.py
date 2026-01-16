# ==============================================================================
# 💿 PROJECT     : Angelss Music Bot (V17 FINAL FIX)
# 👨‍💻 DEVELOPER : ikiii (IT Engineering)
# 🚀 STATUS		: Production Ready
# 🛡️ LICENSE  	 : Personal Project - Angelss Project
# ==============================================================================



"""


DESCRIPTION KUH	:
		
			Bot musik profesional dengan sistem Interactive Dashboard, High-Fidelity Audio,
			dan manajemen antrean cerdas. Dioptimalkan untuk Python 3.10.


"""


















# --- [ 0 ] ---
#
# ==============================================================================
#			[ LIBRARY IMPORT ]
# ==============================================================================


#
# 🐍  0.1:	SYSTEM KERNEL (Standard Library)
# ------------------------------------------------------------------------------
#
#
import os
import asyncio
import datetime
import logging
import json
import math
import time
from collections import deque
from dotenv import load_dotenv
load_dotenv() 


#
# 📡  0.2:	DISCORD UPLINK (API & Networking)
# ------------------------------------------------------------------------------
#  
#
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks


#
# 💿  0.3:	AUDIO ENGINE (Multimedia Processing)
# ------------------------------------------------------------------------------
#  
#  
import yt_dlp





















# --- [ 1 ] ---
#
# ==============================================================================
#			[ SYSTEM LOGGING & TELEMETRY ]
# ==============================================================================


#
# 📜 1.1 :	
# ------------------------------------------------------------------------------
#
#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('AngelssProject')




















# --- [ 2 ] ---
#
# ==============================================================================
#			[ MENARIK TOKEN DISCORD DAN COOKIES IDENTITAS RAHASIA ]
# ==============================================================================


#
# 🌐 2.1 :	
# ------------------------------------------------------------------------------
#
#
TOKEN = os.getenv('DISCORD_TOKEN') # Menggunakan os.getenv lebih aman daripada os.environ.get
COOKIES_FILE = 'www.youtube.com_cookies.txt'




















# --- [ 3 ] ---
#
# ==============================================================================
#			[ YOUTUBE CONVERT AND FFMPEG AUDIO PLAYER CONFIG ]
# ==============================================================================


#
# 🔄 3.1: YDL SOURCE & TRANSCODING CONFIG
# ------------------------------------------------------------------------------
#
#
# --- [ UPDATE DI SECTION 3.1 & 3.2 ] ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False, # Set ke False agar kita bisa menangkap error-nya
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': COOKIES_FILE,
    'cachedir': False,
    'noprogress': True,
    # Penambahan stabilitas streaming
    'extract_flat': False,
    'wait_for_video': (5, 10),
}


#
# 🔊 3.2: AUDIO SIGNAL & STREAMING OPTIONS (STABLE RECONNECT)
# ------------------------------------------------------------------------------
#
FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-reconnect_at_eof 1 -nostdin'
    ),
    'options': (
        '-vn -loglevel warning -bufsize 5120k ' # Buffer 5MB cukup stabil
        '-af "aresample=async=1,loudnorm=I=-16:TP=-1.5:LRA=11"'
    ),
}








#
#  📥 3.3 : INISIALISASI YT-DLP
# ------------------------------------------------------------------------------
# (Mesin utama pengolah metadata & streaming link dari YouTube)

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)






#
# 📜 3.4 : Class QUEUE System | DATA MODEL & QUEUE SYSTEM (DATABASE MEMORY)
# ------------------------------------------------------------------------------
#
queues = {} 

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current_info = None
        self.loop = False
        self.volume = 0.5 
        self.last_dashboard = None
        self.last_search_msg = None
        self.last_queue_msg = None 
        self.text_channel_id = None
        self.update_task = None    
        self.start_time = 0        
        self.total_duration = 0    
        self.pause_time = 0
        # --- [ ANTI-DOUBLE PLAY LOCK ] ---
        self.lock = asyncio.Lock() 

    def clear_all(self):
        self.queue.clear()
        self.current_info = None
        if self.update_task:
            self.update_task.cancel()

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]

def delete_queue(guild_id):
    if guild_id in queues:
        del queues[guild_id]

 
 
 
 
 
 
 
 
 
 
# --- [ 4 ] ---
#
# ==============================================================================
#			[ FUNCTION HELPER - DEF - OLD ]
# ==============================================================================


#
# ⚙️ 4.0.  :	Fungsi ini agar bagus 
# ------------------------------------------------------------------------------
#
#
def buat_embed_status(emoji, pesan, warna):
    """Pesan notifikasi simpel satu baris"""
    return discord.Embed(description=f"{emoji} **{pesan}**", color=warna)

def format_time(sec):
    """Mengubah detik menjadi format 00:00 atau 00:00:00"""
    sec = int(sec)
    hrs = sec // 3600
    mins = (sec % 3600) // 60
    secs = sec % 60
    if hrs > 0:
        return f"{hrs:02}:{mins:02}:{secs:02}"
    else:
        return f"{mins:02}:{secs:02}"
        
        
    
#
# 🎨 4.1 :	Function Embed Skip
# ------------------------------------------------------------------------------
#
#
def buat_embed_skip(user, lagu_dilewati, info_selanjutnya):
    """Fungsi pembantu agar tampilan skip/lompat selalu cantik & seragam ✨"""
    # Membersihkan teks agar tidak ada spasi berlebih
    judul_bersih = str(lagu_dilewati)[:100].strip() 
    
    embed = discord.Embed(
        title="⏭️ NEXT MUSIC SKIP",
        description=(
            f"✨ **{user.mention}** telah melompat ke lagu berikutnya!\n\n"
            f"🗑️ **Dilewati:** `{judul_bersih}`\n"
            f"📥 **Status Antrean:** {info_selanjutnya}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xe67e22 
    )
    embed.set_footer(text="System Skip Otomatis • Angelss Project Final Fix V1", icon_url=user.display_avatar.url)
    return embed



#
# 🛡️ 4.2 :	Funstion Botstarp Validation  
# ------------------------------------------------------------------------------
#
#
def bootstrap():
    """Validasi awal sistem sebelum bot melakukan login."""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("   ANGELSS PROJECT V17 | STARTING SERVICE...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # 1. Pembersihan file sampah saat startup
    count = 0
    for file in os.listdir('.'):
        if file.endswith((".webm", ".m4a", ".mp3", ".part")):
            try:
                os.remove(file)
                count += 1
            except:
                pass
    if count > 0:
        logger.info(f"Cleanup: Berhasil menghapus {count} file sampah.")

    # 2. Validasi Token
    if not TOKEN:
        logger.critical("Fatal Error: DISCORD_TOKEN is missing from environment.")
        exit(1)
        
    if os.path.exists(COOKIES_FILE):
        logger.info(f"Identity: YouTube Cookies loaded from '{COOKIES_FILE}'.")
    else:
        logger.warning(f"Identity: Running without cookies. High-risk of 403 Forbidden.")




#
# 🔘▬ 4.3.  :	Function Progress Bar (REFINED PRECISION)
# ------------------------------------------------------------------------------
#
#
def create_progress_bar(current, total):
    if total <= 0:
        return "🔴 " + "─" * 22 + " [LIVE]"
        
    bar_size = 20 # Ukuran ideal untuk Mobile agar tidak patah baris
    percentage = current / total
    progress = max(0, min(int(percentage * bar_size), bar_size))
    
    # Menggunakan karakter yang lebih tebal untuk area yang sudah terlewati
    bar_filled = "▬" * progress
    bar_empty = "─" * (bar_size - progress)
    
    if progress >= bar_size:
        return bar_filled + "🔘"
    return bar_filled + "🔘" + bar_empty




#
# 🖼️ 4.4.  :	Function Dashboard (SINKRONISASI MODEREN)
# ------------------------------------------------------------------------------
#
#
def buat_embed_dashboard(q, elapsed_time, duration, title, url, thumbnail, user):
    # Hijau jika Loop aktif, Biru Gelap jika standar
    warna = 0x2ecc71 if q.loop else 0x2b2d31
    bar_visual = create_progress_bar(elapsed_time, duration)
    
    time_now = format_time(elapsed_time)
    time_total = format_time(duration)
    
    vol_percent = int(q.volume * 100)
    vol_emoji = "🔇" if vol_percent == 0 else "🔈" if vol_percent < 50 else "🔊"

    embed = discord.Embed(color=warna)
    embed.set_author(name="SEDANG DIPUTAR", icon_url="https://cdn.pixabay.com/animation/2022/12/25/06/28/06-28-22-725_512.gif")
    
    embed.description = (
        f"## 🎵 [{title}]({url})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bar_visual}\n"
        f"⏱️ `{time_now}` / `{time_total}`\n"
    )
    
    embed.add_field(name="👤 Pemesan", value=user.mention, inline=True)
    embed.add_field(name=f"{vol_emoji} Volume", value=f"`{vol_percent}%`", inline=True)
    embed.add_field(name="🔄 Loop Status", value=f"`{'AKTIF' if q.loop else 'OFF'}`", inline=True)
    
    if thumbnail: embed.set_thumbnail(url=thumbnail)
    embed.set_footer(text=f"Angelss Project V17 • Final Fix", icon_url=user.display_avatar.url)
    
    return embed





#
# 🔄 4.5.  :	Function Embed Loop
# ------------------------------------------------------------------------------
#
#
def buat_embed_loop(user, status_aktif, judul_lagu):
    """Pabrik visual untuk status pengulangan (Looping) ✨"""
    if status_aktif:
        emoji = "🔂"
        pesan = "LOOP AKTIF"
        detail = f"Lagu **{judul_lagu}** akan diputar terus-menerus."
        warna = 0x2ecc71  # Hijau Sukses
    else:
        emoji = "🔁"
        pesan = "LOOP DIMATIKAN"
        detail = "Bot akan lanjut memutar lagu berikutnya di antrean."
        warna = 0xe74c3c  # Merah/Normal

    embed = discord.Embed(
        title=f"{emoji} {pesan}",
        description=(
            f"✨ **{user.mention}** mengubah pengaturan pengulangan.\n\n"
            f"ℹ️ **Status:** {detail}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=warna
    )
    
    # Tambahkan footer khas Angelss Project
    embed.set_footer(
        text=f"System Loop • Angelss Project V17", 
        icon_url=user.display_avatar.url
    )
    
    return embed






#
# 🛑 4.6.  :	Function Embed Stop
# ------------------------------------------------------------------------------
#
#
def buat_embed_stop(user, jumlah):
    embed = discord.Embed(
        title="🛑 SYSTEM TERMINATED",
        description=(
            f"✨ **{user.mention}** telah menghentikan sesi musik.\n\n"
            f"🧹 **Antrean:** `{jumlah}` lagu telah dibersihkan.\n"
            f"📡 **Status:** Bot telah meninggalkan Voice Channel.\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x2f3136
    )
    embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
    # Tambahkan ini di def-nya kii biar makin keren
    embed.set_footer(text="Sesi berakhir • Angelss Project V17") 
    return embed




#
# 🔊 4.7.  :	
# ------------------------------------------------------------------------------
#
#
def buat_embed_volume(persen, user):
    """Pabrik visual untuk Volume Audio"""
    # 1. Tentukan Warna & Status
    if persen > 80:
        warna, status = 0xe74c3c, "⚠️ Volume Tinggi"
    elif persen > 50:
        warna, status = 0xf1c40f, "🔉 Volume Sedang"
    else:
        warna, status = 0x3498db, "🔈 Volume Standar"

    # 2. Buat Visual Bar
    bar = "▰" * (persen // 10) + "▱" * (10 - (persen // 10))

    # 3. Rakit Embed
    embed = discord.Embed(
        title="🎚️ Audio Mixer Console",
        description=(
            f"**Status:** {status}\n"
            f"**Level:** `{persen}%` / `100%` \n"
            f"`{bar}`\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=warna
    )
    embed.set_footer(text=f"Requested by {user.display_name}", icon_url=user.display_avatar.url)
    return embed





#
# 🏗️ 4.8.  :	Class Modern Bot & Notification Online System - PINDAH - KE SINI - Akar utama 
# ------------------------------------------------------------------------------
#
#
class ModernBot(commands.Bot):
    def __init__(self):
        # Setup dasar bot dengan intents lengkap untuk musik
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Sinkronisasi command saat bot start dengan error handling."""
        try:
            # SINKRONISASI GLOBAL (Wajib agar /command muncul)
            synced = await self.tree.sync()
            logger.info(f"✅ Berhasil sinkronisasi {len(synced)} slash commands secara global.")
        except Exception as e:
            logger.error(f"❌ Gagal sinkronisasi command: {e}")

    async def on_ready(self):
        """Event saat bot sudah online sepenuhnya dengan sistem pengaman hosting."""
        # 1. Set Status Bot (Listening Mode)
        activity = discord.Activity(
            type=discord.ActivityType.listening, 
            name="/play | Angelss V17"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

        # 2. Logika Kirim Pesan Online (DIBUNGKUS TRY-EXCEPT AGAR TIDAK CRASH)
        target_channel_id = 1456250414638043169 
        
        try:
            channel = self.get_channel(target_channel_id)
            
            if channel:
                # Membersihkan log lama (Dibatasi 10 pesan agar RAM hosting tidak bengkak)
                try:
                    async for message in channel.history(limit=10):
                        if message.author == self.user:
                            await message.delete()
                except Exception as e:
                    logger.warning(f"Gagal menghapus pesan lama: {e}")

                # --- [ TETAP MENGGUNAKAN EMBED ASLI KAMU ] ---
                embed = discord.Embed(
                    title="🚀 SYSTEM RELOADED & UPDATED",
                    description=(
                        "**Bot telah online dan berhasil diperbarui!**\n"
                        "Seluruh engine audio telah dioptimalkan untuk Python 3.10 dan FFmpeg v5.0."
                    ),
                    color=0x2ecc71 
                )
                embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
                
                # Info Statistik
                latensi = round(self.latency * 1000) if self.latency else "---"
                embed.add_field(name="🛰️ Cluster", value="`Jakarta-ID`", inline=True)
                embed.add_field(name="⚡ Latency", value=f"`{latensi}ms`", inline=True)
                embed.add_field(name="📡 Engine", value="`FFmpeg 5.0`", inline=True)
                embed.add_field(name="💡 Guide", value="Ketik `/play` atau `/help` untuk bantuan", inline=False)
                
                # Timestamp WIB
                waktu_sekarang = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
                embed.add_field(name="📅 System Ready", value=f"`{waktu_sekarang} WIB`", inline=False)

                embed.set_footer(
                    text="Angelss Project Final Fix • Powered by ikiii", 
                    icon_url=self.user.display_avatar.url
                )
                embed.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif") 
                
                await channel.send(embed=embed)
            else:
                # Jika channel ID salah/tidak ditemukan, bot tidak crash, hanya log saja
                logger.warning(f"⚠️ Channel ID {target_channel_id} tidak ditemukan. Melewati pesan online.")
                
        except Exception as e:
            logger.error(f"⚠️ Gagal menjalankan fungsi on_ready: {e}")
        
        # 3. Print Console Log (Standard Output untuk Pterodactyl Panel)
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ SYSTEM ONLINE - NOTIFICATION : {self.user.name}")
        print(f"🐍 PYTHON VER  : 3.10.x")
        print(f"📡 LATENCY     : {round(self.latency * 1000)}ms")
        print(f"📅 STARTED AT  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Inisialisasi Instance Bot
bot = ModernBot()

















# --- [ 5 ] ---
#
# ==============================================================================
#			[ CLASS SYSTEM ]
# ==============================================================================
 
#
# 🔍 5.1. :	Class System Search Engine Pilihan
# ------------------------------------------------------------------------------
#
#
class SearchControlView(discord.ui.View):
    def __init__(self, entries, user):
        # Gunakan timeout agar tidak membebani RAM hosting
        super().__init__(timeout=60) 
        self.entries = entries
        self.user = user
        self.add_select_menu()

    def add_select_menu(self):
        self.clear_items()
        options = []
        for i, entry in enumerate(self.entries):
            title = entry.get('title', 'Judul tidak diketahui')[:50]
            # Mengambil URL yang valid
            url = entry.get('url') or entry.get('webpage_url')
            options.append(discord.SelectOption(
                label=f"Lagu Nomor {i+1}", 
                value=url, 
                description=title,
                emoji="🎵"
            ))
            
        select = discord.ui.Select(placeholder="🎯 Pilih lagu untuk ditambahkan...", options=options)
        
        async def callback(interaction: discord.Interaction):
            # 1. Cek Permission User
            if interaction.user != self.user:
                return await interaction.response.send_message(
                    f"⚠️ **Ups!** Hanya {self.user.mention} yang bisa memilih lagu.", 
                    ephemeral=True
                )
            
            # 2. Defer agar bot punya waktu ambil metadata
            await interaction.response.defer()
            
            # 3. Ambil URL lagu yang dipilih
            selected_url = select.values[0]
            
            # 4. Panggil play_music (Ini akan otomatis masuk Queue jika ada lagu yang sedang jalan)
            await play_music(interaction, selected_url)
            
            # 5. [FIXED] Edit pesan pencarian agar user tahu lagu berhasil masuk
            # Kita tidak menghapus view=None di sini supaya user bisa lihat statusnya
            status_embed = self.create_embed()
            status_embed.add_field(
                name="✅ Berhasil Ditambahkan", 
                value=f"Lagu yang dipilih telah masuk ke antrean.", 
                inline=False
            )
            
            # Memberi tahu bahwa pilihan sukses tanpa merusak menu
            await interaction.edit_original_response(embed=status_embed, view=None)
            
            # Tunggu 5 detik lalu bersihkan pesan pencarian agar chat rapi (Level Industri)
            await asyncio.sleep(5)
            try:
                await interaction.delete_original_response()
            except:
                pass


        select.callback = callback
        self.add_item(select)

        # Tombol Tutup
        btn_close = discord.ui.Button(label="Tutup", style=discord.ButtonStyle.danger, emoji="🗑️")
        async def close_callback(interaction: discord.Interaction):
            if interaction.user == self.user:
                await interaction.message.delete()
            else:
                await interaction.response.send_message("❌ Kamu tidak berhak menutup ini!", ephemeral=True)
        btn_close.callback = close_callback
        self.add_item(btn_close)

    def create_embed(self):
        description = "📺 **YouTube Search Engine**\n*(Pilih nomor lagu di bawah ini)*\n\n"
        for i, entry in enumerate(self.entries):
            # Membatasi judul agar tidak kepanjangan di embed
            judul = entry.get('title', 'Unknown Title')
            description += f"✨ `{i+1}.` {judul[:60]}...\n"
            
        embed = discord.Embed(title="🔍 Hasil Pencarian Musik", description=description, color=0xf1c40f)
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif") 
        embed.set_footer(
            text=f"Request oleh: {self.user.display_name} • Menu otomatis tutup dalam 60 detik", 
            icon_url=self.user.display_avatar.url
        )
        return embed

    # Jika waktu habis (timeout), hapus menu select agar tidak error saat diklik nanti
    async def on_timeout(self):
        try:
            # Mengosongkan view saat timeout
            if hasattr(self, 'message') and self.message:
                await self.message.edit(view=None)
        except:
            pass




#
# 🎛️ 5.2.  :	Ui Class Volume Control (STABLE VERSION)
# ------------------------------------------------------------------------------
#
class VolumeControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60) # Menu tutup otomatis dalam 60 detik
        self.guild_id = guild_id

    def create_embed(self):
        """Membuat tampilan awal pop-up volume"""
        q = get_queue(self.guild_id)
        vol_percent = int(q.volume * 100)
        # Gunakan fungsi pabrik agar visualnya konsisten dengan /volume
        from discord import Interaction # Pastikan context tersedia
        # Kita buat dummy user info jika perlu, tapi lebih baik panggil helper
        # Di sini kita pakai embed standar dulu untuk inisialisasi
        embed = discord.Embed(title="🎚️ Audio Mixer Console", color=0x3498db)
        bar = "▰" * (vol_percent // 10) + "▱" * (10 - (vol_percent // 10))
        embed.description = f"**Status:** Menyesuaikan...\n**Level:** `{vol_percent}%`\n`{bar}`"
        return embed

    @discord.ui.button(label="-10%", style=discord.ButtonStyle.danger, emoji="🔉")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        
        # 1. Hitung persen baru (Minimal 0%)
        persen_baru = max(0, int((q.volume - 0.1) * 100))
        q.volume = persen_baru / 100
        
        # 2. Update Voice Client Engine
        vc = interaction.guild.voice_client
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass
        
        # 3. [FIX] Update Dashboard Utama (Jika sedang aktif)
        if q.last_dashboard:
            try:
                emb_dash = q.last_dashboard.embeds[0]
                # Field Volume biasanya ada di index 1 (cek Section 4.4)
                emb_dash.set_field_at(1, name="🔊 Volume", value=f"`{persen_baru}%`", inline=True)
                await q.last_dashboard.edit(embed=emb_dash)
            except: pass
                
        # 4. Update Pop-up Volume saat ini secara INSTAN
        embed_update = buat_embed_volume(persen_baru, interaction.user)
        await interaction.response.edit_message(embed=embed_update)

    @discord.ui.button(label="+10%", style=discord.ButtonStyle.success, emoji="🔊")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        
        # 1. Hitung persen baru (Maksimal 100%)
        persen_baru = min(100, int((q.volume + 0.1) * 100))
        q.volume = persen_baru / 100
        
        # 2. Update Voice Client Engine
        vc = interaction.guild.voice_client
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass

        # 3. [FIX] Update Dashboard Utama (Jika sedang aktif)
        if q.last_dashboard:
            try:
                emb_dash = q.last_dashboard.embeds[0]
                emb_dash.set_field_at(1, name="🔊 Volume", value=f"`{persen_baru}%`", inline=True)
                await q.last_dashboard.edit(embed=emb_dash)
            except: pass

        # 4. Update Pop-up Volume saat ini secara INSTAN
        embed_update = buat_embed_volume(persen_baru, interaction.user)
        await interaction.response.edit_message(embed=embed_update)






#
# 📼 5.3.  :	Ui Class: Dashboard & Audio - Player (FIXED)
# ------------------------------------------------------------------------------
#
#
class MusicDashboard(discord.ui.View):
    def __init__(self, guild_id, bot_instance=None): 
        super().__init__(timeout=None)
        self.guild_id = guild_id
	
	
	# --- TOMBOL 1: -10 ---
    @discord.ui.button(label="-10s", emoji="⏪", style=discord.ButtonStyle.secondary)
    async def backward(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        current_pos = time.time() - q.start_time
        new_pos = max(0, current_pos - 10)
        
        # Beri respon ke Discord agar tidak "Interaction Failed"
        await interaction.response.defer()
        
        # Panggil fungsi khusus seek agar tidak menghapus dashboard
        await self.execute_seek(interaction, new_pos)
        
        
        
        
	# --- TOMBOL 2: JEDA / LANJUT ---
    #
    @discord.ui.button(label="Jeda", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pp(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        if not vc: 
            return await interaction.response.send_message("❌ Bot tidak ada di VC.", ephemeral=True)
        
        if vc.is_playing():
            # LOGIKA PAUSE
            vc.pause()
            q.pause_time = time.time() # Catat waktu jeda
            if q.update_task: 
                q.update_task.cancel()
            
            button.emoji = "▶️"; button.label = "Lanjut"; button.style = discord.ButtonStyle.success 
        else:
            # LOGIKA RESUME
            current_pos = time.time() - q.start_time
            q.start_time = time.time() - current_pos
            vc.resume()
            
            # Restart Progress Bar (FIXED: Using interaction.client to avoid global variable issues)
            q.update_task = interaction.client.loop.create_task(
                update_player_interface(
                    q.last_dashboard, q.total_duration, 
                    q.current_info['title'], q.current_info['webpage_url'], 
                    q.current_info['thumbnail'], interaction.user, self.guild_id
                )
            )
            
            button.emoji = "⏸️"; button.label = "Jeda"; button.style = discord.ButtonStyle.secondary

        # Update visual
        elapsed = time.time() - q.start_time
        if elapsed > q.total_duration: elapsed = q.total_duration
        
        emb_update = buat_embed_dashboard(
            q, elapsed, q.total_duration, 
            q.current_info['title'], q.current_info['webpage_url'], 
            q.current_info['thumbnail'], interaction.user
        )
        
        await interaction.response.edit_message(embed=emb_update, view=self)
	
	
	# --- TOMBOL 3: +10 ---
    @discord.ui.button(label="+10s", emoji="⏩", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        current_pos = time.time() - q.start_time
        new_pos = min(q.total_duration, current_pos + 10)
        
        await interaction.response.defer()
        await self.execute_seek(interaction, new_pos)

    # Tambahkan Fungsi Pembantu di dalam Class MusicDashboard ini:
    async def execute_seek(self, interaction, new_pos):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        if vc and (vc.is_playing() or vc.is_paused()):
            # Hentikan sementara update loop agar tidak tabrakan
            if q.update_task:
                q.update_task.cancel()
            
            # Restart stream di posisi baru tanpa memicu 'next_logic'
            # Kita gunakan flag manual agar after_playing tidak lari ke lagu selanjutnya
            q.is_seeking = True 
            
            # Ambil data stream yang sedang jalan
            data = q.current_info
            ffmpeg_before = FFMPEG_OPTIONS['before_options'] + f" -ss {new_pos}"
            
            audio_source = discord.FFmpegPCMAudio(data['url'], before_options=ffmpeg_before, options=FFMPEG_OPTIONS['options'])
            source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)
            
            vc.stop() # Ini akan memicu after_playing lama
            vc.play(source, after=lambda e: self.after_seek(e, self.guild_id))
            
            # Update waktu start bot
            q.start_time = time.time() - new_pos
            q.is_seeking = False
            
            # Jalankan kembali progress bar
            q.update_task = interaction.client.loop.create_task(
                update_player_interface(
                    q.last_dashboard, q.total_duration, 
                    data['title'], data['webpage_url'], 
                    data['thumbnail'], interaction.user, self.guild_id
                )
            )

    def after_seek(self, error, g_id):
        q = get_queue(g_id)
        if error: logger.error(f"Seek Error: {error}")
        # Jika bukan sedang seeking (berarti lagu beneran habis), baru lanjut ke lagu selanjutnya
        if not getattr(q, 'is_seeking', False):
            bot.loop.create_task(next_logic(g_id))

	# --- TOMBOL 4: SKIP ---
    #
    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        # Pengaman Loop: Matikan loop sebentar agar pindah lagu, bukan memutar ulang lagu yang sama
        original_loop = q.loop
        q.loop = False
        
        if q.update_task: q.update_task.cancel()
        if vc: vc.stop() # Ini akan otomatis memicu after_playing di start_stream
        
        # Kembalikan status loop asli untuk lagu berikutnya
        q.loop = original_loop


	# --- TOMBOL 5: LOOP ---
    #
    @discord.ui.button(label="Loop: OFF", emoji="🔁", style=discord.ButtonStyle.gray)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        q.loop = not q.loop
        button.label = "Loop: ON" if q.loop else "Loop: OFF"
        button.style = discord.ButtonStyle.success if q.loop else discord.ButtonStyle.gray
        button.emoji = "🔂" if q.loop else "🔁"
        
        if interaction.message.embeds:
            emb = interaction.message.embeds[0]
            emb.color = 0x2ecc71 if q.loop else 0x2b2d31
            await interaction.response.edit_message(embed=emb, view=self)
        else:
            await interaction.response.edit_message(view=self)


	# --- TOMBOL 6: VOLUME ---
	#
    @discord.ui.button(label="Volume", emoji="🔊", style=discord.ButtonStyle.gray)
    async def vol(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = VolumeControlView(self.guild_id)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)


    # --- TOMBOL 7: ANTREAN ---
    @discord.ui.button(label="Antrean", emoji="📜", style=discord.ButtonStyle.gray)
    async def list_q_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Memanggil fungsi pusat di Section 6.7
        await logic_tampilkan_antrean(interaction, self.guild_id)
        
        
	# --- TOMBOL 8: STOP ---
	#
    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        if q.update_task: q.update_task.cancel()
        q.queue.clear()
        if vc: await vc.disconnect()
        await interaction.response.send_message(embed=buat_embed_stop(interaction.user, 0), delete_after=10)













# --- [ 6 ] ---
#
# ==============================================================================
#			[ FUNCTION HELPER - ASYNCE DEF  - MODERN ]
# ==============================================================================




#
# ⏱️ 6.1. : Function asynce def system auto update bar and durasi (ANTI-ZOMBIE)
# ------------------------------------------------------------------------------
#
async def update_player_interface(message, duration, title, url, thumbnail, user, guild_id):
    """
    Update progress bar setiap detik. 
    Dilengkapi sistem pengaman agar tidak membebani RAM (Anti-Zombie).
    """
    q = get_queue(guild_id)
    
    try:
        # Loop akan berjalan selama bot online
        while not bot.is_closed():
            vc = message.guild.voice_client
            
            # --- [ PENGAMAN 1: Kondisi Audio ] ---
            # Jika bot keluar VC atau lagu sudah beneran berhenti, hentikan task ini.
            if not vc or not (vc.is_playing() or vc.is_paused()):
                logger.info(f"Task Update di Guild {guild_id} dihentikan: Audio diam.")
                break
                
            # --- [ PENGAMAN 2: Sinkronisasi Dashboard ] ---
            # Jika pesan dashboard yang kita pegang (message.id) ternyata sudah 
            # bukan dashboard yang terdaftar di antrean (q.last_dashboard.id),
            # artinya sudah ada lagu baru atau dashboard baru. Matikan task lama ini.
            if q.last_dashboard and message.id != q.last_dashboard.id:
                logger.info(f"Task Update lama di Guild {guild_id} dimatikan (Dashboard diganti).")
                break

            # --- [ LOGIKA HITUNG WAKTU ] ---
            # Jika sedang jeda (Pause), gunakan waktu saat tombol jeda ditekan
            if vc.is_paused():
                elapsed_time = q.pause_time - q.start_time if hasattr(q, 'pause_time') else time.time() - q.start_time
            else:
                elapsed_time = time.time() - q.start_time
                
            # Pastikan waktu tidak melebihi durasi total atau kurang dari 0
            elapsed_time = max(0, min(elapsed_time, duration))

            try:
                # Rakit kembali Embed dengan data terbaru (Progress bar baru)
                embed = buat_embed_dashboard(q, elapsed_time, duration, title, url, thumbnail, user)
                
                # Edit pesan dashboard
                await message.edit(embed=embed)
                
            except discord.NotFound:
                # Jika pesan dashboard dihapus paksa oleh user/admin, matikan task ini
                break
            except Exception as e:
                # Jika ada error internet saat update, biarkan loop lanjut ke detik berikutnya
                logger.warning(f"Gagal update embed dashboard di {guild_id}: {e}")
                pass
            
            # Jeda update (Setel ke 1 detik agar visual bar smooth)
            # Jika hosting berat, naikkan ke 2 atau 3 detik.
            await asyncio.sleep(1)

    except asyncio.CancelledError:
        # Ini akan terpicu saat kita memanggil q.update_task.cancel() di perintah /skip atau /stop
        logger.info(f"Task Update di Guild {guild_id} berhasil di-cancel secara paksa.")
        raise # Tetap lempar agar asyncio tahu task sudah bersih
    except Exception as e:
        logger.error(f"Error Kritis pada Update Interface: {e}")
    finally:
        # Pintu keluar terakhir: Pastikan log mencatat task ini sudah mati
        pass










#
# 🚀 6.2.  :	
# ------------------------------------------------------------------------------
#
#
# Tambahkan ini di Section 6.1 atau 6.4 (Sebelum start_stream)
async def update_ui_dashboard(guild_id, interaction=None):
    q = get_queue(guild_id)
    chan = bot.get_channel(q.text_channel_id)
    if not chan: return

    # 1. Hapus dashboard lama agar tidak menumpuk di chat
    if q.last_dashboard:
        try: await q.last_dashboard.delete()
        except: pass

    # 2. Siapkan Embed & View
    # Pastikan data current_info sudah ada (diisi oleh start_stream)
    data = q.current_info
    elapsed = 0 # Lagu baru mulai
    
    # Gunakan user dari interaction jika ada, jika tidak pakai bot (untuk auto-next)
    user_obj = interaction.user if interaction else bot.user

    view = MusicDashboard(guild_id)
    embed = buat_embed_dashboard(
        q, elapsed, q.total_duration, 
        data['title'], data['webpage_url'], 
        data['thumbnail'], user_obj
    )

    # 3. Kirim Dashboard Baru
    try:
        if interaction and not interaction.response.is_done():
            # Jika dipicu langsung dari command /play
            msg = await interaction.followup.send(embed=embed, view=view)
        else:
            # Jika dipicu oleh sistem auto-next
            msg = await chan.send(embed=embed, view=view)
            
        q.last_dashboard = msg
        
        # 4. Jalankan progress bar update engine
        if q.update_task: q.update_task.cancel()
        q.update_task = bot.loop.create_task(
            update_player_interface(
                msg, q.total_duration, data['title'], 
                data['webpage_url'], data['thumbnail'], user_obj, guild_id
            )
        )
    except Exception as e:
        logger.error(f"Gagal mengirim dashboard: {e}")
        



#
#  🔊⚠️ 6.3. :	Function Auto Disconnect VC (DEEP CLEAN VERSION)
# ------------------------------------------------------------------------------
#
#
@bot.event
async def on_voice_state_update(member, before, after):
    # Logika: Jika ada user (bukan bot) keluar dari VC
    if not member.bot and before.channel is not None:
        vc = member.guild.voice_client
        
        # Cek apakah bot berada di channel yang ditinggalkan dan sekarang hanya bot sendiri
        if vc and vc.channel.id == before.channel.id and len(vc.channel.members) == 1:
            
            guild_id = member.guild.id
            q = get_queue(guild_id)
            msg_chan = None

            # PRIORITAS CHANNEL: Mencari tempat terbaik untuk kirim notifikasi
            if q.last_dashboard:
                msg_chan = q.last_dashboard.channel
            elif q.text_channel_id:
                msg_chan = bot.get_channel(q.text_channel_id)
            
            if msg_chan:
                try:
                    peringatan = await msg_chan.send(
                        f"⚠️ **Otomatis Keluar:** Voice Channel kosong. Bot akan keluar dalam **30 detik** jika tidak ada yang kembali.", 
                        delete_after=30
                    )
                except:
                    peringatan = None
                
                # Tunggu 30 detik (masa tenggang)
                await asyncio.sleep(30)
                
                # Cek kembali kondisi Voice Client setelah menunggu
                vc_sekarang = member.guild.voice_client
                
                if vc_sekarang and vc_sekarang.channel:
                    # Cek apakah ada manusia (bukan bot) yang kembali ke channel
                    human_members = [m for m in vc_sekarang.channel.members if not m.bot]
                    
                    if len(human_members) > 0:
                        try:
                            if peringatan: await peringatan.delete()
                        except: pass
                        await msg_chan.send("✨ **Informasi:** Seseorang telah kembali! Bot tetap standby.", delete_after=10)
                    else:
                        # --- [ POIN 2: DEEP CLEANING START ] ---
                        
                        # 1. Hentikan task update progress bar agar tidak error (Zombie Task)
                        if q.update_task:
                            q.update_task.cancel()
                        
                        # 2. Hapus pesan dashboard terakhir dari chat agar tidak membingungkan
                        if q.last_dashboard:
                            try: await q.last_dashboard.delete()
                            except: pass
                        
                        # 3. Bersihkan seluruh data antrean di class MusicQueue
                        q.clear_all() 
                        
                        # 4. Hapus object guild dari dictionary global 'queues' (Sangat penting untuk RAM)
                        delete_queue(guild_id) 

                        # 5. Putuskan koneksi suara
                        if vc_sekarang.is_connected():
                            await vc_sekarang.disconnect()
                            await msg_chan.send("👋 **Informasi:** Sesi diakhiri karena Voice Channel kosong terlalu lama.", delete_after=10)




#
# ⏯️ 6.4. : HELPER: System Pause / Resume Dynamic (Sinkronisasi UI)
# ------------------------------------------------------------------------------
#
#
async def sync_dashboard_buttons(message, guild_id):
    if not message: return
    # MusicDashboard sudah ada di bawah, panggil langsung
    view = MusicDashboard(guild_id)
    vc = message.guild.voice_client
    
    for item in view.children:
        if isinstance(item, discord.ui.Button) and item.label in ["Jeda", "Lanjut"]:
            if vc and vc.is_paused():
                item.emoji, item.label, item.style = "▶️", "Lanjut", discord.ButtonStyle.success
            else:
                item.emoji, item.label, item.style = "⏸️", "Jeda", discord.ButtonStyle.secondary
            break
    try:
        await message.edit(view=view)
    except: pass





#
# 📡 6.5 : MESIN UTAMA - START STREAM (ULTIMATE STABLE + SMART ERROR HANDLER)
# ------------------------------------------------------------------------------
#
# --- [ UPDATE DI SECTION 6.4 ] ---
async def start_stream(interaction, url, seek_time=None, guild_id_manual=None):
    g_id = interaction.guild.id if interaction else guild_id_manual
    q = get_queue(g_id)
    
    # 🛑 ANTI-SPAM: Berikan nafas bagi asyncio
    await asyncio.sleep(2) # Gunakan 2-3 detik agar API YouTube/Discord stabil

    async with q.lock:
        if q.update_task:
            q.update_task.cancel()
            try: await q.update_task
            except: pass

        vc = bot.get_guild(g_id).voice_client
        if not vc: return

        try:
            # Metadata Extraction dengan error handling ketat
            data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            q.current_info = data
            q.total_duration = data.get('duration', 0)
            
            # Memastikan URL valid
            stream_url = data.get('url') or (data.get('formats')[0]['url'] if data.get('formats') else None)
            
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(stream_url, before_options=FFMPEG_OPTIONS['before_options'], options=FFMPEG_OPTIONS['options']),
                volume=q.volume
            )
    
            def after_playing(error):
                if error: logger.error(f"Stream Error: {error}")
                # Logika Loop vs Next
                coro = start_stream(None, url, guild_id_manual=g_id) if q.loop else next_logic(g_id)
                bot.loop.create_task(coro)

            vc.play(source, after=after_playing)
            q.start_time = time.time()
            
            # Kirim UI Dashboard Baru
            await update_ui_dashboard(g_id, interaction)

        except Exception as e:
            logger.error(f"Audit Failure: {e}")
            # Jika error, jangan diam, langsung paksa lagu berikutnya
            bot.loop.create_task(next_logic(g_id))







        
        
#
# ⏭️ 6.6 : LOGIKA PINDAH LAGU OTOMATIS
# ------------------------------------------------------------------------------
#
#
async def next_logic(guild_id):
    q = get_queue(guild_id)
    await asyncio.sleep(1.5) # Jeda anti-spam API Discord
    
    if q.queue:
        next_song = q.queue.popleft()
        await start_stream(None, next_song['url'], guild_id_manual=guild_id)
    else:
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        chan = bot.get_channel(q.text_channel_id)
        if chan: await chan.send("✅ **Antrean selesai.**", delete_after=10)







#
# 🎮 6.7 : GATEWAY PEMUTAR (PLAY CONTROL) - AUDIT FIX
# ------------------------------------------------------------------------------
#
#
async def play_music(interaction, url):
    # 1. Ambil queue data
    q = get_queue(interaction.guild_id)
    q.text_channel_id = interaction.channel.id
    
    # 2. DEFINISIKAN VC (Penting: agar variabel 'vc' terbaca di bawah)
    vc = interaction.guild.voice_client
    
    # 3. CEK KONEKSI (Jika bot belum masuk VC, suruh masuk dulu)
    if not vc:
        if interaction.user.voice:
            vc = await interaction.user.voice.channel.connect()
        else:
            # Jika user tidak di VC, kirim pesan dan stop
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Masuk ke Voice dulu kii!", ephemeral=True)
            else:
                await interaction.followup.send("❌ Masuk ke Voice dulu kii!", ephemeral=True)
            return

    # 4. PENANGANAN DEFER (Anti-Timeout)
    # Ini supaya kalau proses ambil link YouTube lama, Discord tidak menganggap bot mati
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)

    # 5. LOGIKA QUEUE VS DIRECT PLAY
    if vc.is_playing() or vc.is_paused():
        # JIKA SEDANG MAIN: Masukkan ke Antrean
        try:
            # Ekstrak metadata di background (agar bot tidak freeze)
            data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            if 'entries' in data: data = data['entries'][0]
            
            # Tambahkan metadata ke deque (antrean)
            q.queue.append({
                'title': data.get('title', 'Unknown Title'), 
                'url': url, 
                'thumbnail': data.get('thumbnail')
            })
            
            # Kirim Embed Konfirmasi (Level Industri)
            emb = discord.Embed(
                title="📥 Antrean Ditambahkan", 
                description=f"✨ **[{data['title']}]({url})**", 
                color=0x3498db
            )
            emb.set_footer(text="Gunakan /queue untuk melihat semua daftar")
            
            await interaction.followup.send(embed=emb, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error saat tambah antrean: {e}")
            await interaction.followup.send(f"⚠️ **Error:** Gagal mengambil data lagu.", ephemeral=True)
    else:
        # JIKA DIAM: Langsung putar lagu pertama
        await start_stream(interaction, url)






#
# 📜 6.8 :	LOGIKA TAMPILAN ANTREAN (CENTRALIZED)
# ------------------------------------------------------------------------------
#
#
async def logic_tampilkan_antrean(interaction: discord.Interaction, guild_id):
    q = get_queue(guild_id)
    
    if not q.queue:
        emb = discord.Embed(description="📪 **Antrean kosong.**", color=0x2b2d31)
        return await (interaction.followup.send if interaction.response.is_done() else interaction.response.send_message)(embed=emb, ephemeral=True)
    
    # Ambil 10 lagu teratas
    daftar = list(q.queue)
    maks = 10
    teks_lagu = [f"`{i+1}.` {item['title'][:50]}" for i, item in enumerate(daftar[:maks])]
    
    sisa = len(daftar) - maks
    deskripsi = "\n".join(teks_lagu)
    if sisa > 0: deskripsi += f"\n\n*...dan `{sisa}` lagu lainnya.*"

    emb = discord.Embed(title="📜 Live Music Queue", description=deskripsi, color=0x3498db)
    
    if q.current_info:
        emb.add_field(name="▶️ Sedang Diputar", value=f"**{q.current_info['title'][:60]}**", inline=False)
    
    emb.set_footer(text=f"Total: {len(daftar)} Lagu • Angelss Project V17")
    
    await (interaction.followup.send if interaction.response.is_done() else interaction.response.send_message)(embed=emb, ephemeral=True)




















# --- [ 7 ] ---
#
# ==============================================================================
#			SECTION: MUSIC COMMANDS (STANDARD)
# ==============================================================================


#
#  ▶️ 7.1 : /play - System
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="play", description="Putar musik menggunakan judul atau link YouTube")
@app_commands.describe(cari="Masukkan Judul Lagu atau Link YouTube")
async def play(interaction: discord.Interaction, cari: str):
    # 1. Defer wajib (ephemeral=True agar hanya user yang bersangkutan yang lihat prosesnya)
    if not interaction.response.is_done():
        await interaction.response.defer(ephemeral=True)
    
    q = get_queue(interaction.guild_id)

    # Bersihkan sisa-sisa pencarian lama
    if q.last_search_msg:
        try: 
            await q.last_search_msg.delete()
        except: 
            pass

    # --- [ LOGIKA A: INPUT ADALAH LINK ] ---
    if "http" in cari.lower(): 
        await interaction.followup.send("🔗 **Menganalisa tautan...**", ephemeral=True)
        # Tambahkan sedikit delay agar API Discord tidak kaget saat transisi ke start_stream
        await play_music(interaction, cari)
        return await interaction.edit_original_response(content=f"✅ **Tautan berhasil dianalisa.**")
    
    # --- [ LOGIKA B: INPUT ADALAH JUDUL (PENCARIAN) ] ---
    else:
        await interaction.followup.send(f"🔍 **Mencari:** `{cari}` di database YouTube...", ephemeral=True)
        
        # Fungsi internal untuk pencarian yang lebih aman (di dalam run_in_executor)
        def safe_search():
            try:
                search_config = YTDL_OPTIONS.copy()
                search_config['extract_flat'] = True
                with yt_dlp.YoutubeDL(search_config) as ydl:
                    # Kita bungkus proses pencarian di dalam context manager 'with'
                    return ydl.extract_info(f"ytsearch5:{cari}", download=False)
            except Exception as e:
                logger.error(f"Pencarian yt-dlp gagal: {e}")
                return None

        try:
            # Eksekusi pencarian secara asynchronous
            data = await bot.loop.run_in_executor(None, safe_search)
            
            # Validasi hasil pencarian
            if not data or 'entries' not in data or not data['entries']:
                return await interaction.edit_original_response(
                    content="❌ **Gagal:** Lagu tidak ditemukan. Pastikan judul benar atau coba gunakan link langsung."
                )
            
            # Ambil entri pencarian (limit 5) dan pastikan tidak ada data None
            entries = [e for e in data['entries'] if e is not None][:5]
            
            if not entries:
                return await interaction.edit_original_response(content="❌ **Gagal:** Hasil pencarian kosong.")

            # Panggil UI Dashboard Pencarian
            view = SearchControlView(entries, interaction.user)
            
            # Kirim hasil ke user
            q.last_search_msg = await interaction.edit_original_response(
                content="✨ **Berikut adalah hasil pencarian terbaik untukmu kii:**", 
                embed=view.create_embed(), 
                view=view
            )

        except Exception as e:
            logger.error(f"Kritis pada System Play: {e}")
            await interaction.edit_original_response(
                content="⚠️ **System Error:** Terjadi gangguan pada koneksi YouTube. Silahkan coba sesaat lagi."
            )

   


#
# ⏸️ 7.2. : /pause - System (REFINED)
# ------------------------------------------------------------------------------
#
@bot.tree.command(name="pause", description="Jeda musik")
async def pause_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        q.pause_time = time.time()
        if q.update_task: q.update_task.cancel()
        
        # SINKRONISASI OTOMATIS (Menggunakan Helper Section 6.3)
        await sync_dashboard_buttons(q.last_dashboard, interaction.guild_id)
        await interaction.response.send_message(embed=buat_embed_status("⏸️", "Musik dijeda.", 0xf1c40f), delete_after=10)
    else:
        await interaction.response.send_message("❌ Tidak ada musik berjalan.", ephemeral=True)


#
# ▶️ 7.3. : /resume - System (REFINED)
# ------------------------------------------------------------------------------
#
@bot.tree.command(name="resume", description="Lanjut memutar musik")
async def resume_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        current_pos = time.time() - q.start_time
        q.start_time = time.time() - current_pos
        vc.resume()
        
        # JALANKAN ULANG ENGINE UPDATE
        if q.last_dashboard and q.current_info:
            q.update_task = bot.loop.create_task(
                update_player_interface(q.last_dashboard, q.total_duration, q.current_info['title'], q.current_info['webpage_url'], q.current_info['thumbnail'], interaction.user, interaction.guild_id)
            )
        
        # SINKRONISASI TOMBOL
        await sync_dashboard_buttons(q.last_dashboard, interaction.guild_id)
        await interaction.response.send_message(embed=buat_embed_status("▶️", "Musik dilanjutkan.", 0x2ecc71), delete_after=10)
    else:
        await interaction.response.send_message("❌ Musik tidak sedang dijeda.", ephemeral=True)





#
# ⏭️ 7.4.  :	/skip - System (FINAL STABLE VERSION)
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="skip", description="Lewati lagu yang sedang berjalan")
async def skip_cmd(interaction: discord.Interaction):
    # 1. Defer wajib agar bot punya waktu bernapas saat koneksi lemot
    await interaction.response.defer(ephemeral=False)
    
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if vc and (vc.is_playing() or vc.is_paused()):
        # --- 2. LOGIKA PENGAMAN LOOP ---
        # Simpan status loop asli user
        original_loop = q.loop
        # Matikan loop paksa agar after_playing() memanggil lagu selanjutnya, bukan mengulang
        q.loop = False

        # --- 3. MATIKAN ENGINE UPDATE ---
        if q.update_task:
            q.update_task.cancel()

        # --- 4. IDENTIFIKASI LAGU (Untuk Visual) ---
        lagu_dilewati = "Lagu tidak diketahui"
        if q.current_info:
            lagu_dilewati = q.current_info.get('title', 'Lagu saat ini')
        
        # Cek apa ada lagu berikutnya di antrean
        if q.queue:
            next_info = f"⏭️ **Selanjutnya:** `{q.queue[0]['title']}`"
        else:
            next_info = "Antrean kosong, bot akan standby. ✨"

        # --- 5. EKSEKUSI PEMUTUSAN AUDIO ---
        # vc.stop() akan memicu fungsi 'after_playing' yang ada di start_stream secara otomatis
        vc.stop()
        
        # Kembalikan status loop asli untuk lagu berikutnya nanti
        q.loop = original_loop

        # --- 6. KIRIM EMBED NOTIFIKASI ---
        embed = buat_embed_skip(interaction.user, lagu_dilewati, next_info)
        skip_msg = await interaction.followup.send(embed=embed)
        
        # Bersihkan pesan skip setelah 15 detik agar chat tidak penuh sampah
        await asyncio.sleep(15)
        try:
            await skip_msg.delete()
        except:
            pass
            
    else:
        # Jika bot sedang diam (idle)
        await interaction.followup.send("❌ **Gagal:** Tidak ada lagu yang sedang diputar untuk dilewati.", ephemeral=True)





#
# 🔂 7.5.  :	/loop - System
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="loop", description="Aktifkan atau matikan pengulangan lagu saat ini")
async def loop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    q.loop = not q.loop
    
    # Ambil judul lagu untuk dimasukkan ke embed
    judul = q.current_info.get('title', 'Lagu saat ini') if q.current_info else "Musik"
    
    # PANGGIL FUNGSI 4.7 TADI
    emb = buat_embed_loop(interaction.user, q.loop, judul)
    
    # Kirim respon
    await interaction.response.send_message(embed=emb, delete_after=15)





#
# 🔊 7.6.  :	/volume - System
# ------------------------------------------------------------------------------
#
#

@bot.tree.command(name="volume", description="Atur Volume Audio (0-100%)")
@app_commands.describe(persen="Masukkan angka antara 0 sampai 100")
async def volume(interaction: discord.Interaction, persen: int):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if 0 <= persen <= 100:
        # 1. Update Engine
        q.volume = persen / 100
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass
            
        # 2. Sinkronisasi ke Dashboard (Jika ada)
        # Kita update field Volume di dashboard yang sedang aktif
        if q.last_dashboard:
            try:
                emb_dash = q.last_dashboard.embeds[0]
                # Cari field volume dan update (pastikan index-nya benar)
                emb_dash.set_field_at(1, name="🔊 Volume", value=f"`{persen}%`", inline=True)
                await q.last_dashboard.edit(embed=emb_dash)
            except: pass

        # 3. Panggil Pabrik & Kirim
        embed_rapi = buat_embed_volume(persen, interaction.user)
        await interaction.response.send_message(embed=embed_rapi, delete_after=15)
        
    else:
        await interaction.response.send_message("❌ **Gagal:** Gunakan angka **0 - 100**.", ephemeral=True)






#
# 📜 7.7.  :	/queue - System
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="queue", description="Lihat daftar lagu yang akan diputar")
async def queue_cmd(interaction: discord.Interaction):
    # Memanggil fungsi pusat di Section 6.7
    await logic_tampilkan_antrean(interaction, interaction.guild_id)








#
#  ⏹️ 7.8.  :	/stop - System 
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="stop", description="Mematikan musik dan mengeluarkan bot dari voice channel")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client

    # 1. Matikan update progress bar jika ada
    if q.update_task:
        q.update_task.cancel()

    if vc:
        # 2. Ambil jumlah antrean untuk laporan sebelum dibersihkan
        jumlah_antrean = len(q.queue)
        
        # 3. Logika Pembersihan
        q.queue.clear()
        q.current_info = None
        
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None

        # 4. Putus Koneksi
        await vc.disconnect()
        
        # 5. PANGGIL PABRIK EMBED (Lebih Rapi!)
        # Kita panggil def yang sudah kita buat tadi di Section Central Embed
        embed_rapi = buat_embed_stop(interaction.user, jumlah_antrean)
        
        # 6. Kirim Respon
        await interaction.response.send_message(embed=embed_rapi, delete_after=20)
        
    else:
        await interaction.response.send_message(
            "❌ **Gagal:** Bot tidak sedang berada di Voice Channel.", 
            ephemeral=True
        )







#
# 🚪 7.9.  :	GROUPING /voice |	Masuk & Keluar 
# ------------------------------------------------------------------------------
#
#
voice_group = app_commands.Group(name="voice", description="Kontrol koneksi bot ke Voice Channel")



#
# 📥 7.9.1.  :	/voice Masuk - System 
# ------------------------------------------------------------------------------
#
#
@voice_group.command(name="masuk", description="Panggil bot ke Voice Channel")
async def masuk(interaction: discord.Interaction):
    # Cek User
    if not interaction.user.voice:
        emb_error = discord.Embed(
            title="🚫 Akses Ditolak",
            description="Kamu **belum masuk** ke Voice Channel!\nMohon masuk dulu agar aku bisa bergabung.",
            color=0xe74c3c
        )
        emb_error.set_footer(text="Gagal bergabung")
        return await interaction.response.send_message(content=interaction.user.mention, embed=emb_error, delete_after=60)

    # Logika Masuk
    vc = interaction.guild.voice_client
    target_channel = interaction.user.voice.channel

    if vc:
        if vc.channel.id == target_channel.id:
            return await interaction.response.send_message("⚠️ Aku sudah ada di sini bersamamu!", ephemeral=True)
        await vc.move_to(target_channel)
    else:
        await target_channel.connect()

    # Embed Sukses
    emb_success = discord.Embed(
        title="📥 Berhasil Bergabung!",
        description=f"Siap memutar musik di **{target_channel.name}** 🎵\nAyo putar lagu kesukaanmu!",
        color=0x2ecc71
    )
    emb_success.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
    
    await interaction.response.send_message(content=interaction.user.mention, embed=emb_success, delete_after=60)



#
# 📥 7.9.2.  :	/voice Keluar - System 
# ------------------------------------------------------------------------------
#
#
@voice_group.command(name="keluar", description="Keluarkan bot dari Voice Channel")
async def keluar(interaction: discord.Interaction):
    # Cek User
    if not interaction.user.voice:
        emb_error = discord.Embed(
            title="🚫 Akses Ditolak",
            description="Kamu **harus berada di Voice Channel** untuk menyuruhku keluar.",
            color=0xe74c3c
        )
        return await interaction.response.send_message(content=interaction.user.mention, embed=emb_error, delete_after=60)

    # Logika Keluar
    vc = interaction.guild.voice_client
    if vc:
        # Bersihkan Memory
        q = get_queue(interaction.guild_id)
        q.queue.clear()
        q.current_info = None
        
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        await vc.disconnect()
        
        # Embed Sukses
        emb_bye = discord.Embed(
            title="👋 Sampai Jumpa!",
            description="Aku telah keluar dari Voice Channel.\nTerima kasih sudah mendengarkan musik bersamaku! ✨",
            color=0xf1c40f
        )
        emb_bye.set_footer(text="Sesi berakhir dengan sukses")
        
        await interaction.response.send_message(content=interaction.user.mention, embed=emb_bye, delete_after=60)
    else:
        await interaction.response.send_message("❌ Aku sedang tidak berada di dalam Voice Channel.", ephemeral=True)







#
# 📤 7.9.3.  :	daftarkan Voice Group 
# ------------------------------------------------------------------------------
#
#
bot.tree.add_command(voice_group)






#
# 💡 7.9.4.  :	/help - System
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="help", description="Panduan lengkap penggunaan bot & info pengembang")
async def help_cmd(interaction: discord.Interaction):
    dev_id = 590774565115002880
    
    # --- EMBED 1: PANDUAN PENGGUNAAN ---
    emb_guide = discord.Embed(
        title="💿 Angelss Music • Player Guide", 
        color=0x3498db,
        description=(
            "Selamat datang di **Angelss Project V17**. Gunakan perintah di bawah ini untuk mengontrol musik secara maksimal.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    )
    
    bot_avatar = bot.user.display_avatar.url if bot.user else None
    emb_guide.set_thumbnail(url=bot_avatar)
    
    emb_guide.add_field(
        name="🎧 Kontrol Musik",
        value=(
            "`/play` ➜ Putar lagu (Judul/Link)\n"
            "`/pause` ➜ Jeda musik sementara\n"
            "`/resume` ➜ Lanjut memutar musik\n"
            "`/skip` ➜ Lewati lagu sekarang\n"
            "`/stop` ➜ Berhenti & hapus antrean\n"
            "`/queue` ➜ Lihat & lompat antrean"
        ), 
        inline=False
    )
    
    emb_guide.add_field(
        name="🎚️ Sistem & Koneksi",
        value=(
            "`/volume` ➜ Atur suara (0-100%)\n"
            "`/voice masuk` ➜ Panggil bot ke Voice\n"
            "`/voice keluar` ➜ Usir bot dari Voice"
        ), 
        inline=False
    )

    emb_guide.add_field(
        name="✨ Fitur Dashboard",
        value="Bot ini dilengkapi dashboard interaktif dengan tombol **Smart Pause**, **Mixer**, dan **Live Queue** untuk kemudahan akses tanpa mengetik.",
        inline=False
    )

    # --- EMBED 2: DEVELOPER PROFILE ---
    emb_dev = discord.Embed(title="👨‍💻 Developer Information", color=0x9b59b6)
    
    emb_dev.description = (
        f"**Project Owner :** ikiii (<@{dev_id}>)\n"
        f"**Role :** Active - IT Engineering\n"
        f"**Specialist :** Python Developer\n\n"
        f"**Note :**\n"
        f"\"Bot ini dibuat oleh **ikiii** yang bijaksana. Segala sesuatu diawali dengan berdo'a 🤲🏻, amiin.\""
    )
    
    emb_dev.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif")
    
    emb_dev.set_footer(
        text=f"Angelss Project FIX FINAL V1 • Requested by {interaction.user.name}", 
        icon_url=interaction.user.display_avatar.url
    )
    
    await interaction.response.send_message(embeds=[emb_guide, emb_dev])






#
# 🛠️ 7.9.5.  :	/debug - Syatem
# ------------------------------------------------------------------------------
#
#
@bot.tree.command(name="debug", description="Cek kesehatan sistem audio dan environment hosting")
async def debug_system(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    import subprocess
    import sys
    import platform
    import os 

    # 1. Cek FFmpeg
    try:
        ffmpeg_version = subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT).decode().split('\n')[0]
        ffmpeg_status = f"✅ Terdeteksi: `{ffmpeg_version[:40]}...`"
    except Exception:
        ffmpeg_status = "❌ **TIDAK TERDETEKSI!** (Bot akan bisu/skip otomatis)"

    # 2. Cek Python & OS
    py_ver = sys.version.split(' ')[0]
    os_info = f"{platform.system()} {platform.release()}"
    
    # 3. Cek yt-dlp
    try:
        import yt_dlp
        ytdl_ver = yt_dlp.version.__version__
        ytdl_status = f"✅ v{ytdl_ver}"
    except:
        ytdl_status = "❌ Not Installed"

    # 4. Cek Folder .local
    local_folder = "Ada (Cek File Manager)" if os.path.exists(".local") else "Tidak Ada (Bersih)"
    python_38_check = "⚠️ Terdeteksi" if os.path.exists(".local/lib/python3.8") else "✅ Aman"

    embed = discord.Embed(title="🛠️ System Diagnostic Tool", color=0x3498db)
    embed.add_field(name="🛰️ FFmpeg Status", value=ffmpeg_status, inline=False)
    embed.add_field(name="🐍 Python Version", value=f"`{py_ver}`", inline=True)
    embed.add_field(name="📦 yt-dlp Version", value=f"`{ytdl_status}`", inline=True)
    embed.add_field(name="📁 Folder .local", value=f"`{local_folder}`", inline=True)
    embed.add_field(name="📂 Konflik Python 3.8", value=f"`{python_38_check}`", inline=True)
    embed.add_field(name="🖥️ OS Info", value=f"`{os_info}`", inline=False)

    if "❌" in ffmpeg_status:
        embed.description = "⚠️ **PERINGATAN:** FFmpeg tidak ditemukan. Gunakan Docker Image yang mendukung FFmpeg di Startup Panel!"
        embed.color = 0xe74c3c
    else:
        embed.description = "✨ Semua sistem terlihat normal. Jika bot masih skip, cek link YouTube-nya."

    await interaction.followup.send(embed=embed)










# --- [ 8 ] --- 8.1
#
# ==============================================================================
#			[ GLOBAL ERROR HANDLER - THE SAFETY NET ]
# ==============================================================================
#
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # Jika error disebabkan oleh cooldown
    if isinstance(error, app_commands.CommandOnCooldown):
        return await interaction.response.send_message(
            f"⏳ **Sabar kii!** Kamu terlalu cepat. Coba lagi dalam `{error.retry_after:.1f}` detik.", 
            ephemeral=True
        )

    # Log error asli ke konsol untuk debug kamu (IT Engineering)
    logger.error(f"Global Error: {error}")

    # Menangani error YouTube saat proses ekstraksi metadata
    err_msg = str(error).lower()
    
    friendly_msg = "⚠️ **Terjadi kesalahan sistem.**"
    
    if "403" in err_msg or "forbidden" in err_msg:
        friendly_msg = "🚫 **YouTube Block (403):** Permintaan ditolak oleh YouTube. Coba lagi nanti atau gunakan link lain."
    elif "private video" in err_msg:
        friendly_msg = "🔒 **Private:** Video ini diprivasi oleh pemiliknya."
    elif "not found" in err_msg:
        friendly_msg = "🔍 **Not Found:** Lagu tidak ditemukan di YouTube."

    # Kirim respon ke user agar mereka tahu apa yang terjadi
    try:
        if interaction.response.is_done():
            await interaction.followup.send(friendly_msg, ephemeral=True)
        else:
            await interaction.response.send_message(friendly_msg, ephemeral=True)
    except:
        pass





# --- [ 9 ] ---
#
# ==============================================================================
#			[ BOOTLOADER ]
# ==============================================================================


#
# 🚀 9.1 :	
# ------------------------------------------------------------------------------
#
#
if __name__ == "__main__":
    bootstrap()
    bot.run(TOKEN)