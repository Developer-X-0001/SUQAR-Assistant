import discord
from discord.ext import commands
from discord import app_commands

class SetStatus(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="status", description="Set bot's presence status")
    @app_commands.choices(activity=[
        app_commands.Choice(name="Playing", value=1),
        app_commands.Choice(name="Listening", value=2),
        app_commands.Choice(name="Watching", value=3)
    ], status=[
        app_commands.Choice(name="Online", value=1),
        app_commands.Choice(name="Offline", value=2),
        app_commands.Choice(name="Do Not Disturb", value=3),
        app_commands.Choice(name="Idle", value=4)
    ])
    async def setStatus(self, interaction: discord.Interaction, activity: app_commands.Choice[int], message: str, status: app_commands.Choice[int]=None):
        set_status = discord.Status.online
        if status is None:
            set_status = discord.Status.online
        if status is not None:
            if status.value == 1:
                set_status = discord.Status.online
            if status.value == 2:
                set_status = discord.Status.offline
            if status.value == 3:
                set_status = discord.Status.dnd
            if status.value == 4:
                set_status = discord.Status.idle

        if activity.value == 1:
            await self.bot.change_presence(activity=discord.Game(name=message), status=set_status)
            await interaction.response.send_message("<:done:1063747663461371914> Presence Updated", ephemeral=True)
        if activity.value == 2:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=message), status=set_status)
            await interaction.response.send_message("<:done:1063747663461371914> Presence Updated", ephemeral=True)
        if activity.value == 3:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=message), status=set_status)
            await interaction.response.send_message("<:done:1063747663461371914> Presence Updated", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetStatus(bot))