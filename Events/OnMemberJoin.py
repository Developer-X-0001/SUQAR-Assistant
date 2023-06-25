import discord
from discord.ext import commands
from discord import app_commands

class OnMemberJoin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild = member.guild
        if not member.bot:
            roles = [guild.get_role(1063775256365506610),guild.get_role(1063776331533402243),guild.get_role(1063776266311979008)]
            for role in roles:
                await member.add_roles(role)
        if member.bot:
            roles = [guild.get_role(1063775256365506610),guild.get_role(1063777296193949716),guild.get_role(1063776200285224990)]
            for role in roles:
                await member.add_roles(role)

async def setup(bot: commands.Bot):
    await bot.add_cog(OnMemberJoin(bot))