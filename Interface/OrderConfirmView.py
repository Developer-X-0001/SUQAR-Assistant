import discord

from discord import ButtonStyle
from discord.ui import View, Button, button
from Interface.UiOrderView import UIOrderModal
from Interface.LogoOrderView import LogoOrderModal
from Interface.VectorOrderView import VectorOrderModal
from Interface.GamepassOrderView import GamepassOrderModal

class OrderButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Confirm", style=ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title="Choose order type",
            description="Choose which type of product you are looking for.",
            color=discord.Color.purple()
        )
        await interaction.response.edit_message(embed=embed, view=OrderTypeButtons())
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="nvm")
    async def nvm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", embed=None, view=None)

class OrderTypeButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @button(label="Logo", style=ButtonStyle.blurple)
    async def logo_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(LogoOrderModal())

    @button(label="Vector", style=ButtonStyle.blurple)
    async def vector_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(VectorOrderModal())

    @button(label="UI", style=ButtonStyle.blurple)
    async def ui_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(UIOrderModal())

    @button(label="Gamepass/Badge", style=ButtonStyle.blurple)
    async def gamepass_badge_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(GamepassOrderModal())

