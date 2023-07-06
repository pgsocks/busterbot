import discord
import redis

import sys
import json

client = discord.Client(intents = discord.Intents.all())
r = redis.Redis(host=sys.argv[2], port = 6379, db = 0)

@client.event
async def on_ready():
    global role
    guild = next((guild for guild in client.guilds if guild.name == "The Bunker Busters"), None)
    if not guild:
        print("Creating guild")
        guild = await client.create_guild(name = "The Bunker Busters")

    role = next((role for role in guild.roles if role.name == "Bunker Buster"), None)
    if not role:
        print("Creating role")
        role = await guild.create_role (
            name = "Bunker Buster",
            permissions = discord.Permissions(70368744177360))
    await role.edit(permissions = discord.Permissions(70368744177360))

@client.event
async def on_message(message):

    voted = False
    for member in message.mentions:
        votes = r.get(member.id)
        if not votes:
            votes = {}
        else:
            votes = json.loads(votes)
        if not message.author.id in votes:
            votes[message.author.id] = 0
        if message.content.startswith("promote"):
            voted = True
            votes[message.author.id] = 1
        if message.content.startswith("demote"):
            voted = True
            votes[message.author.id] = -1
        r.set(member.id, json.dumps(votes))
        if voted:
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
            if count <= -5:
                await member.remove_roles(role,
                    reason = "Community voted demotion")
                await message.channel.send(f"demoted {member.name}")

client.run(sys.argv[1])

