import discord
from discord.ext import commands
from dislash import SlashCommand, Button, SelectMenu
from dislash.model import SlashCommandOptionType, ButtonStyle, SelectMenuOptionType
import yt_dlp
import base64
import os

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix='$', intents=intents)
slash = SlashCommand(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await slash.sync()

@slash.slash(
    name="download",
    description="Downloads a video and sends a link",
    options=[
        create_option(
            name="url",
            description="URL of the video",
            option_type=SlashCommandOptionType.STRING,
            required=True
        ),
        create_option(
            name="file_type",
            description="Type of the file (e.g., mp4, webm)",
            option_type=SlashCommandOptionType.STRING,
            required=True,
            choices=[
                {"name": "MP4", "value": "mp4"},
                {"name": "WEBM", "value": "webm"}
            ]
        )
    ])
async def download(ctx, url: str, file_type: str):
    await ctx.defer()

    # Download video using yt-dlp
    ydl_opts = {
        'format': 'best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'aac',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(tempfile.gettempdir(), '%(title)s.%(ext)s'),
        'merge_output_format': file_type
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)

        # Upload the downloaded file to Discord (consider using libraries like discord.File)
        #  or provide a download link from the temporary location

        await ctx.send(f"Downloaded {info_dict['title']}.{file_type}")

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
    finally:
        # Clean up temporary file
        downloaded_file = os.path.join(tempfile.gettempdir(), f"{info_dict['title']}.{file_type}")
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)

bot.run(TOKEN)
