import discord
import datetime
from discord.ext import commands
from discord import app_commands
from Interface.OrderConfirmView import OrderButtons

class Order(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="order", description="Willing to purchase? place an order now!")
    async def order(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="- { SUQAR } : Open",
            description="Hello. Welcome and thank you for placing an order. Before you proceed make sure to read all my terms and prices to make sure you agree with everything.\n\nClick the corresponding buttons below to confirm your choice",
            timestamp=datetime.datetime.now(),
            color=discord.Color.purple()
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1062038639275692032/1062057665683005471/suqar_thumbnails_3.png")
        embed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.response.send_message(embed=embed, view=OrderButtons(), ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Order(bot))