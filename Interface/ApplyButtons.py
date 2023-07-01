import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, button, Button
from Interface.UsernameInputModal import UsernameInput

database = sqlite3.connect("./Databases/data.sqlite")

class ApplyButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Roblox Verification", style=ButtonStyle.red, emoji=config.EMOJI_ROBLOX, custom_id="ro_verify")
    async def roVerify(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT username FROM Accounts WHERE user_id = ?", (interaction.user.id,)).fetchone()
        if data is None:
            await interaction.response.send_modal(UsernameInput())
        if data is not None:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} An account is already connected to your Discord!", ephemeral=True)
    
    @button(label="One-Click Verification", style=ButtonStyle.blurple, custom_id="verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        role = interaction.guild.get_role(1063715753393659975)
        await interaction.user.add_roles(role)