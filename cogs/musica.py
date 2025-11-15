import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os # ¡Importante para leer la nueva llave de API!

# ¡Importar la librería de Google API!
from googleapiclient.discovery import build

# --- Configuración de llaves y yt-dlp ---

# Cargar la llave de API de YouTube desde las variables de entorno
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
if not YOUTUBE_API_KEY:
    print("¡¡¡ERROR CRÍTICO: YOUTUBE_API_KEY no encontrada!!!")

# Crear el "servicio" de YouTube para buscar
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Opciones de yt-dlp (solo para extraer, no para buscar)
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'socket_timeout': 10,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

# Opciones de FFmpeg
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -loglevel quiet', 
}

# --- Clase de Música (Maneja la cola) ---
class MusicPlayer:
    def __init__(self, ctx):
        self.ctx = ctx
        self.bot = ctx.bot
        self.queue = []
        self.current_track = None
        self.voice_client = ctx.voice_client

    async def play_next(self):
        if not self.queue:
            self.current_track = None
            return 
        
        track_info = self.queue.pop(0)
        self.current_track = track_info
        
        loop = self.bot.loop or asyncio.get_event_loop()
        try:
            # Ahora yt-dlp solo extrae la URL, ¡esto no será bloqueado!
            data = await loop.run_in_executor(None, lambda: yt_dlp.YoutubeDL(YTDL_OPTIONS).extract_info(track_info['url'], download=False))
            source_url = data['url']
        except Exception as e:
            await self.ctx.send(f"Error al extraer audio: {e}")
            await self.play_next() 
            return
            
        source = discord.FFmpegPCMAudio(source_url, **FFMPEG_OPTIONS)
        self.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.check_queue))

    def check_queue(self):
        if not self.voice_client or not self.voice_client.is_connected():
            return
        asyncio.run_coroutine_threadsafe(self.play_next(), self.bot.loop)

    def add_to_queue(self, track_info):
        self.queue.append(track_info)

# --- Cog de Música ---

class Musica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {} 

    async def get_player(self, ctx: commands.Context) -> MusicPlayer:
        if not ctx.author.voice:
            await ctx.send("¡Debes estar en un canal de voz para usar este comando!")
            return None
        
        if ctx.guild.id in self.players:
            player = self.players[ctx.guild.id]
            if player.voice_client and player.voice_client.channel != ctx.author.voice.channel:
                await player.voice_client.move_to(ctx.author.voice.channel)
                player.ctx = ctx
            return player

        try:
            vc = await ctx.author.voice.channel.connect()
            self.players[ctx.guild.id] = MusicPlayer(ctx)
            self.players[ctx.guild.id].voice_client = vc
            return self.players[ctx.guild.id]
        except Exception as e:
            await ctx.send(f"No pude conectarme al canal de voz: {e}")
            return None

    # --- FUNCIÓN DE BÚSQUEDA (ACTUALIZADA) ---
    async def search_youtube(self, query: str):
        """Busca en YouTube usando la API oficial."""
        loop = self.bot.loop or asyncio.get_event_loop()
        
        def blocking_search():
            # Esta es la búsqueda oficial de Google/YouTube
            request = youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=5
            )
            return request.execute()

        try:
            # Ejecutamos la búsqueda en un hilo separado para no bloquear el bot
            response = await loop.run_in_executor(None, blocking_search)
            
            tracks = []
            for item in response.get('items', []):
                tracks.append({
                    'title': item['snippet']['title'],
                    'uploader': item['snippet']['channelTitle'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                })
            return tracks
            
        except Exception as e:
            print(f"Error al buscar con la API de YouTube: {e}")
            # Esto puede pasar si superas la cuota gratuita de 100 búsquedas
            if "quotaExceeded" in str(e):
                return "quota"
            return None

    @commands.command()
    async def mbplay(self, ctx: commands.Context, *, busqueda: str):
        """Busca en YouTube (con API), muestra 5 opciones y reproduce."""
        
        player = await self.get_player(ctx)
        if not player:
            return

        # --- ¡USA LA NUEVA FUNCIÓN DE BÚSQUEDA! ---
        tracks = await self.search_youtube(busqueda)
        
        if tracks == "quota":
            await ctx.send("¡Error! Se ha superado la cuota de búsqueda diaria de Mibo. Intenta de nuevo mañana.")
            return
        if not tracks:
            await ctx.send(f"No encontré ninguna canción en YouTube con '{busqueda}'.")
            return

        embed = discord.Embed(
            title="Resultados de YouTube",
            description="Reacciona con el número de la canción que quieres:",
            color=discord.Color.red()
        )
        
        emojis_reaccion = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        descripcion_embed = ""
        
        for i, track in enumerate(tracks):
            descripcion_embed += f"{emojis_reaccion[i]} **{track['title']}** (por {track.get('uploader', 'Desconocido')})\"n"
        
        embed.description = descripcion_embed
        
        msg = await ctx.send(embed=embed)
        for emoji in emojis_reaccion[:len(tracks)]:
            await msg.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in emojis_reaccion

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send("Selección cancelada (tiempo agotado).")
            return

        chosen_index = emojis_reaccion.index(str(reaction.emoji))
        chosen_track = tracks[chosen_index]
        
        # Guardamos la info (título y URL web)
        track_info = {'title': chosen_track['title'], 'url': chosen_track['url']}
        
        player.add_to_queue(track_info)
        
        await msg.clear_reactions()
        await msg.edit(
            content=f"✅ Añadido a la cola: **{track_info['title']}**",
            embed=None
        )
        
        if not player.voice_client.is_playing():
            await player.play_next()

    # (Los comandos mbskip, mbstop y mbcola no necesitan cambios)

    @commands.command()
    async def mbskip(self, ctx: commands.Context):
        if ctx.guild.id not in self.players:
            return await ctx.send("No estoy reproduciendo nada.")
            
        player = self.players[ctx.guild.id]
        if not player.voice_client.is_playing():
            return await ctx.send("No estoy reproduciendo nada.")
            
        player.voice_client.stop()
        await ctx.send("⏭️ Canción saltada.")

    @commands.command()
    async def mbstop(self, ctx: commands.Context):
        if ctx.guild.id not in self.players:
            return await ctx.send("No estoy conectado a un canal de voz.")

        player = self.players[ctx.guild.id]
        player.queue.clear()
        player.current_track = None
        await player.voice_client.disconnect()
        del self.players[ctx.guild.id]
        await ctx.send("⏹️ Música detenida. ¡Adiós!")

    @commands.command()
    async def mbcola(self, ctx: commands.Context):
        if ctx.guild.id not in self.players:
            return await ctx.send("La cola está vacía.")
            
        player = self.players[ctx.guild.id]
        
        embed = discord.Embed(title="Cola de Reproducción", color=discord.Color.blue())
        
        if player.current_track:
            embed.add_field(name="Reproduciendo Ahora", value=f"**{player.current_track['title']}**", inline=False)
        else:
            embed.add_field(name="Reproduciendo Ahora", value="Nada", inline=False)

        queue_text = ""
        if not player.queue:
            queue_text = "No hay más canciones en la cola."
        else:
            for i, track in enumerate(player.queue):
                queue_text += f"{i+1}. **{track['title']}**\n"
        
        embed.add_field(name="En Cola", value=queue_text, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Musica(bot))