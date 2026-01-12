# ==============================================================================
# 💿 PROJECT   : Angelss Music Bot (V17 FINAL FIX)
# 👨‍💻 DEVELOPER : ikiii (IT Engineering)
# 🚀 STATUS    : Production Ready
# 🛡️ LICENSE   : Personal Project - Angelss Project
# ==============================================================================
"""


DESCRIPTION KUH	:
		
			Bot musik profesional dengan sistem Interactive Dashboard, High-Fidelity Audio,
			dan manajemen antrean cerdas. Dioptimalkan untuk Python 3.10.


"""




# --- [ 0.1. SYSTEM INITIALIZATION ] ---
#
#
# import static_ffmpeg          # <--- HAPUS
# static_ffmpeg.add_paths()     # <--- HAPUS







# --- [ 0.2. CORE DEPENDENCIES ] ---
#
#
import os
import asyncio
import datetime
import logging
import json
from collections import deque
from dotenv import load_dotenv  # <--- 1. Tambahkan import ini

# Memuat file .env ke dalam sistem environment
load_dotenv() # <--- 2. Jalankan fungsi ini di sini







# --- [ 0.3. DISCORD API LIBRARIES ] ---
#
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import tasks





# --- [ 0.4. MULTIMEDIA LIBRARIES ] ---
#
import yt_dlp




#.--- Import Untuk Progress Bar 
#
import math
import time




# --- [ 0.5. LOGGING SYSTEM CONFIGURATION ] ---
#
# ---  :   Menggunakan format log industri untuk memudahkan tracking error di Octavia
#
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('AngelssProject')







# --- [ 0.6. GLOBAL CONSTANTS & CONFIGURATION ] ---
#
# ---  :    Menarik identitas rahasia dari Environment Variables
#
TOKEN = os.getenv('DISCORD_TOKEN') # Menggunakan os.getenv lebih aman daripada os.environ.get
COOKIES_FILE = 'youtube_cookies.txt'







# --- [ 0.7. BOOTSTRAP VALIDATION ] ---
#
#
def bootstrap():
    """Validasi awal sistem sebelum bot melakukan login."""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🚀 ANGELSS PROJECT V17 | STARTING SERVICE...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if not TOKEN:
        logger.critical("Fetal Error: DISCORD_TOKEN is missing from environment.")
        exit(1)
        
    if os.path.exists(COOKIES_FILE):
        logger.info(f"Identity: YouTube Cookies loaded from '{COOKIES_FILE}'.")
    else:
        logger.warning(f"Identity: Running without cookies. High-risk of 403 Forbidden.")







# --- [ 0.8. Jalankan validasi ] ---
#
#
bootstrap()






# --- [ 0.9. QUEUE & MEMORY STORAGE ] ---
#
# ---  :    Variabel global untuk menampung seluruh sesi server
#
#
queues = {} 
























# ==============================================================================
# ⚡ NEXT: PROJECT BOT MUSIC - INITIALIZING ENGINE
# ==============================================================================










# --- [ 1. SETTINGS - FORMAT CONVERTER (OPTIMIZED FOR HOSTING) ] ---
#
# --- [ AUDITED CONFIGURATION ] ---

YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'youtube_cookies.txt', 
    # [FIX 1]: Menghapus 'audioformat' dan 'extractaudio'. 
    # Kita melakukan direct streaming, bukan konversi file lokal. 
    # Memaksa format di sini menambah latensi decoding.
    
    # [FIX 2]: High Network Optimization
    # Buffer diperbesar ke 10MB untuk menampung lonjakan data tanpa putus
    'http_chunk_size': 10485760, 
}


FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-reconnect_at_eof 1 '
        '-nostdin'
    ),
    'options': (
        '-vn '
        '-b:a 192k '             # High-Quality sesuai dashboard
        '-ar 48000 '             # Sample rate Studio
        '-ac 2 '
        '-loglevel warning '
        '-af "aresample=async=1:min_hard_comp=0.100000:first_pts=0" ' # Fix Durasi 00:00
    ),
}















# --- [ 3. INISIALISASI YT-DLP ] ---
#
#
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)











# --- [ 4 - 5 :	GABUNGAN 4 & 5 ] ---
#
#
# ==============================================================================
# 🏗️ SECTION C: BOT INFRASTRUCTURE & LIFECYCLE MANAGEMENT
# ==============================================================================
# Definisi Class Utama (ModernBot) dan penanganan Lifecycle Event (on_ready).
# Menggabungkan setup koneksi dan sinkronisasi pengumuman sistem.
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
        print(f"✅ SYSTEM ONLINE: {self.user.name}")
        print(f"🐍 PYTHON VER  : 3.10.x")
        print(f"📡 LATENCY     : {round(self.latency * 1000)}ms")
        print(f"📅 STARTED AT  : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# Inisialisasi Instance Bot
bot = ModernBot()
















# --- [ 5. NOTIFIKASI - BOT - ONLINE UPDATE ] ---  PINDAH 
#
#
# @bot.event












# --- [ 6. QUEUE SYSTEM (SINKRON DENGAN GLOBAL STORAGE ] ---
#
#
class MusicQueue:
    """Objek untuk menyimpan data musik spesifik per server (Guild)."""
    def __init__(self):
        # deque digunakan untuk efisiensi performa saat popleft (ganti lagu)
        self.queue = deque()
        self.current_info = None
        self.loop = False
        self.volume = 0.5  # Default volume standar 50%
        self.last_dashboard = None
        self.last_search_msg = None
        self.last_queue_msg = None 
        self.text_channel_id = None
      
        # --- TAMBAHKAN 3 BARIS INI ---
        self.update_task = None    # Untuk menyimpan proses update bar
        self.start_time = 0        # Untuk mencatat detik mulai lagu
        self.total_duration = 0    # Untuk mencatat total durasi lagu


    def clear_all(self):
        """Reset total data sesi (digunakan saat command /stop)."""
        self.queue.clear()
        self.current_info = None
        self.last_dashboard = None
        self.last_search_msg = None
        self.last_queue_msg = None

def get_queue(guild_id):
    """
    Mengambil data antrean server. 
    Jika belum ada, akan membuat instance MusicQueue baru.
    """
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]

def delete_queue(guild_id):
    """
    Menghapus data dari RAM. 
    Wajib dipanggil saat bot disconnect agar hemat RAM (2GB RAM Limit).
    """
    if guild_id in queues:
        del queues[guild_id]












# --- [ 7. AUTO-DISCONNECT (REFINED LOGIC) ] ---
#
#
@bot.event
async def on_voice_state_update(member, before, after):
    # Logika: Jika ada user (bukan bot) keluar dari VC
    if not member.bot and before.channel is not None:
        vc = member.guild.voice_client
        
        # Cek apakah bot berada di channel yang ditinggalkan dan sekarang hanya sendirian
        if vc and vc.channel.id == before.channel.id and len(vc.channel.members) == 1:
            
            q = get_queue(member.guild.id)
            msg_chan = None

            # PRIORITAS CHANNEL: Mencari tempat terbaik untuk kirim notifikasi
            if q.last_dashboard:
                msg_chan = q.last_dashboard.channel
            elif q.text_channel_id:
                msg_chan = bot.get_channel(q.text_channel_id)
            
            # Jika msg_chan ditemukan, kirim peringatan
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
                        # Ada manusia kembali! Batalkan keluar
                        try:
                            if peringatan: await peringatan.delete()
                        except: pass
                        await msg_chan.send("✨ **Informasi:** Seseorang telah kembali! Bot tetap standby di sini.", delete_after=10)
                    else:
                        # Masih kosong (hanya bot sendiri), bersihkan data dan keluar
                        q.queue.clear()
                        # Hapus dashboard terakhir agar tidak membingungkan
                        if q.last_dashboard:
                            try: await q.last_dashboard.delete()
                            except: pass
                        q.last_dashboard = None
                        
                        if vc_sekarang.is_connected():
                            await vc_sekarang.disconnect()
                            await msg_chan.send("👋 **Informasi:** Bot telah keluar karena Voice Channel kosong terlalu lama.", delete_after=10)












# --- [ 8. SYSTEM SEARCH ENGINE PILIHAN ] ---
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
            # Cek Permission
            if interaction.user != self.user:
                return await interaction.response.send_message(
                    f"⚠️ **Ups!** Hanya {self.user.mention} yang bisa memilih lagu dari hasil ini.", 
                    ephemeral=True
                )
            
            await interaction.response.defer()
            
            # Memproses ke play_music
            await play_music(interaction, select.values[0])
            
            # Ubah tampilan menjadi 'Sukses' lalu hapus menunya agar chat bersih
            status_embed = discord.Embed(
                title="✅ Berhasil!",
                description=f"🎶 Lagu pilihan **{interaction.user.display_name}** telah ditambahkan ke antrean.",
                color=0x2ecc71
            )
            # Menghapus View (Tombol & Select) agar tidak bisa diklik lagi
            await interaction.edit_original_response(embed=status_embed, view=None)
            
            # Tunggu sebentar lalu hapus pesan pencariannya (Opsional agar chat rapi)
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












# --- [ 9. UI CLASS:	 DASHBOARD & VOLUME ] ---
#
#
class VolumeControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    def create_embed(self):
        q = get_queue(self.guild_id)
        vol_percent = int(q.volume * 100)
        embed = discord.Embed(title="🎚️ Pengaturan Audio", color=0x3498db)
        
        # Visual Bar (Lebih akurat)
        bar_length = 10
        filled = round(q.volume * 10)
        bar = "▰" * filled + "▱" * (bar_length - filled)
        
        embed.description = f"Volume Saat Ini: **{vol_percent}%**\n`{bar}`"
        embed.set_footer(text="Gunakan tombol di bawah untuk menyesuaikan suara.")
        return embed

    @discord.ui.button(label="-10%", style=discord.ButtonStyle.danger, emoji="🔉")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        
        q.volume = max(0.0, q.volume - 0.1)
        
        vc = interaction.guild.voice_client
        # PENGAMAN: Cek apakah source mendukung pengaturan volume
        if vc and vc.source:
            try:
                vc.source.volume = q.volume
            except AttributeError:
                # Jika source bukan PCMVolumeTransformer, kita tidak bisa ubah volumenya secara langsung
                pass
                
        await interaction.edit_original_response(embed=self.create_embed())

    @discord.ui.button(label="+10%", style=discord.ButtonStyle.success, emoji="🔊")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        
        q.volume = min(1.0, q.volume + 0.1) 
        
        vc = interaction.guild.voice_client
        if vc and vc.source:
            try:
                vc.source.volume = q.volume
            except AttributeError:
                pass

        await interaction.edit_original_response(embed=self.create_embed())












# --- [ 10. FUNCTION:	 EMBED - SKIP ] ---
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












# --- [ 11. UI CLASS: DASHBOARD & AUDIO - PLAYER ] ---
#
#
class MusicDashboard(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    async def update_button(self, message):
        """Fungsi manual untuk menyamakan tampilan tombol (SINKRONISASI)"""
        vc = message.guild.voice_client
        if not self.children: return
        button = self.children[0] 
        if vc and vc.is_paused():
            button.emoji = "▶️"; button.label = "Lanjut"; button.style = discord.ButtonStyle.success
        else:
            button.emoji = "⏸️"; button.label = "Jeda"; button.style = discord.ButtonStyle.secondary
        await message.edit(view=self)

    @discord.ui.button(label="Jeda", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pp(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        if not vc: return await interaction.response.send_message("❌ Bot tidak ada di VC.", ephemeral=True)
        
        if vc.is_playing():
            # LOGIKA PAUSE
            vc.pause()
            if q.update_task: q.update_task.cancel()
            button.emoji = "▶️"; button.label = "Lanjut"; button.style = discord.ButtonStyle.success 
        else:
            # LOGIKA RESUME (SINKRONISASI WAKTU & TASK)
            current_pos = time.time() - q.start_time
            q.start_time = time.time() - current_pos
            vc.resume()
            
            # Memulai kembali looping bar dengan guild_id yang benar
            q.update_task = bot.loop.create_task(
                update_player_interface(
                    interaction, 
                    q.last_dashboard, 
                    q.total_duration, 
                    q.current_info['title'], 
                    q.current_info['webpage_url'], 
                    q.current_info['thumbnail'], 
                    interaction.user,
                    self.guild_id # Fix: Sinkron ID
                )
            )
            button.emoji = "⏸️"; button.label = "Jeda"; button.style = discord.ButtonStyle.secondary
        
        await interaction.response.edit_message(view=self)

    # --- TOMBOL 2: VOLUME ---
    @discord.ui.button(label="Volume", emoji="🔊", style=discord.ButtonStyle.gray)
    async def vol(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = VolumeControlView(self.guild_id)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)
    
    # --- TOMBOL 3: ANTREAN ---
    @discord.ui.button(label="Antrean", emoji="📜", style=discord.ButtonStyle.gray)
    async def list_q_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.tampilkan_antrean(interaction)

    async def tampilkan_antrean(self, interaction: discord.Interaction):
        q = get_queue(self.guild_id)
        if q.last_queue_msg:
            try: await q.last_queue_msg.delete()
            except: pass

        if not q.queue:
            msg_empty = "📪 Antrean saat ini kosong."
            if interaction.response.is_done():
                return await interaction.followup.send(msg_empty, ephemeral=True)
            return await interaction.response.send_message(msg_empty, ephemeral=True)
        
        emb = discord.Embed(title="📜 Antrean Musik (Publik)", color=0x2b2d31)
        description = "Pilih lagu di bawah untuk langsung diputar (Lompat Antrean)!\n\n"
        
        options = []
        for i, item in enumerate(list(q.queue)[:10]):
            description += f"**{i+1}.** {item['title'][:50]}...\n"
            options.append(discord.SelectOption(
                label=f"{i+1}. {item['title'][:25]}", 
                value=str(i),
                emoji="🎵"
            ))
        
        emb.description = description
        select = discord.ui.Select(placeholder="🚀 Pilih lagu untuk dilompati...", options=options)

        async def select_callback(inter: discord.Interaction):
            for option in select.options:
                if option.value == select.values[0]:
                    option.emoji = "✅"
            await inter.response.edit_message(view=view_select)
            
            idx = int(select.values[0])
            chosen = q.queue[idx]
            judul_lama = "Lagu sebelumnya"
            if q.last_dashboard and q.last_dashboard.embeds:
                try: 
                    judul_lama = q.last_dashboard.embeds[0].description.split('[')[1].split(']')[0]
                except: pass

            del q.queue[idx]
            q.queue.appendleft(chosen)
            
            try:
                embed_rapi = buat_embed_skip(inter.user, judul_lama, f"⏭️ **Selanjutnya:** {chosen['title']}")
                skip_msg = await inter.followup.send(embed=embed_rapi)
            except:
                skip_msg = await inter.followup.send(f"⏭️ Melompati ke: **{chosen['title']}**")

            if inter.guild.voice_client: inter.guild.voice_client.stop()
            await asyncio.sleep(15); 
            try: await skip_msg.delete()
            except: pass

        select.callback = select_callback
        view_select = discord.ui.View(timeout=60)
        view_select.add_item(select)
        
        if interaction.response.is_done():
            q.last_queue_msg = await interaction.followup.send(embed=emb, view=view_select)
        else:
            await interaction.response.send_message(embed=emb, view=view_select)
            q.last_queue_msg = await interaction.original_response()

    # --- TOMBOL 4: SKIP ---
    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        if q.update_task: q.update_task.cancel()
        
        if not vc or not (vc.is_playing() or vc.is_paused()):
            return await interaction.followup.send("❌ **Informasi:** Tidak ada lagu untuk di-skip.", ephemeral=True)

        current_title = "Tidak diketahui"
        if q.last_dashboard and q.last_dashboard.embeds:
            try:
                current_title = q.last_dashboard.embeds[0].description.split('[')[1].split(']')[0]
            except: pass

        next_info = "Antrean habis, bot akan standby. ✨"
        if q.queue: next_info = f"⏭️ **Selanjutnya:** {q.queue[0]['title']}"

        embed = discord.Embed(
            title="⏭️ MUSIC SKIP SYSTEM",
            description=(
                f"✨ **{interaction.user.mention}** telah melewati lagu!\n\n"
                f"🗑️ **Dilewati:** {current_title}\n"
                f"📥 **Status Antrean:** {next_info}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0xe74c3c
        )
        embed.set_footer(text="Gunakan /play untuk menambah lagu", icon_url=interaction.user.display_avatar.url)
        vc.stop()
        await interaction.followup.send(embed=embed)
        await asyncio.sleep(15)
        try:
            msg = await interaction.original_response()
            await msg.delete()
        except: pass

    # --- TOMBOL 5: STOP ---
    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        if q.update_task: q.update_task.cancel()
        
        jumlah_antrean = len(q.queue) 
        q.queue.clear()
        if vc: await vc.disconnect()
            
        embed = discord.Embed(
            title="🛑 SYSTEM TERMINATED",
            description=(
                f"✨ **{interaction.user.mention}** telah mematikan pemutar musik.\n\n"
                f"🧹 **Pembersihan:** `{jumlah_antrean}` lagu telah dihapus dari antrean.\n"
                f"📡 **Status:** Bot telah keluar dari Voice Channel.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x2f3136
        )
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        await interaction.response.send_message(embed=embed, delete_after=20)











# --- [ 12. CORE LOGIC:	 SYSTEM - DURASI AUTO 00:00 ] ---
#

# ==============================================================================
# 💿 SECTION: CORE MUSIC ENGINE (START, NEXT, & PLAY LOGIC)
# ==============================================================================

# --- [ 12.1. NEXT LOGIC ] ---
async def next_logic(interaction):
    """Logika otomatis untuk memutar lagu berikutnya dari antrean."""
    q = get_queue(interaction.guild_id)
    
    # Jeda 2 detik agar sesi FFmpeg sebelumnya benar-benar tertutup bersih
    await asyncio.sleep(2)
    
    if q.queue:
        next_song = q.queue.popleft()
        # Memanggil start_stream untuk lagu berikutnya
        await start_stream(interaction, next_song['url'])
    else:
        # Jika antrean habis, bersihkan dashboard aktif
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
            
        emb_finish = discord.Embed(
            title="✨ Antrean Selesai",
            description="Semua lagu telah diputar. Bot standby dalam mode hemat daya. 💤",
            color=0x34495e
        )
        # Kirim pesan ke channel terakhir yang aktif
        channel = bot.get_channel(q.text_channel_id) or interaction.channel
        if channel:
            await channel.send(embed=emb_finish, delete_after=15)






















# --- [ 12.2. START STREAM LOGIC (PATCHED) ] ---
# Simpan task update di global/class variable agar bisa di-cancel saat stop/skip
current_update_task = None 
start_time_tracker = 0

async def start_stream(interaction, url):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if not vc: return

    # 1. Matikan update bar sebelumnya jika masih jalan
    if q.update_task and not q.update_task.done():
        q.update_task.cancel()

    try:
        # 2. Ambil data lagu (Gunakan YTDL)
        data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data: data = data['entries'][0]
        
        stream_url = data.get('url')
        
        # 3. Setup Player
        audio_source = discord.FFmpegPCMAudio(stream_url, **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)

        def after_playing(error):
            if q.update_task: q.update_task.cancel() # Matikan update bar saat lagu mati
            if error: logger.error(f"⚠️ Player Error: {error}")
            bot.loop.create_task(next_logic(interaction))

        if vc.is_playing(): vc.stop()
        vc.play(source, after=after_playing)
        
        # 4. Simpan data untuk Timer Dashboard
        q.start_time = time.time()
        q.total_duration = data.get('duration', 0)
        q.current_info = data # Simpan info lengkap
        
        thumbnail = data.get('thumbnail')
        title = data.get('title')
        web_url = data.get('webpage_url', url)
        requester = interaction.user

        # 5. Hapus dashboard lama agar chat bersih
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass

        # (Lanjutan Bagian 5 ke bawah pada fungsi start_stream kamu)

        # 5. Hapus dashboard lama agar chat bersih
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass

        # 6. Kirim Dashboard Baru (Awal)
        # --- TAMBAHKAN interaction.guild_id DI AKHIR ---
        emb = generate_embed(0, q.total_duration, title, web_url, thumbnail, requester, interaction.guild_id)
        q.last_dashboard = await interaction.channel.send(embed=emb, view=MusicDashboard(interaction.guild_id))

        # 7. JALANKAN MESIN UPDATE BAR
        # --- TAMBAHKAN interaction.guild_id DI AKHIR ---
        q.update_task = bot.loop.create_task(
            update_player_interface(interaction, q.last_dashboard, q.total_duration, title, web_url, thumbnail, requester, interaction.guild_id)
        )

    except Exception as e:
        logger.error(f"Gagal Start Stream: {e}")
        await interaction.channel.send(f"⚠️ Terjadi kesalahan: {e}", delete_after=5)




























# ==============================================================================
# 🛠️ SECTION: HELPER FUNCTIONS & LOGIC
# ==============================================================================
# (PENTING: Fungsi ini ditaruh DI ATAS command /play agar terbaca sistem dulu)


async def play_music(interaction, url):
    """Fungsi kontrol untuk memutuskan apakah lagu diputar langsung atau antre."""
    q = get_queue(interaction.guild_id)
    q.text_channel_id = interaction.channel.id
    
    # 1. Koneksi otomatis ke Voice Channel
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            try:
                await interaction.user.voice.channel.connect()
            except Exception as e:
                return await interaction.followup.send(f"❌ Gagal koneksi: {e}", ephemeral=True)
        else:
            return await interaction.followup.send("❌ **Gagal:** Kamu harus masuk ke Voice Channel dulu!", ephemeral=True)
    
    vc = interaction.guild.voice_client
    
    # 2. Cek apakah bot sedang memutar musik atau dijeda
    if vc.is_playing() or vc.is_paused():
        try:
            # Ambil info lagu untuk ditampilkan di pesan antrean
            data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            if 'entries' in data: data = data['entries'][0]

            q.queue.append({'title': data['title'], 'url': url})
            
            # --- TETAP PAKAI EMBED ASLI KAMU ---
            emb_q = discord.Embed(
                title="📥 Antrean Ditambahkan",
                description=f"✨ **[{data['title']}]({url})**",
                color=0x3498db
            )
            emb_q.set_footer(text=f"Posisi Antrean: {len(q.queue)}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=emb_q, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ Gagal menambahkan ke antrean: {str(e)[:50]}", ephemeral=True)
    
    else:
        # 3. Jika bot sedang menganggur, bersihkan player lama dulu (Anti-Stuck)
        if vc.is_playing(): 
            vc.stop()
            
        # Langsung jalankan mesin pemutar (Pastikan start_stream sudah pakai FFMPEG_OPTIONS hasil audit)
        await start_stream(interaction, url)



























# ==============================================================================
# 🎵 SECTION: MUSIC COMMANDS (STANDARD)
# ==============================================================================

# --- [ COMMAND /PLAY ] ---
@bot.tree.command(name="play", description="Putar musik menggunakan judul atau link YouTube")
async def play(interaction: discord.Interaction, cari: str):
    # 1. Defer wajib untuk menghindari timeout 3 detik
    await interaction.response.defer(ephemeral=True)
    
    q = get_queue(interaction.guild_id)

    # Bersihkan pesan pencarian lama jika ada
    if q.last_search_msg:
        try: await q.last_search_msg.delete()
        except: pass

    # A. LOGIKA JIKA INPUT ADALAH LINK
    if "http" in cari: 
        await interaction.followup.send("🔗 **Menganalisa tautan...**", ephemeral=True)
        # Langsung lempar ke play_music (Sekarang aman karena play_music ada di atas)
        await play_music(interaction, cari)
        # Berikan konfirmasi akhir pada original response
        await interaction.edit_original_response(content=f"✅ **Tautan diterima:** Memproses permintaan.")
    
    # B. LOGIKA JIKA INPUT ADALAH JUDUL (PENCARIAN)
    else:
        await interaction.followup.send(f"🔍 **Mencari:** `{cari}`...", ephemeral=True)
        try:
            search_opts = {'extract_flat': True, 'quiet': True}
            # Menjalankan pencarian di background agar bot tidak freeze
            data = await bot.loop.run_in_executor(
                None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(f"ytsearch5:{cari}", download=False)
            )
            
            if not data or 'entries' not in data or len(data['entries']) == 0:
                return await interaction.edit_original_response(content="❌ **Gagal:** Lagu tidak ditemukan.")
            
            # Tampilkan pilihan lagu (SearchControlView)
            view = SearchControlView(data['entries'], interaction.user)
            q.last_search_msg = await interaction.edit_original_response(
                content=None, 
                embed=view.create_embed(), 
                view=view
            )

        except Exception as e:
            logger.error(f"Error search: {e}")
            await interaction.edit_original_response(content="⚠️ Terjadi kesalahan saat sistem mencari lagu.")


# --- [ COMMAND /STOP ] ---
@bot.tree.command(name="stop", description="Mematikan musik dan mengeluarkan bot dari voice channel")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client

    # --- TAMBAHKAN INI AGAR BAR BERHENTI ---
    if q.update_task:
        q.update_task.cancel()
    # ---------------------------------------

    # Ambil data jumlah antrean sebelum dihapus untuk laporan
    jumlah_antrean = len(q.queue)
    
    if vc:
        # 1. LOGIKA PEMBERSIHAN MEMORY (SANGAT PENTING)
        q.queue.clear()
        q.current_info = None
        
        # 2. BERSIHKAN DASHBOARD (Agar tidak ada tombol 'hantu' di chat)
        if q.last_dashboard:
            try:
                await q.last_dashboard.delete()
            except:
                pass
            q.last_dashboard = None

        # 3. PUTUS KONEKSI
        await vc.disconnect()
        
        # 4. BUAT EMBED YANG ESTETIK
        embed = discord.Embed(
            title="🛑 SYSTEM TERMINATED",
            description=(
                f"✨ **{interaction.user.mention}** telah menghentikan sesi musik.\n\n"
                f"🧹 **Antrean:** `{jumlah_antrean}` lagu telah dibersihkan.\n"
                f"📡 **Status:** Bot telah meninggalkan Voice Channel.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x2f3136 # Warna Dark Grey yang mewah
        )
        
        # Gunakan logo bot sebagai thumbnail
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        
        # Footer dengan pengaman avatar
        bot_avatar = bot.user.display_avatar.url if bot.user else None
        embed.set_footer(text="Sesi berakhir • Angelss Project V17", icon_url=bot_avatar)

        # Kirim respon publik agar semua tahu siapa yang menonaktifkan
        await interaction.response.send_message(embed=embed, delete_after=20)
        
    else:
        # Respon jika bot memang tidak sedang aktif (ephemeral=True agar tidak nyampah)
        await interaction.response.send_message(
            "❌ **Gagal:** Bot tidak sedang berada di Voice Channel.", 
            ephemeral=True
        )


# --- [ COMMAND /PAUSE ] ---
@bot.tree.command(name="pause", description="Jeda musik yang sedang diputar")
async def pause(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if vc and vc.is_playing():
        vc.pause()
        if q.update_task: q.update_task.cancel() # STOP bar di sini
        embed = discord.Embed(description="⏸️ **Musik telah dijeda.**", color=0xf1c40f)
        await interaction.response.send_message(embed=embed, delete_after=10)
        
        # SINKRONISASI TOMBOL DASHBOARD
        if q.last_dashboard:
            view = MusicDashboard(interaction.guild_id)
            await view.update_button(q.last_dashboard)
    else:
        await interaction.response.send_message("❌ **Gagal:** Tidak ada musik yang sedang berbunyi.", ephemeral=True)


# --- [ COMMAND /RESUME ] ---
@bot.tree.command(name="resume", description="Lanjutkan musik yang sedang dijeda")
async def resume(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    # Validasi: Apakah bot memang sedang dalam kondisi Pause?
    if vc and vc.is_paused():
        # HITUNG ULANG start_time agar bar sinkron lagi
            # (Waktu mulai baru = Waktu sekarang - posisi detik terakhir)
        current_pos = time.time() - q.start_time
        q.start_time = time.time() - current_pos

        vc.resume()
        
        # Jalankan ulang mesin bar
        q.update_task = bot.loop.create_task(
            update_player_interface(interaction, q.last_dashboard, q.total_duration, q.current_info['title'], q.current_info['webpage_url'], q.current_info['thumbnail'], interaction.user)
        )
        
        embed = discord.Embed(description="▶️ **Musik dilanjutkan kembali.**", color=0x2ecc71)
        await interaction.response.send_message(embed=embed, delete_after=10)
        
        # SINKRONISASI DASHBOARD
        if q.last_dashboard:
            view = MusicDashboard(interaction.guild_id)
            await view.update_button(q.last_dashboard)
    else:
        # Jika bot tidak pause, beri tahu user alasannya
        status = "sedang berjalan" if vc and vc.is_playing() else "tidak ada lagu"
        await interaction.response.send_message(f"❌ **Gagal:** Musik {status}.", ephemeral=True)





# --- [ COMMAND /SKIP ] ---
@bot.tree.command(name="skip", description="Lewati lagu yang sedang berjalan")
async def skip_cmd(interaction: discord.Interaction):
    # 1. Defer agar tidak timeout
    await interaction.response.defer(ephemeral=False)
    
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
            
        
    # --- TAMBAHKAN INI AGAR BAR BERHENTI ---
    if q.update_task:
        q.update_task.cancel()
    # ---------------------------------------

    if vc and (vc.is_playing() or vc.is_paused()):
        # 2. Logika Pengambilan Judul 
        lagu_dilewati = "Lagu saat ini"
        if q.current_info:
            lagu_dilewati = q.current_info.get('title', 'Tidak diketahui')
        elif q.last_dashboard and q.last_dashboard.embeds:
            try:
                full_desc = q.last_dashboard.embeds[0].description
                if "[" in full_desc and "]" in full_desc:
                    lagu_dilewati = full_desc.split('[')[1].split(']')[0]
            except: pass

        # 3. Info Antrean Berikutnya
        if q.queue:
            next_info = f"⏭️ **Selanjutnya:** `{q.queue[0]['title']}`"
        else:
            next_info = "Antrean kosong, bot akan standby. ✨"

        # 4. PAKAI FUNGSI EMBED YANG SUDAH KITA BUAT
        embed = buat_embed_skip(interaction.user, lagu_dilewati, next_info)

        # 5. EKSEKUSI SKIP
        vc.stop()
        
        # Kirim notifikasi skip
        skip_msg = await interaction.followup.send(embed=embed)
        
        # 6. BERSIHKAN PESAN
        await asyncio.sleep(15)
        try:
            await skip_msg.delete()
        except:
            pass
            
    else:
        await interaction.followup.send("❌ **Gagal:** Tidak ada lagu yang sedang diputar.", ephemeral=True)


# --- [ COMMAND /VOLUME ] ---
@bot.tree.command(name="volume", description="Atur Volume Audio (0-100%)")
@app_commands.describe(persen="Masukkan angka antara 0 sampai 100")
async def volume(interaction: discord.Interaction, persen: int):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if 0 <= persen <= 100:
        # 1. Update Memory & Engine
        q.volume = persen / 100
        if vc and vc.source:
            try:
                vc.source.volume = q.volume
            except AttributeError:
                pass
            
        # 2. Logika Warna & Status
        if persen > 80:
            warna_embed, status_teks = 0xe74c3c, "⚠️ Volume Tinggi"
        elif persen > 50:
            warna_embed, status_teks = 0xf1c40f, "🔉 Volume Sedang"
        else:
            warna_embed, status_teks = 0x3498db, "🔈 Volume Standar"
        
        # 3. Visual Bar
        bar = "▰" * (persen // 10) + "▱" * (10 - (persen // 10))
        
        # 4. SINKRONISASI KE DASHBOARD
        if q.last_dashboard:
            try:
                current_embed = q.last_dashboard.embeds[0]
                current_embed.set_field_at(1, name="🔊 Volume", value=f"`{persen}%`", inline=True)
                await q.last_dashboard.edit(embed=current_embed)
            except:
                pass

        # 5. Kirim Respon Konfirmasi
        embed = discord.Embed(
            title="🎚️ Audio Mixer Console",
            description=(
                f"**Status:** {status_teks}\n"
                f"**Level:** `{persen}%` / `100%` \n"
                f"`{bar}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=warna_embed
        )
        embed.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, delete_after=15)
        
    else:
        await interaction.response.send_message("❌ **Gagal:** Gunakan angka **0 - 100**.", ephemeral=True)


# --- [ COMMAND /QUEUE ] ---
@bot.tree.command(name="queue", description="Lihat antrean dan pilih lagu untuk dilompati")
async def queue_cmd(interaction: discord.Interaction):
    # 1. Defer dulu
    await interaction.response.defer(ephemeral=False)
    
    try:
        # 2. Panggil fungsi dashboard yang sudah kita buat
        view = MusicDashboard(interaction.guild_id)
        await view.tampilkan_antrean(interaction)
        
    except Exception as e:
        print(f"Error pada command /queue: {e}")
        await interaction.followup.send(
            "⚠️ Terjadi kendala saat memuat antrean. Pastikan bot sedang aktif.", 
            ephemeral=True
        )


# ==============================================================================
# 🎙️ SECTION: VOICE GROUP SYSTEM
# ==============================================================================
# (PENTING: Definisikan wadah -> isi command -> baru add_command)

# 1. Definisikan Wadah Group
voice_group = app_commands.Group(name="voice", description="Kontrol koneksi bot ke Voice Channel")

# 2. Sub-Command: /voice masuk
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





# 3. Sub-Command: /voice keluar
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

# 4.DAFTARKAN GRUP (Wajib dilakukan setelah sub-command dibuat)
bot.tree.add_command(voice_group)


# ==============================================================================
# ℹ️ SECTION: SYSTEM & UTILITY COMMANDS
# ==============================================================================

# --- [ COMMAND /HELP ] ---
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


# --- [ COMMAND /DEBUG ] ---
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



























def create_progress_bar(current, total):
    if total <= 0:
        return "🔴 " + "─" * 30 # Garis panjang untuk Live
        
    # --- SESUAIKAN ANGKA INI ---
    max_size = 33 # Naikkan ke 33 agar full mentok di embed HP
    
    # Logika Dinamis: 
    # Lagu pendek (1-3 mnt) bar akan terlihat lebih ringkas.
    # Lagu panjang (>10 mnt) bar akan memanjang sampai max_size.
    dynamic_size = max(20, min(int(total / 30), max_size)) 
    
    
    progress = min(int((current / total) * dynamic_size), dynamic_size)
    
    
    # Gabungan simbol: ▬ untuk yang sudah lewat, 🔘 posisi skrg, ─ garis sisa
    bar = "▬" * progress + "🔘" + "─" * (dynamic_size - progress)
    return bar





def generate_embed(current, total, title, url, thumb, req, guild_id):
    """Desain Dashboard Media Player Premium Style"""
    q = get_queue(guild_id)
    vol_percent = int(q.volume * 100)
    
    # --- FIX FORMATTER JAM ---
    def fmt(sec):
        sec = int(sec)
        hrs = sec // 3600
        mins = (sec % 3600) // 60
        secs = sec % 60
        if hrs > 0:
            return f"{hrs}:{mins:02}:{secs:02}"
        else:
            return f"{mins:02}:{secs:02}"
    # -------------------------

    dur_str = f"**{fmt(current)}** / **{fmt(total)}**" if total else "🔴 **LIVE STREAM**"
    
    # Sisanya tetap sama seperti kode asli kamu...
    prog_bar = create_progress_bar(current, total)
    embed = discord.Embed(color=0x2b2d31) 
    # - Logo Roket 
    #embed.set_author(name="SEDANG DIPUTAR", icon_url="https://cdn.pixabay.com/animation/2023/06/13/15/12/15-12-37-624_512.gif")
    
    # - Logo Circle muter 
    #embed.set_author(name="SEDANG DIPUTAR", icon_url="https://cdn.pixabay.com/animation/2024/03/20/05/16/05-16-04-416_512.gif")
    
    # - Logo kreta muter 
    embed.set_author(name="SEDANG DIPUTAR", icon_url="https://cdn.pixabay.com/animation/2022/12/25/06/28/06-28-22-725_512.gif")
    
    # - Logo Awal
	#embed.set_author(name="SEDANG DIPUTAR", icon_url="https://cdn.pixabay.com/animation/2023/06/13/15/12/15-12-37-624_512.gif")
    embed.description = (f"## 🎵 [{title}]({url})\n" f"━━━━━━━━━━━━━━━━━━━━━━\n" f"{prog_bar}\n" f"{dur_str}\n")
    vol_emoji = "🔇" if vol_percent == 0 else "🔈" if vol_percent < 40 else "🔉" if vol_percent < 70 else "🔊"
    embed.add_field(name="👤 Pemesan", value=req.mention, inline=True)
    embed.add_field(name=f"{vol_emoji} Volume", value=f"`{vol_percent}%`", inline=True)
    embed.add_field(name="📡 Audio Source", value="`Lossless 192kbps`", inline=True)
    if thumb: embed.set_thumbnail(url=thumb)
    embed.set_footer(text=f"Angelss V17 Premium • {req.display_name}", icon_url=req.display_avatar.url)
    return embed






# Tambahkan 'guild_id' di dalam kurung paling akhir
async def update_player_interface(interaction, message, total_duration, title, url, thumb, req, guild_id):
    """Looping background dengan interval 5 detik (Struktur Asli Kamu + Sinkron ID)"""
    # Ambil antrean berdasarkan guild_id yang dikirim
    q = get_queue(guild_id) 
    try:
        while True:
            # 1. Hitung waktu berjalan secara real-time
            current_time = time.time() - q.start_time
            
            # 2. Berhenti jika lagu sudah mencapai akhir durasi
            if total_duration > 0 and current_time > total_duration:
                break
                
            # 3. Buat tampilan embed terbaru (Sekarang mengoper guild_id ke generate_embed)
            new_embed = generate_embed(current_time, total_duration, title, url, thumb, req, guild_id)
            
            try:
                # 4. Kirim update ke Discord
                await message.edit(embed=new_embed)
            except (discord.NotFound, Exception):
                # Berhenti jika pesan dashboard dihapus atau ada error jaringan
                break 

            # --- JEDA 5 DETIK ---
            await asyncio.sleep(5) 
            
    except asyncio.CancelledError:
        # Berhenti jika lagu di-skip atau tombol Stop ditekan
        pass




# ==============================================================================
# 🚀 SECTION: START ENGINE
# ==============================================================================
bot.run(TOKEN)
