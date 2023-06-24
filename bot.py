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

def query_db(command, params = None):
    db_connect = connector.connect(**db_config)
    db_cursor = db_connect.cursor()
    db_cursor.execute(command, params)
    response = db_cursor.fetchall()
    db_cursor.close()
    db_connect.close()
    return response
    

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
        print("Bot is ready.")
    except Exception as e:
        print(e)


@bot.tree.command(description = "Adds an order into the order form.")
async def addorder(interaction: discord.Interaction, 
                      name: str, 
                      quantity: int, 
                      website: str, 
                      type: Type):
    # Adds the new order into the form, NULL for ID to automatically increment.
    modify_db("INSERT INTO ORDER_FORM (ID, Name, Quantity, Website, Type) VALUES (NULL, %s, %s, %s, %s)",
              (name, quantity, website, type.name, ))
    await interaction.response.send_message(f"Inserted ({name}, {quantity}, {website}, {type.name}) into order form!")


@bot.tree.command(description = "Removes an order from the order form based on its ID.")
async def removeorder(interaction: discord.Interaction, 
                      id: int):
    modify_db("DELETE FROM ORDER_FORM WHERE ID = %s", (id, ))
    await interaction.response.send_message(f"Order #{id} removed!")


@bot.tree.command(description = "Gives a CSV file of the order form.")
async def getorderform(interaction: discord.Interaction):
    response = query_db("SELECT * FROM ORDER_FORM")
    filename = "order_form.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerow(["ID", "Name", "Quantity", "Website", "Type"])
        csvFile.writerows(response)
    await interaction.response.send_message(file=discord.File(filename))
    os.remove(filename)


@bot.tree.command(description = "Clears all data from the order form if the user is an Admin.")
@app_commands.checks.has_role("Admin")
async def clearorderform(interaction: discord.Interaction):
    modify_db("TRUNCATE ORDER_FORM")
    await interaction.response.send_message("Orders cleared!")


@bot.tree.command(description = "Gets the work hours of the caller or user given.")
async def gethours(interaction: discord.Interaction,
                  user: discord.User = None):
    if not user:
        user = interaction.user
    response = query_db("SELECT Hours FROM TIME_SHEET WHERE ID = %s", (user.id, ))
    hours = 0 if not response else response[0][0]
    await interaction.response.send_message(f"User {user.name} has contributed {hours} hours.")


@bot.tree.command(description = "Changes work hours to the caller or user given.")
async def changehours(interaction: discord.Interaction,
                      hours: int,
                      user: discord.User = None):
    if not user:
        user = interaction.user
    response = query_db("SELECT Hours FROM TIME_SHEET WHERE ID = %s", (user.id, ))
    if not response:
        modify_db("INSERT INTO TIME_SHEET (ID, Name, Hours) VALUES (%s, %s, %s)", (user.id, user.name, 0, ))
        response = [(0,)]
    hours = max(0, response[0][0] + hours)
    modify_db("UPDATE TIME_SHEET SET Hours = %s WHERE ID = %s", (hours, user.id, ))
    await interaction.response.send_message(f"Set {user.name}'s hours to {hours} hours.")


@bot.tree.command(description = "Gives a CSV file of the time sheet.")
async def gettimesheet(interaction: discord.Interaction):
    response = query_db("SELECT Name, Hours FROM TIME_SHEET")
    filename = "time_sheet.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerow(["Name", "Hours"])
        csvFile.writerows(response)
    await interaction.response.send_message(file=discord.File(filename))
    os.remove(filename)


@bot.tree.command(description = "Clears all data from the time sheet if the user is an Admin.")
@app_commands.checks.has_role("Admin")
async def cleartimesheet(interaction: discord.Interaction):
    modify_db("TRUNCATE TIME_SHEET")
    await interaction.response.send_message("Time sheet cleared!")


bot.run(config["token"])