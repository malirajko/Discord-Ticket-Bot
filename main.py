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
    
    pitanje1 = discord.ui.TextInput(
        label="1. Lični podaci",
        style=discord.TextStyle.short,
        placeholder="Unesi svoje ime, godište i IC ime sa servera...",
        required=True
    )
    
    pitanje2 = discord.ui.TextInput(
        label="2. Prethodno iskustvo",
        style=discord.TextStyle.long,
        placeholder="Na kojim serverima si bio Staff i na kojoj poziciji?",
        required=True
    )

    pitanje3 = discord.ui.TextInput(
        label="3. Dnevna aktivnost",
        style=discord.TextStyle.short,
        placeholder="Koliko sati dnevno možeš da provedeš na serveru/Discordu?",
        required=True
    )
    
    pitanje4 = discord.ui.TextInput(
        label="4. Zašto baš ti?",
        style=discord.TextStyle.long,
        placeholder="Zašto bismo izabrali baš tebe i šta možeš da doprineseš timu?",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        
        existing_channel = discord.utils.get(guild.channels, name=f"prijava-{user.name.lower()}")
        if existing_channel:
            await interaction.response.send_message(f"Već imaš aktivnu prijavu ovde: {existing_channel.mention}", ephemeral=True)
            return

        await interaction.response.send_message("Kreiram tvoju prijavu, sačekaj trenutak...", ephemeral=True)

        # Dozvole: Korisnik vidi, ali ne može da piše dok admini ne odobre (da ne spama)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        admin_role = discord.utils.get(guild.roles, name="Administrator")
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)

        ticket_channel = await guild.create_text_channel(name=f"prijava-{user.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"📝 Nova Prijava za Staffa — {user.name}",
            description=f"Korisnik {user.mention} je popunio konkurs.",
            color=discord.Color.blue()
        )
        embed.add_field(name="👤 Podaci:", value=self.pitanje1.value, inline=False)
        embed.add_field(name="🛠️ Iskustvo:", value=self.pitanje2.value, inline=False)
        embed.add_field(name="⏰ Aktivnost:", value=self.pitanje3.value, inline=False)
        embed.add_field(name="❓ Zašto on:", value=self.pitanje4.value, inline=False)
        
        close_view = discord.ui.View(timeout=None)
        close_button = discord.ui.button(label="🔒 Zatvori i Obriši", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
        
        async def close_callback(close_interaction: discord.Interaction):
            await close_interaction.response.send_message("Prijava se briše za 5 sekundi...")
            await asyncio.sleep(5)
            await close_interaction.channel.delete()
            
        close_button.callback = close_callback
        close_view.add_item(close_button)

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
intents.presences = True

bot = commands.Bot(command_prefix="t!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot je spreman! Ulogovan kao {bot.user}')
    bot.add_view(TicketButton())
    await bot.change_presence(activity=discord.Game(name="t!setup"))

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
