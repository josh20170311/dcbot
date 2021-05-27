import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix = '!')

@bot.command(name = '消毒')
async def Test(ctx):
    await ctx.send('<:disinfection:845207148559335435>')
    
@bot.command(name = '確診')
async def infected(ctx):
    url = 'https://covid19dashboard.cdc.gov.tw/dash3'
    html = requests.get(url)
    sp = BeautifulSoup(html.text, 'html5lib')
    site_json = json.loads(sp.text)
    embed = discord.Embed(title = 'COVID-19', url = 'https://www.cdc.gov.tw/', color = 0xFF0000)
    keys = list(site_json['0'].keys())
    values = list(site_json['0'].values())
    for i in range(len(keys)):
        embed.add_field(name = keys[i], value = values[i], inline = False)
    await ctx.send(embed = embed)
    
bot.run(TOKEN)