import os
import json
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import requests
import sqlite3
from bs4 import BeautifulSoup

DB_NAME = "./db/users.db"

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intent = discord.Intents.default()
intent.members = True

bot = commands.Bot(command_prefix='/coco ', intents=intent)


@bot.event
async def on_ready():
	print("on ready")


@bot.command(name='alcohol', help="Use alcohol to disinfect.")
async def alcohol(ctx):
	await ctx.send('<:alcohol:848182559644188674>')


@bot.command(name="hi", help="Say hi to coco.")
async def hi(ctx):
	await ctx.send("hi")


@bot.command(name="news", help="Get news from CDC.")
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


@bot.command(name='infected', help="Get population of infected people in taiwan from CDC.")
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


@bot.command(name='set', help='Set location. usage : /coco set [location]')
async def set_(ctx):
	args = ctx.message.content.split(' ')
	author = ctx.message.author
	if len(args) < 3:
		return
	conn = sqlite3.connect(DB_NAME)
	rows = conn.execute("select count(*) from user where id = {}".format(author.id)).fetchone()
	location = check(args[2])
	name = check(author.name)

	if rows[0] == 0:
		sql_str = "insert into user values({}, '{}', '{}')".format(author.id, name, location)
	else:
		sql_str = "update user set name = '{}', location = '{}' where id = {}".format(name, location, author.id)
	print(sql_str)
	conn.execute(sql_str)
	conn.commit()
	conn.close()


@bot.command(name="locale", help="Get number of comfirmed people in locale.")
async def locale(ctx):
	author = ctx.message.author

	conn = sqlite3.connect(DB_NAME)
	rows = conn.execute("select location from user where id = {}".format(author.id)).fetchone()

	if (rows[0] == None):
		await ctx.send("location not set")


def getLocleNumber():
	url = "https://covid-19.nchc.org.tw/dt_005-covidTable_taiwan.php"
	html = requests.get(url, verify=False)
	sp = BeautifulSoup(html.text, 'html5lib')
	date = sp.find(attrs={"class": "col-lg-4 col-sm-6 text-center my-5"}).text
	date = date.replace("\n", "")
	date = date.replace("\t", "")
	# print(date)
	boxes = sp.find_all(attrs={"class": "col-lg-12 main"})
	output = ''
	site_domain = 'https://www.cdc.gov.tw'
	links = boxes[1].find_all('a')
	data = []
	for link in links:
		span = link.find("span")
		text = span.text
		location, number = text.split(" ")
		number = number.split("+")
		number[-1] = "".join(number[-1].split())  # 去除\xa0
		# print(location, number)
		data.append([location, number])
	return [date, data]


def check(value):
	value = value.replace("\'", "\'\'")
	value = value.replace("\"", "\\\"")
	return value


@tasks.loop(hours=24)
async def job():
	async for g in bot.fetch_guilds():
		print(g.name)
		async for m in g.fetch_members():
			if not m.bot:
				print("{}\t{}".format(m.name, m.id))


job.start()
bot.run(TOKEN)

print("finish")
