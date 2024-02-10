import discord
from discord.ext import commands, tasks
import asyncio
from dotenv import load_dotenv
import os
import requests
import g4f

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)

channels = {}
messages = {}


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.listening, name="to you"),
    )


@bot.event
async def on_command_error(ctx, error):
    await ctx.respond(error)


@bot.event
async def on_message(message):
    if (message.author == bot.user) or not (
        message.guild.id in channels
        and message.channel.id == channels[message.guild.id]
    ):
        return

    async with message.channel.typing():

        if message.author.id not in messages:
            messages[message.author.id] = []

        messages[message.author.id].append({"role": "user", "content": message.content})

        response = await g4f.ChatCompletion.create_async(
            model="gpt-3.5-turbo",
            messages=messages[message.author.id],
        )

        messages[message.author.id].append({"role": "system", "content": response})

        await message.reply(response)


@bot.slash_command(description="Set the current channel to be the talking channel")
async def start(ctx):
    await ctx.defer()

    if ctx.author.guild_permissions.administrator:
        channels[ctx.guild.id] = ctx.channel.id
        embed = discord.Embed(
            title="Channel Setting", color=discord.Color.green()
        ).add_field(
            name="Success",
            value=f"Succesfully set <#{ctx.channel.id}> for {ctx.guild.name}",
            inline=False,
        )

    else:
        embed = discord.Embed(
            title="Channel Setting", color=discord.Color.red()
        ).add_field(
            name="Error",
            value="You must have administrator in order to set this guild's channel!",
            inline=False,
        )

    await ctx.respond(embed=embed)


@bot.slash_command(description="Directly ask the bot a question")
async def ask(ctx, question):
    await ctx.defer()

    response = await g4f.ChatCompletion.create_async(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": question}],
    )

    await ctx.respond(response)


bot.run(os.getenv("TOKEN"))
