import discord
from discord.ext import commands
import redis

import sys
import json

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())
r = redis.Redis(host=sys.argv[2], port = 6379, db = 0)

@bot.event
async def on_ready():
    global role
    guild = next((guild for guild in bot.guilds if guild.name == "The Bunker Busters"), None)
    if not guild:
        print("Creating guild")
        guild = await bot.create_guild(name = "The Bunker Busters")

    role = next((role for role in guild.roles if role.name == "Bunker Buster"), None)
    if not role:
        print("Creating role")
        role = await guild.create_role (
            name = "Bunker Buster",
            permissions = discord.Permissions(70368744177360))
    await role.edit(permissions = discord.Permissions(70368744177360))

@bot.command()
async def promote(ctx: commands.Context):

    message = ctx.message
    for member in message.mentions:
        votes = r.get(member.id)
        if not votes:
            votes = {}
        else:
            votes = json.loads(votes)
        if not message.author.id in votes:
            votes[message.author.id] = 0
        votes[message.author.id] = 1
        r.set(member.id, json.dumps(votes))
        await message.channel.send("promote: " + ", ".join([
            str(k)
            for k, v
            in votes.items()
            if v > 0]))
        await message.channel.send("demote: " + ", ".join([
            str(k)
            for
            k, v
            in
            votes.items()
            if v < 0]))
        count = sum(votes.values())
        if count >= 3:
            await member.add_roles(role,
                reason = "Community voted promotion")
            await message.channel.send(f"promoted {member.name}")

@bot.command()
async def demote(ctx: commands.Context):

    message = ctx.message
    for member in message.mentions:
        votes = r.get(member.id)
        if not votes:
            votes = {}
        else:
            votes = json.loads(votes)
        if not message.author.id in votes:
            votes[message.author.id] = 0
        votes[message.author.id] = -1
        r.set(member.id, json.dumps(votes))
        await message.channel.send("promote: " + ", ".join([
            str(k)
            for k, v
            in votes.items()
            if v > 0]))
        await message.channel.send("demote: " + ", ".join([
            str(k)
            for
            k, v
            in
            votes.items()
            if v < 0]))
        count = sum(votes.values())
        if count <= -5:
            await member.remove_roles(role,
                reason = "Community voted demotion")
            await message.channel.send(f"demoted {member.name}")

@bot.command()
async def avatar(ctx: commands.Context):

    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        await attachment.save(attachment.filename)
        with open(attachment.filename, "rb") as f:
            await ctx.guild.edit(icon = f.read())
    else:
        await ctx.send("Attach a server avatar image")

bot.run(sys.argv[1])

