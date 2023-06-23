import discord
from discord.ext import commands
from discord import app_commands
from mysql import connector
import json
import csv
import os
from enum import Enum


class Type(Enum):
    VEX = 1
    Other = 2


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix = '/', intents = intents)


config = {}
with open("config.json", 'r') as configFile:
    config = json.load(configFile)


db_config = {
    "host" : config["db_host"],
    "user" : config["db_user"],
    "password" : config["db_pass"],
    "database" : config["db_name"],
    "port" : config["db_port"]
}

def modify_db(command, params = None):
    db_connect = connector.connect(**db_config)
    db_cursor = db_connect.cursor()
    db_cursor.execute(command, params)
    db_connect.commit()
    db_cursor.close()
    db_connect.close()


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        print("Bot is ready.")
    except Exception as e:
        print(e)


@bot.tree.command(name = "insert-order", 
                  description = "Inserts an order into the order form.")
async def insertorder(interaction: discord.Interaction, 
                      name: str, 
                      quantity: int, 
                      website: str, 
                      type: Type):
    # Inserts the new order into the form, NULL for ID to automatically increment.
    modify_db("INSERT INTO ORDER_FORM (ID, Name, Quantity, Website, Type) VALUES (NULL, %s, %s, %s, %s)",
              (name, quantity, website, type.name, ))
    await interaction.response.send_message(f"Inserted ({name}, {quantity}, {website}, {type.name}) into order form!")


@bot.tree.command(name = "remove-order", 
                  description = "Removes an order from the order form based on its ID.")
async def removeorder(interaction: discord.Interaction, 
                      id: int):
    modify_db("DELETE FROM ORDER_FORM WHERE ID = %s", (id, ))
    await interaction.response.send_message(f"Order #{id} removed!")


@bot.tree.command(name = "get-order-form", 
                  description = "Gives a CSV file of the order form.")
async def getorders(interaction: discord.Interaction):
    db_connect = connector.connect(**db_config)
    db_cursor = db_connect.cursor()
    db_cursor.execute("SELECT Name, Quantity, Website, Type FROM ORDER_FORM")
    query = db_cursor.fetchall()
    filename = "order_form.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerow(["Name", "Quantity", "Website", "Type"])
        csvFile.writerows(query)
    await interaction.response.send_message(file=discord.File(filename))
    os.remove(filename)
    db_cursor.close()
    db_connect.close()


@bot.tree.command(name= "clear-order-form", 
                  description = "Clears all data from the order form if the user is an Admin.")
@app_commands.checks.has_role("Admin")
async def clearorders(interaction: discord.Interaction):
    modify_db.execute("TRUNCATE ORDER_FORM")
    await interaction.response.send_message("Orders cleared!")


bot.run(config["token"])
