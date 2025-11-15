import discord
from discord.ext import commands
import random

class Social(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mbmoneda(self, ctx):
        """Lanza una moneda al aire."""
        resultado = random.choice(['Cara', 'Sello'])
        await ctx.send(f"🪙 ¡Ha salido **{resultado}**!")

    @commands.command()
    async def mbelegir(self, ctx, *opciones):
        """Elige una opción al azar entre varias."""
        if not opciones:
            await ctx.send("Debes darme opciones para elegir. Ejemplo: `!mbelegir pizza hamburguesa`")
            return
        
        eleccion = random.choice(opciones)
        await ctx.send(f"Entre {', '.join(opciones)}, elijo... 🤔 ¡**{eleccion}**!")

    @commands.command()
    async def mbdado(self, ctx, caras: int = 6):
        """Tira un dado. Por defecto 6 caras."""
        if caras <= 1:
            await ctx.send("Un dado debe tener al menos 2 caras.")
            return
        
        resultado = random.randint(1, caras)
        await ctx.send(f"🎲 Has tirado un dado de {caras} caras y ha salido: **{resultado}**")

    # --- INICIO DE LA CORRECCIÓN DE 'mbencuesta' ---
    @commands.command()
    async def mbencuesta(self, ctx, pregunta: str, *opciones):
        """Crea una encuesta con reacciones.
        Ejemplo: !mbencuesta "¿Cuál eliges?" "Opción 1" "Opción 2"
        """
        
        # ¡HEMOS QUITADO LA COMPROBACIÓN DE COMILLAS QUE DABA EL ERROR!
        # La librería ya se encarga de agrupar la pregunta por nosotros.

        if not opciones:
            await ctx.send("Debes incluir al menos una opción después de la pregunta. Ejemplo: `!mbencuesta \"Pregunta\" \"Op1\" \"Op2\"`")
            return
        
        if len(opciones) > 10:
            await ctx.send("No puedo crear una encuesta con más de 10 opciones.")
            return

        # Emojis para las opciones
        emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
        
        descripcion = []
        for i, opcion in enumerate(opciones):
            descripcion.append(f"{emojis[i]} {opcion}")
        
        # Creamos el Embed
        embed = discord.Embed(
            title=pregunta, # La 'pregunta' ya viene sin comillas
            description="\n".join(descripcion),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Encuesta creada por {ctx.author.display_name}")

        # Enviamos el mensaje y guardamos la referencia
        msg = await ctx.send(embed=embed)

        # Añadimos las reacciones al mensaje del bot
        for i in range(len(opciones)):
            await msg.add_reaction(emojis[i])
    # --- FIN DE LA CORRECCIÓN ---


async def setup(bot):
    await bot.add_cog(Social(bot))