import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask
import asyncio

# --- 1. DEO: Flask Web Server (za 24/7 rad na Renderu) ---
app = Flask('')

@app.route('/')
def home():
    return "Tiket bot je ziv i zdrav!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. DEO: Sistem za Tikete (Dugmići i Interakcija) ---
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Dugme radi zauvek, čak i nakon restarta bota

    @discord.ui.button(label="🎫 Otvori Tiket", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user
        
        # Provera da li korisnik već ima otvoren tiket
        existing_channel = discord.utils.get(guild.channels, name=f"tiket-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Već imaš otvoren tiket ovde: {existing_channel.mention}", ephemeral=True)
            return

        # Dozvole za kanal (samo korisnik, bot i admini vide kanal)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Ako na serveru ima uloga "Administrator", dajemo i njima pristup automatski
        admin_role = discord.utils.get(guild.roles, name="Administrator")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

        # Kreiranje privatnog kanala za tiket
        ticket_channel = await guild.create_text_channel(name=f"tiket-{user.name}", overwrites=overwrites)
        
        # Poruka unutar tiketa i dugme za zatvaranje
        embed = discord.Embed(
            title="🎫 Novi Tiket",
            description=f"Pozdrav {user.mention}, administracija će ti odgovoriti čim stigne.\n\nKlikni na dugme ispod ako želiš da zatvoriš ovaj tiket.",
            color=discord.Color.blue()
        )
        
        close_view = discord.ui.View(timeout=None)
        close_button = discord.ui.button(label="🔒 Zatvori Tiket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
        
        async def close_callback(close_interaction: discord.Interaction):
            await close_interaction.response.send_message("Kanal će biti obrisan za 5 sekundi...")
            await asyncio.sleep(5)
            await close_interaction.channel.delete()
            
        close_button.callback = close_callback
        close_view.add_item(close_button)

        await ticket_channel.send(embed=embed, view=close_view)
        
        # Skrivena potvrda korisniku koji je kliknuo
        await interaction.response.send_message(f"Tvoj tiket je otvoren: {ticket_channel.mention}", ephemeral=True)

# --- 3. DEO: Konfiguracija Bota ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="t!", intents=intents) # Prefiks za ovog bota je t!

@bot.event
async def on_ready():
    print(f'Tiket bot je ulogovan kao {bot.user}')
    bot.add_view(TicketButton()) # Aktivacija trajnog dugmeta
    await bot.change_presence(activity=discord.Game(name="🎫 t!ticket_setup"))

# --- 4. DEO: Komande ---
@bot.command()
@commands.has_permissions(administrator=True) # Samo administratori mogu da postave panel
async def ticket_setup(ctx):
    embed = discord.Embed(
        title="🎫 Podrška / Tiket Sistem",
        description="Ukoliko ti je potrebna pomoć administracije, klikni na dugme ispod da otvoriš privatni tiket kanal.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketButton())

# --- 5. DEO: Pokretanje ---
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
