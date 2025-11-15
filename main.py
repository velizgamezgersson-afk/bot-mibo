import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# 1. Cargar el Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Definir los "Intents" (Intenciones)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True # ¡Sigue siendo crucial para música!
intents.reactions = True

# 3. Crear la instancia del Bot
bot = commands.Bot(command_prefix='!', intents=intents)

# 4. Evento "On Ready" (Cuando el bot se conecta)
@bot.event
async def on_ready():
    print(f'¡Mibo está en línea como {bot.user}!')
    
    activity = discord.Game(name="!mbayuda", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

    print("Cargando cogs...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f' - Se cargó {filename}')
            except Exception as e:
                print(f' ! No se pudo cargar {filename}: {e}')

# 5. Comandos para Cargar/Descargar Cogs (para el dueño)
@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        await bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Se cargó el cog: {extension}')
    except Exception as e:
        await ctx.send(f'Error al cargar {extension}: {e}')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Se descargó el cog: {extension}')
    except Exception as e:
        await ctx.send(f'Error al descargar {extension}: {e}')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.unload_extension(f'cogs.{extension}')
        await bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Se recargó el cog: {extension}')
    except Exception as e:
        await ctx.send(f'Error al recargar {extension}: {e}')


# 6. --- ¡SECCIÓN DE MÚSICA ELIMINADA! ---
# Ya no necesitamos el "setup_hook" ni "NodePool" de Wavelink.
# El bot ahora es mucho más simple.


# 7. Ejecutar el Bot
bot.run(TOKEN)