import os
import config
import sqlite3
import discord
from discord.ext import commands
from Interface.ApplyButtons import ApplyButtons
from Interface.OrderManagingViews import OrderStatusButtons, OrderDeleteButton, OrderRateButtons

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all(),
            activity=discord.Game(name='under development'),
            status=discord.Status.idle,
            application_id=config.APPLICATION_ID,
        )

    async def setup_hook(self):
        sqlite3.connect("./Databases/data.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS Accounts (
                    user_id INTEGER,
                    username TEXT,
                    Primary Key (user_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS AuthCodes (
                    user_id INTEGER,
                    username TEXT,
                    code TEXT,
                    alt_code TEXT,
                    Primary Key (user_id)
                )       
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS OrderNo (
                    order_no INTEGER,
                    Primary Key (order_no)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS OrderMessage (
                    embed_id INTEGER,
                    message_id INTEGER,
                    Primary Key (embed_id)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS Orders (
                    embed_id INTEGER,
                    order_no INTEGER,
                    order_type TEXT,
                    user_id INTEGER,
                    message_id INTEGER,
                    status TEXT,
                    priority TEXT,
                    timestamp INTEGER,
                    stars INTEGER,
                    review TEXT,
                    Primary Key (embed_id)
                )
            '''
        ).connection.commit()

        sqlite3.connect("./Databases/orders.sqlite").execute(
            '''
                CREATE TABLE IF NOT EXISTS LogoOrders (
                    order_no INTEGER,
                    user_id INTEGER,
                    logo_for TEXT,
                    logo_text TEXT,
                    logo_color TEXT,
                    logo_payment TEXT,
                    logo_vector TEXT,
                    logo_extra TEXT,
                    logo_deadline TEXT,
                    Primary Key (order_no)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS VectorOrders (
                    order_no INTEGER,
                    user_id INTEGER,
                    vector_desc TEXT,
                    vector_payment TEXT,
                    Primary Key (order_no)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS UIOrders (
                    order_no INTEGER,
                    user_id INTEGER,
                    ui_type TEXT,
                    ui_package TEXT,
                    ui_needed TEXT,
                    ui_payment TEXT,
                    Primary Key (order_no)
                )
            '''
        ).execute(
            '''
                CREATE TABLE IF NOT EXISTS GamepassOrders (
                    order_no INTEGER,
                    user_id INTEGER,
                    gamepass_amount TEXT,
                    gamepass_type TEXT,
                    gamepass_payment TEXT,
                    Primary Key (order_no)
                )
            '''
        ).connection.commit()
        
        # execute("CREATE TABLE IF NOT EXISTS OrderData (user_id, logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline)")
        # execute("CREATE TABLE IF NOT EXISTS OrdersInformation (order_no, user_id, logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline, PRIMARY KEY(order_no))")
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