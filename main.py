# =================================================================
# 💿 ANGELSS MUSIC PROJECT - PREMIUM EDITION [OCTAVIA HOSTING]
# =================================================================
# Developer : ikiii
# Status    : Active - IT - Engineering
# =================================================================

# --- 1. IMPORT LIBRARIES ---
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







# --- 2. INITIALIZATION & FFMPEG CHECK ---
load_dotenv()





# ---  Logika Jaga-Jaga FFmpeg (Sangat Penting di Hosting Generic)
#
if shutil.which("ffmpeg") is None:
    print("⚠️ FFmpeg tidak ditemukan di sistem, mengaktifkan static-ffmpeg...")
    try:
        static_ffmpeg.add_paths()
    except Exception as e:
        print(f"❌ Gagal memuat static-ffmpeg: {e}")
else:
    print("✅ FFmpeg terdeteksi di sistem.")




# --- 3. GLOBAL CONFIGURATION ---
TOKEN = os.getenv('DISCORD_TOKEN')
COOKIES_FILE = 'youtube_cookies.txt'



# Validasi Token agar tidak crash
if not TOKEN:
    print("❌ ERROR: DISCORD_TOKEN tidak ditemukan di Environment Variables!")
    sys.exit(1)
    
 
 
 
 
 
    
# --- 4. SETTINGS - FORMAT CONVERTER (YTDL) - EVOLVED ---
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'source_address': '0.0.0.0',
    'cookiefile': COOKIES_FILE if os.path.exists(COOKIES_FILE) else None,
    'cachedir': False,
    # --- TRIK PENYAMARAN ANDROID ---
    'postprocessor_args': ['-threads', '1'],
    'extract_flat': False,
    'http_chunk_size': 1048576,
}



# --- 5. SETTINGS - FORMAT AUDIO PLAYER (FFMPEG) - OPTIMIZED ---
#
FFMPEG_OPTIONS = {
    'before_options': (
        '-reconnect 1 '
        '-reconnect_streamed 1 '
        '-reconnect_delay_max 5 '
        '-nostdin'
    ),
    'options': (
        '-vn '
        # Filter compand untuk suara jernih (Anti-Mendelep)
        '-af "volume=1.0, compand=0.3|0.3:6:-90/-60|-60/-40|-40/-20|-20/0:6:0:-90:0.2, aresample=48000" '
        '-ac 2 '
        '-b:a 192k '
        '-f s16le' # Wajib ada agar VolumeTransformer tidak error
    )
}





# INISIALISASI YT-DLP
ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)










# --- 6. SETUP - BOT ---
#
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











# --- 7. NOTIFIKASI - BOT - ONLINE UPDATE--
#
@bot.event
async def on_ready():
    target_channel_id = 1456250414638043169 
    
    channel = bot.get_channel(target_channel_id)
    if channel:
        # --- FITUR PEMBERSIH ---
        try:
            async for message in channel.history(limit=10):
                if message.author == bot.user:
                    await message.delete()
        except Exception as e:
            print(f"Gagal menghapus pesan lama: {e}")

        # --- KIRIM PESAN BARU ---
        embed = discord.Embed(
            title="🚀 SYSTEM RELOADED & UPDATED - [OCTAVIA PREMIUM] ",
            description="**Bot telah online di hosting premium!**\nLayanan audio Angelss kini berjalan dengan performa maksimal.",
            color=0x2ecc71 
        )
        
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        
        # --- BAGIAN YANG DIUBAH (LEBIH SESUAI SPEK BARU) ---
        embed.add_field(name="🛰️ Server Cluster", value="`Jakarta-Premium-ID`", inline=True)
        embed.add_field(name="⚡ Resources", value="`2vCPU / 2GB RAM`", inline=True)
        embed.add_field(name="📡 Status", value="`High Performance`", inline=True)
        
        # Field Tambahan untuk Latency
        embed.add_field(name="🚀 Connection", value=f"`{round(bot.latency * 1000)}ms Latency`", inline=False)
        embed.add_field(name="💡 Guide", value="Ketik `/help` untuk panduan", inline=False)
        
        # Waktu update 
        waktu_sekarang = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')
        embed.add_field(name="📅 Terakhir Diupdate", value=f"`{waktu_sekarang} WIB`", inline=False)

        embed.set_footer(
            text="System Announcement Online • ikiii angels Project Premium", 
            icon_url=bot.user.avatar.url if bot.user.avatar else None
        )
        
        embed.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif") 
        
        await channel.send(embed=embed)
    
    print(f"✅ Logged in as {bot.user} - Notifikasi Premium Terkirim!")









# --- 8.  QUEUE SYSTEM (DENGAN MEMORY CHANNEL) ---
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
        self.last_queue_msg = None  # Tambahkan ini untuk tracking pesan /queue
        self.text_channel_id = None


def get_queue(guild_id):
    if guild_id not in queues:
        queues[guild_id] = MusicQueue()
    return queues[guild_id]









# --- 9. AUTO-DISCONNECT (FIX TARGET CHANNEL) ---
#
@bot.event
async def on_voice_state_update(member, before, after):
    # Logika: Jika ada user keluar dan bot sendirian di VC
    if not member.bot and before.channel is not None:
        vc = member.guild.voice_client
        if vc and vc.channel.id == before.channel.id and len(before.channel.members) == 1:
            
            q = get_queue(member.guild.id)
            msg_chan = None

            # PRIORITAS CHANNEL (Mencegah Pesan Nyasar):
            # 1. Gunakan channel dashboard terakhir
            if q.last_dashboard:
                msg_chan = q.last_dashboard.channel
            # 2. Jika dashboard tidak ada, gunakan channel tempat /play terakhir
            elif q.text_channel_id:
                msg_chan = bot.get_channel(q.text_channel_id)
            # 3. Cadangan terakhir: Cari channel teks di kategori yang sama
            elif before.channel.category:
                for channel in before.channel.category.text_channels:
                    if channel.permissions_for(member.guild.me).send_messages:
                        msg_chan = channel
                        break

            if msg_chan:
                # Kirim peringatan 30 detik
                peringatan = await msg_chan.send(
                    f"⚠️ **Informasi:** Tidak ada pengguna di Voice Channel. Bot akan otomatis keluar dalam **30 detik**.", 
                    delete_after=30
                )
                
                await asyncio.sleep(30)
                
                # Cek kondisi setelah 30 detik
                vc_sekarang = member.guild.voice_client
                if vc_sekarang and vc_sekarang.channel:
                    # Jika ada orang masuk lagi (pembatalan)
                    if len(vc_sekarang.channel.members) > 1:
                        try: await peringatan.delete()
                        except: pass
                        await msg_chan.send("✅ **Informasi:** Ada user yang masuk, bot akan membatalkan keluar otomatis. ✨", delete_after=15)
                    
                    # Jika masih kosong, baru disconnect
                    else:
                        q.queue.clear()
                        q.last_dashboard = None
                        await vc_sekarang.disconnect()
                        await msg_chan.send("👋 **Informasi:** Bot telah keluar karena tidak ada aktivitas di Voice Channel.", delete_after=10)











# --- 	10. SYSTEM SEARCH ENGINE PILIHAN	---
#
class SearchControlView(discord.ui.View):
    def __init__(self, entries, user):
        super().__init__(timeout=None) 
        self.entries = entries
        self.user = user
        self.add_select_menu()

    def add_select_menu(self):
        self.clear_items()
        options = []
        for i, entry in enumerate(self.entries):
            title = entry.get('title', 'Judul tidak diketahui')[:50]
            url = entry.get('url') or entry.get('webpage_url')
            options.append(discord.SelectOption(
                label=f"Pilih Nomor {i+1}", 
                value=url, 
                description=title,
                emoji="🎵"
            ))
            
        select = discord.ui.Select(placeholder="🎯 Pilih lagu untuk ditambahkan...", options=options)
        
        async def callback(interaction: discord.Interaction):
            # Permission: Hanya pencari yang bisa milih
            if interaction.user != self.user:
                return await interaction.response.send_message(
                    f"⚠️ **Ups!** Hanya {self.user.mention} yang bisa memilih lagu dari hasil ini.", 
                    ephemeral=True
                )
            
            await interaction.response.defer()
            await play_music(interaction, select.values[0])
            
            # Status sementara
            status_embed = discord.Embed(
                title="✅ Berhasil Ditambahkan!",
                description="Lagu sedang diproses ke antrean...",
                color=0x2ecc71
            )
            await interaction.edit_original_response(embed=status_embed, view=None)
            await asyncio.sleep(2)
            await interaction.edit_original_response(embed=self.create_embed(), view=self)

        select.callback = callback
        self.add_item(select)

        # Tombol Tutup
        btn_close = discord.ui.Button(label="Tutup Menu", style=discord.ButtonStyle.danger, emoji="🗑️")
        async def close_callback(interaction: discord.Interaction):
            if interaction.user == self.user:
                await interaction.message.delete()
            else:
                await interaction.response.send_message("❌ Kamu tidak berhak menutup ini!", ephemeral=True)
        btn_close.callback = close_callback
        self.add_item(btn_close)

    def create_embed(self):
        description = "📺 **YouTube Search Engine**\n*(Hanya pembuat request yang dapat memilih)*\n\n"
        for i, entry in enumerate(self.entries):
            description += f"✨ `{i+1}.` {entry.get('title', 'Unknown Title')[:60]}...\n"
        embed = discord.Embed(title="🔍 Hasil Pencarian Musik", description=description, color=0xf1c40f)
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif") 
        embed.set_footer(text=f"Request oleh: {self.user.display_name} • Menu Aktif", icon_url=self.user.display_avatar.url)
        return embed











# --- 	11. UI CLASS:	 DASHBOARD & VOLUME	---
#
# ---  ---
class VolumeControlView(discord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=60)
        self.guild_id = guild_id

    def create_embed(self):
        q = get_queue(self.guild_id)
        vol_percent = int(q.volume * 100)
        embed = discord.Embed(title="🎚️ Pengaturan Audio", color=0x3498db)
        # Bar volume (1 kotak = 10%, total 10 kotak untuk 100%)
        bar_length = 10
        filled = int(vol_percent / 10)
        bar = "▰" * filled + "▱" * (bar_length - filled)
        embed.description = f"Volume Saat Ini: **{vol_percent}%**\n`{bar}`"
        embed.set_footer(text="Batas aman standar: 100%")
        return embed

    @discord.ui.button(label="-10%", style=discord.ButtonStyle.danger, emoji="🔉")
    async def down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        # Kurangi 0.1 (10%), minimal tetap 0.0 (0%)
        q.volume = max(0.0, q.volume - 0.1)
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = q.volume
        await interaction.edit_original_response(embed=self.create_embed())

    @discord.ui.button(label="+10%", style=discord.ButtonStyle.success, emoji="🔊")
    async def up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer() 
        q = get_queue(self.guild_id)
        # Tambah 0.1 (10%), maksimal tetap 1.0 (100%) sesuai standar internasional
        q.volume = min(1.0, q.volume + 0.1) 
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = q.volume
        await interaction.edit_original_response(embed=self.create_embed())










# --- 	12. FUNCTION:	 EMBED - SKIP	---
#
# ---  ---
def buat_embed_skip(user, lagu_dilewati, info_selanjutnya):
    """Fungsi pembantu agar tampilan skip/lompat selalu cantik & seragam ✨"""
    embed = discord.Embed(
        title="⏭️ NEXT MUSIC SKIP",
        description=(
            f"✨ **{user.mention}** telah melompat ke lagu berikutnya!\n\n"
            f"🗑️ **Dilewati:** `{lagu_dilewati}`\n"
            f"📥 **Status Antrean:** {info_selanjutnya}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=0xe67e22 # Warna Orange Sunset yang elegan
    )
    # Menambahkan icon user yang melakukan skip di footer
    embed.set_footer(text="System Skip Otomatis • Angelss Project v17", icon_url=user.display_avatar.url)
    return embed










# --- 	13. UI CLASS:	 DASHBOARD & AUDIO - PLAYER	---
#
# ---  ---
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
            button.emoji = "▶️"
            button.label = "Lanjut"
            button.style = discord.ButtonStyle.success 
        else:
            vc.resume()
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
        # Ini khusus untuk klik tombol di dashboard
        await self.tampilkan_antrean(interaction)

    async def tampilkan_antrean(self, interaction: discord.Interaction):
        q = get_queue(self.guild_id)
        
        # 1. Refresh System: Hapus pesan antrean lama
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
            options.append(discord.SelectOption(
                label=f"{i+1}. {item['title'][:25]}", 
                value=str(i),
                emoji="🎵"
            ))
        
        emb.description = description
        select = discord.ui.Select(placeholder="🚀 Pilih lagu untuk dilompati...", options=options)

        async def select_callback(inter: discord.Interaction):
            # Beri centang pada pilihan
            for option in select.options:
                if option.value == select.values[0]:
                    option.emoji = "✅"
            
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

            if inter.guild.voice_client:
                inter.guild.voice_client.stop()
            
            await asyncio.sleep(15)
            try: await skip_msg.delete()
            except: pass

        select.callback = select_callback
        view_select = discord.ui.View(timeout=60)
        view_select.add_item(select)
        
        # Kirim pesan baru
        if interaction.response.is_done():
            q.last_queue_msg = await interaction.followup.send(embed=emb, view=view_select)
        else:
            await interaction.response.send_message(embed=emb, view=view_select)
            q.last_queue_msg = await interaction.original_response()


    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def sk(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)
        q = get_queue(self.guild_id)
        vc = interaction.guild.voice_client
        
        if not vc or not (vc.is_playing() or vc.is_paused()):
            return await interaction.followup.send("❌ **Informasi:** Tidak ada lagu untuk di-skip.", ephemeral=True)

        current_title = "Tidak diketahui"
        if q.last_dashboard and q.last_dashboard.embeds:
            try:
                full_desc = q.last_dashboard.embeds[0].description
                if "[" in full_desc and "]" in full_desc:
                    current_title = full_desc.split('[')[1].split(']')[0]
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

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def st(self, interaction: discord.Interaction, button: discord.ui.Button):
        q = get_queue(interaction.guild_id)
        vc = interaction.guild.voice_client
        jumlah_antrean = len(q.queue)
        
        q.queue.clear()
        if vc:
            await vc.disconnect()
            
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










# --- 	14. CORE LOGIC:	 SYSTEM - DURASI AUTO 00:00	---
#
# ---  ---

# - Next - Logic	:
#
async def next_logic(interaction):
    """Logika pintar untuk memutar lagu berikutnya atau membersihkan antrean"""
    q = get_queue(interaction.guild_id)
    
    if q.queue:
        next_song = q.queue.popleft()
        await start_stream(interaction, next_song['url'])
    else:
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            q.last_dashboard = None
        
        emb_finish = discord.Embed(
            title="✨ Antrean Selesai",
            description="Semua lagu telah diputar. Bot standby menunggu perintah baru. 💤",
            color=0x34495e
        )
        await interaction.channel.send(embed=emb_finish, delete_after=15)


# - Start - Logic	:
#
async def start_stream(interaction, url):
    q = get_queue(interaction.guild_id)
    q.text_channel_id = interaction.channel.id
    
    vc = interaction.guild.voice_client
    if not vc: return
    
    try:
        if vc.is_playing() or vc.is_paused():
            vc.stop()
        
        await asyncio.sleep(0.5)

        # Proses ambil data video tanpa download
        data = await asyncio.get_event_loop().run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        
        if 'entries' in data:
            data = data['entries'][0]

        # Inisialisasi Audio Source (PCMAudio agar support VolumeTransformer)
        audio_source = discord.FFmpegPCMAudio(data['url'], **FFMPEG_OPTIONS)
        source = discord.PCMVolumeTransformer(audio_source, volume=q.volume)
        
        def after_playing(error):
            if error: print(f"Player error: {error}")
            asyncio.run_coroutine_threadsafe(next_logic(interaction), bot.loop)
            
        vc.play(source, after=after_playing)
        
        # Hapus dashboard lama jika ada
        if q.last_dashboard:
            try: await q.last_dashboard.delete()
            except: pass
            
        # Kirim Dashboard Baru
        emb = discord.Embed(
            title="🎶 Sedang Diputar", 
            description=f"**[{data['title']}]({data.get('webpage_url', url)})**", 
            color=0x2ecc71 
        )
        
        duration = str(datetime.timedelta(seconds=data.get('duration', 0)))
        emb.add_field(name="⏱️ Durasi", value=f"`{duration}`", inline=True)
        emb.add_field(name="🔊 Volume", value=f"`{int(q.volume * 100)}%`", inline=True)
        
        emb.set_thumbnail(url=data.get('thumbnail'))
        emb.set_footer(
            text=f"Request oleh: {interaction.user.display_name} • Angelss Project v17", 
            icon_url=interaction.user.display_avatar.url
        )
        
        # Tampilkan dashboard dengan view MusicDashboard
        q.last_dashboard = await interaction.channel.send(embed=emb, view=MusicDashboard(interaction.guild_id))
        
    except Exception as e:
        print(f"CRITICAL ERROR start_stream: {e}")
        emb_error = discord.Embed(
            title="⚠️ Gagal Memutar Lagu",
            description="Terjadi kesalahan pada link audio atau cookies. Melewati ke antrean berikutnya...",
            color=0xe74c3c
        )
        await interaction.channel.send(embed=emb_error, delete_after=10)
        asyncio.run_coroutine_threadsafe(next_logic(interaction), bot.loop)


 
# - Play - Logic	:
#
async def play_music(interaction, url):
    """Fungsi kontrol untuk play langsung atau masuk queue"""
    q = get_queue(interaction.guild_id)
    # Update memory channel setiap kali /play digunakan
    q.text_channel_id = interaction.channel.id
    
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
        else:
            return await interaction.channel.send("❌ **Gagal:** Kamu harus masuk ke Voice Channel terlebih dahulu!")
    
    vc = interaction.guild.voice_client
    
    if vc.is_playing() or vc.is_paused():
        data = await asyncio.get_event_loop().run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        q.queue.append({'title': data['title'], 'url': url})
        
        emb_q = discord.Embed(
            title="📥 Antrean Ditambahkan",
            description=f"✨ **[{data['title']}]({url})**\nBerhasil masuk ke dalam daftar putar.",
            color=0x3498db
        )
        emb_q.set_footer(text=f"Posisi Antrean: {len(q.queue)}", icon_url=interaction.user.display_avatar.url)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=emb_q, ephemeral=True)
        else:
            await interaction.response.send_message(embed=emb_q, ephemeral=True, delete_after=20)
    else:
        msg = "🚀 **Memproses lagu ke player...**"
        if not interaction.response.is_done():
            await interaction.response.send_message(msg, ephemeral=True, delete_after=5)
        else:
            await interaction.followup.send(msg, ephemeral=True)
            
        await start_stream(interaction, url)






# --- 	15. TREE COMMAND:	 [ SYSTEM / COMMAND ]	---
#
# ---  ---


#	----	Command - /PLAY
#
@bot.tree.command(name="play", description="Putar musik")
async def play(interaction: discord.Interaction, cari: str):
    await interaction.response.defer() # Biar tidak interaction failed
    q = get_queue(interaction.guild_id)

    # --- FITUR AUTO-CLEAN SEARCH LAMA ---
    if hasattr(q, 'last_search_msg') and q.last_search_msg:
        try: await q.last_search_msg.delete()
        except: pass

    if "http" in cari: 
        await play_music(interaction, cari)
        await interaction.followup.send("✅ Link berhasil diproses!", ephemeral=True)
    else:
        search_opts = {'extract_flat': True, 'quiet': True}
        data = await asyncio.get_event_loop().run_in_executor(
            None, lambda: yt_dlp.YoutubeDL(search_opts).extract_info(f"ytsearch5:{cari}", download=False)
        )
        
        view = SearchControlView(data['entries'], interaction.user)
        # Simpan pesan pencarian ke dalam queue agar bisa dihapus nanti
        q.last_search_msg = await interaction.followup.send(embed=view.create_embed(), view=view)



#	----	Command - /STOP
#
@bot.tree.command(name="stop", description="Mematikan musik dan mengeluarkan bot dari voice channel")
async def stop_cmd(interaction: discord.Interaction):
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    # Ambil data jumlah antrean sebelum dihapus
    jumlah_antrean = len(q.queue)
    
    if vc:
        # Logika pembersihan
        q.queue.clear()
        await vc.disconnect()
        
        # Buat Embed yang sinkron dengan tombol dashboard
        embed = discord.Embed(
            title="🛑 COMMAND STOP EXECUTED",
            description=(
                f"✨ **{interaction.user.mention}** telah menghentikan seluruh sesi musik.\n\n"
                f"🧹 **Pembersihan:** `{jumlah_antrean}` lagu di antrean telah dibersihkan.\n"
                f"📡 **Status:** Koneksi Voice Channel diputuskan.\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0x2f3136 # Warna gelap profesional
        )
        embed.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif")
        embed.set_footer(text="Sesi berakhir via Slash Command", icon_url=bot.user.avatar.url)

        # Kirim ke publik agar semua tahu siapa yang mematikan musik
        await interaction.response.send_message(embed=embed, delete_after=20)
    else:
        # Jika bot tidak ada di voice channel
        await interaction.response.send_message("❌ **Gagal:** Bot tidak sedang berada di Voice Channel.", ephemeral=True)



#	----	Command - /VOLUME
#
@bot.tree.command(name="volume", description="Atur Volume (0-100%)")
@app_commands.describe(persen="Masukkan angka antara 0 sampai 100")
async def volume(interaction: discord.Interaction, persen: int):
    q = get_queue(interaction.guild_id)
    
    # 1. Batasi input agar sesuai standar internasional (Max 100)
    if 0 <= persen <= 100:
        # Ubah ke angka desimal (misal 50 jadi 0.5)
        q.volume = persen / 100
        
        # 2. Terapkan langsung ke audio yang sedang berjalan
        if interaction.guild.voice_client and interaction.guild.voice_client.source:
            interaction.guild.voice_client.source.volume = q.volume
            
        # 3. Buat visual bar agar keren seperti di dashboard
        bar_length = 10
        filled = int(persen / 10)
        bar = "▰" * filled + "▱" * (bar_length - filled)
        
        embed = discord.Embed(
            title="🔊 Volume Updated",
            description=f"Volume telah diatur ke **{persen}%**\n`{bar}`",
            color=0x3498db
        )
        await interaction.response.send_message(embed=embed, delete_after=15)
    else:
        # Pesan jika user input di luar 0-100
        await interaction.response.send_message(
            "❌ **Gagal:** Gunakan angka antara **0 sampai 100** saja untuk menjaga kualitas audio tetap jernih.", 
            ephemeral=True
        )




#	----	Command - /PAUSE
#
@bot.tree.command(name="pause", description="Jeda musik")
async def pause(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_playing(): interaction.guild.voice_client.pause(); await interaction.response.send_message("⏸️ Musik dijeda.")
    else: await interaction.response.send_message("❌ Tidak ada lagu yang diputar.", ephemeral=True)



#	----	Command - /RESUME
#
@bot.tree.command(name="resume", description="Lanjut musik")
async def resume(interaction: discord.Interaction):
    if interaction.guild.voice_client and interaction.guild.voice_client.is_paused(): interaction.guild.voice_client.resume(); await interaction.response.send_message("▶️ Musik dilanjutkan.")
    else: await interaction.response.send_message("❌ Tidak ada lagu yang dijeda.", ephemeral=True)



#	----	Command - /SKIP
#
@bot.tree.command(name="skip", description="Lewati lagu yang sedang berjalan")
async def skip_cmd(interaction: discord.Interaction):
    # 1. Defer agar tidak "Interaction Failed"
    await interaction.response.defer(ephemeral=False)
    
    q = get_queue(interaction.guild_id)
    vc = interaction.guild.voice_client
    
    if vc and (vc.is_playing() or vc.is_paused()):
        # 2. Ambil Judul Lagu (Logika yang lebih aman)
        current_title = "Tidak diketahui"
        if q.last_dashboard and q.last_dashboard.embeds:
            try:
                full_desc = q.last_dashboard.embeds[0].description
                if "[" in full_desc and "]" in full_desc:
                    current_title = full_desc.split('[')[1].split(']')[0]
            except:
                pass

        # 3. Cek Antrean Berikutnya
        next_info = "Antrean kosong, bot akan standby. ✨"
        if q.queue:
            next_info = f"⏭️ **Selanjutnya:** {q.queue[0]['title']}"

        # 4. Buat Embed yang Elegan
        embed = discord.Embed(
            title="⏭️ COMMAND SKIP EXECUTED",
            description=(
                f"✨ **{interaction.user.mention}** meminta skip lagu!\n\n"
                f"🗑️ **Dilewati:** {current_title}\n"
                f"📥 **Status:** {next_info}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            color=0xe67e22 # Warna orange keren
        )
        embed.set_footer(text="System Skip Otomatis", icon_url=bot.user.avatar.url if bot.user.avatar else None)

        # 5. Eksekusi
        vc.stop()
        
        # Kirim menggunakan followup karena sudah di-defer
        await interaction.followup.send(embed=embed)
        
        # Hapus pesan otomatis setelah 15 detik
        await asyncio.sleep(15)
        try:
            msg = await interaction.original_response()
            await msg.delete()
        except:
            pass
    else:
        # Jika tidak ada lagu, kirim pesan error (lewat followup karena sudah defer)
        await interaction.followup.send("❌ **Gagal:** Bot tidak sedang memutar musik.", ephemeral=True)




#	----	Command - /QUEUE
#
@bot.tree.command(name="queue", description="Lihat antrean dan pilih lagu")
async def queue_cmd(interaction: discord.Interaction):
    # Buat instance dashboard sementara untuk mengakses fungsinya
    view = MusicDashboard(interaction.guild_id)
    await view.tampilkan_antrean(interaction)





#	----	Command - /MASUK_VC	---	(VALIDASI + EMBED + AUTO DELETE 60s) ---
#
@bot.tree.command(name="masuk_vc", description="Panggil bot ke Voice Channel")
async def masuk(interaction: discord.Interaction):
    # 1. Cek apakah User ada di Voice Channel
    if not interaction.user.voice:
        emb_error = discord.Embed(
            title="🚫 Akses Ditolak",
            description=(
                "Kamu **belum masuk** ke Voice Channel!\n"
                "Mohon masuk ke voice channel terlebih dahulu agar aku bisa bergabung."
            ),
            color=0xe74c3c # Merah
        )
        emb_error.set_footer(text="Gagal bergabung")
        # content=... untuk Tag User, delete_after=60 untuk hapus otomatis
        return await interaction.response.send_message(content=interaction.user.mention, embed=emb_error, delete_after=60)

    # 2. Logika Masuk Voice
    vc = interaction.guild.voice_client
    target_channel = interaction.user.voice.channel

    if vc:
        if vc.channel.id == target_channel.id:
            return await interaction.response.send_message("⚠️ Aku sudah ada di sini bersamamu!", ephemeral=True)
        await vc.move_to(target_channel)
    else:
        await target_channel.connect()

    # 3. Embed Sukses
    emb_success = discord.Embed(
        title="📥 Berhasil Masuk!",
        description=f"Siap memutar musik di **{target_channel.name}** 🎵\nAyo putar lagu kesukaanmu!",
        color=0x2ecc71 # Hijau
    )
    emb_success.set_thumbnail(url="https://i.ibb.co.com/KppFQ6N6/Logo1.gif") # Opsional: Pakai logo botmu
    
    await interaction.response.send_message(content=interaction.user.mention, embed=emb_success, delete_after=60)





#	----	Command - /KELAUR_VC
#
@bot.tree.command(name="keluar_vc", description="Keluarkan bot dari Voice Channel")
async def keluar(interaction: discord.Interaction):
    # 1. Cek apakah User ada di Voice Channel (Sesuai request kamu)
    if not interaction.user.voice:
        emb_error = discord.Embed(
            title="🚫 Akses Ditolak",
            description=(
                "Kamu **harus berada di Voice Channel** untuk menggunakan perintah ini.\n"
                "Masuklah dulu, baru kamu bisa menyuruhku keluar."
            ),
            color=0xe74c3c
        )
        return await interaction.response.send_message(content=interaction.user.mention, embed=emb_error, delete_after=60)

    # 2. Logika Keluar
    vc = interaction.guild.voice_client
    if vc:
        # Bersihkan antrean agar bersih saat masuk lagi nanti
        q = get_queue(interaction.guild_id)
        q.queue.clear()
        
        await vc.disconnect()
        
        # 3. Embed Sukses Keluar
        emb_bye = discord.Embed(
            title="👋 Sampai Jumpa!",
            description="Aku telah keluar dari Voice Channel.\nTerima kasih sudah mendengarkan musik bersamaku! ✨",
            color=0xf1c40f # Kuning/Emas
        )
        emb_bye.set_footer(text="Disconnect success")
        
        await interaction.response.send_message(content=interaction.user.mention, embed=emb_bye, delete_after=60)
    else:
        # Jika bot memang tidak ada di voice
        await interaction.response.send_message("❌ Aku sedang tidak berada di dalam Voice Channel manapun.", ephemeral=True)




#	----	Command - /HELP
#
@bot.tree.command(name="help", description="Lihat Panduan & Info Developer")
async def help_cmd(interaction: discord.Interaction):
    dev_id = 590774565115002880
    
    # --- EMBED PANDUAN ---
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

    # --- EMBED DEVELOPER (TEXT SESUAI REQUEST) ---
    emb_dev = discord.Embed(title="👨‍💻 Developer Profile", color=0x9b59b6)
    emb_dev.description = (
        f"**Developer :** ikiii\n"
        f"**User ID :** `{dev_id}`\n"
        f"**Status :** Active - IT - Engineering\n"
        f"**Contact :** <@{dev_id}>\n\n"
        f"**Kata - kata :**\n"
        f"Bot ini dibuat oleh seorang yang bernama **ikiii** yang bijaksana, dan yang melakukan segala hal apapun diawali dengan berdo'a 🤲🏻, amiin."
    )
    
    # Banner & Footer
    emb_dev.set_image(url="https://i.getpantry.cloud/apf/help_banner.gif")
    emb_dev.set_footer(text="Projects Bot • Music Ikiii hehehe ....", icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embeds=[emb_guide, emb_dev])


bot.run(TOKEN)
