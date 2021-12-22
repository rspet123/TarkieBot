import os
import discord
import csv
from replit import db
import requests
import random
import json
import keep_alive
import time
import datetime
token = os.environ['TOKEN']
currency_dict = {"USD":"$","RUB":"₽","EUR":"€"}
trader_dict = {"fleaMarket":"Flea",
               "peacekeeper":"Peacekeeper",
               "prapor":"Prapor",
               "fence":"Fence",
               "mechanic":"Mechanic",
               "therapist":"Therapist",
               "jaeger":"Jaeger",
               "skier":"Skier"
              }
def check(message):
  #Replace this later lol
    return True

def format_num(number):
    out = number
    post = ""
    if number > 1000:
        post = "K"
        out = number / 1000
    if number > 1000000:
        post = "M"
        out = number / 1000000
    if number > 1000000000:
        post = "B"
        out = number / 1000000000
    return (str(round(out, 2)) + post)

def comma_num(number):
    number = round(number,0)
    out = "{:,}".format(number)
    return str(out)
  
def run_query(query):
    response = requests.post('https://tarkov-tools.com/graphql', json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(response.status_code, query))
      
client = discord.Client()
print("Starting...")


@client.event
async def on_ready():
    print("Tarkie Running as {0.user}".format(client))
    g = client.guilds
    print("In servers: ")
    for gld in g:
      print(gld)
      for channel in gld.text_channels:
        print(channel)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!traders'):
        search_user = message.author
        itemname = message.content.split('!traders ')[1]
        new_query = """
{
    itemsByName(name: "xyzzy") {
        id
        name
        types
        iconLink
    		sellFor{
          source
          currency
          price
        }
    		buyFor{
          source
          currency
          price
          requirements{
        		type
            value
          }
        }
    }
}
"""
        ex = new_query.replace("xyzzy", itemname)
        result = run_query(ex)["data"]["itemsByName"]
        if len(result) > 1:
          item_list = ""
          type_list = ""
          for i,item in enumerate(result):
            #print(str(i) + " " + item["name"])
            item_list += (str(i) + ": " + item["name"]) + "\n"
            types = ""
            for curr_type in item["types"]:
              types += curr_type
              types +=" "
            type_list += types + "\n"
          embed=discord.Embed(title="Searching for: " + itemname, description="Pick 0 -" + str(len(result)-1), color=0x00fe15)
          embed.add_field(name="Item", value=item_list, inline=True)
          embed.add_field(name="Type", value=type_list, inline=True)
          try:
            await message.channel.send(embed=embed)
            msg = await client.wait_for('message', check=check, timeout=30)
            try:
              index = int(msg.content)
            except Exception:
              await message.channel.send("That's not a number, idiot")
              await message.channel.send("Try again")
              try:
                msg = await client.wait_for('message', check=check, timeout=30)
                index = int(msg.content)
              except Exception:
                await message.channel.send("You are unfixably stupid")
            try:
              result = result[index]
            except Exception:
              await message.channel.send("I said 1 to " + str(len(result)-1) + ", you moron")
              await message.channel.send("Try again")
              try:
                msg = await client.wait_for('message', check=check, timeout=30)
                index = int(msg.content)
                result = result[index]
              except Exception:
                await message.channel.send("You are unfixably stupid")
          except discord.errors.HTTPException:
            await message.channel.send("Too many items to display, try again")
        else:
          try:
            result = result[0]
          except Exception:
            await message.channel.send("I can't find " + itemname + "...?")
            return
        buys = result["buyFor"]
        buys = sorted(buys, key = lambda i: i['price'])
        sells = result["sellFor"]
        sells = sorted(sells, key = lambda i: i['price'],reverse = True)
        buy_str = ""
        sell_str = ""
        for buy in buys:
          lv = ""
          if not type(buy["currency"]) == str:
            buy["currency"] = "RUB"
          if buy["requirements"][0]["type"] == "loyaltyLevel":
            lv = "LL" + str(buy["requirements"][0]["value"])
          buy_str += trader_dict[buy["source"]] +" " +lv +": "+ currency_dict[buy["currency"]] + comma_num(buy["price"]) + "\n"
        for sell in sells:
          if not type(sell["currency"]) == str:
            sell["currency"] = "RUB"
          sell_str += trader_dict[sell["source"]] +": "+ currency_dict[sell["currency"]]+ comma_num(sell["price"])  + "\n"
        embed2=discord.Embed(title=result["name"], description="Traders", color=0x00fe15)
        if buy_str=="":
          buy_str = "N\A"
        if sell_str=="":
          sell_str = "N\A"
        embed2.set_thumbnail(url=result["iconLink"])
        embed2.add_field(name="Buy from", value=buy_str, inline=True)
        embed2.add_field(name="Sell to", value=sell_str, inline=True)
        await message.channel.send(embed=embed2)
        

  

if __name__ == "__main__":
  keep_alive.keep_alive()
  client.run(token)

