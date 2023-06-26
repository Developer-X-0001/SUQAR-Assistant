import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from discord.ui import View, Modal, Button, TextInput, button
from Interface.OrderManagingViews import OrderStatusButtons

database = sqlite3.connect('./Databases/data.sqlite')
orders_database = sqlite3.connect("./Databases/orders.sqlite")

class VectorOrderExtrasButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Proceed", style=ButtonStyle.green, custom_id="proceed")
    async def proceed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="<a:loading:1062104001245614130> **Creating your Order**", embed=None, view=None)
        order_no = int(interaction.message.embeds[0].footer.text[10:])

        message = await interaction.guild.get_channel(config.QUEUE_CHANNEL_ID).send(content=f"**>------- Order ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {interaction.user.mention}\n**Order No:** `{order_no}`\n**Order Status:** `Pending`\n**Order Type:** `Vector`")

        data = orders_database.execute("SELECT order_no, user_id, vector_desc, vector_payment FROM VectorOrders WHERE order_no = ?", (order_no,)).fetchone()

        for category in interaction.guild.categories:
            if 'order tickets' in category.name.lower():
                embed = discord.Embed(
                    title="- { SUQAR } : Order",
                    description=f"`Ticket {order_no}`. Thank you for placing an order in **{interaction.guild.name}**. If you have any questions or concerns, feel free to ask.\n\nYour Order Information:\n```ini\n[Type of vectors needed:]\n{data[2]}\n[Payment?]\n{data[3]}\n```",
                    color=discord.Color.purple()
                )
                embed.set_image(url="https://media.discordapp.net/attachments/1062050898081226802/1062062336472514580/suqarart_temporary_banner.png")

                permissions = {
                    interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True),
                    interaction.guild.get_role(1062446612519075910): discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, manage_messages=True),
                    interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }
                ticket = await interaction.guild.create_text_channel(name=f"ticket-{interaction.user.name}", overwrites=permissions, category=category)
                await interaction.edit_original_response(content=f"{config.EMOJI_DONE} Order created: {ticket.mention}")
                view = OrderStatusButtons()
                embed_msg = await ticket.send(embed=embed, content=interaction.user.mention, view=view)
                
                database.execute(
                    '''
                        INSERT INTO OrderMessage VALUES (?, ?)
                    ''',
                    (
                        embed_msg.id,
                        message.id,
                    )
                ).execute(
                    '''
                        INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)
                    ''',
                    (
                        embed_msg.id,
                        order_no,
                        'vector',
                        interaction.user.id,
                        message.id,
                        'pending',
                        'no',
                        round(datetime.datetime.now().timestamp()),
                    )
                ).connection.commit()
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="nvm")
    async def nvm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", embed=None, view=None)

class VectorOrderModal(Modal, title="Vector Order Form"):
    def __init__(self):
        super().__init__(timeout=None)

    vector_desc = TextInput(
        label="What kind of Vectors do you want?",
        style=TextStyle.short,
        placeholder="Vectors are small little designs like coin, shopping cart, etc",
        required=True
    )
    vector_payment = TextInput(
        label="Payment?",
        style=TextStyle.short,
        placeholder="Robux or PayPal",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        order_no_data = database.execute("SELECT order_no FROM OrderNo").fetchone()
        order_no = 1 if order_no_data is None else int(order_no_data[0]) + 1

        if order_no_data is None:
            database.execute("INSERT INTO OrderNo VALUES (?)", (int(order_no),)).connection.commit()
        else:
            database.execute("UPDATE OrderNo set order_no = ?", (order_no,)).connection.commit()

        orders_database.execute(
            '''
                INSERT INTO VectorOrders VALUES (?, ?, ?, ?)
            ''',
            (
                order_no,
                interaction.user.id,
                self.vector_desc.value,
                self.vector_payment.value,
            )
        ).connection.commit()

        embed = discord.Embed(
            title="- { SUQAR } : Order",
            description=f"Hello! Welcome to your order. Please make sure the following information that you've provided is all correct. If you want to add any extra things for the logo or want to give a specific deadline, please click the button below.\n\n```ini\n[Type of vectors needed:]\n{self.vector_desc.value}\n[Payment?]\n{self.vector_payment.value}\n```",
            timestamp=datetime.datetime.now(),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Order No: {}".format(order_no))
        await interaction.response.edit_message(embed=embed, view=VectorOrderExtrasButtons())