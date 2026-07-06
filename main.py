import discord
from discord.ext import commands
import os
from threading import Thread
from flask import Flask
import asyncio

# --- 1. DEO: Flask Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "Staff prijava bot je ziv!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. DEO: Formular (Modal) ---
class StaffApplicationModal(discord.ui.Modal, title="Prijava za Staff Tim"):
    
    pitanje1 = discord.ui.TextInput(label="1. Lični podaci", style=discord.TextStyle.short, required=True)
    pitanje2 = discord.ui.TextInput(label="2. Prethodno iskustvo", style=discord.TextStyle.long, required=True)
    pitanje3 = discord.ui.TextInput(label="3. Dnevna aktivnost", style=discord.TextStyle.short, required=True)
    pitanje4 = discord.ui.TextInput(label="4. Zašto baš ti?", style=discord.TextStyle.long, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        # Provera duplih kanala po imenu
        clean_name = f"prijava-{user.name.lower()}".replace(" ", "-")
        existing_channel = discord.utils.get(guild.channels, name=clean_name)
        if existing_channel:
            await interaction.response.send_message(f"Već imaš aktivnu prijavu ovde: {existing_channel.mention}", ephemeral=True)
            return

        # Odmah odgovaramo da Discord ne baci grešku
        await interaction.response.send_message("Kreiram tvoju prijavu, sačekaj trenutak...", ephemeral=True)

        # Čisto kreiranje kanala bez ikakvih teških dozvola koje blokiraju Discord
        ticket_channel = await guild.create_text_channel(name=clean_name)
        
        # Odmah dodajemo pravo igraču da vidi SVOJ kanal i da piše
        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)

        # Generisanje poruke sa odgovorima
        embed = discord.Embed(
            title=f"📝 Nova Prijava za Staffa — {user.name}",
            description=f"Korisnik {user.mention} je uspešno poslao prijavu.",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 1. Lični podaci:", value=self.pitanje1.value, inline=False)
        embed.add_field(name="🛠️ 2. Prethodno iskustvo:", value=self.pitanje2.value, inline=False)
        embed.add_field(name="⏰ 3. Dnevna aktivnost:", value=self.pitanje3.value, inline=False)
        embed.add_field(name="❓ 4. Zašto baš on:", value=self.pitanje4.value, inline=False)
        
        close_view = discord.ui.View(timeout=None)
        close_button = discord.ui.Button(label="🔒 Zatvori i Obriši", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
        
        async def close_callback(close_interaction: discord.Interaction):
            await close_interaction.response.send_message("Prijava se briše za 5 sekundi...")
            await asyncio.sleep(5)
            await close_interaction.channel.delete()
            
        close_button.callback = close_callback
        close_view.add_item(close_button)

        # Šaljemo sve odgovore u kanal
        await ticket_channel.send(embed=embed, view=close_view)

# --- 3. DEO: Panel dugme ---
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📝 Otvori Konkurs", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffApplicationModal())

# --- 4. DEO: Konfiguracija bota ---
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="t!", intents=intents)

@bot.event
async def on_ready():
    bot.add_view(TicketButton())
    print(f'Bot je spreman!')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="📋 Konkurs za Staff Tim",
        description="Ukoliko želiš da postaneš deo našeg Staff tima, klikni na dugme ispod i odgovori na pitanja u formularu.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=TicketButton())

# --- 5. DEO: Pokretanje ---
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
