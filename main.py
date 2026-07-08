import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask
import asyncio

# --- 1. DEO: Ispravan Flask Web Server za Render ---
app = Flask('')
@app.route('/')
def home():
    return "Staff prijava bot je ziv!"
    
def run():
    # Render automatski dodeljuje PORT, ako ga nema koristi se 10000
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- OSTATAK KODA ZA TICKET BOTA OSTAJE ISTI ---
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Zatvori i Obriši", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Prijava se briše za 5 sekundi...")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Greska pri brisanju kanala: {e}")

class StaffApplicationModal(discord.ui.Modal, title="Prijava za Staff Tim"):
    pitanje1 = discord.ui.TextInput(label="1. Lični podaci", style=discord.TextStyle.short, required=True)
    pitanje2 = discord.ui.TextInput(label="2. Prethodno iskustvo", style=discord.TextStyle.long, required=True)
    pitanje3 = discord.ui.TextInput(label="3. Dnevna aktivnost", style=discord.TextStyle.short, required=True)
    pitanje4 = discord.ui.TextInput(label="4. Zašto baš ti?", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        clean_name = f"prijava-{user.name.lower()}".replace(" ", "-")
        existing_channel = discord.utils.get(guild.channels, name=clean_name)
        if existing_channel:
            await interaction.response.send_message(f"Već imaš aktivnu prijavu ovde: {existing_channel.mention}", ephemeral=True)
            return
        await interaction.response.send_message("Kreiram tvoju prijavu, sačekaj trenutak...", ephemeral=True)
        current_category = interaction.channel.category
        ticket_channel = await guild.create_text_channel(name=clean_name, category=current_category)
        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)
        embed = discord.Embed(
            title=f"📝 Nova Prijava za Staffa — {user.name}",
            description=f"Korisnik {user.mention} je uspešno poslao prijavu.",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 1. Lični podaci:", value=self.pitanje1.value, inline=False)
        embed.add_field(name="🛠️ 2. Prethodno iskustvo:", value=self.pitanje2.value, inline=False)
        embed.add_field(name="⏰ 3. Dnevna aktivnost:", value=self.pitanje3.value, inline=False)
        embed.add_field(name="❓ 4. Zašto baš on:", value=self.pitanje4.value, inline=False)
        await ticket_channel.send(embed=embed, view=CloseTicketView())

class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="📝 Otvori Konkurs", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffApplicationModal())

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="ti!", intents=intents)

@bot.event
async def on_ready():
    bot.add_view(TicketButton())
    bot.add_view(CloseTicketView())
    print(f'Ticket bot spreman!')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="📋 Konkurs za Staff Tim",
        description="Ukoliko želiš da postaneš deo našeg Staff tima, klikni na dugme ispod i odgovori na pitanja u formularu.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=TicketButton())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)

@bot.command()
async def help(ctx):
    poruka = (
        "<:arrow_join6:1516798345568456714> **__Next Level Ticket Help Bot__**\n\n"
        "<:arrow_join6:1516798345568456714> Kako da se prijavis?\n"
        "- __U kanalu: https://discord.com/channels/1404528302559068200/1523627320852873348 kliknite na plavo dugme/gumb__ **Otvori Konkurs** __nakon toga ce vam izaci formular koji morate da popunite nakon toga ce prijava biti poslata.__\n\n"
        "<:arrow_join6:1516798345568456714> Sta treba da bi postali deo administracije?\n"
        "- __Potrebno je osnovno znanje u SAMP modovima,kreshovima itd, aktivan facebook nalog,aktivnost na serveru,kulturnost,znanje da se resi odredjena situacija.__\n\n"
        "<:arrow_join6:1516798345568456714> Privilegije nase administracije\n"
        "- __Kao deo nase administracije na kraju svakog meseca clan koji se najbolje dokaze dobija neku placenu platformu kao sto su: Netflix,Spotify Premium,HBO,Disney ili nitro pretplata.__\n\n"
        "<:arrow_join6:1516798345568456714> **UKOLIKO ZELIS DA POSTANES DEO ADMINSTRACIJE JAVI NAM SE PUTEM TIKETA !**"
    )
    await ctx.send(poruka)
