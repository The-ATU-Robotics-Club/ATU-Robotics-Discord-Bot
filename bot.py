import discord
from discord.ext import commands
from discord import app_commands
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


@bot.event
async def on_ready():
    print("Bot is ready.")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)


@bot.tree.command(name="insertorder")
async def insertorder(interaction: discord.Interaction, 
                      name: str, 
                      quantity: int, 
                      website: str, 
                      type: str):
    # Inserts the new order into the form, NULL for ID to automatically increment.
    db_cursor.execute("INSERT INTO ORDER_FORM (ID, Name, Quantity, Website, Type) VALUES (NULL, %s, %s, %s, %s)",
                      (name, quantity, website, type, ))
    db_connect.commit()
    await interaction.response.send_message(f"Inserted ({name}, {quantity}, {website}, {type}) into order form!")


@bot.tree.command(name="removeorder")
async def removeorder(interaction: discord.Interaction, 
                      id: int):
    db_cursor.execute("DELETE FROM ORDER_FORM WHERE ID = %s", (id, ))
    db_connect.commit()
    await interaction.response.send_message(f"Order #{id} removed!")


@bot.tree.command(name="getorders")
async def getorders(interaction: discord.Interaction):
    db_cursor.execute("SELECT * FROM ORDER_FORM")
    query = db_cursor.fetchall()
    filename = "order_form.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerows(query)
    await interaction.response.send_message(file=discord.File(filename))
    os.remove(filename)


@bot.tree.command(name="clearorders")
@commands.has_role("Admin")
async def clearorders(interaction: discord.Interaction):
    db_cursor.execute("TRUNCATE ORDER_FORM")
    db_connect.commit()


bot.run(config["token"])
