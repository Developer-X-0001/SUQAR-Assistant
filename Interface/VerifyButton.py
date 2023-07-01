import config
import sqlite3
import discord
import robloxpy

from discord import ButtonStyle
from discord.ui import View, button, Button
from Interface.ChangeNicknameButtons import ChangeNickname

database = sqlite3.connect("./Databases/data.sqlite")

class Verify(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Verify", style=ButtonStyle.green, custom_id="verify")
    async def verify(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(1063715753393659975)
        data = database.execute("SELECT username, code, alt_code FROM AuthCodes WHERE user_id = ?", (interaction.user.id,)).fetchone()
        if data is not None:
            await interaction.response.edit_message(content=f"{config.EMOJI_LOADING} Verifying Account `{data[0]}`", view=None)
            rblx_id = robloxpy.User.External.GetID(Username=data[0])
            desc = robloxpy.User.External.GetDescription(UserID=rblx_id)
            get_code = ""
            for i in str(data[1]):
                if i.upper() in desc:
                    get_code += i

            if get_code == str(data[1]):
                await interaction.user.add_roles(role)
                await interaction.edit_original_response(content=f"{config.EMOJI_DONE} Verification Successful!\n{config.EMOJI_DONE} You've got {role.mention} role\n\nWould you like to change your nickname to your Roblox username?", view=ChangeNickname())
                database.execute("DELETE FROM AuthCodes WHERE user_id = ?", (interaction.user.id,)).connection.commit()
                database.execute("INSERT INTO Accounts VALUES (?, ?)", (interaction.user.id, data[0],)).connection.commit()

            else:
                get_code_2 = ""
                for i in str(data[2]):
                    if i in desc:
                        get_code_2 += i
                
                if get_code_2 == str(data[2]):
                    await interaction.user.add_roles(role)
                    await interaction.edit_original_response(content=f"{config.EMOJI_DONE} Verification Successful!\n{config.EMOJI_DONE} You've got {role.mention} role\n\nWould you like to change your nickname to your Roblox username?", view=ChangeNickname())
                    database.execute("DELETE FROM AuthCodes WHERE user_id = ?", (interaction.user.id,)).connection.commit()
                    database.execute("INSERT INTO Account VALUES (?, ?)", (interaction.user.id, data[0],)).connection.commit()
                else:
                    database.execute("DELETE FROM AuthCodes WHERE user_id = ?", (interaction.user.id,)).connection.commit()
                    await interaction.edit_original_response(content=f"{config.EMOJI_ERROR} Unable to verify, make sure your you've added the Authentication Code to your account description.")
    
    @button(label="Code Hashed?", style=ButtonStyle.red, custom_id="hashed")
    async def codeHashed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message(content="**Code hashed by ROBLOX?**\nYou can add add each letter of the code separately in your account description.\ne.g Code Hashed: `My description SFLKGB` -> `My description ######`\nAdd Shuffled Code: `SFMy LdescriptionKGB`", ephemeral=True)