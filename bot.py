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


@bot.command(name="locale", help="Get number of confirmed people in locale. usage : /coco locale OR /coco locale [location]")
async def locale(ctx):
	return_str = ""
	args = ctx.message.content.split(' ')
	date, data = get_locale_infected()
	return_str += "更新日期: {} \n".format(date)
	return_str += "\n\t\t\t\t（本日新增人數／累積確診人數）\n"
	is_specific = False
	if len(args) > 2:
		arg_location = args[2]
		is_specific = True

	for location, number in data:
		total = number[0]
		new_cases = 0
		if len(number) > 1:
			new_cases = number[1]
		if is_specific:
			if location == arg_location:
				return_str += "{}:{:>4d}\t/{:>4d}\n".format(location, int(new_cases), int(total))
				break
			else:
				continue
		return_str += "{}:{:>4d}\t/{:>4d}\n".format(location, int(new_cases), int(total))
	await ctx.send(return_str)


def get_locale_infected():
	url = "https://covid-19.nchc.org.tw/dt_005-covidTable_taiwan.php"
	html = requests.get(url, verify=False)
	sp = BeautifulSoup(html.text, 'html5lib')
	date = sp.find(attrs={"class": "col-lg-4 col-sm-6 text-center my-5"}).text
	date = date.replace("\n", "")
	date = date.replace("\t", "")
	# print(date)
	boxes = sp.find_all(attrs={"class": "col-lg-12 main"})
	links = boxes[1].find_all('a')
	data = []
	for link in links:
		span = link.find("span")
		text = span.text
		location, numbers = text.split(" ")
		numbers = numbers.split("+")
		numbers[-1] = "".join(numbers[-1].split())  # 去除\xa0
		# print(location, numbers)
		data.append([location, numbers])
	return [date, data]


def check(value):
	value = value.replace("\'", "\'\'")
	value = value.replace("\"", "\\\"")
	return value


lastdate = ""
@tasks.loop(minutes=5)
async def job():
	date, data = get_locale_infected()
	if date == lastdate:
		return
	lastdate = date
	conn = sqlite3.connect(DB_NAME)
	for location, numbers in data:
		if len(numbers) == 1:
			continue
		if int(numbers[1]) > 0:
			rows = conn.execute("select * from user where location = '{}'".format(location))
			for row in rows:
				user = await bot.fetch_user(int(row[0]))
				await user.send("更新日期:{} {} 新增確診:{}例".format(date, location, numbers[1]))

	conn.commit()
	conn.close()

	# async for g in bot.fetch_guilds():
	# 	print(g.name)
	# 	async for m in g.fetch_members():
	# 		if not m.bot:
	# 			print("{}\t{}".format(m.name, m.id))


job.start()
bot.run(TOKEN)

print("finish")
