import discord
from discord.ext import commands
import aiohttp

class Memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mbmeme(self, ctx):
        """Publica un meme aleatorio en español."""
        
        # --- INICIO DE LA CORRECCIÓN ---
        # Volvemos a pedir un sub en español, pero uno que no esté roto.
        url = "https://meme-api.com/gimme/dankgentina" 
        # (Si este no te gusta, podemos probar con "yo_elvr")
        # --- FIN DE LA CORRECCIÓN ---

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    
                    if resp.status != 200:
                        await ctx.send(f"La API de memes falló 😥. (Código de error: {resp.status})")
                        return
                    
                    data = await resp.json()
                    
                    if data.get('nsfw', False):
                        await ctx.send("¡El meme aleatorio era NSFW! Intenta de nuevo.")
                        return

                    meme_url = data.get('url')
                    if not meme_url:
                        await ctx.send("La API no me devolvió una imagen. Intenta de nuevo.")
                        return

                    if not meme_url.endswith(('.png', '.jpg', '.gif')):
                        await ctx.send("El meme era un formato raro (no imagen). Intenta de nuevo.")
                        return

                    embed = discord.Embed(
                        title=data['title'],
                        color=discord.Color.orange()
                    )
                    embed.set_image(url=meme_url)
                    embed.set_footer(text=f"Publicado en r/{data['subreddit']} por u/{data['author']}")
                    
                    await ctx.send(embed=embed)
                
        except Exception as e:
            await ctx.send(f"Ocurrió un error al buscar el meme: {e}")


async def setup(bot):
    await bot.add_cog(Memes(bot))