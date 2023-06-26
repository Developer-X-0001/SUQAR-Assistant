import config
import sqlite3
import discord
import asyncio
import datetime

from discord import ButtonStyle, TextStyle
from discord.ui import View, Modal, Button, TextInput, button

database = sqlite3.connect("./Databases/data.sqlite")

class OrderStatusButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OrderStatusSelect())

    @button(label="Mark as Completed", style=ButtonStyle.green, emoji="<:approved:1062484431513849906>", custom_id="completed", row=1)
    async def completed(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            data = database.execute("SELECT message_id FROM OrderMessage WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.green()
            embed.set_footer(text=f"✅ Order marked as completed")
            database.execute("UPDATE Orders SET status = ? WHERE embed_id = ?", ('completed', interaction.message.id,)).connection.commit()
            order_data = database.execute("SELECT order_no, order_type, user_id, status, priority, timestamp FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            embed.description = f"`Ticket {order_data[0]}`. Thanks for buying! Hope you will order again!\n\nOrder Review:\n```css\n[Rating]\nNot rated\n[Review]\nNone\n```"
            await interaction.response.edit_message(embed=embed, view=OrderRateButtons())
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[2])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[5]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[3]).capitalize()}`\n**Order Type:** `{str(order_data[1]).capitalize()}`\n**Priority Order:** `{str(order_data[4]).capitalize()}`")
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)

    @button(label="Cancel Order", style=ButtonStyle.red, emoji="<:rejected:1062484427281809479>", custom_id="cancelled", row=1)
    async def cancelled(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            data = database.execute("SELECT message_id FROM OrderMessage WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.red()
            embed.set_footer(text=f"❌ Order cancelled")
            await interaction.response.edit_message(embed=embed, view=OrderDeleteButton())
            database.execute("UPDATE Orders SET status = ? WHERE embed_id = ?", ('cancelled', interaction.message.id,)).connection.commit()
            order_data = database.execute("SELECT order_no, order_type, user_id, status, priority, timestamp FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[2])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[5]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[3]).capitalize()}`\n**Order Type:** `{str(order_data[1]).capitalize()}`\n**Priority Order:** `{str(order_data[4]).capitalize()}`")
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)
    
    @button(label="Mark as Priority Order ->", style=ButtonStyle.gray, custom_id="mark_dead", disabled=True, row=2)
    async def mark_dead(self, interaction: discord.Interaction, button: Button):
        return

    @button(style=ButtonStyle.blurple, emoji="⭐", custom_id="mark", row=2)
    async def mark(self, interaction: discord.Interaction, button: Button):
        role = interaction.guild.get_role(config.SUQAR_ROLE_ID)
        if role in interaction.user.roles:
            data = database.execute("SELECT message_id FROM OrderMessage WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            embed = interaction.message.embeds[0]
            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            embed.color = discord.Color.gold()
            embed.set_footer(text="⭐ Order marked as priority")
            self.mark.disabled = True
            self.mark.style = ButtonStyle.gray
            await interaction.response.edit_message(embed=embed, view=self)
            database.execute("UPDATE Orders SET priority = ? WHERE embed_id = ?", ('yes', interaction.message.id,)).connection.commit()
            order_data = database.execute("SELECT order_no, order_type, user_id, status, priority, timestamp FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[2])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[5]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[3]).capitalize()}`\n**Order Type:** `{str(order_data[1]).capitalize()}`\n**Priority Order:** `{str(order_data[4]).capitalize()}`")
        if not role in interaction.user.roles:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You aren't authorized to do that!", ephemeral=True)

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
            data = database.execute("SELECT message_id FROM OrderMessage WHERE embed_id = ?", (interaction.message.id,)).fetchone()

            queue_channel = interaction.guild.get_channel(config.QUEUE_CHANNEL_ID)
            order_msg = await queue_channel.fetch_message(data[0])

            database.execute("UPDATE Orders SET status = ? WHERE embed_id = ?", (self.values[0], interaction.message.id,)).connection.commit()
            order_data = database.execute("SELECT order_no, order_type, user_id, status, priority, timestamp FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
            
            user = interaction.client.get_guild(config.GUILD_ID).get_member(order_data[2])
            await order_msg.edit(content=f"**>------- Order ----[ <t:{order_data[5]}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_data[0]}`\n**Order Status:** `{str(order_data[3]).capitalize()}`\n**Order Type:** `{str(order_data[1]).capitalize()}`\n**Priority Order:** `{str(order_data[4]).capitalize()}`")
            await interaction.response.send_message(content=f"{config.EMOJI_DONE} Order status updated!", ephemeral=True)

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
        data = database.execute("SELECT order_no, order_type, user_id, stars, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
        if data is not None:
            user = interaction.guild.get_member(data[2])
            order_no = int(data[0])
            if data[3] is None and data[4] is None:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You can't post empty review!", ephemeral=True)

            else:
                if data[3] is None:
                    await interaction.response.send_message(content="**Please rate the order!**", ephemeral=True)
                    return
                
                if data[4] is None:
                    await interaction.response.send_message(content="**Please leave a review on the order!**", ephemeral=True)
                    return
                
                stars = int(data[3])
                review = str(data[4])

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

                await review_channel.send(content=f"**>------- Review ----[ <t:{round(datetime.datetime.now().timestamp())}:R> ]----<**\n**Name:** {user.mention}\n**Order No:** `{order_no}`\n**Order Type:** `{str(data[1]).capitalize()}`\n**Rating:** `{stars}`\n**Review:**\n`{review}`")
                await interaction.response.edit_message(view=OrderDeleteButton())
            
        if data is None:
            await interaction.response.send_message(content=f"{config.EMOJI_ERROR} You can't post empty review!", ephemeral=True)
    
    @button(label="Nevermind", style=ButtonStyle.red, custom_id="ratenvm", row=0)
    async def noReview(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(view=OrderDeleteButton())

    @button(label="1", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate1", row=1)
    async def rate1(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
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

                database.execute("UPDATE Orders SET stars = 1 WHERE embed_id = ?", (interaction.message.id,)).connection.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)

    @button(label="2", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate2", row=1)
    async def rate2(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
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

                database.execute("UPDATE Orders SET stars = 2 WHERE embed_id = ?", (interaction.message.id,)).connection.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
    
    @button(label="3", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate3", row=1)
    async def rate3(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
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

                database.execute("UPDATE Orders SET stars = 3 WHERE embed_id = ?", (interaction.message.id,)).connection.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
            
    @button(label="4", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate4", row=1)
    async def rate4(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
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

                database.execute("UPDATE Orders SET stars = 4 WHERE embed_id = ?", (interaction.message.id,)).connection.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)
            
    @button(label="5", style=ButtonStyle.blurple, emoji="⭐", custom_id="rate5", row=1)
    async def rate5(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id, review FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
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

                database.execute("UPDATE Orders SET stars = 5 WHERE embed_id = ?", (interaction.message.id,)).connection.commit()
                await interaction.response.edit_message(embed=embed, view=self)
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)

    @button(label="Add Review", style=ButtonStyle.blurple, custom_id="review", row=2)
    async def leaveReview(self, interaction: discord.Interaction, button: Button):
        data = database.execute("SELECT order_no, user_id FROM Orders WHERE embed_id = ?", (interaction.message.id,)).fetchone()
        
        if data is not None:
            user = interaction.guild.get_member(data[1])
            if interaction.user == user:
                await interaction.response.send_modal(RateModal(self))
            
            if interaction.user != user:
                await interaction.response.send_message(content=f"{config.EMOJI_ERROR} Only the client is authorized to rate the order!", ephemeral=True)

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
        embed = interaction.message.embeds[0]
        description_to_list = embed.description.split("\n")
        description_to_list.remove(description_to_list[-2])
        description_to_list.insert(-1, str(self.input))
        description_to_string = ''
        for i in description_to_list:
            description_to_string += i + "\n"
        embed.description = description_to_string
        
        database.execute("UPDATE Orders SET review = ?", (self.input.value,)).connection.commit()
        view = self.view
        view.leaveReview.label = "Edit Review"
        await interaction.response.edit_message(embed=embed, view=view)