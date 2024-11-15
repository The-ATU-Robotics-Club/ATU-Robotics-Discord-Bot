import discord
from discord.ext import commands
from discord import app_commands
from mysql import connector
import json
import csv
import os
import math


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)


config = {}
with open("config.json", 'r') as configFile:
    config = json.load(configFile)


db_config = {
    "host": config["db_host"],
    "user": config["db_user"],
    "password": config["db_pass"],
    "database": config["db_name"],
    "port": config["db_port"]
}


def modify_db(command, params=None):
    db_connect = connector.connect(**db_config)
    db_cursor = db_connect.cursor()
    db_cursor.execute(command, params)
    db_connect.commit()
    db_cursor.close()
    db_connect.close()


def query_db(command, params=None):
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


@bot.tree.command(description="Adds an order into the order form.")
async def addorder(interaction: discord.Interaction,
                   name: str,
                   website: str,
                   quantity: int,
                   unitprice: float):
    """Adds an order onto the order form. 

    Args:
        interaction (discord.Interaction): Discord context.
        name (str): The name of the item to be ordered.
        website (str): The website where it can be found.
        quantity (int): How many to order.
        unitprice (float): How much one costs (approximately).
    """
    # Adds the new order into the form, NULL for ID to automatically increment.
    unitprice = unitprice
    totalprice = quantity * unitprice
    modify_db("INSERT INTO ORDER_FORM (ID, Name, Website, Quantity, UnitPrice, TotalPrice) VALUES (NULL, %s, %s, %s, %s, %s)",
              (name, website, quantity, unitprice, totalprice, ))
    await interaction.response.send_message(f"Inserted ({name}, {website}, {quantity}, {unitprice}, {totalprice}) into order form!")


@bot.tree.command(description="Removes an order from the order form based on its ID.")
async def removeorder(interaction: discord.Interaction,
                      id: int):
    """Removes an order from the order form based on the provided ID. Call getorderform to see item ids. 

    Args:
        interaction (discord.Interaction): Discord context.
        id (int): The order ID to delete. 
    """
    modify_db("DELETE FROM ORDER_FORM WHERE ID = %s", (id, ))
    await interaction.response.send_message(f"Order #{id} removed!")


@bot.tree.command(description="Gives a CSV file of the order form.")
async def getorderform(interaction: discord.Interaction):
    """Gets the order form as a CSV file. 

    Args:
        interaction (discord.Interaction): Discord context.
    """
    response = query_db("SELECT * FROM ORDER_FORM")
    filename = "order_form.csv"
    with open(filename, 'w') as file:
        csvFile = csv.writer(file)
        csvFile.writerow(
            ["ID", "Name", "Website", "Quantity", "UnitPrice", "TotalPrice"])
        csvFile.writerows(response)
    await interaction.response.send_message(file=discord.File(filename))
    os.remove(filename)


@bot.tree.command(description="Gives the total approximated cost of the order.")
async def gettotal(interaction: discord.Interaction):
    """Gets the total approximated price of the order form. 

    Args:
        interaction (discord.Interaction): Discord context.
    """
    responses = query_db("SELECT TotalPrice FROM ORDER_FORM")
    prices = [response[0] for response in responses]
    await interaction.response.send_message(f"Order Form Total Price: ${sum(prices)}")


@bot.tree.command(description="Clears all data from the order form if the user is an Admin.")
@app_commands.checks.has_role("Admin")
async def clearorderform(interaction: discord.Interaction):
    """Clears the order form; must be admin to use. 

    Args:
        interaction (discord.Interaction): Discord context.
    """
    modify_db("TRUNCATE ORDER_FORM")
    await interaction.response.send_message("Orders cleared!")


bot.run(config["token"])
