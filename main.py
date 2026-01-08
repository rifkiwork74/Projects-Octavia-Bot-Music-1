# =================================================================
# 💿 ANGELSS MUSIC PROJECT - PREMIUM EDITION [HYBRID FINAL FIX]
# =================================================================
# Developer : ikiii
# Status    : Active - IT - Engineering
# =================================================================

import datetime
import asyncio
import os
import shutil
import sys
from collections import deque
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import static_ffmpeg
from dotenv import load_dotenv

# --- 1. INITIALIZATION ---
load_dotenv()

# Mengaktifkan jalur FFmpeg untuk hosting
try:
    static_ffmpeg.add_paths()
except Exception as e:
    print(f"⚙️ Info static-ffmpeg: {e}")

# --- 2. CONFIGURATION ---
TOKEN = os.getenv('DISCORD_TOKEN')
COOKIES_FILE = 'youtube_cookies.txt'

if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN tidak ditemukan!")
    sys.exit(1)

# --- 3. SETTINGS - FORMAT CONVERTER (OPTIMIZED) ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    'cachedir': False,
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
}

# FFmpeg Options milik kamu yang asli (Sangat Optimal)
FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-nostdin '          
        '-probesize 7M '    
        '-analyzeduration 5M'
    ),
    'options': (
        '-vn '
        '-af "alimiter=limit=0.9, dynaudnorm=f=800:g=31:m=5.0, treble=g=2, bass=g=5" '
        '-ac 2 '
        '-ar 48000 '
        '-b:a 192k '         
        '-vbr on '
        '-compression_level 6'
    )
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

# --- 4. SETUP BOT ---
class ModernBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.voice_states = True 
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ SISTEM V1 FIX FINAL ONLINE!")

bot = ModernBot()

# --- 5. QUEUE SYSTEM ---
queues = {}

class MusicQueue:
    def __init__(self):
        self.queue = deque()
        self.current_info = None
        self.volume = 0.5
        self.last_dashboard = None
        self.last_search_msg = None
        self.last_queue_msg = None
        self.text_channel_id = None

def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]

# --- 6. HELPER FUNCTIONS ---
def buat_embed_skip(user, lagu_dilewati, info_selanjutnya):
    embed = discord.Embed(
        title="⏭️ NEXT MUSIC SKIP",
        description=(
            f"✨ **{user.mention}** telah melompat ke lagu berikutnya!\n\n"
            f"🗑️ **Dilewati:** `{lagu_dilewati}`\n"
            f"📥 **Status Antrean:** {info_selanjutnya}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xe67e22
    )
    embed.set_footer(text="System Skip Otomatis • Angelss Project v17", icon_url=user.display_avatar.url)
    return embed

# --- 7. UI CLASSES (DASHBOARD & VOLUME) ---
class VolumeControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    def create_embed(self):
        q = get_queue(self.guild_id)
        vol_percent = int(q.volume * 100)
        bar = "▰" * int(vol_percent / 10) + "▱" * (10 - int(vol_percent / 10))
        embed = discord.Embed(title="🎚️ Pengaturan Audio", description=f"Volume Saat Ini: **{vol_percent}%**\n`{bar}`", color=0x3498db)
        embed.set_footer(text="Batas aman standar: 100%")
        return embed

    @discord.ui.button(label="-10%", style=discord.ButtonStyle.danger, emoji="🔉")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        q = get_queue(self.guild_id)
        q.volume = max(0.0, q.volume - 0.1)
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = q.volume
        await interaction.edit_original_response(embed=self.create_embed())

    @discord.ui.button(label="+10%", style=discord.ButtonStyle.success, emoji="🔊")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        q = get_queue(self.guild_id)
        q.volume = min(1.0, q.volume + 0.1)
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = q.volume
        await interaction.edit_original_response(embed=self.create_embed())

class MusicDashboard(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @discord.ui.button(label="Jeda", emoji="⏸️", style=discord.ButtonStyle.secondary)
    async def pp(self, interaction: discord.Interaction, button: discord.ui.Button):
        vc = interaction.guild.voice_client
        if not vc: return
        if vc.is_playing():
            vc.pause()
            button.emoji, button.label, button.style = "▶️", "Lanjut", discord.ButtonStyle.success
        else:
            vc.resume()
            button.emoji, button.label, button.style = "⏸️", "Jeda", discord.ButtonStyle.secondary
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
            if interaction.response.is_done():
                return await interaction.followup.send("📪 Antrean saat ini kosong.", ephemeral=True)
            else:
                return await interaction.response.send_message("📪 Antrean saat ini kosong.", ephemeral=True)
        
        emb = discord.Embed(title="📜 Antrean Musik (Publik)", color=0x2b2d31)
        description = "Pilih lagu di bawah untuk langsung diputar (Lompat Antrean)!\n\n"
        options = []
        for i, item in enumerate(list(q.queue)[:10]):
            description += f"**{i+1}.** {item['title'][:50]}...\n"
            options.append(discord.SelectOption(label=f"{i+1}. {item['title'][:25]}", value=str(i), emoji="🎵"))
        
        emb.description = description
        select = discord.ui.Select(placeholder="🚀 Pilih lagu untuk dilompati...", options=options)

        async def select_callback(inter: discord.Interaction):
            for option in select.options:
                if option.value == select.values[0]: option.emoji = "✅"
            await inter.response.edit_message(view=view_select)
            idx = int(select.values[0])
            chosen = q.queue[idx]
            judul_lama = "Tidak diketahui"
            if q.last_dashboard and q.last_dashboard.embeds:
                try: judul_lama = q.last_dashboard.embeds[0].description.split('[')[1].split(']')[0]
                except: pass
            del q.queue[idx]
            q.queue.appendleft(chosen)
            embed_rapi = buat_embed_skip(inter.user, judul_lama, f"⏭️ **Selanjutnya:** {chosen['title']}")
            skip_msg = await inter.followup.send(embed=embed_rapi)
            if inter.guild.voice_client: inter.guild.voice_client.stop()
            await asyncio.sleep(15)
            try: await skip_msg.delete()
            except: pass

        select.callback = select_callback
        view_select = discord.ui.View(timeout=60); view_select.add_item(select)
        if interaction.response.is_done(): q.last_queue_msg = await interaction.followup.send(embed=emb, view=view_select)
        else: await interaction.response.send_message(embed=emb, view=view_select); q.last_queue_msg = await interaction.original_response()

    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        if vc: vc.stop()

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(interaction.guild_id)
        q.queue.clear()
        if interaction.guild.voice_client: await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("⏹️ Musik dihentikan.", delete_after=5)

# --- 8. AUDIO ENGINE (OPTIMIZED) ---
async def start_stream(interaction, url):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if not vc: return
    try:
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        if 'entries' in data: data = data['entries'][0]
        # executable="ffmpeg" krusial untuk kestabilan hosting
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(data['url'], executable="ffmpeg", **FFMPEG_OPTIONS), volume=q.volume)
        def after_playing(error):
            if error: print(f"Player error: {error}")
            asyncio.run_coroutine_threadsafe(next_logic(interaction), bot.loop)
        vc.play(source, after=after_playing)
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
        emb = discord.Embed(title="🎶 Sedang Diputar", description=f"**[{data['title']}]({data.get('webpage_url', url)})**", color=0x2ecc71)
        emb.add_field(name="⏱️ Durasi", value=f"`{str(datetime.timedelta(seconds=data.get('duration', 0)))}`", inline=True)
        emb.add_field(name="🔊 Volume", value=f"`{int(q.volume * 100)}%`", inline=True)
        emb.set_thumbnail(url=data.get('thumbnail'))
        emb.set_footer(text=f"Request oleh: {interaction.user.display_name} • Angelss Project v17", icon_url=interaction.user.display_avatar.url)
        q.last_dashboard = await interaction.channel.send(embed=emb, view=MusicDashboard(interaction.guild_id))
    except Exception as e:
        print(f"❌ Error: {e}")
        await next_logic(interaction)

async def next_logic(interaction):
    q = get_queue(interaction.guild_id)
    if q.queue:
        await start_stream(interaction, q.queue.popleft()['url'])
    else:
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
        await interaction.channel.send("✨ Antrean Selesai.", delete_after=10)

async def play_music(interaction, url):
    q = get_queue(interaction.guild_id)
    if not interaction.guild.voice_client:
        if interaction.user.voice: await interaction.user.voice.channel.connect()
        else: return await interaction.channel.send("❌ Masuk VC dulu!")
    vc = interaction.guild.voice_client
    if vc.is_playing() or vc.is_paused():
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        q.queue.append({'title': data['title'], 'url': url})
        emb_q = discord.Embed(title="📥 Antrean Ditambahkan", description=f"✨ **[{data['title']}]({url})**", color=0x3498db)
        await interaction.followup.send(embed=emb_q, ephemeral=True)
    else:
        await start_stream(interaction, url)

# --- 9. SLASH COMMANDS (FULL SINKRON) ---
@bot.tree.command(name="play", description="Putar musik")
async def play(interaction: discord.Interaction, cari: str):
    await interaction.response.defer()
    q = get_queue(interaction.guild_id)
    if "http" in cari: await play_music(interaction, cari)
    else:
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch1:{cari}", download=False))
        await play_music(interaction, data['entries'][0]['webpage_url'])
    await interaction.followup.send("✅ Diproses!", ephemeral=True)

@bot.tree.command(name="stop", description="Mematikan musik dan keluar VC")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    if vc:
        num = len(q.queue); q.queue.clear(); await vc.disconnect()
        emb = discord.Embed(title="🛑 COMMAND STOP EXECUTED", description=f"✨ **{interaction.user.mention}** menghentikan musik.\n🧹 **Pembersihan:** `{num}` lagu dibersihkan.", color=0x2f3136)
        emb.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        await interaction.response.send_message(embed=emb, delete_after=20)
    else: await interaction.response.send_message("❌ Bot tidak di VC.", ephemeral=True)

@bot.tree.command(name="pause", description="Jeda musik")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
        interaction.guild.voice_client.pause(); await interaction.response.send_message("⏸️ Musik dijeda.")
    else: await interaction.response.send_message("❌ Gagal menjeda.", ephemeral=True)

@bot.tree.command(name="resume", description="Lanjut musik")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused():
        interaction.guild.voice_client.resume(); await interaction.response.send_message("▶️ Musik dilanjutkan.")
    else: await interaction.response.send_message("❌ Gagal melanjutkan.", ephemeral=True)

@bot.tree.command(name="skip", description="Lewati lagu")
async def skip_cmd(interaction: discord.Interaction):
    await interaction.response.defer()
    vc = interaction.guild.voice_client
    if vc: vc.stop(); await interaction.followup.send("⏭️ Skip berhasil!")
    else: await interaction.followup.send("❌ Gagal skip.", ephemeral=True)

# Command - /HELP
@bot.tree.command(name="help", description="Lihat Panduan & Info Developer")
async def help_cmd(interaction: discord.Interaction):
    dev_id = 590774565115002880
    
    emb_guide = discord.Embed(title="💿 Panduan Sistem Angelss Music", color=0x3498db)
    if bot.user.avatar: emb_guide.set_thumbnail(url=bot.user.avatar.url)
    
    emb_guide.description = (
        "╭🎧 **KONTROL MUSIK**\n"
        "┃\n" 
        "┕ 📀 `/play`   - Putar musik (Judul/Link)\n"
        "┕ ⏸️ `/pause`  - Jeda lagu sementara\n"
        "┕ ▶️ `/resume` - Lanjut memutar lagu\n"
        "┕ ⏭️ `/skip`   - Lewati lagu sekarang\n"
        "┕ ⏹️ `/stop`   - Stop & Hapus antrean\n"
        "┕ 📑 `/queue`  - Cek daftar antrean lagu\n\n"
        "╭🎚️ **SISTEM & KONEKSI**\n"
        "┃\n" 
        "┕ 🎚️ `/volume`    - Atur suara (0-100%)\n"
        "┕ 🎙️ `/masuk_vc`  - Panggil bot ke Voice\n"
        "┕ 👋 `/keluar_vc` - Usir bot dari Voice\n\n"
        "╭✨ **DASHBOARD PLAYER (TOMBOL)**\n"
        "┃\n" 
        "┕ ⏯️ **Smart Pause** : Tombol Jeda/Lanjut otomatis\n"
        "┕ 🎛️ **Audio Mixer** : Tombol pengatur volume instan\n"
        "┕ 📜 **Live Queue** : Pilih & lompat antrean via menu\n"
        "┕ ⚡ **Insta Skip** : Lewati lagu tanpa mengetik"
    )

    emb_dev = discord.Embed(title="👨‍💻 Developer Profile", color=0x9b59b6)
    emb_dev.description = (
        f"**Developer :** ikiii\n"
        f"**User ID :** `{dev_id}`\n"
        f"**Status :** Active - IT - Engineering\n"
        f"**Contact :** <@{dev_id}>\n\n"
        f"**Kata - kata :**\n"
        f"Bot ini dibuat oleh seorang yang bernama **ikiii** yang bijaksana, dan yang melakukan segala hal apapun diawali dengan berdo'a 🤲🏻, amiin."
    )
    
    emb_dev.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif")
    emb_dev.set_footer(text="Projects Bot • Music Ikiii hehehe ....", icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embeds=[emb_guide, emb_dev])
    
    
# --- 10. EVENTS ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} - Sistem Sinkron Aktif!")

bot.run(TOKEN)
