import os
import config
import discord
import aiosqlite
from discord.ext import commands
from Interface.ApplyButtons import ApplyButtons
from Interface.ViewsAndModals import OrderStatusButtons, OrderRateButtons, OrderDeleteButton

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            application_id=config.APPLICATION_ID
        )

    async def setup_hook(self):
        self.add_view(ApplyButtons())
        self.add_view(OrderStatusButtons())
        self.add_view(OrderRateButtons())
        self.add_view(OrderDeleteButton())
        for filename in os.listdir("./Commands"):
            if filename.endswith('.py'):
                await self.load_extension(f'Commands.{filename[:-3]}')
                print(f"Loaded {filename}")
            if filename.startswith("__"):
                pass
        
        for filename in os.listdir("./Events"):
            if filename.endswith('.py'):
                await self.load_extension(f'Events.{filename[:-3]}')
                print(f"Loaded {filename}")
            if filename.startswith("__"):
                pass

        await bot.tree.sync()

bot = Bot()

@bot.event
async def on_ready():
    database = await aiosqlite.connect("./Databases/data.db")
    await database.execute("CREATE TABLE IF NOT EXISTS OrderNo (order_no)")
    await database.execute("CREATE TABLE IF NOT EXISTS Accounts (user_id, username, PRIMARY KEY(user_id))")
    await database.execute("CREATE TABLE IF NOT EXISTS AuthCodes (user_id, username, code, alt_code, PRIMARY KEY(user_id))")
    await database.execute("CREATE TABLE IF NOT EXISTS OrderMessage (embed_id, message_id, PRIMARY KEY(embed_id))")
    await database.execute("CREATE TABLE IF NOT EXISTS Orders (embed_id, order_no, user_id, message_id, status, priority, timestamp, stars, review, PRIMARY KEY(embed_id))")
    await database.execute("CREATE TABLE IF NOT EXISTS OrderData (user_id, logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline)")
    await database.execute("CREATE TABLE IF NOT EXISTS OrdersInformation (order_no, user_id, logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline, PRIMARY KEY(order_no))")
    print(f"{bot.user} is connected to Discord, current latency is {round(bot.latency * 1000)}ms")

@bot.command(name="reload")
async def reload(ctx: commands.Context, cog:str):
    # Reloads the file, thus updating the Cog class.
    await bot.reload_extension(f"Commands.{cog}")
    await ctx.send(f"🔁 {cog} reloaded!")

@bot.command(name="load")
async def load(ctx: commands.Context, cog:str):
    # Reloads the file, thus updating the Cog class.
    await bot.load_extension(f"Commands.{cog}")
    await ctx.send(f"🆙 {cog} loaded!")

bot.run(config.TOKEN)