from pyrogram import Client, filters
import time,csv,os,re
import speedtest
import subprocess
import threading
import requests
from bs4 import BeautifulSoup
from hurry.filesize import size
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)
import asyncio
from datetime import *
import pytz,yt_dlp
import geocoder
from datetime import datetime
import zipfile
import urllib.parse
from fun import *





now=datetime.now(pytz.timezone("Asia/Kolkata"))

#os.system("wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux")
#os.system("mv yt-dlp_linux yt-dlp")





api_id = 3702208
api_hash = "3ee1acb7c7622166cf06bb38a19698a9"
bot_token = "6949923423:AAF6CnXxgA8I-xI_Wao-tTLAnVORxKiBsBw"


app = Client(
    "ydl",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)

shared_data = {}









@app.on_message(filters.command(["start", "help"]))
def start_command(client, message):
    help_text = (
        "Send me links using the following commands:\n"
        "/ytdl <link> - Download using yt-dlp\n"
        "/leech <link1> <link2> ... - Bulk download using aria2c\n"
        "/speedtest - To Test Speed"
    )
    message.reply_text(help_text)



@app.on_message(filters.command("ytdl"))
async def start_command(client, message):
    try:
        formats = ['144', '240', '360', '480', '720', '1080', '1440', '2160', 'Audio']
        
        # Using hash of the link as a unique identifier
        unique_id = hash(message.text.split()[-1])
        
        # Store the link and unique_id in shared_data
        shared_data[unique_id] = message.text.split()[-1]

        button_list = [
            [
                InlineKeyboardButton(format, callback_data=f"{format}__{unique_id}") for format in formats[i:i+2]
            ] for i in range(0, len(formats), 2)
        ]
        button_list.append([InlineKeyboardButton('Cancel', callback_data='Cancel')])

        reply_markup = InlineKeyboardMarkup(button_list)
        await message.reply_text("Select The Format:", reply_markup=reply_markup)

    except Exception as error:
        await message.reply_text(f"Error Occurred. Contact Owner About This.\n{error}")

@app.on_callback_query()
async def answer(client, call):
      await app.delete_messages(call.message.chat.id,call.message.id)
      data = call.data.split("__")
      if data[0] != 'Cancel': 
         if data[0] in ['144', '240', '360', '480', '720', '1080', '1440', '2160']:
                 format = f'-f "bv*[height<=?{data[0]}][ext=mp4]+ba[ext=m4a]/b[height<=?{data[0]}]"'
         elif data[0] in ['Audio']:
                  format= '--extract-audio --audio-format mp3'
         id = call.message.id
         unique_id = data[1]
         link = shared_data[int(unique_id)]
         cmd = f"""yt-dlp --downloader aria2c -P "downloads" {format} {link}"""
         print(cmd)
         
         os.system(cmd)
         for i in os.listdir("downloads"):
              if i.endswith('mp4') or i.endswith('webm'):
                os.system(f'''vcsi """downloads/{i}""" -g 1x1 --metadata-position hidden -o """downloads/{i.replace('.mp4','.png')}""" ''')
                await app.send_video(call.message.chat.id,video='downloads/'+i,caption="_".join(i.split(".")[0:-1]),thumb='downloads/'+i.replace(".mp4",".png"))
              elif i.endswith('mp3'):
                await app.send_audio(call.message.chat.id,audio='downloads/'+i,caption="_".join(i.split(".")[0:-1]))
              try:
                os.remove('downloads/'+i)
                #os.remove('downloads/'+i.replace('.mp4','.jpg'))
                os.remove('downloads/'+i.replace('.mp4','.png'))
              except:
                 pass


             
                
@app.on_message(filters.command("speedtest"))
def start_command(client,message):
    wait=app.send_message(chat_id=message.chat.id,text="Running Speed Test. Wait about some secs.",reply_to_message_id=message.id)
    result = internet_speed_test()
    text=""
    for category, data in result[0].items():
        fir=True
        co=0
        text+=f"\t《 {category} 》\n"
        for key, value in data.items():
            co+=1
            if fir:
                text+=f'<b>╭─ {key}: {value}\n'
                fir=False
            elif len(data)==co:
                text+=f'<b>╰─ {key}: {value}\n'
            else:
                 text+=f'<b>├ {key}: {value}\n'
    wait.delete()
    app.send_photo(chat_id=message.chat.id,photo=result[1],caption=text,
reply_to_message_id=message.id)


@app.on_message(filters.command("leech"))
def process_links(client, message):
    chat_id = message.chat.id
    links = message.text.split()[1:]

    if links:
        download_and_send_concurrently(app,links, chat_id,"a",None)



@app.on_message(filters.command("leechget"))
def get_hrefs_handler(client,message):
    chat_id = message.chat.id
    try:
        url = message.text.split()[1]
        bulker(app,chat_id,url)
    except IndexError:
        message.reply_text("Please provide a valid URL after the command.")

@app.on_message(filters.command("zipleechget"))
def get_hrefs_handler2(client,message):
    chat_id = message.chat.id
    try:
        url = message.text.split()[1]
        bulker(app,chat_id,url,True)
    except IndexError:
        message.reply_text("Please provide a valid URL after the command.")
      








      
@app.on_message(filters.command("shell"))
def shall_command(client,message):
       cmd = message.text.split()[1:]
       result = subprocess.run(cmd, stdout=subprocess.PIPE)
       message.reply_text(result.stdout)




@app.on_message(filters.command("sendfiles"))
def send_files_command(client, message):
    global terminate_flag
    chat_id = message.chat.id
    upload_id = shah(message.text.split()[-1])
    sts = app.send_message(chat_id,text=f"Download Started....")
    files[upload_id]=[sts.id,0,total]
    local_directory = '.'     
    terminate_flag = False
    Thread(target=send_files, args=(app, local_directory, chat_id,upload_id)).start()







print("bot Started..")
app.run()
