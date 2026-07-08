import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# 1. PODEŠAVANJE FLASK SERVERA ZA ODRŽAVANJE BUDNOSTI (keep_alive)
app = Flask('')

@app.route('/')
def home():
    return "Staff prijava bot je ziv!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. INICIJALIZACIJA BOTA I GAŠENJE FABRIČKOG HELP-A
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="ti!", intents=intents)
bot.remove_command('help')  # Isključujemo fabrički sivi help

# 3. DOGAĐAJI (EVENTS)
@bot.event
async def on_ready():
    print(f'Ticket bot spreman!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

# 4. KOMANDA: ti!setup
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="📋 Konkurs za Staff Tim",
        description="Ukoliko želiš da postaneš deo našeg Staff tima, klikni na dugme ispod i odgovori na pitanja u formularu.",
        color=discord.Color.purple()
    )
    # Ovde se pretpostavlja da je klasa TicketButton definisana negde iznad ili u uvozu
    # Ako ti je u kôdu bila definisana i klasa za dugme, spusti je iznad ove komande
    await ctx.send(embed=embed, view=TicketButton())

# 5. NOVA PRILAGOĐENA KOMANDA: ti!help
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

# 6. POKRETANJE BOTA (Mora da bude na samom dnu fajla)
keep_alive()
token = os.environ.get("DISCORD_TOKEN")
bot.run(token)
