import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.utils.manage_commands import create_option
import yt_dlp
import base64
import os

TOKEN = os.environ.get("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@slash.slash(name="download",
             description="Downloads a video from URL and sends as Base64",
             options=[
                 create_option(
                     name="url",
                     description="URL of the video",
                     option_type=3,
                     required=True
                 ),
                 create_option(
                     name="file_type",
                     description="Type of the file (e.g., mp4, webm)",
                     option_type=3,
                     required=True,
                     choices=[
                         "mp4",
                         "webm"
                     ]
                 )
             ])
async def download(ctx, url: str, file_type: str):
    await ctx.defer()  # Acknowledge the command first

    # Download video using yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': './downloads/%(title)s.%(ext)s',  # Adjust the output folder as needed
        'merge_output_format': file_type
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)

    # Get the downloaded file path
    file_path = f"./downloads/{info_dict['title']}.{file_type}"

    # Base64 encode the file
    with open(file_path, "rb") as file:
        base64_data = base64.b64encode(file.read()).decode("utf-8")

    # Delete the downloaded file
    os.remove(file_path)

    # Send Base64 data to Discord
    await ctx.send(f"Base64 encoded data for {info_dict['title']}.{file_type}: \n```\n{base64_data}\n```")

bot.run(TOKEN)
