# ==============================================================================
# 💿 PROJECT     : Angelss Music Bot (V17 FINAL FIX)
# 👨‍💻 DEVELOPER : ikiii (IT Engineering)
# 🚀 STATUS		: Production Ready
# 🛡️ LICENSE  	 : Personal Project - Angelss Project
# ==============================================================================



"""


DESCRIPTION KUUUHH	:
		
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
import shutil  
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


# --- [ 3.1: YTDL WAR-MODE CONFIG ] ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': COOKIES_FILE, 
    'cachedir': False,
    # --- [ BYPASS TRICKS ] ---
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'ios', 'web'],
            'po_token': ['web+web_embedded_player'], # Memicu bypass token terbaru
        }
    },
    'http_chunk_size': 10485760,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.youtube.com',
        'Referer': 'https://www.youtube.com/',
        'Sec-Fetch-Mode': 'navigate',
    }
}


# --- [ 3.2: HIGH-FIDELITY AUDIO ENGINE ] ---
FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-reconnect_at_eof 1 '
        '-nostdin '
        '-threads 0' # Menggunakan seluruh core CPU yang tersedia untuk proses cepat
    ),
    'options': (
        '-vn ' # Abaikan video
        '-ac 2 ' # Stereo channel
        '-ar 48000 ' # Resample ke 48kHz (Optimal untuk Discord)
        #'-b:a 192k ' # Bitrate tinggi
        '-af "loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000:async=1" ' # Normalisasi suara premium
        '-loglevel warning'
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
        self.lock = asyncio.Lock() 
        self.is_seeking = False  
        self.last_msg = None 
        
        

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
    """Fungsi pembantu agar tampilan skip selalu cantik & seragam ✨"""
    judul_bersih = str(lagu_dilewati)[:100].strip() 
    
    embed = discord.Embed(
        title="⏭️ MUSIC SKIPPED",
        description=(
            f"✨ **{user.mention}** telah melompat ke lagu berikutnya!\n\n"
            f"🗑️ **Dilewati:** `{judul_bersih}`\n"
            f"📥 **Status:** {info_selanjutnya}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xe67e22 
    )
    embed.set_footer(text="System Skip • Angelss Project V17", icon_url=user.display_avatar.url)
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
    


    # 2. Validasi Token
    if not TOKEN:
        logger.critical("Fatal Error: DISCORD_TOKEN is missing from environment.")
        exit(1)
        
    if os.path.exists(COOKIES_FILE):
        logger.info(f"Identity: YouTube Cookies loaded from '{COOKIES_FILE}'.")
    else:
        logger.warning(f"Identity: Running without cookies. High-risk of 403 Forbidden.")






# ==============================================================================
# 🔘▬ 4.3. : Function Progress Bar (DYNAMIC SCALE VERSION)
# ==============================================================================
def create_progress_bar(current, total):
    """
    Progress Bar dengan karakter yang lebih smooth (Modern Tech Style).
    """
    if total < 300: length = 12
    elif total < 1800: length = 20
    else: length = 30

    if total <= 0: return "0:00 ━━🔘───────── 0:00"
    
    percentage = current / total
    progress = int(length * percentage)
    progress = min(progress, length - 1)
    
    # Menggunakan kombinasi garis tebal dan tipis
    bar = "━" * progress + "🔘" + "─" * (max(0, length - progress - 1))
    
    return bar





# ==============================================================================
# 🖼️ 4.4. : Function Dashboard (PREMIUM VERSION)
# ==============================================================================
def buat_embed_dashboard(q, elapsed_time, duration, title, url, thumbnail, user):
    warna = 0x2ecc71 if q.loop else 0x5865f2 # Biru Blurple khas Discord
    bar_visual = create_progress_bar(elapsed_time, duration)
    
    time_now = format_time(elapsed_time)
    time_total = format_time(duration)
    
    vol_percent = int(q.volume * 100)
    vol_emoji = "🔇" if vol_percent == 0 else "🔈" if vol_percent < 50 else "🔊"

    embed = discord.Embed(color=warna, timestamp=datetime.datetime.now())
    
    # Header: Menampilkan siapa yang memutar sesi pertama (Pinned User)
    embed.set_author(
        name=f"ANGELSS AUDIO ENGINE • NOW PLAYING", 
        icon_url="https://cdn.pixabay.com/animation/2022/12/25/06/28/06-28-22-725_512.gif"
    )
    
    # Body: Judul Bold dengan Garis Rapi
    embed.description = (
        f"### 🎵 [{title[:60]}]({url})\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"```\n"
        f"{time_now} {bar_visual} {time_total}\n"
        f"      ⏳ Status: {'Playing' if not q.pause_time else 'Paused'}\n"
        f"```"
    )
    
    # Fields: Informasi Teknis yang Rapi
    embed.add_field(name="🛰️ Server", value="`Jakarta-ID`", inline=True)
    embed.add_field(name=f"{vol_emoji} Volume", value=f"`{vol_percent}%`", inline=True)
    embed.add_field(name="🔁 Loop", value=f"`{'ON' if q.loop else 'OFF'}`", inline=True)
    
    # Mention Requester dengan Emoticon Sesuai
    embed.add_field(name="👤 Requested By", value=f"{user.mention} ✨", inline=False)
    
    if thumbnail: 
        embed.set_thumbnail(url=thumbnail)
        
    embed.set_footer(
        text=f"Angelss Project V17 • Stability Mode • {user.display_name}", 
        icon_url=user.display_avatar.url
    )
    
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
# --- [ 4.8 ] ---
# --- [ 4.8 ] ---
# ==============================================================================
# 🏗️ CLASS MODERN BOT & NOTIFICATION ONLINE SYSTEM (SINGLE FILE VERSION)
# ==============================================================================
class ModernBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        
        super().__init__(
            command_prefix="!", 
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        try:
            synced = await self.tree.sync()
            logger.info(f"✅ Berhasil sinkronisasi {len(synced)} slash commands secara global.")
        except Exception as e:
            logger.error(f"❌ Gagal sinkronisasi command: {e}")

    async def on_ready(self):

        # 1. Set Status
        activity = discord.Activity(type=discord.ActivityType.listening, name="/play | Angelss V17")
        await self.change_presence(status=discord.Status.online, activity=activity)

        # 2. Logika Waktu Indonesia (WIB)
        tz_wib = datetime.timezone(datetime.timedelta(hours=7))
        waktu_sekarang_wib = datetime.datetime.now(tz_wib)
        target_channel_id = 1456250414638043169 
        
        try:
            channel = self.get_channel(target_channel_id)
            if channel:
                # Clean up history
                try:
                    async for message in channel.history(limit=10):
                        if message.author == self.user: await message.delete()
                except: pass

                # --- [ EMBED ASLI KAMU - TIDAK DIUBAH ] ---
                embed = discord.Embed(
                    title="🚀 SYSTEM RELOADED & UPDATED",
                    description=(
                        "**Bot telah online dan berhasil diperbarui!**\n"
                        "Seluruh engine audio telah dioptimalkan untuk Python 3.10 dan FFmpeg v5.0."
                    ),
                    color=0x2ecc71 
                )
                embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
                latensi = round(self.latency * 1000) if self.latency else "---"
                embed.add_field(name="🛰️ Cluster", value="`Jakarta-ID`", inline=True)
                embed.add_field(name="⚡ Latency", value=f"`{latensi}ms`", inline=True)
                embed.add_field(name="📡 Engine", value="`FFmpeg 5.0`", inline=True)
                embed.add_field(name="💡 Guide", value="Ketik `/play` atau `/help` untuk bantuan", inline=False)
                
                str_waktu = waktu_sekarang_wib.strftime('%d/%m/%Y %H:%M')
                embed.add_field(name="📅 System Ready", value=f"`{str_waktu} WIB`", inline=False)

                embed.set_footer(text="Angelss Project Final Fix • Powered by ikiii", icon_url=self.user.display_avatar.url)
                embed.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif") 
                await channel.send(embed=embed)
        except Exception as e:
            logger.error(f"⚠️ Gagal on_ready: {e}")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"✅ SYSTEM ONLINE - NOTIFICATION : {self.user.name}")
        print(f"🐍 PYTHON VER  : 3.10.x")
        print(f"📅 STARTED AT  : {waktu_sekarang_wib.strftime('%Y-%m-%d %H:%M:%S')} WIB")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

bot = ModernBot()










#


# ==============================================================================
# 📥 4.9. : Function Added Queue (SINKRON VERSION)
# ==============================================================================
def buat_embed_added_queue(title, url, thumbnail, user, posisi):
    embed = discord.Embed(
        title="📥 LAGU DITAMBAHKAN KE ANTREAN",
        description=(
            f"### 🎵 [{title[:60]}]({url})\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0x3498db
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    embed.add_field(name="🔢 Posisi", value=f"`{posisi}`", inline=True)
    embed.add_field(name="👤 Pemesan", value=user.mention, inline=True)
    embed.add_field(name="📡 Status", value="`Standby`", inline=True)
    
    embed.set_footer(text="Gunakan /queue untuk melihat semua daftar", icon_url=user.display_avatar.url)
    return embed














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
# 🔍 5.1. :	Class System Search Engine Pilihan
# ------------------------------------------------------------------------------
class SearchControlView(discord.ui.View):
    def __init__(self, entries, user):
        super().__init__(timeout=60) 
        self.entries = entries
        self.user = user
        self.add_select_menu()

    def add_select_menu(self):
        self.clear_items()
        options = []
        for i, entry in enumerate(self.entries):
            title = entry.get('title', 'Judul tidak diketahui')[:50]
            url = entry.get('url') or entry.get('webpage_url')
            options.append(discord.SelectOption(label=f"Lagu Nomor {i+1}", value=url, description=title, emoji="🎵"))
            
        select = discord.ui.Select(placeholder="🎯 Pilih lagu untuk ditambahkan...", options=options)
        
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                return await interaction.response.send_message("⚠️ Hanya pemanggil yang bisa memilih!", ephemeral=True)
            
            # FIX: Gunakan edit_message agar interaksi dianggap selesai & menu hilang
            await interaction.response.edit_message(content="⌛ **Memproses pilihan kii...**", embed=None, view=None)
            
            # Panggil play_music (Logic play_music sudah di-fix di bawah)
            await play_music(interaction, select.values[0])

        select.callback = callback
        self.add_item(select)

    def create_embed(self):
        description = "📺 **YouTube Search Engine**\n*(Pilih nomor lagu di bawah ini)*\n\n"
        for i, entry in enumerate(self.entries):
            description += f"✨ `{i+1}.` {entry.get('title', 'Unknown Title')[:60]}...\n"
        embed = discord.Embed(title="🔍 Hasil Pencarian Musik", description=description, color=0xf1c40f)
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif") 
        return embed




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
# 📋 5.3.  : UI Class: Queue Selector (LOMPAT KE LAGU TERTENTU)
# ------------------------------------------------------------------------------
#
class QueueControlView(discord.ui.View):
    def __init__(self, guild_id, user, options):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.user = user
        select = discord.ui.Select(placeholder="🎯 Pilih lagu untuk langsung diputar...", options=options)
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.user:
            return await interaction.response.send_message("⚠️ Hanya pemanggil yang bisa memilih!", ephemeral=True)
        
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        index_dipilih = int(interaction.data['values'][0])
        
        # --- [ LOGIKA PINDAH LAGU TANPA MENGHAPUS ] ---
        # Ambil lagu yang dipilih dari daftar
        daftar_antrean = list(q.queue)
        lagu_pilihan = daftar_antrean.pop(index_dipilih)
        
        # Masukkan kembali sisa lagu ke antrean utama (agar tidak hilang)
        q.queue.clear()
        for s in daftar_antrean:
            q.queue.append(s)

        if vc:
            # Beritahu sistem bahwa kita mau 'Force Start' lagu baru
            q.is_seeking = False 
            # Kita jalankan play_music atau start_stream untuk lagu pilihan
            await interaction.response.send_message(f"🚀 **Melompat ke:** `{lagu_pilihan['title'][:50]}`", ephemeral=True)
            await start_stream(interaction, lagu_pilihan['url'])









#
#
# 📼 5.4.  : UI Class: Dashboard & Audio Player (STABILIZED)
# ------------------------------------------------------------------------------
class MusicDashboard(discord.ui.View):
    def __init__(self, guild_id): 
        super().__init__(timeout=None)
        self.guild_id = guild_id
	
    # --- TOMBOL 1: MUNDUR 10 DETIK ---
    @discord.ui.button(label="-10s", emoji="⏪", style=discord.ButtonStyle.secondary)
    async def backward(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        q = get_queue(self.guild_id)
        current_pos = time.time() - q.start_time
        new_pos = max(0, current_pos - 10)
        await self.execute_premium_seek(interaction, new_pos)
        
    # --- TOMBOL 2: JEDA / LANJUT ---
    @discord.ui.button(label="Jeda", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pp(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Gunakan defer/edit_message agar UI sinkron
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        if not vc: return
        
        if vc.is_playing():
            vc.pause()
            q.pause_time = time.time()
            button.emoji, button.label, button.style = "▶️", "Lanjut", discord.ButtonStyle.success 
        else:
            current_pos = q.pause_time - q.start_time
            q.start_time = time.time() - current_pos
            vc.resume()
            button.emoji, button.label, button.style = "⏸️", "Jeda", discord.ButtonStyle.secondary

        await interaction.response.edit_message(view=self)
	
    # --- TOMBOL 3: MAJU 10 DETIK ---
    @discord.ui.button(label="+10s", emoji="⏩", style=discord.ButtonStyle.secondary)
    async def forward(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        q = get_queue(self.guild_id)
        current_pos = time.time() - q.start_time
        new_pos = min(q.total_duration, current_pos + 10)
        await self.execute_premium_seek(interaction, new_pos)
        
    # --- TOMBOL 4: SKIP ---
    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        if not vc or not (vc.is_playing() or vc.is_paused()):
            return await interaction.response.send_message("❌ Tidak ada lagu untuk di-skip!", ephemeral=True)

        await interaction.response.defer()
        q.loop = False 
        q.is_seeking = False 
        
        if q.update_task:
            q.update_task.cancel() 
            
        vc.stop() 

    # --- TOMBOL 5: ANTREAN ---
    @discord.ui.button(label="Antrean", emoji="📜", style=discord.ButtonStyle.gray)
    async def list_q_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Tambahkan defer agar tidak failed saat memproses list antrean
        if not interaction.response.is_done():
            await interaction.response.defer()
        await logic_tampilkan_antrean(interaction, self.guild_id)

    # --- TOMBOL 6: LOOP ---
    @discord.ui.button(label="Loop: OFF", emoji="🔁", style=discord.ButtonStyle.gray)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        q.loop = not q.loop
        button.label = "Loop: ON" if q.loop else "Loop: OFF"
        button.style = discord.ButtonStyle.success if q.loop else discord.ButtonStyle.gray
        button.emoji = "🔂" if q.loop else "🔁"
        await interaction.response.edit_message(view=self)
        
    # --- TOMBOL 7: Volume ---
    @discord.ui.button(label="Volume", emoji="🔊", style=discord.ButtonStyle.gray)
    async def vol_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Tombol ini membuka view baru, tidak perlu defer di sini karena send_message sudah cukup
        view = VolumeControlView(self.guild_id)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)
        
    # --- TOMBOL 8: STOP ---
    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Tambahkan defer sebelum memproses disconnect
        if not interaction.response.is_done():
            await interaction.response.defer()
            
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        q.queue.clear()
        if vc: await vc.disconnect()
        await interaction.followup.send(embed=buat_embed_stop(interaction.user, 0))

    # --- [ FUNGSI JANTUNG PREMIUM SEEK ] ---
    async def execute_premium_seek(self, interaction, new_pos):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        if vc and (vc.is_playing() or vc.is_paused()):
            q.is_seeking = True 
            data = q.current_info
            
            ffmpeg_before = FFMPEG_OPTIONS['before_options'] + f" -ss {new_pos}"
            audio_source = discord.FFmpegPCMAudio(data['url'], before_options=ffmpeg_before, options=FFMPEG_OPTIONS['options'])
            source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)
            
            vc.stop() 
            vc.play(source, after=lambda e: bot.loop.create_task(next_logic(self.guild_id)) if not q.is_seeking else None)
            
            q.start_time = time.time() - new_pos
            await asyncio.sleep(1)
            q.is_seeking = False













# --- [ 6 ] ---
#
# ==============================================================================
#			[ FUNCTION HELPER - ASYNCE DEF  - MODERN ]
# ==============================================================================




#
#
# ⏱️ 6.1. : Function asynce def system auto update bar and durasi (ANTI-ZOMBIE)
# ------------------------------------------------------------------------------
#
async def update_player_interface(message, duration, title, url, thumbnail, user, guild_id):
    q = get_queue(guild_id)
    try:
        while not bot.is_closed():
            vc = message.guild.voice_client
            
            # --- [ PENGAMAN TAMBAHAN ] ---
            # Jika VC hilang atau bot disconnect secara paksa, hentikan loop.
            if not vc or not vc.is_connected():
                logger.info(f"Task Update {guild_id} dihentikan: Bot Disconnected.")
                break
                
            if (not (vc.is_playing() or vc.is_paused()) and not getattr(q, 'is_seeking', False)):
                break
                
            if q.last_dashboard and message.id != q.last_dashboard.id:
                break

            # Hitung waktu
            if vc.is_paused():
                elapsed_time = q.pause_time - q.start_time
            else:
                elapsed_time = time.time() - q.start_time
                
            elapsed_time = max(0, min(elapsed_time, duration))

            try:
                embed = buat_embed_dashboard(q, elapsed_time, duration, title, url, thumbnail, user)
                await message.edit(embed=embed)
            except discord.NotFound:
                break
            except Exception:
                pass
            
            await asyncio.sleep(1) # Update tiap 1 detik

    except asyncio.CancelledError:
        raise 
    except Exception as e:
        logger.error(f"Error Interface: {e}")











#
#  🔊⚠️ 6.2. :	Function Auto Disconnect VC (DEEP CLEAN VERSION)
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
# ⏯️ 6.3. : HELPER: System Pause / Resume Dynamic (Sinkronisasi UI)
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





# 📡 6.4 : MESIN UTAMA - START STREAM (ULTIMATE SINGLE MESSAGE VERSION)
# ------------------------------------------------------------------------------
async def start_stream(interaction, url, seek_time=None, guild_id_manual=None):
    g_id = interaction.guild.id if interaction else guild_id_manual
    if not g_id: return
    
    q = get_queue(g_id)
    if interaction: q.text_channel_id = interaction.channel.id

    guild = bot.get_guild(g_id)
    vc = guild.voice_client if guild else None
    
    if not vc:
        logger.error(f"Bot tidak terdeteksi di VC pada Guild {g_id}")
        return

    # --- [ FIX DASHBOARD PERSISTENCE ] ---
    if interaction and not interaction.response.is_done():
        try: await interaction.response.defer(ephemeral=True)
        except: pass

    async with q.lock:
        if q.update_task:
            q.update_task.cancel()

        # Hapus Dashboard lama agar yang baru muncul di paling bawah
        if q.last_dashboard:
            try: 
                await q.last_dashboard.delete()
                q.last_dashboard = None
            except: pass

        try:
            def fetch_info():
                with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                    return ydl.extract_info(url, download=False)

            data = await bot.loop.run_in_executor(None, fetch_info)
            if not data: raise Exception("Metadata tidak ditemukan")
            if 'entries' in data: data = data['entries'][0]
            
            q.current_info = data
            stream_url = data.get('url') 
            q.total_duration = data.get('duration') or 0
            
            ffmpeg_before = FFMPEG_OPTIONS['before_options']
            if seek_time: ffmpeg_before += f" -ss {seek_time}"

            audio_source = discord.FFmpegPCMAudio(stream_url, before_options=ffmpeg_before, options=FFMPEG_OPTIONS['options'])
            source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)

            def after_playing(error):
                if getattr(q, 'is_seeking', False): return
                if q.update_task: 
                    bot.loop.call_soon_threadsafe(q.update_task.cancel)
                
                if q.loop and q.current_info:
                    bot.loop.create_task(start_stream(None, q.current_info['webpage_url'], guild_id_manual=g_id))
                else:
                    bot.loop.create_task(next_logic(g_id))
            
            if vc.is_playing() or vc.is_paused(): 
                vc.stop()
            
            await asyncio.sleep(0.5) 
            vc.play(source, after=after_playing)
            q.start_time = time.time() - (float(seek_time) if seek_time else 0)
            
            # --- [ KIRIM DASHBOARD ] ---
            channel = bot.get_channel(q.text_channel_id)
            if channel:
                if hasattr(q, 'last_msg') and q.last_msg:
                    try: await q.last_msg.delete()
                    except: pass
                    q.last_msg = None

                penerbit = data.get('requester')
                if not penerbit:
                    penerbit = interaction.user if interaction else bot.user

                # Pakai Embed Dashboard Aslimu kii
                emb = buat_embed_dashboard(
                    q, float(seek_time or 0), q.total_duration, 
                    data['title'], data['webpage_url'], 
                    data.get('thumbnail'), penerbit
                )
                
                q.last_dashboard = await channel.send(embed=emb, view=MusicDashboard(g_id))
                
                q.update_task = bot.loop.create_task(
                    update_player_interface(
                        q.last_dashboard, q.total_duration, 
                        data['title'], data['webpage_url'], 
                        data.get('thumbnail'), penerbit, g_id
                    )
                )

        except Exception as e:
            # --- [ KODE NOTIFIKASI ERROR ASLIMU (TETAP DIJAGA) ] ---
            error_str = str(e)
            logger.error(f"Kritis di Start Stream Guild {g_id}: {error_str}")
            
            chan = bot.get_channel(q.text_channel_id)
            if chan:
                if "403" in error_str:
                    msg = "🚫 **YouTube Error (403):** Akses ditolak. Mencoba memutar lagu berikutnya..."
                elif "sign in" in error_str.lower():
                    msg = "🔞 **YouTube Error:** Lagu ini dibatasi umur (Age Restricted)."
                elif "video unavailable" in error_str.lower():
                    msg = "❌ **YouTube Error:** Video tidak tersedia/dihapus."
                else:
                    msg = f"⚠️ **Audio Error:** Masalah pada stream. `{error_str[:50]}...`"
                
                await chan.send(msg, delete_after=15)

            if q.update_task:
                q.update_task.cancel()

            # Lanjut ke lagu berikutnya kalau error
            bot.loop.create_task(next_logic(g_id))









        
        
#
# ⏭️ 6.5 : LOGIKA PINDAH LAGU OTOMATIS
# ------------------------------------------------------------------------------
#
#
async def next_logic(guild_id):
    q = get_queue(guild_id)
    
    # Tunggu sebentar untuk memastikan engine FFmpeg benar-benar tertutup
    await asyncio.sleep(2) 
    
    if q.queue:
        next_song = q.queue.popleft()
        # PENTING: Gunakan start_stream untuk memutar lagu berikutnya
        await start_stream(None, next_song['url'], guild_id_manual=guild_id)
    else:
        # Jika antrean habis
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        chan = bot.get_channel(q.text_channel_id)
        if chan: 
            await chan.send("✅ **Antrean selesai. Bot standby.**", delete_after=10)




# ------------------------------------------------------------------------------
# 🎵 6.6 : LOGIKA PLAY MUSIC (SINKRONISASI NOTIFIKASI & AUTO-JOIN) - UPDATED
# ------------------------------------------------------------------------------
 # ------------------------------------------------------------------------------
# 🎵 6.6 : LOGIKA PLAY MUSIC (SINKRONISASI NOTIFIKASI & AUTO-JOIN)
# ------------------------------------------------------------------------------
async def play_music(interaction, search):
    q = get_queue(interaction.guild_id)
   
    try:
        # 1. Pastikan interaksi tidak hangus
        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        # 2. Cek Voice Channel
        if not interaction.user.voice:
            return await interaction.followup.send("⚠️ Kamu harus masuk ke Voice Channel dulu!", ephemeral=True)

        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()

        # 3. Fungsi pencarian YouTube
        def search_yt():
            with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl:
                info = ydl.extract_info(f"ytsearch:{search}" if "http" not in search else search, download=False)
                if 'entries' in info: return info['entries'][0]
                return info

        data = await bot.loop.run_in_executor(None, search_yt)
        if not data:
            return await interaction.followup.send("❌ Lagu tidak ditemukan.", ephemeral=True)

        song_data = {
            'url': data['webpage_url'],
            'title': data['title'],
            'duration': data.get('duration', 0),
            'requester': interaction.user,
            'thumbnail': data.get('thumbnail')
        }
        
        # 4. Hapus notifikasi pencarian lama jika ada
        if q.last_search_msg:
            try: await q.last_search_msg.delete()
            except: pass
            q.last_search_msg = None

        # 5. Logika Antrean (Queue)
        if vc.is_playing() or vc.is_paused():
            q.queue.append(song_data)
            posisi = len(q.queue)
            emb_queue = buat_embed_added_queue(data['title'], data['webpage_url'], data.get('thumbnail'), interaction.user, posisi)
            
            if q.last_msg:
                try: await q.last_msg.delete()
                except: pass
            
            q.last_msg = await interaction.channel.send(embed=emb_queue)
            await interaction.followup.send("✅ Berhasil masuk antrean!", ephemeral=True)
        else:
            # 6. Langsung Putar
            await interaction.followup.send(f"🚀 Memutar: **{data['title'][:50]}**", ephemeral=True)
            await start_stream(interaction, data['webpage_url'])

    except Exception as e:
        # --- FIX INDENTASI TOTAL DI SINI ---
        logger.error(f"Play Music Error: {e}")
        try:
            if interaction.response.is_done():
                await interaction.followup.send(f"⚠️ **Sistem Error:** `{e}`", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ **Sistem Error:** `{e}`", ephemeral=True)
        except:
            pass

            
    
    

        




#
# 

# --- [ SEKSI 6.7: LOGIKA & VIEW ANTREAN (FIXED) ] ---

async def logic_tampilkan_antrean(interaction, guild_id):
    """Fungsi pusat untuk menampilkan daftar antrean lagu"""
    q = get_queue(guild_id)
    
    if not q.queue and not q.current_info:
        return await interaction.response.send_message("📭 **Antrean kosong kii!** Ayo tambahkan lagu pake `/play`.", ephemeral=True)

    # 1. Header Antrean
    embed = discord.Embed(title="📜 DAFTAR ANTREAN MUSIK", color=0x3498db)
    
    # 2. Info Lagu Saat Ini
    if q.current_info:
        embed.add_field(
            name="🎧 Sedang Diputar", 
            value=f"**[{q.current_info['title'][:60]}]({q.current_info['webpage_url']})**", 
            inline=False
        )

    # 3. List Antrean (Maksimal 15 lagu untuk display)
    description = ""
    options = []
    
    if q.queue:
        # Convert ke list untuk indexing aman
        queue_list = list(q.queue)
        for i, song in enumerate(queue_list[:15]):
            description += f"`{i+1}.` {song['title'][:50]}...\n"
            # Buat opsi untuk Select Menu
            options.append(discord.SelectOption(
                label=f"Lagu Ke-{i+1}", 
                value=str(i), 
                description=song['title'][:45], 
                emoji="🎯"
            ))
        embed.description = f"**Selanjutnya:**\n{description}"
    else:
        embed.description = "*(Tidak ada lagu selanjutnya di antrean)*"

    embed.set_footer(text=f"Total: {len(q.queue)} lagu dalam antrean")

    # 4. Kirim dengan Select Menu jika ada antrean
    if options:
        # Kirim user agar hanya pengklik tombol yang bisa milih (Opsional, sudah ada di classmu)
        view = QueueControlView(guild_id, interaction.user, options)
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)
    else:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)


class QueueControlView(discord.ui.View):
    def __init__(self, guild_id, user, options):
        super().__init__(timeout=60)
        self.guild_id = guild_id
        self.user = user
        
        # Inisialisasi Select Menu
        self.select = discord.ui.Select(
            placeholder="🎯 Pilih lagu untuk langsung diputar (Skip to)...",
            options=options
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        # Proteksi User
        if interaction.user != self.user:
            return await interaction.response.send_message("⚠️ Ini bukan antreanmu kii!", ephemeral=True)
        
        # 1. Kasih feedback instan agar tidak timeout
        await interaction.response.edit_message(content="⌛ **Melompat ke lagu pilihan...**", view=None, embed=None)
        
        q = get_queue(self.guild_id)
        
        # Ambil index dari pilihan dropdown
        try:
            index_target = int(self.select.values[0])
        except (IndexError, ValueError):
            return

        if 0 <= index_target < len(q.queue):
            # 2. HENTIKAN PROSES LAMA (Task update bar & Dashboard lama)
            if q.update_task:
                q.update_task.cancel()
            
            # 3. Buang lagu-lagu sebelum target (Skimming)
            for _ in range(index_target):
                q.queue.popleft()
            
            # 4. Ambil lagu target dan hapus dari antrean untuk diputar
            target_song = q.queue.popleft()
            
            # 5. EKSEKUSI PEMUTARAN BARU
            # Kita panggil start_stream secara utuh agar dashboard terkirim lagi
            await start_stream(
                interaction=None, 
                url=target_song['url'], 
                guild_id_manual=self.guild_id
            )
        else:
            await interaction.followup.send("❌ Lagu sudah tidak ada di antrean kii!", ephemeral=True)








# --- [ 7 ] ---
# ==============================================================================
#			SECTION: MUSIC COMMANDS (STANDARD)
# ==============================================================================

# ▶️ 7.1 : /play - Search Engine (MODERN UI)
# ------------------------------------------------------------------------------
# --- [ SEKSI 7.1: /play (FINAL SINKRON - FIXED) ] ---
@bot.tree.command(name="play", description="Putar musik dari YouTube")
@app_commands.describe(cari="Masukkan judul lagu atau link YouTube")
async def play(interaction: discord.Interaction, cari: str):
    # Gunakan defer di awal untuk mencegah "Interaction Failed"
    # Pastikan ephemeral=True agar notifikasi proses bersifat privat
    await interaction.response.defer(ephemeral=True) 
    
    q = get_queue(interaction.guild.id)
    q.text_channel_id = interaction.channel.id 

    if not interaction.user.voice:
        return await interaction.followup.send("❌ **Gagal:** Kamu harus masuk Voice Channel dulu kii!", ephemeral=True)

    try:
        # Langsung panggil logika play_music
        await play_music(interaction, cari)
    except Exception as e:
        logger.error(f"Error Command Play: {e}")
        try:
            await interaction.followup.send(f"⚠️ Terjadi kesalahan: {e}", ephemeral=True)
        except:
            pass





# ⏸️ 7.2. : /pause - System (REFINED)
# ------------------------------------------------------------------------------
@bot.tree.command(name="pause", description="Jeda musik")
async def pause_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        q.pause_time = time.time()
        if q.update_task: q.update_task.cancel()
        
        await sync_dashboard_buttons(q.last_dashboard, interaction.guild_id)
        await interaction.response.send_message(embed=buat_embed_status("⏸️", "Musik dijeda.", 0xf1c40f), delete_after=10)
    else:
        await interaction.response.send_message("❌ Tidak ada musik berjalan.", ephemeral=True)

# ▶️ 7.3. : /resume - System (REFINED)
# ------------------------------------------------------------------------------
@bot.tree.command(name="resume", description="Lanjut memutar musik")
async def resume_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        current_pos = time.time() - q.start_time
        q.start_time = time.time() - current_pos
        vc.resume()
        
        if q.last_dashboard and q.current_info:
            # Gunakan data requester asli agar tidak berubah jadi bot
            penerbit = q.current_info.get('requester', interaction.user)
            q.update_task = bot.loop.create_task(
                update_player_interface(q.last_dashboard, q.total_duration, q.current_info['title'], q.current_info['webpage_url'], q.current_info['thumbnail'], penerbit, interaction.guild_id)
            )
        
        await sync_dashboard_buttons(q.last_dashboard, interaction.guild_id)
        await interaction.response.send_message(embed=buat_embed_status("▶️", "Musik dilanjutkan.", 0x2ecc71), delete_after=10)
    else:
        await interaction.response.send_message("❌ Musik tidak sedang dijeda.", ephemeral=True)

# ⏭️ 7.4.  :	/skip - System (PUBLIC & AUTO-CLEAN VERSION)
# ------------------------------------------------------------------------------
@bot.tree.command(name="skip", description="Lewati lagu yang sedang berjalan")
async def skip_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    # Bersihkan notif antrean/skip sebelumnya
    if hasattr(q, 'last_msg') and q.last_msg:
        try: await q.last_msg.delete()
        except: pass
        q.last_msg = None

    if vc and (vc.is_playing() or vc.is_paused()):
        lagu_dilewati = q.current_info.get('title', 'Lagu saat ini') if q.current_info else "Unknown"
        next_info = f"Memutar lagu selanjutnya: **{q.queue[0]['title']}**" if q.queue else "Antrean habis, bot akan standby. ✨"

        # Matikan loop sementara agar tidak mengulang lagu yang sama
        original_loop = q.loop
        q.loop = False 
        q.is_seeking = False

        if q.update_task: q.update_task.cancel()

        vc.stop() # Memicu after_playing -> next_logic()
        q.loop = original_loop

        embed = buat_embed_skip(interaction.user, lagu_dilewati, next_info)
        q.last_msg = await interaction.followup.send(embed=embed)
        
        if not q.queue:
            await asyncio.sleep(15)
            try:
                if q.last_msg: await q.last_msg.delete()
            except: pass
    else:
        await interaction.followup.send("❌ **Gagal:** Tidak ada lagu yang sedang diputar.", ephemeral=True)

# 🔂 7.5.  :	/loop - System
# ------------------------------------------------------------------------------
@bot.tree.command(name="loop", description="Aktifkan atau matikan pengulangan lagu saat ini")
async def loop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    q.loop = not q.loop
    judul = q.current_info.get('title', 'Lagu saat ini') if q.current_info else "Musik"
    emb = buat_embed_loop(interaction.user, q.loop, judul)
    await interaction.response.send_message(embed=emb, delete_after=15)

# 🔊 7.6.  :	/volume - System
# ------------------------------------------------------------------------------
@bot.tree.command(name="volume", description="Atur Volume Audio (0-100%)")
@app_commands.describe(persen="Masukkan angka antara 0 sampai 100")
async def volume(interaction: discord.Interaction, persen: int):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if 0 <= persen <= 100:
        q.volume = persen / 100
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass
            
        if q.last_dashboard:
            try:
                emb_dash = q.last_dashboard.embeds[0]
                # Update field volume (biasanya di index 1)
                emb_dash.set_field_at(1, name="🔊 Volume", value=f"`{persen}%`", inline=True)
                await q.last_dashboard.edit(embed=emb_dash)
            except: pass

        await interaction.response.send_message(embed=buat_embed_volume(persen, interaction.user), delete_after=15)
    else:
        await interaction.response.send_message("❌ **Gagal:** Gunakan angka **0 - 100**.", ephemeral=True)

# 📜 7.7.  :	/queue - System
# ------------------------------------------------------------------------------
@bot.tree.command(name="queue", description="Lihat daftar lagu yang akan diputar")
async def queue_cmd(interaction: discord.Interaction):
    await logic_tampilkan_antrean(interaction, interaction.guild_id)


# ⏹️ 7.8.  :	/stop - System 
# ------------------------------------------------------------------------------
@bot.tree.command(name="stop", description="Mematikan musik dan keluar")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client

    if q.update_task:
        q.update_task.cancel()
        q.update_task = None

    if vc:
        jumlah_antrean = len(q.queue)
        q.queue.clear()
        q.current_info = None
        
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None

        await vc.disconnect()
        await interaction.response.send_message(embed=buat_embed_stop(interaction.user, jumlah_antrean), delete_after=20)
    else:
        await interaction.response.send_message("❌ **Gagal:** Bot tidak sedang berada di Voice Channel.", ephemeral=True)



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
#
# 💡 7.9.4. : /help - System (REFINED PREMIUM UI)
# ------------------------------------------------------------------------------
@bot.tree.command(name="help", description="Panduan lengkap penggunaan bot & info pengembang")
async def help_cmd(interaction: discord.Interaction):
    # Banner Profile (Optional - Menggunakan avatar bot)
    bot_thumb = bot.user.display_avatar.url
    
    # --- EMBED UTAMA: USER GUIDE ---
    emb_guide = discord.Embed(
        title="💿 ANGELSS MUSIC • COMMAND CENTER", 
        color=0x3498db,
        description=(
            "Selamat datang di **Angelss Project V17**. Gunakan perintah di bawah ini "
            "untuk mengontrol sesi musik kamu.\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
    )
    emb_guide.set_thumbnail(url=bot_thumb)

    # Group 1: Musik Utama (Dibuat Bold & Monospace)
    emb_guide.add_field(
        name="🎵 AUDIO CONTROL",
        value=(
            "```\n"
            "/play   • Putar lagu/link\n"
            "/pause  • Jeda musik\n"
            "/resume • Lanjut putar\n"
            "/skip   • Lewati lagu\n"
            "/stop   • Matikan musik\n"
            "```"
        ), 
        inline=False
    )

    # Group 2: Antrean & Volume
    emb_guide.add_field(
        name="🎚️ MIXER & QUEUE",
        value=(
            "```\n"
            "/queue  • Lihat daftar antrean\n"
            "/volume • Atur suara (0-100)\n"
            "/loop   • Ulangi lagu ini\n"
            "```"
        ), 
        inline=True
    )

    # Group 3: Voice & System
    emb_guide.add_field(
        name="📡 VOICE & SYSTEM",
        value=(
            "```\n"
            "/voice  • Masuk/Keluar VC\n"
            "/debug  • Cek kesehatan bot\n"
            "/help   • Bantuan ini\n"
            "```"
        ), 
        inline=True
    )

    # Tips & Info Interactive
    emb_guide.add_field(
        name="✨ SMART DASHBOARD",
        value=(
            "> Bot ini menggunakan dashboard interaktif. Gunakan tombol di bawah "
            "pesan *Now Playing* untuk kontrol instan tanpa mengetik!"
        ),
        inline=False
    )

    # --- EMBED KEDUA: DEVELOPER PROFILE ---
    emb_dev = discord.Embed(
        title="👨‍💻 SYSTEM DEVELOPER", 
        color=0x9b59b6,
        description=(
            "**Developed by ikiii (IT Engineering)**\n"
            "Sistem ini berjalan di atas **Python 3.10** dengan **FFmpeg 5.0 Stable**.\n"
            "Seluruh engine dioptimalkan untuk latensi rendah."
        )
    )
    
    # Banner bawah untuk estetika
    emb_dev.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif")
    
    emb_dev.set_footer(
        text=f"Angelss Project V17 • Requested by {interaction.user.name}", 
        icon_url=interaction.user.display_avatar.url
    )
    
    # Kirim kedua embed sekaligus
    await interaction.response.send_message(embeds=[emb_guide, emb_dev])






#
#
# 🛠️ 7.9.5.  :	/debug - System (PUBLIC & AUTO-CLEAN)
# ------------------------------------------------------------------------------
#
@bot.tree.command(name="debug", description="Cek kesehatan sistem audio dan environment hosting")
async def debug_system(interaction: discord.Interaction):
    # 1. Jadikan PUBLIC (Semua orang bisa lihat kondisi bot)
    await interaction.response.defer(ephemeral=False)
    
    q = get_queue(interaction.guild_id)
    
    # 2. Logika Pembersihan: Hapus pesan debug/notifikasi sebelumnya jika ada
    if hasattr(q, 'last_msg') and q.last_msg:
        try: await q.last_msg.delete()
        except: pass

    import subprocess
    import sys
    import platform
    import os 

    # --- [ PROSES CEK SISTEM ] ---
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

    # 4. Cek Environment
    local_folder = "Ada (Cek File Manager)" if os.path.exists(".local") else "Tidak Ada (Bersih)"
    python_38_check = "⚠️ Terdeteksi" if os.path.exists(".local/lib/python3.8") else "✅ Aman"

    # --- [ RAKIT EMBED - Visual Tetap Ori ] ---
    embed = discord.Embed(title="🛠️ System Diagnostic Tool", color=0x3498db)
    embed.add_field(name="🛰️ FFmpeg Status", value=ffmpeg_status, inline=False)
    embed.add_field(name="🐍 Python Version", value=f"`{py_ver}`", inline=True)
    embed.add_field(name="📦 yt-dlp Version", value=f"`{ytdl_status}`", inline=True)
    embed.add_field(name="📁 Folder .local", value=f"`{local_folder}`", inline=True)
    embed.add_field(name="📂 Konflik Python 3.8", value=f"`{python_38_check}`", inline=True)
    embed.add_field(name="🖥️ OS Info", value=f"`{os_info}`", inline=False)

    if "❌" in ffmpeg_status:
        embed.description = "⚠️ **PERINGATAN:** FFmpeg tidak ditemukan. Gunakan Docker Image yang mendukung FFmpeg!"
        embed.color = 0xe74c3c
    else:
        embed.description = "✨ Semua sistem terlihat normal kii. Jika bot masih skip, cek link YouTube-nya."

    # 3. Kirim dan Simpan ke last_msg agar bisa dihapus otomatis nanti
    q.last_msg = await interaction.followup.send(embed=embed)
    
    # Tambahan: Pesan debug publik biasanya dihapus otomatis setelah 30 detik agar chat tidak kotor
    await asyncio.sleep(30)
    try:
        if q.last_msg: await q.last_msg.delete()
    except: pass








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
