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




# --- [ 0.2. CORE DEPENDENCIES ] ---
import os
import asyncio
import datetime
import logging
import json
from collections import deque
from dotenv import load_dotenv

# Memuat file .env ke dalam sistem environment
load_dotenv()

# --- [ 0.3. DISCORD API LIBRARIES ] ---
import discord
from discord import app_commands
from discord.ext import commands

# --- [ 0.4. MULTIMEDIA LIBRARIES ] ---
import yt_dlp





# ----- LIBRARY - WEB SOCKET
from flask import Flask
from threading import Thread

web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot Music Angels is Online!"

def run():
    # Menggunakan port 25618 (pastikan port ini dibuka di panel Octavia kamu)
    web_app.run(host='0.0.0.0', port=25618)

def keep_alive():
    """Fungsi untuk menjalankan Flask di thread terpisah agar tidak mengganggu bot."""
    t = Thread(target=run)
    t.start()




# ==============================================================================
# 📝 SECTION 0.5: PROFESSIONAL LOGGING SYSTEM (SILENCED VERSION)
# ==============================================================================

# 1. Setup Logger Utama
logger = logging.getLogger('Angelss_V17')
logger.setLevel(logging.INFO)

# --- [ TAMBAHKAN KODE INI DI SINI ] ---
# Membisukan log "berisik" dari library luar agar tidak memenuhi konsol
logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('yt_dlp').setLevel(logging.ERROR)
logging.getLogger('asyncio').setLevel(logging.WARNING)
# --------------------------------------

# 2. Format Log (Waktu - Level - Pesan)
log_formatter = logging.Formatter(
    fmt='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 3. Handler File
file_handler = logging.FileHandler('SystemLog_BotMusicAngels-1.log', encoding='utf-8', mode='a')
file_handler.setFormatter(log_formatter)

# 4. Handler Konsol
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# 5. Pasang Handler ke Logger
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
# ------------------------------------------------------------------------------








# --- [ 0.6. GLOBAL CONSTANTS & CONFIGURATION ] ---
TOKEN = os.getenv('DISCORD_TOKEN') 
COOKIES_FILE = 'youtube_cookies.txt'




# --- [ 0.7. BOOTSTRAP VALIDATION ] ---
def bootstrap():
    """Validasi awal sistem sebelum bot melakukan login."""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  🚀 ANGELSS PROJECT V17 | STARTING SERVICE...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    if not TOKEN:
        logger.critical("❌ FATAL ERROR: DISCORD_TOKEN is missing from environment.")
        exit(1)
        
    if os.path.exists(COOKIES_FILE):
        logger.info(f"✅ IDENTITY: YouTube Cookies loaded from '{COOKIES_FILE}'.")
    else:
        logger.warning(f"⚠️ IDENTITY: Running without cookies. High-risk of 403 Forbidden.")

# --- [ 0.8. Jalankan validasi ] ---
bootstrap()

# --- [ 0.9. QUEUE & MEMORY STORAGE ] ---
queues = {} 




# ==============================================================================
# ⚡ NEXT: PROJECT BOT MUSIC - INITIALIZING ENGINE
# ==============================================================================

# --- [ 1. YTDL OPTIONS: High Quality Source Fetching ] ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': 'youtube_cookies.txt', 
    'cachedir': False, # MATIKAN cache agar lagu selalu mulai dari awal 00:00
    'http_chunk_size': 10485760, 
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    }
}




# --- [ 2. FFMPEG OPTIONS: The "Audiophile" Processing ] ---
FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 '
        '-probesize 20M '
        '-analyzeduration 20M '
    ),
    'options': (
        '-vn '
        '-threads 2 '  # Menggunakan 2 threads agar beban dibagi ke 2 vCPU
        '-ar 48000 '
        '-ac 2 '
        '-b:a 192k '
        '-f s16le '
        '-bufsize 12000k ' # Buffer dinaikkan agar transisi antrean lancar
        '-preset ultrafast ' # Mempercepat proses encoding agar lagu langsung mulai 00:00
        '-af "loudnorm=I=-16:TP=-1.5:LRA=11,acompressor=threshold=-12dB:ratio=2:attack=20:release=100"'
    )
}


# --- [ 3. INISIALISASI YT-DLP ] ---
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)











# ==============================================================================
# 🏗️ SECTION C: BOT INFRASTRUCTURE & LIFECYCLE MANAGEMENT
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
            logger.info(f"✅ SYNC: Berhasil sinkronisasi {len(synced)} slash commands secara global.")
        except Exception as e:
            logger.error(f"❌ SYNC ERROR: Gagal sinkronisasi command: {e}")

    async def on_ready(self):
        activity = discord.Activity(
            type=discord.ActivityType.listening, 
            name="/play | Angelss V17"
        )
        await self.change_presence(status=discord.Status.online, activity=activity)

        target_channel_id = 1456250414638043169 
        try:
            channel = self.get_channel(target_channel_id)
            if channel:
                try:
                    async for message in channel.history(limit=10):
                        if message.author == self.user:
                            await message.delete()
                except Exception as e:
                    logger.warning(f"⚠️ CLEANUP: Gagal menghapus pesan lama: {e}")

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






# --- [ 6. QUEUE SYSTEM ] ---
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

    def clear_all(self):
        self.queue.clear()
        self.current_info = None
        self.last_dashboard = None
        self.last_search_msg = None
        self.last_queue_msg = None

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]
    
    
    
    
    

# --- [ 7. AUTO-DISCONNECT ] ---
@bot.event
async def on_voice_state_update(member, before, after):
    if not member.bot and before.channel is not None:
        vc = member.guild.voice_client
        if vc and vc.channel.id == before.channel.id and len(vc.channel.members) == 1:
            q = get_queue(member.guild.id)
            logger.info(f"⏳ IDLE: Channel kosong di {member.guild.name}, memulai timer disconnect.")
            
            msg_chan = None
            if q.last_dashboard:
                msg_chan = q.last_dashboard.channel
            elif q.text_channel_id:
                msg_chan = bot.get_channel(q.text_channel_id)
            
            if msg_chan:
                try:
                    peringatan = await msg_chan.send(f"⚠️ **Otomatis Keluar:** Channel kosong. Keluar dalam 30 detik.", delete_after=30)
                except: peringatan = None
                
                await asyncio.sleep(30)
                
                vc_sekarang = member.guild.voice_client
                if vc_sekarang and vc_sekarang.channel:
                    human_members = [m for m in vc_sekarang.channel.members if not m.bot]
                    if len(human_members) > 0:
                        logger.info(f"✨ IDLE: User kembali ke channel. Batal disconnect.")
                    else:
                        q.queue.clear()
                        if q.last_dashboard:
                            try: await q.last_dashboard.delete()
                            except: pass
                        q.last_dashboard = None
                        
                        if vc_sekarang.is_connected():
                            await vc_sekarang.disconnect()
                            logger.info(f"👋 DISCONNECT: Bot keluar otomatis dari {member.guild.name} karena inaktif.")
                            await msg_chan.send("👋 **Informasi:** Bot telah keluar karena sepi.", delete_after=10)









# --- [ 8. SYSTEM SEARCH ENGINE PILIHAN ] ---
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
            title = entry.get('title', 'Unknown')[:50]
            url = entry.get('url') or entry.get('webpage_url')
            options.append(discord.SelectOption(label=f"Lagu Nomor {i+1}", value=url, description=title, emoji="🎵"))
            
        select = discord.ui.Select(placeholder="🎯 Pilih lagu...", options=options)
        
        async def callback(interaction: discord.Interaction):
            if interaction.user != self.user:
                return await interaction.response.send_message(f"⚠️ Bukan sesi kamu.", ephemeral=True)
            
            await interaction.response.defer()
            logger.info(f"🖱️ SELECTION: {interaction.user.name} memilih lagu dari menu pencarian.")
            await play_music(interaction, select.values[0])
            
            status_embed = discord.Embed(title="✅ Berhasil!", description=f"🎶 Lagu pilihan **{interaction.user.display_name}** ditambahkan.", color=0x2ecc71)
            await interaction.edit_original_response(embed=status_embed, view=None)
            await asyncio.sleep(5)
            try: await interaction.delete_original_response()
            except: pass

        select.callback = callback
        self.add_item(select)

        btn_close = discord.ui.Button(label="Tutup", style=discord.ButtonStyle.danger, emoji="🗑️")
        async def close_callback(interaction: discord.Interaction):
            if interaction.user == self.user:
                await interaction.message.delete()
            else:
                await interaction.response.send_message("❌ Akses ditolak.", ephemeral=True)
        btn_close.callback = close_callback
        self.add_item(btn_close)

    def create_embed(self):
        description = "📺 **YouTube Search Engine**\n\n"
        for i, entry in enumerate(self.entries):
            judul = entry.get('title', 'Unknown Title')
            description += f"✨ `{i+1}.` {judul[:60]}...\n"
        embed = discord.Embed(title="🔍 Hasil Pencarian Musik", description=description, color=0xf1c40f)
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif") 
        embed.set_footer(text=f"Request: {self.user.display_name}", icon_url=self.user.display_avatar.url)
        return embed
        
        
        
        
        

# --- [ 9. UI CLASS: DASHBOARD & VOLUME ] ---
class VolumeControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    def create_embed(self):
        q = get_queue(self.guild_id)
        vol_percent = int(q.volume * 100)
        embed = discord.Embed(title="🎚️ Pengaturan Audio", color=0x3498db)
        bar_length = 10
        filled = round(q.volume * 10)
        bar = "▰" * filled + "▱" * (bar_length - filled)
        embed.description = f"Volume: **{vol_percent}%**\n`{bar}`"
        return embed

    @discord.ui.button(label="-10%", style=discord.ButtonStyle.danger, emoji="🔉")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        q.volume = max(0.0, q.volume - 0.1)
        vc = interaction.guild.voice_client
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass
        await interaction.edit_original_response(embed=self.create_embed())

    @discord.ui.button(label="+10%", style=discord.ButtonStyle.success, emoji="🔊")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        q.volume = min(1.0, q.volume + 0.1) 
        vc = interaction.guild.voice_client
        if vc and vc.source:
            try: vc.source.volume = q.volume
            except: pass
        await interaction.edit_original_response(embed=self.create_embed())









# --- [ 10. FUNCTION: EMBED - SKIP ] ---
def buat_embed_skip(user, lagu_dilewati, info_selanjutnya):
    judul_bersih = str(lagu_dilewati)[:100].strip() 
    embed = discord.Embed(
        title="⏭️ NEXT MUSIC SKIP",
        description=(f"✨ **{user.mention}** melompat ke lagu berikutnya!\n🗑️ **Skip:** `{judul_bersih}`\n📥 **Status:** {info_selanjutnya}"),
        color=0xe67e22 
    )
    embed.set_footer(text="Skip System • Angelss V17", icon_url=user.display_avatar.url)
    return embed
    
    
    
    
    
    

# --- [ 11. UI CLASS: DASHBOARD & AUDIO - PLAYER ] ---
class MusicDashboard(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    async def update_button(self, message):
        vc = message.guild.voice_client
        if not self.children: return
        button = self.children[0] 
        if vc and vc.is_paused():
            button.emoji = "▶️"
            button.label = "Lanjut"
            button.style = discord.ButtonStyle.success
        else:
            button.emoji = "⏸️"
            button.label = "Jeda"
            button.style = discord.ButtonStyle.secondary
        await message.edit(view=self)

    @discord.ui.button(label="Jeda", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pp(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if not vc: return await interaction.response.send_message("❌ Bot tidak ada.", ephemeral=True)
        
        if vc.is_playing():
            vc.pause()
            logger.info(f"⏯️ DASHBOARD: {interaction.user.name} menjeda musik.")
            button.emoji = "▶️"
            button.label = "Lanjut"
            button.style = discord.ButtonStyle.success 
        else:
            vc.resume()
            logger.info(f"⏯️ DASHBOARD: {interaction.user.name} melanjutkan musik.")
            button.emoji = "⏸️"
            button.label = "Jeda"
            button.style = discord.ButtonStyle.secondary
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="Volume", emoji="🔊", style=discord.ButtonStyle.gray)
    async def vol(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = VolumeControlView(self.guild_id)
        await interaction.response.send_message(embed=view.create_embed(), view=view, ephemeral=True)
    
    @discord.ui.button(label="Antrean", emoji="📜", style=discord.ButtonStyle.gray)
    async def list_q_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.tampilkan_antrean(interaction)

    async def tampilkan_antrean(self, interaction: discord.Interaction):
        q = get_queue(self.guild_id)
        if q.last_queue_msg:
            try: await q.last_queue_msg.delete()
            except: pass

        if not q.queue:
            return await interaction.response.send_message("📪 Antrean kosong.", ephemeral=True)
        
        emb = discord.Embed(title="📜 Antrean Musik", color=0x2b2d31)
        description = "Pilih lagu untuk lompat antrean!\n\n"
        options = []
        for i, item in enumerate(list(q.queue)[:10]):
            description += f"**{i+1}.** {item['title'][:50]}...\n"
            options.append(discord.SelectOption(label=f"{i+1}. {item['title'][:25]}", value=str(i), emoji="🎵"))
        
        emb.description = description
        select = discord.ui.Select(placeholder="🚀 Lompat ke...", options=options)

        async def select_callback(inter: discord.Interaction):
            await inter.response.defer()
            idx = int(select.values[0])
            chosen = q.queue[idx]
            del q.queue[idx]
            q.queue.appendleft(chosen)
            
            logger.info(f"📜 QUEUE JUMP: {inter.user.name} melompat ke lagu {chosen['title']}.")
            
            if inter.guild.voice_client: inter.guild.voice_client.stop()
            await inter.followup.send(f"⏭️ Melompati ke: **{chosen['title']}**", delete_after=10)

        select.callback = select_callback
        view_select = discord.ui.View(timeout=60)
        view_select.add_item(select)
        
        if interaction.response.is_done():
            q.last_queue_msg = await interaction.followup.send(embed=emb, view=view_select)
        else:
            await interaction.response.send_message(embed=emb, view=view_select)
            q.last_queue_msg = await interaction.original_response()

    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        if not vc: return await interaction.followup.send("❌ Tidak ada lagu.", ephemeral=True)
        
        logger.info(f"⏭️ DASHBOARD: {interaction.user.name} menekan tombol skip.")
        vc.stop()
        await interaction.followup.send("⏭️ **Skipped via Dashboard**", delete_after=5)

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(interaction.guild_id)
        vc = interaction.guild.voice_client
        q.queue.clear()
        if vc: await vc.disconnect()
        
        logger.info(f"🛑 DASHBOARD: {interaction.user.name} mematikan bot.")
        await interaction.response.send_message("🛑 **Stopped via Dashboard**", delete_after=5)














# ==============================================================================
# 💿 SECTION: CORE MUSIC ENGINE
# ==============================================================================




# --- [ 12.1. NEXT LOGIC ] ---
async def next_logic(interaction):
    """Logika otomatis untuk memutar lagu berikutnya."""
    q = get_queue(interaction.guild_id)
    await asyncio.sleep(2)
    
    if q.queue:
        next_song = q.queue.popleft()
        logger.info(f"🔄 AUTOPLAY: Memutar lagu selanjutnya '{next_song['title']}'.")
        await start_stream(interaction, next_song['url'])
    else:
        logger.info("💤 END: Antrean habis. Standby mode.")
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        channel = bot.get_channel(q.text_channel_id) or interaction.channel
        if channel:
            await channel.send("✨ **Antrean Selesai.**", delete_after=15)





# --- [ 12.2. START STREAM LOGIC ] ---
async def start_stream(interaction, url):
    """Mesin utama dengan Error Handling & Logging."""
    q = get_queue(interaction.guild_id)
    q.text_channel_id = interaction.channel.id
    vc = interaction.guild.voice_client
    
    if not vc or not vc.is_connected(): return

    try:
        data = await asyncio.wait_for(
            bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False)),
            timeout=35
        )
        if data is None: raise Exception("Cookies Expired / IP Blok")
        if 'entries' in data: data = data['entries'][0]

        stream_url = data.get('url')
        if not stream_url: raise Exception("Stream URL Missing")

        audio_source = discord.FFmpegPCMAudio(stream_url, executable="ffmpeg", **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)
        
        def after_playing(error):
            if error: logger.error(f"⚠️ PLAYER ERROR: {error}")
            future = asyncio.run_coroutine_threadsafe(next_logic(interaction), bot.loop)
            try: future.result(timeout=1)
            except: pass 

        if vc.is_playing(): vc.stop()
        vc.play(source, after=after_playing)
        
        # Logging Play Sukses
        logger.info(f"▶️ PLAYING: {data['title']} (Durasi: {data.get('duration')}s)")
        
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            
        durasi_detik = data.get('duration', 0)
        durasi_str = str(datetime.timedelta(seconds=durasi_detik)) if durasi_detik else "Live"

        emb = discord.Embed(title="🎶 Sedang Diputar", description=f"**[{data['title']}]({data.get('webpage_url', url)})**", color=0x2ecc71)
        emb.add_field(name="⏱️ Durasi", value=f"`{durasi_str}`", inline=True)
        emb.add_field(name="🔊 Volume", value=f"`{int(q.volume * 100)}%`", inline=True)
        emb.set_thumbnail(url=data.get('thumbnail'))
        emb.set_footer(text=f"Requested by {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        q.last_dashboard = await interaction.channel.send(embed=emb, view=MusicDashboard(interaction.guild_id))
        
    except Exception as e:
        logger.error(f"🔥 PLAY ERROR: Gagal memutar {url}. Reason: {e}")
        embed_err = discord.Embed(title="🚫 System Failure", description=f"Error: `{str(e)[:100]}`", color=0xff4757)
        await interaction.channel.send(embed=embed_err, delete_after=20)
        await asyncio.sleep(3)
        await next_logic(interaction)




# ==============================================================================
# 🛠️ SECTION: HELPER FUNCTIONS
# ==============================================================================

async def play_music(interaction, url):
    q = get_queue(interaction.guild_id)
    q.text_channel_id = interaction.channel.id
    
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            try: await interaction.user.voice.channel.connect()
            except Exception as e:
                logger.error(f"❌ CONNECTION ERROR: {e}")
                return await interaction.followup.send(f"❌ Gagal koneksi: {e}", ephemeral=True)
        else:
            return await interaction.followup.send("❌ Masuk Voice dulu!", ephemeral=True)
    
    vc = interaction.guild.voice_client
    
    if vc.is_playing() or vc.is_paused():
        try:
            data = await bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            if 'entries' in data: data = data['entries'][0]

            q.queue.append({'title': data['title'], 'url': url})
            
            logger.info(f"📥 ADD QUEUE: {interaction.user.name} menambahkan '{data['title']}' ke antrean.")
            
            emb_q = discord.Embed(title="📥 Antrean Ditambahkan", description=f"✨ **[{data['title']}]({url})**", color=0x3498db)
            emb_q.set_footer(text=f"Posisi: {len(q.queue)}", icon_url=interaction.user.display_avatar.url)
            await interaction.followup.send(embed=emb_q, ephemeral=True)
            
        except Exception as e:
            logger.error(f"⚠️ QUEUE ERROR: {e}")
            await interaction.followup.send(f"⚠️ Gagal antre: {str(e)[:50]}", ephemeral=True)
    else:
        if vc.is_playing(): vc.stop()
        logger.info(f"▶️ START: {interaction.user.name} memulai sesi musik baru.")
        await start_stream(interaction, url)








# ==============================================================================
# 🎵 SECTION: MUSIC COMMANDS
# ==============================================================================





@bot.tree.command(name="play", description="Putar musik menggunakan judul atau link")
async def play(interaction: discord.Interaction, cari: str):
    await interaction.response.defer(ephemeral=True)
    q = get_queue(interaction.guild_id)
    if q.last_search_msg:
        try: await q.last_search_msg.delete()
        except: pass

    logger.info(f"⌨️ COMMAND: {interaction.user.name} uses /play query='{cari}'")

    if "http" in cari: 
        await interaction.followup.send("🔗 **Memproses tautan...**", ephemeral=True)
        await play_music(interaction, cari)
        await interaction.edit_original_response(content=f"✅ **Tautan diterima.**")
    else:
        await interaction.followup.send(f"🔍 **Mencari:** `{cari}`...", ephemeral=True)
        try:
            search_opts = {'extract_flat': True, 'quiet': True}
            data = await bot.loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(f"ytsearch5:{cari}", download=False))
            
            if not data or 'entries' not in data or len(data['entries']) == 0:
                logger.warning(f"⚠️ SEARCH 404: Tidak ditemukan untuk '{cari}'")
                return await interaction.edit_original_response(content="❌ Lagu tidak ditemukan.")
            
            view = SearchControlView(data['entries'], interaction.user)
            q.last_search_msg = await interaction.edit_original_response(content=None, embed=view.create_embed(), view=view)

        except Exception as e:
            logger.error(f"❌ SEARCH ERROR: {e}")
            await interaction.edit_original_response(content="⚠️ Error saat mencari.")







@bot.tree.command(name="stop", description="Stop dan bersihkan")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    jumlah_antrean = len(q.queue)
    
    logger.info(f"🛑 COMMAND: {interaction.user.name} uses /stop. ({jumlah_antrean} items cleared)")
    
    if vc:
        q.queue.clear()
        q.current_info = None
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None

        await vc.disconnect()
        
        embed = discord.Embed(title="🛑 SYSTEM TERMINATED", description=(f"✨ **{interaction.user.mention}** menghentikan sesi.\n🧹 **Clear:** `{jumlah_antrean}` lagu."), color=0x2f3136)
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        await interaction.response.send_message(embed=embed, delete_after=20)
    else:
        await interaction.response.send_message("❌ Bot tidak aktif.", ephemeral=True)







@bot.tree.command(name="pause", description="Jeda musik")
async def pause(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_playing():
        vc.pause()
        logger.info(f"⏸️ COMMAND: {interaction.user.name} uses /pause.")
        embed = discord.Embed(description="⏸️ **Musik dijeda. |  Oleh ->	: {interaction.user.mention}.**", color=0xf1c40f)
        await interaction.response.send_message(embed=embed, delete_after=10)
        if q.last_dashboard:
            await MusicDashboard(interaction.guild_id).update_button(q.last_dashboard)
    else:
        await interaction.response.send_message("❌ Gagal.", ephemeral=True)






@bot.tree.command(name="resume", description="Lanjut musik")
async def resume(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc and vc.is_paused():
        vc.resume()
        logger.info(f"▶️ COMMAND: {interaction.user.name} uses /resume.")
        embed = discord.Embed(description="▶️ **Musik dilanjutkan  |  Oleh ->	: {interaction.user.mention}.**", color=0x2ecc71)
        await interaction.response.send_message(embed=embed, delete_after=10)
        if q.last_dashboard:
            await MusicDashboard(interaction.guild_id).update_button(q.last_dashboard)
    else:
        await interaction.response.send_message(f"❌ Gagal.", ephemeral=True)








@bot.tree.command(name="skip", description="Lewati lagu")
async def skip_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if vc and (vc.is_playing() or vc.is_paused()):
        logger.info(f"⏭️ COMMAND: {interaction.user.name} uses /skip.")
        
        lagu_dilewati = "Lagu saat ini"
        if q.last_dashboard and q.last_dashboard.embeds:
            try:
                full_desc = q.last_dashboard.embeds[0].description
                if "[" in full_desc: lagu_dilewati = full_desc.split('[')[1].split(']')[0]
            except: pass

        next_info = f"⏭️ **Next:** `{q.queue[0]['title']}`" if q.queue else "Antrean habis."
        embed = buat_embed_skip(interaction.user, lagu_dilewati, next_info)

        vc.stop()
        skip_msg = await interaction.followup.send(embed=embed)
        await asyncio.sleep(15)
        try: await skip_msg.delete()
        except: pass  
    else:
        await interaction.followup.send("❌ **Gagal:** Tidak ada lagu yang sedang diputar.", delete_after=15)
       









@bot.tree.command(name="volume", description="Atur Volume (0-100)")
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
        logger.info(f"🔊 COMMAND: {interaction.user.name} set volume to {persen}%.")
        
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
        await interaction.response.send_message("❌ **Gagal:** Gunakan angka **0 - 100**.", delete_after=60)
        
	
    
    
    
    
    


@bot.tree.command(name="queue", description="Lihat antrean")
async def queue_cmd(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=False)
    try:
        view = MusicDashboard(interaction.guild_id)
        await view.tampilkan_antrean(interaction)
    except Exception as e:
        logger.error(f"❌ QUEUE CMD ERROR: {e}")
        await interaction.followup.send("⚠️ Error memuat antrean.", ephemeral=True)










# ==============================================================================
# 🎙️ SECTION: VOICE GROUP SYSTEM
# ==============================================================================
voice_group = app_commands.Group(name="voice", description="Kontrol koneksi")

@voice_group.command(name="masuk", description="Panggil bot")
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
        logger.info(f"🎙️ VOICE JOIN: {interaction.user.name} memanggil bot")
        if vc.channel.id == target_channel.id:
            return await interaction.response.send_message("⚠️ Aku sudah di sini!", ephemeral=True)
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
    
	
	
	
	
	
    
@voice_group.command(name="keluar", description="Usir bot")
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
        logger.info(f"🎙️ VOICE LEAVE: {interaction.user.name} mengeluarkan bot.")
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
        await interaction.response.send_message("❌ Aku sedang tidak berada di dalam Voice Channel.",  delete_after=30)

	
	
	
	
	
	
	
    vc = interaction.guild.voice_client
    if vc:

        q = get_queue(interaction.guild_id)
        q.queue.clear()
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        await vc.disconnect()
        emb_bye = discord.Embed(title="👋 Sampai Jumpa!", description="Disconnected.", color=0xf1c40f)
        await interaction.response.send_message(embed=emb_bye, delete_after=60)
    else:
        await interaction.response.send_message("❌ Bot tidak di Voice.", ephemeral=True)

bot.tree.add_command(voice_group)
















# ==============================================================================
# ℹ️ SECTION: SYSTEM & UTILITY
# ==============================================================================
@bot.tree.command(name="help", description="Panduan bot")
async def help_cmd(interaction: discord.Interaction):
    logger.info(f"ℹ️ HELP: {interaction.user.name} melihat menu bantuan.")
    
    
    # ... (Kode embed help kamu disingkat agar muat, isinya sama) ...
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










@bot.tree.command(name="debug", description="Cek kesehatan sistem")
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

    
    logger.info(f"🛠️ DEBUG: {interaction.user.name} menjalankan diagnosa sistem.")
    
    await interaction.followup.send(embed=embed)
    
    
   
    

# ==============================================================================
# 🚀 SECTION: START ENGINE
# ==============================================================================
keep_alive()  # Ini akan menjalankan web server kecil untuk dipantau UptimeRobot
bot.run(TOKEN)