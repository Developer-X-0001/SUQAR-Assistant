import config
import sqlite3
import discord
import datetime

from discord import ButtonStyle, TextStyle
from discord.ui import View, Modal, Button, TextInput, button
from Interface.OrderManagingViews import OrderStatusButtons

database = sqlite3.connect('./Databases/data.sqlite')
orders_database = sqlite3.connect("./Databases/orders.sqlite")

class LogoOrderExtrasButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Proceed", style=ButtonStyle.green, custom_id="proceed")
    async def proceed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="<a:loading:1062104001245614130> **Creating your Order**", embed=None, view=None)
        order_no = int(interaction.message.embeds[0].footer.text[10:])

        message = await interaction.guild.get_channel(config.QUEUE_CHANNEL_ID).send(content=f"**>------- Order ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {interaction.user.mention}\n**Order No:** `{order_no}`\n**Order Status:** `Pending`\n**Order Type:** `Logo`")

        data = orders_database.execute("SELECT logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline FROM LogoOrders WHERE order_no = ?", (order_no,)).fetchone()

        for category in interaction.guild.categories:
            if 'order tickets' in category.name.lower():
                embed = discord.Embed(
                    title="- { SUQAR } : Order",
                    description=f"`Ticket {order_no}`. Thank you for placing an order in **{interaction.guild.name}**. If you have any questions or concerns, feel free to ask.\n\nYour Order Information:\n```ini\n[Purpose of Logo]\n{data[0]}\n[Text on the Logo:]\n{data[1]}\n[Colors]\n{data[2]}\n[Payment]\n{data[3]}\n[Provided Vectors:]\n{data[4]}\n```",
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
                        'logo',
                        interaction.user.id,
                        message.id,
                        'pending',
                        'no',
                        round(datetime.datetime.now().timestamp()),
                    )
                ).connection.commit()
    
    @button(label="Proceed with Extras", style=ButtonStyle.blurple, custom_id="extras")
    async def addextras(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(LogoOrderExtrasModal())
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="nvm")
    async def nvm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", embed=None, view=None)

class LogoOrderModal(Modal, title="Logo Order Form"):
    def __init__(self):
        super().__init__(timeout=None)

    logo_for = TextInput(
        label="What is the logo for?",
        style=TextStyle.short,
        placeholder="NSFW Commissions will be denied...",
        required=True
    )
    logo_text = TextInput(
        label="Name of the Text for the logo:",
        style=TextStyle.short,
        placeholder="i.e SUQAR",
        required=True
    )
    logo_color = TextInput(
        label="Colors for the text?",
        style=TextStyle.long,
        placeholder="top word red, bottom word, etc or I can pick...",
        required=True
    )
    logo_payment = TextInput(
        label="Payment?",
        style=TextStyle.short,
        placeholder="Robux or PayPal",
        required=True
    )
    logo_vectors = TextInput(
        label="Vectors for the logos:",
        style=TextStyle.long,
        placeholder="e.g bubbles, seaweed around the text, 2-3 max vectors any extra will cost you",
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
                INSERT INTO LogoOrders VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)
            ''',
            (
                order_no,
                interaction.user.id,
                self.logo_for.value,
                self.logo_text.value,
                self.logo_color.value,
                self.logo_payment.value,
                self.logo_vectors.value,
            )
        ).connection.commit()

        embed = discord.Embed(
            title="- { SUQAR } : Order",
            description=f"Hello! Welcome to your order. Please make sure the following information that you've provided is all correct. If you want to add any extra things for the logo or want to give a specific deadline, please click the button below.\n\n```ini\n[What is the logo for:]\n{self.logo_for}\n[Name of the Text for the logo:]\n{self.logo_text}\n[Colors for the text?:]\n{self.logo_color}\n[Payment?]\n{self.logo_payment}\n[Provided Vectors:]\n{str(self.logo_vectors)}\n```",
            timestamp=datetime.datetime.now(),
            color=discord.Color.purple()
        )
        embed.set_footer(text="Order No: {}".format(order_no))
        await interaction.response.edit_message(embed=embed, view=LogoOrderExtrasButtons())

class LogoOrderExtrasModal(Modal, title="Order Extras"):
    def __init__(self):
        super().__init__(timeout=None)

    logo_extra = TextInput(
        label="Any extra things for logo?",
        style=TextStyle.long,
        required=True
    )
    logo_deadline = TextInput(
        label="Specific Deadline:",
        style=TextStyle.short,
        placeholder="If you want 1 day you must pay the fee $15 extra or 2k Robux...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="<a:loading:1062104001245614130> **Creating your Order**", embed=None, view=None)
        order_no = int(interaction.message.embeds[0].footer.text[10:])

        orders_database.execute(
            '''
                UPDATE LogoOrders SET
                    logo_extra = ?,
                    logo_deadline = ?
                    WHERE order_no = ?
            ''',
            (
                self.logo_extra.value,
                self.logo_deadline.value,
                order_no,
            )
        ).connection.commit()

        message = await interaction.guild.get_channel(config.QUEUE_CHANNEL_ID).send(content=f"**>------- Order ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {interaction.user.mention}\n**Order No:** `{order_no}`\n**Order Status:** `Pending`\n**Order Type:** `Logo`")

        data = orders_database.execute("SELECT logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline FROM LogoOrders WHERE order_no = ?", (order_no,)).fetchone()

        for category in interaction.guild.categories:
            if 'order tickets' in category.name.lower():
                embed = discord.Embed(
                    title="- { SUQAR } : Order",
                    description=f"`Ticket {order_no}`. Thank you for placing an order in **{interaction.guild.name}**. If you have any questions or concerns, feel free to ask.\n\nYour Order Information:\n```ini\n[Purpose of Logo]\n{data[0]}\n[Text on the Logo]\n{data[1]}\n[Colors]\n{data[2]}\n[Payment]\n{data[3]}\n[Provided Vectors]\n{data[4]}\n[Extras]\n{data[5]}\n[Specific Deadline]\n{data[6]}\n```",
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
                embed_msg = await ticket.send(embed=embed, content=interaction.user.mention, view=OrderStatusButtons())

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
                        INSERT INTO Orders VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)
                    ''',
                    (
                        embed_msg.id,
                        order_no,
                        interaction.user.id,
                        message.id,
                        'pending',
                        'no',
                        round(datetime.datetime.now().timestamp()),
                    )
                ).connection.commit()