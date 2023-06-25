import config
import discord
import robloxpy
from discord import TextStyle
from discord.ui import Modal, TextInput
from Interface.AccountConfirmButtons import AccountConfirmButtons

class UsernameInput(Modal, title="Submit your account Username"):
    def __init__(self):
        super().__init__(timeout=None)

    input = TextInput(
        label="Username",
        style=TextStyle.short,
        placeholder="Type your username not display name...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"{config.EMOJI_LOADING} Finding account named `{self.input}`", ephemeral=True)
        id = robloxpy.User.External.GetID(Username=self.input)
        await interaction.edit_original_response(content=f"{config.EMOJI_DONE} Account Found\n{config.EMOJI_LOADING} Fetching Info")

        try:
            username = robloxpy.User.External.GetUserName(UserID=id)
            url = f"https://web.roblox.com/users/{id}/profile"
            joindate = robloxpy.User.External.CreationDate(UserID=id)
            friends = robloxpy.User.Friends.External.GetCount(UserID=id)
            followers = robloxpy.User.Friends.External.GetFollowerCount(UserID=id)
            await interaction.edit_original_response(content=f"{config.EMOJI_DONE} Account Found\n{config.EMOJI_DONE} Fetched Info")
            embed = discord.Embed(
                title=f"Account Found {config.EMOJI_DONE}",
                description=f"[__**Information:**__]({url})\n"
                        f":identification_card: **Username**: {username}\n"
                        f"🆔 **User ID**: {id}\n"
                        f"📆 **Join Date**: {joindate}\n\n"
                        f":people_hugging: **Friends Count**: {friends}\n"
                        f"👥 **Followers Count**: {followers}\n\n"
                        "❓ Is this your account?",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(content=None, embed=embed, view=AccountConfirmButtons(self.input))
        except:
            await interaction.edit_original_response(content=f"{config.EMOJI_ERROR} Something Went Wrong")
            raise Exception