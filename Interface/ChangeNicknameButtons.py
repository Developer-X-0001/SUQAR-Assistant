import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, button, Button

database = sqlite3.connect("./Databases/data.sqlite")

class ChangeNickname(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Update Nickname", style=ButtonStyle.green, custom_id="update_nick")
    async def updateNick(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT username FROM Accounts WHERE user_id = ?", (interaction.user.id,)).fetchone()
        await interaction.user.edit(nick=str(data[0]))
        await interaction.response.edit_message(content=f"{config.EMOJI_DONE} Username Updated\n`{interaction.user.name}` -> **{interaction.user.nick}**", view=None)
    
    @button(label="No Thanks", style=ButtonStyle.red, custom_id="np")
    async def noThanks(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", view=None)