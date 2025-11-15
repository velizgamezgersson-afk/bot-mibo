import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from aiohttp import web # ¡Importante para el "truco" de Render!

# 1. Cargar el Token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# 2. Definir los "Intents" (Intenciones)
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.reactions = True

# 3. Crear la instancia del Bot
bot = commands.Bot(command_prefix='!', intents=intents)

# 4. Evento "On Ready" (Cuando el bot se conecta)
@bot.event
async def on_ready():
    print(f'¡Mibo está en línea como {bot.user}!')
    
    # Establecer el estado "Jugando a: !mbayuda"
    activity = discord.Game(name="!mbayuda", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

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

# 6. --- ¡EL "TRUCO" PARA RENDER 24/7 GRATIS! ---
async def web_server():
    """Crea una mini-web 'estoy vivo' para el plan gratuito de Render."""
    async def handle_request(request):
        return web.Response(text="¡Mibo está vivo!")

    app = web.Application()
    app.add_routes([web.get('/', handle_request)])
    
    port = int(os.environ.get("PORT", 10000))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    
    try:
        await site.start()
        print(f"--- Servidor web (para Render) iniciado en el puerto {port} ---")
    except Exception as e:
        print(f"--- Error al iniciar el servidor web de Render: {e} ---")

@bot.event
async def setup_hook():
    """Se ejecuta ANTES de que el bot inicie sesión."""
    
    # 1. Cargar todos los Cogs (módulos)
    print("Cargando cogs...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f' - Se cargó {filename}')
            except Exception as e:
                print(f' ! No se pudo cargar {filename}: {e}')
    
    # 2. Iniciar la mini-web (el "truco") en segundo plano
    bot.loop.create_task(web_server())

# --- FIN DEL "TRUCO" ---

# 7. Ejecutar el Bot
bot.run(TOKEN)