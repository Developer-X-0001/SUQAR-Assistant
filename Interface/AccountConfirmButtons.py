import random
import string
import discord
import aiosqlite
from discord import ButtonStyle
from discord.ui import View, button, Button
from Interface.VerifyButton import Verify

class AccountConfirmButtons(View):
    def __init__(self, username):
        self.username = username
        super().__init__(timeout=None)

    @button(label="Yes!", style=ButtonStyle.green, custom_id="account_yes")
    async def accountyes(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT code FROM AuthCodes WHERE user_id = {interaction.user.id}") as cursor:
            data = await cursor.fetchone()
        if data is None:
            id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]).upper()
            alt_id = f"SUQAR {random.randint(1000, 9999)}"
            await database.execute(f"INSERT INTO AuthCodes VALUES ({interaction.user.id}, '{self.username}', '{id}', '{alt_id}')")
            await database.commit()
            await database.close()
            await interaction.response.edit_message(content=f"**Your Auth Code:** `{id}`\n**Alternate Phrase:** `{alt_id}`\n\nAdd one of these to your account description and click **Verify**", embed=None, view=Verify())
        if data is not None:
            await database.execute(f"DELETE FROM AuthCodes WHERE user_id = {interaction.user.id}")
            id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)]).upper()
            alt_id = f"SUQAR {random.randint(1000, 9999)}"
            await database.execute(f"INSERT INTO AuthCodes VALUES ({interaction.user.id}, '{self.username}', '{id}', '{alt_id}')")
            await database.commit()
            await database.close()
            await interaction.response.edit_message(content=f"**Your Auth Code:** `{id}`\n**Alternate Phrase:** `{alt_id}`\n\nAdd one of these to your account description and click **Verify**", embed=None, view=Verify())
    
    @button(label="Nope", style=ButtonStyle.red, custom_id="account_no")
    async def accountno(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        await database.execute(f"DELETE FROM AuthCodes WHERE user_id = {interaction.user.id}")
        await database.commit()
        await database.close()
        await interaction.response.edit_message(content="Nevermind! Apply again...", view=None)