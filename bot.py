import discord
from discord.ext import commands
import json
import csv
from mysql import connector
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)


config = {}
with open("config.json", 'r') as configFile:
    config = json.load(configFile)

db_connect = connector.connect(
            host = config["db_host"],
            user = config["db_user"],
            password = config["db_pass"],
            database = config["db_name"],
            port = config["db_port"]
        )
db_cursor = db_connect.cursor()


@bot.command()
async def insertOrder(ctx, name, quantity, website, type):
    # Inserts the new order into the form, NULL for ID to automatically increment.
    db_cursor.execute("INSERT INTO ORDER_FORM (ID, Name, Quantity, Website, Type) VALUES (NULL, %s, %s, %s, %s);",
                      (name, quantity, website, type))
    db_connect.commit()
    await ctx.send(f"Inserted ({name}, {quantity}, {website}, {type}) into order form!")


@bot.command()
async def getForm(ctx):
    db_cursor.execute("SELECT NAME, QUANTITY, WEBSITE, TYPE FROM ORDER_FORM;")
    query = db_cursor.fetchall()
    filename = "order_form.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerows(query)
    await ctx.send(file=discord.File(filename))
    os.remove(filename)


@bot.command()
@commands.has_role("Admin")
async def clearForm(ctx):
    db_cursor.execute("TRUNCATE ORDER_FORM;")
    db_connect.commit()


bot.run(config["token"])
