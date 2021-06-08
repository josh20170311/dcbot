import os
import json
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import threading

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intent = discord.Intents.default()
intent.members = True

bot = commands.Bot(command_prefix='/coco ', intents=intent)


@bot.event
async def on_ready():
	print("on ready")


@bot.command(name='alcohol')
async def alcohol(ctx):
	await ctx.send('<:alcohol:848182559644188674>')


@bot.command(name="hi")
async def hi(ctx):
	await ctx.send("hi")


@bot.command(name="news")
async def news(ctx):
	url = "https://www.cdc.gov.tw/Bulletin/List/MmgtpeidAR5Ooai4-fgHzQ"
	html = requests.get(url)
	sp = BeautifulSoup(html.text, 'html5lib')
	boxes = sp.find_all(attrs={"class": "content-boxes-v3"})
	output = ''
	site_domain = 'https://www.cdc.gov.tw'
	for box in boxes:
		links = box.find_all('a')
		for link in links:
			if link.get('title'):
				# output += link.get('title') + "\n"
				output += site_domain + link.get('href') + '\n'
	await ctx.send(output)


@bot.command(name='infected')
async def infected(ctx):
	url = 'https://covid19dashboard.cdc.gov.tw/dash3'
	html = requests.get(url)
	sp = BeautifulSoup(html.text, 'html5lib')
	site_json = json.loads(sp.text)
	embed = discord.Embed(title='COVID-19', url='https://www.cdc.gov.tw/', color=0xFF0000)
	keys = list(site_json['0'].keys())
	values = list(site_json['0'].values())
	for i in range(len(keys)):
		embed.add_field(name=keys[i], value=values[i], inline=False)
	await ctx.send(embed=embed)


@bot.command(name='set', help='set location [location]')
async def set_(ctx):
	args = ctx.message.content.split(' ')
	author = ctx.message.author
	print(author)
	print(type(author))
	await author.send("ee")
	print(args)
	if len(args) < 4:
		return
	if args[2] == 'location':
		print(args[3] + str(author.id))


@tasks.loop(seconds=20)
async def job():
	async for g in bot.fetch_guilds():
		print(g.name)
		async for m in g.fetch_members():
			if not m.bot:
				print("{}\t{}".format(m.name, m.id))


job.start()
bot.run(TOKEN)

print("finish")
