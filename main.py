import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import datetime

# ==========================================
# 1. FLASK SERVER ZA KEEP-ALIVE
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
bot.remove_command('help')  # Isključujemo fabrički help

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

    @discord.ui.button(label="Zatvori Tiket", style=discord.ButtonStyle.danger, custom_id="zatvori_tiket_dugme")
    async def zatvori_tiket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ovaj tiket će biti obrisan za 5 sekundi...")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

# ==========================================
# 5. DOGAĐAJI (EVENTS)
# ==========================================
@bot.event
async def on_ready():
    print(f'Ticket bot spreman!')
    bot.add_view(TicketButton())
    bot.add_view(TicketZatvoriView())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

# ==========================================
# 6. BOT KOMANDE
# ==========================================
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="📋 Konkurs za Staff Tim",
        description="Ukoliko želiš da postaneš deo našeg Staff tima, klikni na dugme ispod i odgovori na pitanja u formularu.",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=TicketButton())

@bot.command(name="help")
async def ticket_help(ctx):
    opis_poruke = (
        "<:arrow_join6:1516798345568456714> Kako da se prijavis?\n"
        "- __U kanalu: https://discord.com/channels/1404528302559068200/1523627320852873348 kliknite na plavo dugme/gumb__ **Otvori Konkurs** __nakon toga ce vam izaci formular koji morate da popunite nakon toga ce prijava biti poslata.__\n\n"
        "<:arrow_join6:1516798345568456714> Sta treba da bi postali deo administracije?\n"
        "- __Potrebno je osnovno znanje u SAMP modovima,kreshovima itd, aktivan facebook nalog,aktivnost na serveru,kulturnost,znanje da se resi odredjena situacija.__\n\n"
        "<:arrow_join6:1516798345568456714> Privilegije nase administracije\n"
        "- __Kao deo nase administracije na kraju svakog meseca clan koji se najbolje dokaze dobija neku placenu platformu kao sto su: Netflix,Spotify Premium,HBO,Disney ili nitro pretplata.__\n\n"
        "<:arrow_join6:1516798345568456714> **UKOLIKO ZELIS DA POSTANES DEO ADMINSTRACIJE JAVI NAM SE PUTEM TIKETA !**"
    )
    
    embed = discord.Embed(
        title="<:arrow_join6:1516798345568456714> **__Next Level Ticket Help Bot__**",
        description=opis_poruke,
        color=0x7ED321
    )
    await ctx.send(embed=embed)

# ==========================================
# 7. POKRETANJE BOTA
# ==========================================
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
