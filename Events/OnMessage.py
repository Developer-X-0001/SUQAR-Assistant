import config
import discord
from discord.ext import commands

class OnMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        suqar_role = message.guild.get_role(config.SUQAR_ROLE_ID)
        if suqar_role in message.author.roles or message.author == self.bot.user:
            return

        if message.channel.id == config.ORDER_CHANNEL_ID:
            await message.delete()

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMessage(bot))