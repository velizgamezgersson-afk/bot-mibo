import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mbayuda(self, ctx):
        """Muestra este mensaje de ayuda."""
        
        embed = discord.Embed(
            title="Panel de Ayuda del Bot Mibo",
            description="¡Hola! Soy Mibo. Aquí están todos los comandos que puedes usar:",
            color=discord.Color.green()
        )

        # Categoría Música
        embed.add_field(
            name="🎵 Música (!mb)",
            value="`!mbplay <búsqueda>` - Busca en SoundCloud y muestra 5 opciones.\n"
                  "`!mbskip` - Salta la canción actual.\n"
                  "`!mbstop` - Detiene la música, vacía la cola y me voy.\n"
                  "`!mbcola` - Muestra las canciones en espera.",
            inline=False 
        )

        # Categoría Memes
        embed.add_field(
            name="😂 Memes (!mb)",
            value="`!mbmeme` - Publica un meme aleatorio en español.",
            inline=False
        )

        # Categoría Social
        embed.add_field(
            name="🎲 Social (!mb)",
            
            # --- INICIO DE LA CORRECCIÓN ---
            # Actualizamos la ayuda de !mbencuesta
            value="`!mbencuesta \"Pregunta\" \"Op1\" \"Op2\"...` - Crea una encuesta (¡Usa comillas!).\n"
            # --- FIN DE LA CORRECCIÓN ---
            
                  "`!mbmoneda` - Lanza una moneda (Cara o Sello).\n"
                  "`!mbelegir <op1> <op2>...` - Elijo una opción por ti.\n"
                  "`!mbdado [caras]` - Lanza un dado (6 caras por defecto).",
            inline=False
        )
        
        embed.set_footer(text="¡Gracias por usar Mibo!")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Ayuda(bot))