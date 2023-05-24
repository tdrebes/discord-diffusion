import configparser
import re
import subprocess
import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

permitted_author_ids = [] # set permitted author ids here

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='$', intents=intents, activity=discord.Game(name='StableDiffusion'))

async def load_replacements():
    parser = configparser.ConfigParser()
    parser.read('prompt_replacements.ini')

    print(parser.items('DEFAULT'))

    replace_dict = dict(parser.items('DEFAULT'))
    print(f'Loaded {len(replace_dict)} replacement pairs')
    return replace_dict

def find_and_replace(string_to_review, replacements):
    total_replacements = 0
    old_string, cur_string = string_to_review, string_to_review

    for k, v in replacements.items():
        (cur_string, count) = re.subn(k, v, cur_string.lower())
        total_replacements += int(count)

    if cur_string.lower() == old_string.lower():
        cur_string = old_string

    return cur_string, total_replacements

async def generate_image(prompt, file_name):
    print("requesting image")
    url = "http://127.0.0.1:7860"
    print(prompt)
    replaced = find_and_replace(prompt, await load_replacements())
    print(f'Replaced {replaced[1]} times. Current prompt: {replaced[0]}')
    prompt = replaced[0]

    payload = {
        "prompt": prompt,
        "steps": 20,
        "negative_prompt": "EasyNegative, paintings, sketches, (worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, glans,extra fingers,fewer fingers,(strange fingers:1.2), bad hand,6 fingers,extra legs, (strange legs:1.4),extra arms, strange arms,extra feet, strange feet, 3 legs,(fused fingers:1.2), (too many fingers:1.2), extra arms",
    }

    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)

    r = response.json()

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
            "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'out/{file_name}', pnginfo=pnginfo)

@bot.command()
async def ping(context: Context):
    print(context.author.id)
    await context.send(content=f'pooong! {context.author.mention}')
    # subprocess.call(['python', 'sd.py'])

@bot.command()
async def image(context: Context):
    author_id = context.author.id

    print(f'Command requested by: {author_id}')
    if (author_id not in permitted_author_ids):
        print(f'Author {author_id} is not permitted')
        return
    
    msg = context.message
    msg_content = msg.content
    msg_content_prompt = msg.content.partition(" ")[-1]

    print(f'Command {msg_content}')
    print(f'Message part: {msg_content_prompt}')

    if (msg_content_prompt == ''):
        return

    await generate_image(msg_content_prompt, str(context.author.id) + '.png')
    file_path = f'out/{str(context.author.id)}.png'
    
    await msg.reply(file=discord.File(file_path, spoiler=True))

bot.run('') # set bot token here

