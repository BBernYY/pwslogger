import discord
from datetime import datetime
import discord.utils
from discord.ext import commands
import json
import os
import time
import copy
bot = commands.Bot(command_prefix='.log ', intents=discord.Intents.all())
bot.remove_command('help')

user = {
    "start_time": -1, # unix timestamp of start time, -1 when theres no active session
        "logs": [
        # Example: {"name": "Worked on app.", "started": 423423, "duration": 60000} 
        ]
}
def get_list(dictionary, key):
  output = []
  for k, v in dictionary.items():
    output.append(v[key])
  return output
def load_data():
    return json.load(open("data.json"))
def write_data(data):
    json.dump(data, open("data.json", "w"), indent=4)
def remove_list(li):
  return " ".join(li)
@bot.event
async def on_ready():
  global me
  me = bot.user
  print(f'startup at {datetime.now()} using @{me.name}#{me.discriminator}')
@bot.command()
async def help(ctx, command=None):
    data = load_data()
    if command:
      embed=discord.Embed(title=command, description=data["commands"][command]["description"])
      embed.add_field(name="usage", value=data["commands"][command]["usage"])
    else:
      embed=discord.Embed(title='Help', description='commands and the description', color=0xFF5733)
      embed.add_field(name="command", value="\n".join(list(data["commands"].keys())))
      embed.add_field(name="description", value="\n".join(get_list(data["commands"], "description")))
      embed.add_field(name="usage", value="\n".join(get_list(data["commands"], "usage")))
    await ctx.channel.send("I'm glad to help!", embed=embed)

@bot.command()
async def start(ctx):
    data = load_data()
    id = str(ctx.author.id)
    if not id in data["users"]:
        u = copy.copy(user)
    else:
        u = data["users"][id]
    u["start_time"] = int(time.time())
    data["users"][id] = u
    write_data(data)
    await ctx.channel.send(f"Starting stopwatch on <t:{u["start_time"]}:F>")

@bot.command()
async def stop(ctx, *log):
    data = load_data()
    log = " ".join(log)
    u = data["users"][str(ctx.author.id)]
    if u["start_time"] < 0:
        await ctx.channel.send("You haven't started the timer yet.")
        return
    if log.replace(" ", "") == "":
        await ctx.channel.send("Please provide a log name.")
        return
    current_time = int(time.time())
    start_time = u["start_time"]
    duration = current_time - start_time
    u["logs"].append({"name": log, "started": u["start_time"], "duration": duration})
    u["start_time"] = -1
    data["users"][str(ctx.author.id)] = u
    write_data(data)
    await ctx.channel.send(f"Got it! You were busy with `{log}` for `{duration//60} minutes` on <t:{start_time}:D>")

@bot.command()
async def show(ctx):
    data = load_data()
    l = data["users"][str(ctx.author.id)]["logs"]
    csv = "Date,Description,Duration\n"
    for i in l:
        csv += f"<t:{i["started"]}:D>,{i["name"]},{int(i["duration"])//60} minutes\n"
    await ctx.channel.send(f"{csv}")

# connect token
@bot.event
async def on_message(message):
    if not message.guild and not message.content.startswith('.log ') and not message.author.id == me.id:
        print(message.author.name+": "+message.content)
    else:
      await bot.process_commands(message)
with open('token.env') as f:
  token = f.read()
if __name__ == '__main__':
    bot.run(token)
