import config
import sqlite3
import discord

from discord import ButtonStyle
from discord.ui import View, Button, button

class ChooseCommissionTypeButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Logo", style=ButtonStyle.blurple)

    @button(label="Vector", style=ButtonStyle.blurple)

    @button(label="UI", style=ButtonStyle.blurple)

    @button(label="Gamepass/Badge", style=ButtonStyle.blurple)