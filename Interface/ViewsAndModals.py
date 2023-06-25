import config
import asyncio
import discord
import datetime
import aiosqlite
from discord import ButtonStyle, TextStyle
from discord.ui import View, button, Button, Modal, TextInput

class OrderButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Confirm", style=ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(OrderModal())
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="nvm")
    async def nvm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", embed=None, view=None)

class OrderExtrasButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Proceed", style=ButtonStyle.green, custom_id="proceed")
    async def proceed(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="<a:loading:1062104001245614130> **Creating your Order**", embed=None, view=None)
        database = await aiosqlite.connect("./Databases/data.db")

        async with database.execute(f"SELECT logo_for, logo_text, logo_color, logo_payment, logo_vector FROM OrderData WHERE user_id = {interaction.user.id}") as cursor:
            data = await cursor.fetchone()

        async with database.execute(f"SELECT order_no FROM OrderNo ORDER BY order_no DESC") as cursor_2:
            data_2 = await cursor_2.fetchone()
        
        order_no = 0
        if data_2 is None:
            order_no = 1
            await database.execute("INSERT INTO OrderNo VALUES (1)")
            await database.commit()
        if data_2 is not None:
            order_no = int(data_2[0]) + 1
            await database.execute("UPDATE OrderNo SET order_no = order_no + 1")
            await database.commit()

        message = await interaction.guild.get_channel(config.QUEUE_CHANNEL_ID).send(content=f"**>------- Order ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {interaction.user.mention}\n**Order No:** `{order_no}`\n**Order Status:** `Pending`")
        await database.execute(f"INSERT INTO OrdersInformation VALUES (?, ?, ?, ?, ?, ?, ?, NULL, NULL)", (order_no, interaction.user.id, data[0], data[1], data[2], data[3], data[4]))
        await database.commit()

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
                await database.execute(f"INSERT INTO OrderMessage VALUES ({embed_msg.id}, {message.id})")
                await database.execute(f"INSERT INTO Orders VALUES ({embed_msg.id}, {order_no}, {interaction.user.id}, {message.id}, 'pending', 'no', {round(datetime.datetime.now().timestamp())}, NULL, NULL)")
                await database.commit()
                await database.close()
    
    @button(label="Proceed with Extras", style=ButtonStyle.blurple, custom_id="extras")
    async def addextras(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_modal(OrderExtrasModal())
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="nvm")
    async def nvm(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="👋🏻 Have a nice day!", embed=None, view=None)

class OrderStatusButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OrderStatusSelect())

    @button(label="Mark as Completed", style=ButtonStyle.green, emoji="<:approved:1062484431513849906>", custom_id="completed", row=1)
    async def completed(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            database = await aiosqlite.connect("./Databases/data.db")
            async with database.execute(f"SELECT message_id FROM OrderMessage WHERE embed_id = {interaction.message.id}") as cursor:
                data = await cursor.fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.green()
            embed.set_footer(text=f"✅ Order marked as completed")
            await database.execute(f"UPDATE Orders SET status = 'completed' WHERE embed_id = {interaction.message.id}")
            await database.commit()
            async with database.execute(f"SELECT order_no, user_id, status, priority, timestamp FROM Orders WHERE embed_id = {interaction.message.id}") as cursor2:
                order_data = await cursor2.fetchone()
            
            embed.description = f"`Ticket {order_data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\nNot rated\n[Review]\nNone\n```"
            await interaction.response.edit_message(embed=embed, view=OrderRateButtons())
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[1])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[4]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[2]).capitalize()}`\n**Priority Order:** `{str(order_data[3]).capitalize()}`")
            await database.close()
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)

    @button(label="Cancel Order", style=ButtonStyle.red, emoji="<:rejected:1062484427281809479>", custom_id="cancelled", row=1)
    async def cancelled(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            database = await aiosqlite.connect("./Databases/data.db")
            async with database.execute(f"SELECT message_id FROM OrderMessage WHERE embed_id = {interaction.message.id}") as cursor:
                data = await cursor.fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.red()
            embed.set_footer(text=f"❌ Order cancelled")
            await interaction.response.edit_message(embed=embed, view=OrderDeleteButton())
            await database.execute(f"UPDATE Orders SET status = 'cancelled' WHERE embed_id = {interaction.message.id}")
            await database.commit()
            async with database.execute(f"SELECT order_no, user_id, status, priority, timestamp FROM Orders WHERE embed_id = {interaction.message.id}") as cursor2:
                order_data = await cursor2.fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[1])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[4]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[2]).capitalize()}`\n**Priority Order:** `{str(order_data[3]).capitalize()}`")
            await database.close()
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)
    
    @button(label="Mark as Priority Order ->", style=ButtonStyle.gray, custom_id="mark_dead", disabled=True, row=2)
    async def mark_dead(self, interaction: discord.Interaction, button: Button):
        return

    @button(style=ButtonStyle.blurple, emoji="⭐", custom_id="mark", row=2)
    async def mark(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            database = await aiosqlite.connect("./Databases/data.db")
            async with database.execute(f"SELECT message_id FROM OrderMessage WHERE embed_id = {interaction.message.id}") as cursor:
                data = await cursor.fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.gold()
            embed.set_footer(text="⭐ Order marked as priority")
            self.mark.disabled = True
            self.mark.style = ButtonStyle.gray
            await interaction.response.edit_message(embed=embed, view=self)
            await database.execute(f"UPDATE Orders SET priority = 'yes' WHERE embed_id = {interaction.message.id}")
            await database.commit()
            async with database.execute(f"SELECT order_no, user_id, status, priority, timestamp FROM Orders WHERE embed_id = {interaction.message.id}") as cursor2:
                order_data = await cursor2.fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[1])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[4]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[2]).capitalize()}`\n**Priority Order:** `{str(order_data[3]).capitalize()}`")
            await database.close()
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)

class OrderRateButtons(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Waiting for review", style=ButtonStyle.gray, custom_id="rateorder", disabled=True, row=0)
    async def rateOrder(self, interaction: discord.Interaction, button: Button):
        return
    
    @button(label="Confirm Review", style=ButtonStyle.green, custom_id="confirm", row=0)
    async def confirmReview(self, interaction: discord.Interaction, button: Button):
        review_channel = interaction.guild.get_channel(config.REVIEW_CHANNEL_ID)
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, stars, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            order_no = int(data[0])
            if data[2] is None and data[3] is None:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You can't post empty review!", ephemeral=True)

            else:
                if data[2] is None:
                    await interaction.response.send_message(content="**Please rate the order!**", ephemeral=True)
                    return
                
                if data[3] is None:
                    await interaction.response.send_message(content="**Please leave a review on the order!**", ephemeral=True)
                    return
                
                stars = int(data[2])
                review = str(data[3])

                if stars == 1:
                    stars = '⭐'
                elif stars == 2:
                    stars = '⭐⭐'
                elif stars == 3:
                    stars = '⭐⭐⭐'
                elif stars == 4:
                    stars = '⭐⭐⭐⭐'
                elif stars == 5:
                    stars = '⭐⭐⭐⭐⭐'

                await review_channel.send(content=f"**>------- Review ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_no}`\n**Rating:** `{stars}`\n**Review:**\n`{review}`")
                await interaction.response.edit_message(view=OrderDeleteButton())
            
        if data is None:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You can't post empty review!", ephemeral=True)
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="ratenvm", row=0)
    async def noReview(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=OrderDeleteButton())

    @button(label="1", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate1", row=1)
    async def rate1(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                self.rate1.disabled = True
                self.rate2.disabled = True
                self.rate2.style = ButtonStyle.gray
                self.rate3.disabled = True
                self.rate3.style = ButtonStyle.gray
                self.rate4.disabled = True
                self.rate4.style = ButtonStyle.gray
                self.rate5.disabled = True
                self.rate5.style = ButtonStyle.gray
                embed = interaction.message.embeds[0]
                if not '⭐' in embed.description:
                    embed.description = f"`Ticket {data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\n⭐\n[Review]\n{data[2]}\n```"
                else:
                    description_to_list = embed.description.split("\n")
                    description_to_list.remove(description_to_list[5])
                    description_to_list.insert(5, '⭐')
                    description_to_string = ''
                    for i in description_to_list:
                        description_to_string += i + "\n"
                    embed.description = description_to_string

                await database.execute(f"UPDATE Orders SET stars = 1 WHERE embed_id = {interaction.message.id}")
                await database.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()

    @button(label="2", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate2", row=1)
    async def rate2(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                self.rate1.disabled = True
                self.rate1.style = ButtonStyle.gray
                self.rate2.disabled = True
                self.rate3.disabled = True
                self.rate3.style = ButtonStyle.gray
                self.rate4.disabled = True
                self.rate4.style = ButtonStyle.gray
                self.rate5.disabled = True
                self.rate5.style = ButtonStyle.gray
                
                embed = interaction.message.embeds[0]
                if not '⭐' in embed.description:
                    embed.description = f"`Ticket {data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\n⭐⭐\n[Review]\n{data[2]}\n```"
                else:
                    description_to_list = embed.description.split("\n")
                    description_to_list.remove(description_to_list[5])
                    description_to_list.insert(5, '⭐⭐')
                    description_to_string = ''
                    for i in description_to_list:
                        description_to_string += i + "\n"
                    embed.description = description_to_string

                await database.execute(f"UPDATE Orders SET stars = 2 WHERE embed_id = {interaction.message.id}")
                await database.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()
    
    @button(label="3", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate3", row=1)
    async def rate3(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                self.rate1.disabled = True
                self.rate1.style = ButtonStyle.gray
                self.rate2.disabled = True
                self.rate2.style = ButtonStyle.gray
                self.rate3.disabled = True
                self.rate4.disabled = True
                self.rate4.style = ButtonStyle.gray
                self.rate5.disabled = True
                self.rate5.style = ButtonStyle.gray

                embed = interaction.message.embeds[0]
                if not '⭐' in embed.description:
                    embed.description = f"`Ticket {data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\n⭐⭐⭐\n[Review]\n{data[2]}\n```"
                else:
                    description_to_list = embed.description.split("\n")
                    description_to_list.remove(description_to_list[5])
                    description_to_list.insert(5, '⭐⭐⭐')
                    description_to_string = ''
                    for i in description_to_list:
                        description_to_string += i + "\n"
                    embed.description = description_to_string

                await database.execute(f"UPDATE Orders SET stars = 3 WHERE embed_id = {interaction.message.id}")
                await database.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()
            
    @button(label="4", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate4", row=1)
    async def rate4(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                self.rate1.disabled = True
                self.rate1.style = ButtonStyle.gray
                self.rate2.disabled = True
                self.rate2.style = ButtonStyle.gray
                self.rate3.disabled = True
                self.rate3.style = ButtonStyle.gray
                self.rate4.disabled = True
                self.rate5.disabled = True
                self.rate5.style = ButtonStyle.gray

                embed = interaction.message.embeds[0]
                if not '⭐' in embed.description:
                    embed.description = f"`Ticket {data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\n⭐⭐⭐⭐\n[Review]\n{data[2]}\n```"
                else:
                    description_to_list = embed.description.split("\n")
                    description_to_list.remove(description_to_list[5])
                    description_to_list.insert(5, '⭐⭐⭐⭐')
                    description_to_string = ''
                    for i in description_to_list:
                        description_to_string += i + "\n"
                    embed.description = description_to_string

                await database.execute(f"UPDATE Orders SET stars = 4 WHERE embed_id = {interaction.message.id}")
                await database.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()
            
    @button(label="5", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate5", row=1)
    async def rate5(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id, review FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                self.rate1.disabled = True
                self.rate1.style = ButtonStyle.gray
                self.rate2.disabled = True
                self.rate2.style = ButtonStyle.gray
                self.rate3.disabled = True
                self.rate3.style = ButtonStyle.gray
                self.rate4.disabled = True
                self.rate4.style = ButtonStyle.gray
                self.rate5.disabled = True

                embed = interaction.message.embeds[0]
                if not '⭐' in embed.description:
                    embed.description = f"`Ticket {data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\n⭐⭐⭐⭐⭐\n[Review]\n{data[2]}\n```"
                else:
                    description_to_list = embed.description.split("\n")
                    description_to_list.remove(description_to_list[5])
                    description_to_list.insert(5, '⭐⭐⭐⭐⭐')
                    description_to_string = ''
                    for i in description_to_list:
                        description_to_string += i + "\n"
                    embed.description = description_to_string

                await database.execute(f"UPDATE Orders SET stars = 5 WHERE embed_id = {interaction.message.id}")
                await database.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()

    @button(label="Add Review", style=ButtonStyle.blurple, custom_id="review", row=2)
    async def leaveReview(self, interaction: discord.Interaction, button: Button):
        database = await aiosqlite.connect("./Databases/data.db")
        async with database.execute(f"SELECT order_no, user_id FROM Orders WHERE embed_id = {interaction.message.id}") as cursor:
            data = await cursor.fetchone()
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                await interaction.response.send_modal(RateModal(self))
                await database.close()
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
                await database.close()

class OrderDeleteButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Delete Ticket", style=ButtonStyle.red, emoji="🗑", custom_id="delete")
    async def deleteTicket(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            self.deleteTicket.disabled = True
            self.deleteTicket.emoji = "<a:timer10:1063759331931193364>"
            self.deleteTicket.label = "Deleting Ticket..."
            await interaction.response.edit_message(view=self)
            await asyncio.sleep(9)
            await interaction.channel.delete(reason=f"{interaction.user.name} closed the ticket")
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)

#------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------MODALS-----------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------

class RateModal(Modal, title="Order Review"):
    def __init__(self, view):
        super().__init__(timeout=None)
        self.view = view

    input = TextInput(
        label="How was your experience?",
        style=TextStyle.long,
        placeholder="Give a detailed review...",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        database = await aiosqlite.connect("./Databases/data.db")

        embed = interaction.message.embeds[0]
        description_to_list = embed.description.split("\n")
        description_to_list.remove(description_to_list[-2])
        description_to_list.insert(-1, str(self.input))
        description_to_string = ''
        for i in description_to_list:
            description_to_string += i + "\n"
        embed.description = description_to_string

        await database.execute(f"UPDATE Orders SET review = '{str(self.input)}'")
        await database.commit()
        view = self.view
        view.leaveReview.label = "Edit Review"
        await interaction.response.edit_message(embed=embed, view=view)

class OrderModal(Modal, title="Advanced Logo Chart"):
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
        database = await aiosqlite.connect("./Databases/data.db")
        await database.execute(f'INSERT INTO OrderData VALUES(?, ?, ?, ?, ?, ?, NULL, NULL)', (interaction.user.id, str(self.logo_for), str(self.logo_text), str(self.logo_color), str(self.logo_payment), str(self.logo_vectors)))
        await database.commit()

        embed = discord.Embed(
            title="- { SUQAR } : Order",
            description=f"Hello! Welcome to your order. Please make sure the following information that you've provided is all correct. If you want to add any extra things for the logo or want to give a specific deadline, please click the button below.\n\n```ini\n[What is the logo for:]\n{self.logo_for}\n[Name of the Text for the logo:]\n{self.logo_text}\n[Colors for the text?:]\n{self.logo_color}\n[Payment?]\n{self.logo_payment}\n[Provided Vectors:]\n{str(self.logo_vectors)}\n```",
            timestamp=datetime.datetime.now(),
            color=discord.Color.purple()
        )
        await database.close()
        await interaction.response.edit_message(embed=embed, view=OrderExtrasButtons())

class OrderExtrasModal(Modal, title="Order Extras"):
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
        database = await aiosqlite.connect("./Databases/data.db")
        await database.execute(f'UPDATE OrderData SET logo_extra = ?, logo_deadline = ? WHERE user_id = {interaction.user.id}', (str(self.logo_extra), str(self.logo_deadline)))
        await database.commit()

        async with database.execute(f"SELECT logo_for, logo_text, logo_color, logo_payment, logo_vector, logo_extra, logo_deadline FROM OrderData WHERE user_id = {interaction.user.id}") as cursor:
            data = await cursor.fetchone()
        async with database.execute(f"SELECT order_no FROM OrderNo ORDER BY order_no DESC") as cursor_2:
            data_2 = await cursor_2.fetchone()
        order_no = 0
        if data_2 is None:
            order_no = 1
            await database.execute("INSERT INTO OrderNo VALUES (1)")
            await database.commit()
        if data_2 is not None:
            order_no = int(data_2[0]) + 1
            await database.execute("UPDATE OrderNo SET order_no = order_no + 1")
            await database.commit()
        message = await interaction.guild.get_channel(config.QUEUE_CHANNEL_ID).send(content=f"**>------- Order ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {interaction.user.mention}\n**Order No:** `{order_no}`\n**Order Status:** `Pending`")
        await database.execute(f"INSERT INTO OrdersInformation VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (order_no, interaction.user.id, data[0], data[1], data[2], data[3], data[4], data[5], data[6]))
        await database.execute(f"DELETE FROM OrderData WHERE user_id = {interaction.user.id}")
        await database.commit()
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
                await database.execute(f"INSERT INTO OrderMessage VALUES ({embed_msg.id}, {message.id})")
                await database.execute(f"INSERT INTO Orders VALUES ({embed_msg.id}, {order_no}, {interaction.user.id}, {message.id}, 'pending', 'no', {round(datetime.datetime.now().timestamp())}, NULL, NULL)")
                await database.commit()
                await database.close()

#------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------SELECT MENUS-----------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------

class OrderStatusSelect(discord.ui.Select):
    def __init__(self):
        status = [
            discord.SelectOption(label="Processing", description="Set order status as processing"),
            discord.SelectOption(label="Sketching", description="Set order status as sketching"),
            discord.SelectOption(label="Waiting for Approval", description="Set order status as waiting for approval"),
            discord.SelectOption(label="Finalizing", description="Set order status as finalizing"),
            discord.SelectOption(label="Waiting for Payment", description="Set order status as waiting for payment"),
            discord.SelectOption(label="Paid", description="Set order status as paid"),
            discord.SelectOption(label="Refunded", description="Set order status as refunded")
        ]

        super().__init__(placeholder="Change order status...", min_values=1, max_values=1, options=status, custom_id="status_selector")
    
    async def callback(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            database = await aiosqlite.connect("./Databases/data.db")
            async with database.execute(f"SELECT message_id FROM OrderMessage WHERE embed_id = {interaction.message.id}") as cursor:
                data = await cursor.fetchone()

            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            await database.execute(f"UPDATE Orders SET status = '{self.values[0]}' WHERE embed_id = {interaction.message.id}")
            await database.commit()
            async with database.execute(f"SELECT order_no, user_id, status, priority, timestamp FROM Orders WHERE embed_id = {interaction.message.id}") as cursor2:
                order_data = await cursor2.fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[1])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[4]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[2]).capitalize()}`\n**Priority Order:** `{str(order_data[3]).capitalize()}`")
            await interaction.response.send_message(content=f"{config.EMOJI_DONE} Order status updated!", ephemeral=True)
            await database.close()

        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)
