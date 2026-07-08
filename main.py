import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# ==========================================
# 1. FLASK SERVER ZA KEEP-ALIVE (UptimeRobot)
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "Staff prijava bot je ziv!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ==========================================
# 2. INICIJALIZACIJA BOTA I GAŠENJE DEFAULT HELP-A
# ==========================================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="ti!", intents=intents)
bot.remove_command('help')  # Force gašenje fabričkog help-a

# ==========================================
# 3. FORMULAR (MODAL) ZA STAFF PRIJAVU
# ==========================================
class StaffFormular(discord.ui.Modal, title="Prijava za Staff Tim"):
    ime = discord.ui.TextInput(label="Ime i Godište", placeholder="Npr. Marko, 18", min_length=2, max_length=50)
    discord_username = discord.ui.TextInput(label="Discord Username", placeholder="Npr. marko123", min_length=2, max_length=50)
    fb_link = discord.ui.TextInput(label="Link Facebook profila", placeholder="https://www.facebook.com/...", min_length=10)
    iskustvo = discord.ui.TextInput(label="Znanje o SAMP modovima/krešovima (1-10)", placeholder="Opišite ukratko vaše znanje...", style=discord.TextStyle.long)
    zasto_bas_ti = discord.ui.TextInput(label="Zašto baš ti?", placeholder="Zašto želiš da postaneš deo administracije?", style=discord.TextStyle.long)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        guild = interaction.guild
        admin_role = discord.utils.get(guild.roles, name="Admin")
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        kanal_ime = f"prijava-{interaction.user.name}"
        ticket_channel = await guild.create_text_channel(name=kanal_ime, overwrites=overwrites)

        embed = discord.Embed(title=f"Nova Staff Prijava - {interaction.user.display_name}", color=discord.Color.green())
        embed.add_field(name="Ime i Godište", value=self.ime.value, inline=False)
        embed.add_field(name="Discord", value=self.discord_username.value, inline=False)
        embed.add_field(name="Facebook Profil", value=self.fb_link.value, inline=False)
        embed.add_field(name="SAMP Znanje", value=self.iskustvo.value, inline=False)
        embed.add_field(name="Zašto baš on?", value=self.zasto_bas_ti.value, inline=False)

        await ticket_channel.send(embed=embed, view=TicketZatvoriView())
        await interaction.followup.send(f"Vaša prijava je uspešno napravljena! Pogledajte kanal: {ticket_channel.mention}", ephemeral=True)

# ==========================================
# 4. DUGMAD ZA OTVARANJE I ZATVARANJE TIKETA
# ==========================================
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Otvori Konkurs", style=discord.ButtonStyle.primary, custom_id="otvori_konkurs_dugme")
    async def otvori_konkurs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffFormular())

class TicketZatvoriView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zatvori Tiket", style=discord
