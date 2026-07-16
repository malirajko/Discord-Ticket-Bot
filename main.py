import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import datetime

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
# 2. INICIJALIZACIJA BOTA I UKLJUČIVANJE INTENTS-A
# ==========================================
intents = discord.Intents.all() # Promenjeno na all() da bi kreiranje kanala i permisije radile bez greške
intents.message_content = True

bot = commands.Bot(command_prefix="ti!", intents=intents)
bot.remove_command('help')  # Isključujemo fabrički help

# ==========================================
# 3. FORMULARI (MODALS) ZA TIKETE
# ==========================================

# --- FORMULAR 1: POMOĆ / SUPPORT ---
class SupportFormular(discord.ui.Modal, title="Pomoć / Support"):
    discord_username = discord.ui.TextInput(label="Discord Username", placeholder="Npr. marko123", min_length=2, max_length=50)
    pitanje = discord.ui.TextInput(label="Koje je vaše pitanje?", placeholder="Opišite detaljno šta vam je potrebno...", style=discord.TextStyle.long, min_length=5)

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

        ticket_channel = await guild.create_text_channel(name=f"support-{interaction.user.name}", overwrites=overwrites)

        embed = discord.Embed(title=f"🔧 Novi Support Tiket - {interaction.user.display_name}", color=0x7ED321)
        embed.add_field(name="Discord Korisnik", value=self.discord_username.value, inline=False)
        embed.add_field(name="Pitanje", value=self.pitanje.value, inline=False)

        await ticket_channel.send(embed=embed, view=TicketZatvoriView())
        await interaction.followup.send(f"Vaš tiket za pomoć je uspešno otvoren! Pogledajte kanal: {ticket_channel.mention}", ephemeral=True)


# --- FORMULAR 2: STAFF PRIJAVA (Tvoj originalni formular sa slike) ---
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

        ticket_channel = await guild.create_text_channel(name=f"prijava-{interaction.user.name}", overwrites=overwrites)

        embed = discord.Embed(title=f"👑 Nova Staff Prijava - {interaction.user.display_name}", color=0x7ED321)
        embed.add_field(name="Ime i Godište", value=self.ime.value, inline=False)
        embed.add_field(name="Discord", value=self.discord_username.value, inline=False)
        embed.add_field(name="Facebook Profil", value=self.fb_link.value, inline=False)
        embed.add_field(name="SAMP Znanje", value=self.iskustvo.value, inline=False)
        embed.add_field(name="Zašto baš on?", value=self.zasto_bas_ti.value, inline=False)

        await ticket_channel.send(embed=embed, view=TicketZatvoriView())
        await interaction.followup.send(f"Vaša prijava je uspešno napravljena! Pogledajte kanal: {ticket_channel.mention}", ephemeral=True)


# --- FORMULAR 3: BUG REPORT ---
class BugFormular(discord.ui.Modal, title="Bug Report"):
    discord_username = discord.ui.TextInput(label="Discord Username", placeholder="Npr. marko123", min_length=2, max_length=50)
    vrsta_buga = discord.ui.TextInput(label="Kakvu vrstu bug-a ste pronašli?", placeholder="Opišite bug detaljno (gde se dešava, kako)...", style=discord.TextStyle.long, min_length=5)
    dokaz = discord.ui.TextInput(label="Dokaz (slika/video)", placeholder="Npr. imgur.com/... ili youtube.com/...", min_length=5)

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

        ticket_channel = await guild.create_text_channel(name=f"bug-{interaction.user.name}", overwrites=overwrites)

        embed = discord.Embed(title=f"🚫 Novi Bug Report - {interaction.user.display_name}", color=0x7ED321)
        embed.add_field(name="Discord Korisnik", value=self.discord_username.value, inline=False)
        embed.add_field(name="Opis Bug-a", value=self.vrsta_buga.value, inline=False)
        embed.add_field(name="Dokaz", value=self.dokaz.value, inline=False)

        await ticket_channel.send(embed=embed, view=TicketZatvoriView())
        await interaction.followup.send(f"Vaš tiket za bug je uspešno otvoren! Pogledajte kanal: {ticket_channel.mention}", ephemeral=True)


# ==========================================
# 4. DUGMAD ZA OTVARANJE I ZATVARANJE TIKETA
# ==========================================
class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # 🔧 DUGME 1: POMOĆ / SUPPORT
    @discord.ui.button(label="Pomoć / Support", style=di
scord.ButtonStyle.secondary, custom_id="otvori_support_dugme", emoji="🔧")
    async def otvori_support(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SupportFormular())

    # 📋 DUGME 2: STAFF PRIJAVA
    @discord.ui.button(label="Otvori Konkurs", style=discord.ButtonStyle.primary, custom_id="otvori_konkurs_dugme", emoji="📋")
    async def otvori_konkurs(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(StaffFormular())

    # 🚫 DUGME 3: BUG REPORT
    @discord.ui.button(label="Bug Report", style=discord.ButtonStyle.danger, custom_id="otvori_bug_dugme", emoji="🚫")
    async def otvori_bug(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BugFormular())


class TicketZatvoriView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zatvori Tiket", style=discord.ButtonStyle.danger, custom_id="zatvori_tiket_dugme")
    async def zatvori_tiket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Ovaj tiket će biti obrisan za 5 sekundi...")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=5))
        await interaction.channel.delete()

# ==========================================
# 5. DOGAĐAJI (EVENTS) + CUSTOM STATUS
# ==========================================
@bot.event
async def on_ready():
    print(f'Ticket bot spreman!')
    bot.add_view(TicketButton())
    bot.add_view(TicketZatvoriView())
    await bot.change_presence(activity=discord.CustomActivity(name="Za Pomoc: ti!help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

# ==========================================
# 6. BOT KOMANDE
# ==========================================

# ➡️ KOMANDA: ti!setup (Sada postavlja sva 3 dugmeta)
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.message.delete()
    
    embed = discord.Embed(
        title="📩 NEXT LEVEL | PODRŠKA, KONKURSI I PRIJAVE",
        description=(
            "Dobrodošli u centar za podršku Next Level zajednice.\n"
            "Kliknite na odgovarajuće dugme ispod kako biste otvorili formular za vaš zahtev.\n\n"
            "🔧 **Pomoć / Support** — Imate pitanje ili vam je potrebna pomoć oko nečega.\n"
            "📋 **Otvori Konkurs** — Želite da se prijavite za naš Staff tim.\n"
            "🚫 **Bug Report** — Pronašli ste grešku/bug na serveru ili u modovima."
        ),
        color=0x7ED321 # Tvoja prepoznatljiva zelena boja
    )
    await ctx.send(embed=embed, view=TicketButton())

# ==========================================
# 7. POKRETANJE BOTA
# ==========================================
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
