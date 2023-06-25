import discord
from discord.ext import commands
from Interface.ApplyButtons import ApplyButtons

class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="test")
    async def test(self, ctx: commands.Context, id:int):
        embed = {
            "thumbnail": {
                "url": "https://th.bing.com/th/id/R.5e2b4bf2fbbbe5ee655c5ef468aa7530?rik=jC0lTr%2bOmJoqhg&pid=ImgRaw&r=0"
            },
            "fields": [
                {
                "inline": False,
                "name": "We have two verification methods available:",
                "value": "1. Roblox Verification\n2. One-Click Verification"
                },
                {
                "inline": False,
                "name": "1. Roblox Verification",
                "value": " Steps to connect your Roblox account:\n  \\\u25aa Click on **Connect Roblox** button.\n  \\\u25aa  It will ask for your username, continue with entering your Roblox username.\n  \\\u25aa  It will ask for account confirmation, make sure you are connecting the account you own.\n  \\\u25aa  It will generate a unique OTP, you have to put that OTP to your Roblox account description.\n  \\\u25aa  Finally the bot will verify the OTP and you'll be verified! "
                },
                {
                "inline": False,
                "name": "2. One-Click Verification",
                "value": "Just click on **One-Click Verify** button and you'll be verified immediately, however verifying with Roblox is preferred."
                }
            ],
            "color": 8087790,
            "type": "rich",
            "description": "Hello! Please verify to gain access to the rest of the server.",
            "title": "Verify Yourself"
            }
        await ctx.send(embed=discord.Embed.from_dict(embed), view=ApplyButtons())

async def setup(bot: commands.Bot):
    await bot.add_cog(Test(bot))