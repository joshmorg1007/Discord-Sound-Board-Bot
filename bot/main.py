import discord
from discord.ext import commands, tasks
import os
import sys
import asyncio
import json

bot = commands.Bot(command_prefix="!", description="Simple soundboard bot")
with open("/root/Discord-Sound-Board-Bot/audio/soundboard.json", 'r') as soundboard_table:
    table = json.load(soundboard_table)
print(table)


@bot.event
async def on_ready():
    print("Connected")


@bot.command()
async def play(ctx, *args):
    if(len(args) != 1):
        await ctx.send("Incorrect Number of Parameters Usage: !play <clip_identifier>")
        return
    else:
        clip_path = table.get(args[0])

    if(clip_path is None):
        await ctx.send("No clip with name: " + args[0])

    # Sets up event to allow the bot to wait until the clip has been played before leaving
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()

    def wait_for_audio(error):
        if error:
            print(error)

        def clear():
            stop_event.set()
        loop.call_soon_threadsafe(clear)

    # Joins the calling users channel
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

    # Attempt to play audio
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.play(discord.FFmpegPCMAudio(
        clip_path, executable='/usr/bin/ffmpeg'), after=wait_for_audio)

    # Leave the voice voice channel
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        # waits for the audio to stop
        await stop_event.wait()
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command()
async def list_clips(ctx, *args):
    working_string = "**List Of Clip Names:**\n"
    for key in table:
        working_string += key + "\n"
    await ctx.send(working_string)


@bot.command()
async def add_clip(ctx, *args):
    if(len(args) != 1):
        await ctx.send("Incorrect Number of Parameters Usage: !add_clip <clip_identifier>")
        return

    if table.get(args[0]):
        await ctx.send("clip identifier '" + args[0] + "' is already in use")
        return

    if not ctx.message.attachments:
        await ctx.send("No clip attached")
        return

    clip = ctx.message.attachments[0]

    if clip.filename.split(".")[1] != "wav".casefold():
        await ctx.send("Clip is not a .wav file")
        return

    await clip.save(fp="../audio/" + clip.filename)
    verify_wav("../audio/" + clip.filename)
    table[args[0]] = "../audio/" + clip.filename
    update_json_table()
    print(clip.filename)


def verify_wav(wav_filepath):
    print("TODO")


def update_json_table():
    with open("/root/Discord-Sound-Board-Bot/audio/soundboard.json", 'w') as soundboard_table:
        json.dump(table, soundboard_table)


token = os.getenv("TOKEN")
bot.run(token)
sys.stout.flush()
