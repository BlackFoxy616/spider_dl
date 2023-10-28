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
import speedtest
import geocoder
from datetime import datetime

def internet_speed_test():
    st = speedtest.Speedtest()
    
    # Speedtest Info
    upload_speed = st.upload() / 1_000_000  # Convert to MB/s
    download_speed = st.download() / 1_000_000  # Convert to MB/s
    ping = st.results.ping
    time_stamp = datetime.utcnow().isoformat()

    # Data Usage
    data_sent = st.results.bytes_sent / (1024 ** 2)  # Convert to MB
    data_received = st.results.bytes_received / (1024 ** 2)  # Convert to MB

    # Speedtest Server Info
    server_info = st.get_best_server()
    server_name = server_info["host"]
    server_country = server_info["country"]
    server_sponsor = server_info["sponsor"]
    server_latency = server_info["latency"]
    server_latitude = server_info["lat"]
    server_longitude = server_info["lon"]

    # Client Details
    public_ip = get_public_ip()
    client_location = get_location()
    client_latitude = client_location[0]
    client_longitude = client_location[1]
    client_country = client_location[2]
    isp = st.results.client.get("isp", "Unknown")
    isp_rating = 3.7  # Replace with the actual rating

    # Build result dictionary
    result = {
        "Speedtest Info": {
            "Upload": f"{upload_speed:.2f} MB/s",
            "Download": f"{download_speed:.2f} MB/s",
            "Ping": f"{ping:.3f} ms",
            "Time": time_stamp,
            "Data Sent": f"{data_sent:.2f} MB",
            "Data Received": f"{data_received:.2f} MB",
        },
        "Speedtest Server": {
            "Name": server_name,
            "Country": server_country,
            "Sponsor": server_sponsor,
            "Latency": f"{server_latency:.3f} ms",
            "Latitude": server_latitude,
            "Longitude": server_longitude,
        },
        "Client Details": {
            "IP Address": public_ip,
            "Latitude": client_latitude,
            "Longitude": client_longitude,
            "Country": client_country,
            "ISP": isp,
            "ISP Rating": isp_rating,
        }
    }

    return result,st.results.share()

def get_public_ip():
    return geocoder.ip('me').ip

def get_location():
    g = geocoder.ip('me')
    return g.latlng + [g.country]
  
now=datetime.now(pytz.timezone("Asia/Kolkata"))

#os.system("wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux")
#os.system("mv yt-dlp_linux yt-dlp")



def fetch_hrefs(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        allowed_extensions = {'.mp4', '.jpg', '.png', '.jpeg', '.mp3', '.mkv'}
        hrefs = [link.get('href') for link in soup.find_all('a', href=True) if link.get('href').lower().endswith(tuple(allowed_extensions))]
        return hrefs
    except Exception as e:
        return str(e)

api_id = 3702208
api_hash = "3ee1acb7c7622166cf06bb38a19698a9"
bot_token = "6949923423:AAF6CnXxgA8I-xI_Wao-tTLAnVORxKiBsBw"


app = Client(
    "ydl",
    api_id=api_id, api_hash=api_hash,
    bot_token=bot_token
)

shared_data = {}


def extract(yturl):
    ydl = yt_dlp.YoutubeDL()
    with ydl:
        qualityList = []
        r = ydl.extract_info(yturl, download=False)
        """ with open ("dump.txt","w+") as file:
             file.write(str(r))"""
        if False :
         for format in r['formats']:
            if not "dash" in str(format['format']).lower():
                if "filesize" in format and format['filesize'] != None and format['video_ext'] !="webm" :
                  qualityList.append(" ".join([str(format['format']),size(format['filesize']),str(format['video_ext'])]))

   
   
    return r["title"]










def download_and_sendar(link, chat_id):
    download_path = "downloads"
    os.makedirs(download_path, exist_ok=True)

    file_name = link.split("/")[-1]  # Extracting the filename from the link
    file_path = os.path.join(download_path, file_name)
    
    command = [
        "aria2c",
        "--seed-time=0",
        "--summary-interval=1",
        "-x", "16",
        "-s", "16",
        "-d", download_path,
        link
    ]
    start_time = datetime.now() 
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    sts = app.send_message(chat_id,text=f"Download Started....")
    st_id = sts.id
    old = ""
    for line in process.stdout:
        if 'MiB' in line:
               spe=line.strip().split()[-2][3:].replace('MiB','MiB/s')
               siz=line.strip().split()[1].replace("/"," of ")[:-5]
               con = stats = f'<b>├  FileName : </b>{file_name}\n'\
                             f'<b>├  Engine : </b>Aria2c\n'\
                             f'<b>├  Size : </b>{siz}\n'\
                             f'<b>├  Speed : </b>{spe}\n'\
                             f'<b>╰  Time Taken: </b>{str(datetime.now()-start_time).split(":")[2].split(".")[0]}\n\n'
               if con != old:
                 #print(old,con)
                 app.edit_message_text(chat_id,st_id,text=con)
                 old = con
                 #print(old,con)
        
        # Extract download speed
        match = re.search(r'Speed: ([0-9.]+)MiB/s', line)
        
        if "MiB/s" in line :
            speed = line.split("|")[2].strip()
            #sp = app.edit_message_text(chat_id,st_id,text=f"Average Download Speed: {speed}")
            

    process.wait()

    if process.returncode == 0:
        for i in os.listdir("downloads"):
               if i.endswith("mp4") or i.endswith("mp3"):
                 thumbnail = f"{i.replace('.mp4', '.png')}"
                 os.system(f'vcsi "{"downloads/"+i}" -g 1x1 --metadata-position hidden -o "{thumbnail}"')
                 app.send_video(chat_id, video="downloads/"+i, caption=i, thumb=thumbnail)
               elif i.endswith("jpg") or i.endswith("png") :
                 app.send_photo(chat_id, photo="downloads/"+i, caption=i)

               try:
                  os.remove(i)
                  os.remove(thumbnail)
                 
               except:
                   pass
    else:
        error_message = f"Download failed for link: {link}"
        app.send_message(chat_id, text=error_message)


def download_and_sendfi(file_path, chat_id):
    download_path = "downloads"
    os.makedirs(download_path, exist_ok=True)

    #file_name = link.split("/")[-1]  # Extracting the filename from the link
    #file_path = os.path.join(download_path, file_name)
    
    command = [
        "aria2c",
        "-i",
        file_path,
        "--seed-time=0",
        "--summary-interval=1",
        "-x", "16",
        "-s", "16",
        "-d", download_path
    ]
    start_time = datetime.now() 
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    sts = app.send_message(chat_id,text=f"Download Started....")
    st_id = sts.id
    old = ""
    for line in process.stdout:
        if 'MiB' in line:
               spe=line.strip().split()[-2][3:].replace('MiB','MiB/s')
               siz=line.strip().split()[1].replace("/"," of ")[:-5]
               con = stats = f'<b>├  FileName : </b>Multiple Files\n'\
                             f'<b>├  Engine : </b>Aria2c\n'\
                             f'<b>├  Size : </b>{siz}\n'\
                             f'<b>├  Speed : </b>{spe}\n'\
                             f'<b>╰  Time Taken: </b>{str(datetime.now()-start_time).split(":")[2].split(".")[0]}\n\n'
               if con != old:
                 #print(old,con)
                 app.edit_message_text(chat_id,st_id,text=con)
                 old = con
                 #print(old,con)
        
        # Extract download speed
        match = re.search(r'Speed: ([0-9.]+)MiB/s', line)
        
        if "MiB/s" in line :
            speed = line.split("|")[2].strip()
            #sp = app.edit_message_text(chat_id,st_id,text=f"Average Download Speed: {speed}")
            

    process.wait()

    if process.returncode == 0:
        for i in os.listdir("downloads"):
               if i.endswith("mp4") or i.endswith("mp3"):
                 thumbnail = f"{i.replace('.mp4', '.png')}"
                 os.system(f'vcsi "{"downloads/"+i}" -g 1x1 --metadata-position hidden -o "{thumbnail}"')
                 app.send_video(chat_id, video="downloads/"+i, caption=i, thumb=thumbnail)
               elif i.endswith("jpg") or i.endswith("png") :
                 app.send_photo(chat_id, photo="downloads/"+i, caption=i)

               try:
                  os.remove(i)
                 
               except:
                   pass
    else:
        error_message = f"Download failed for link: {link}"
        app.send_message(chat_id, text=error_message)
  



def download_and_sendyt(chat_id, format_option, link):
    try:
        download_path = "downloads"
        os.makedirs(download_path, exist_ok=True)

        format_arg = (
            f'-f "bv*[height<=?{format_option}][ext=mp4]+ba[ext=m4a]/b[height<=?{format_option}]"'
            if format_option in ['144', '240', '360', '480', '720', '1080', '1440', '2160']
            else '--extract-audio --audio-format mp3' if format_option == 'Audio'
            else ''
        )

        cmd = f'./yt-dlp """{link}""" --downloader aria2c {format_arg} '
        print(cmd)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        sts = app.send_message(chat_id,text=f"Download Started....")
        st_id = sts.id
        old = ""
        for line in process.stdout:
                print(line)
                if '%' in line:
                    spe=line.strip().split()[-2][3:].replace('MiB','MiB/s')
                    siz=line.strip().split()[1].replace("/"," of ")[:-5]
                    con = stats = f'<b>├  FileName : </b>{extract(link)[0]}\n'\
                                  f'<b>├  Engine : </b>Yt-dlp\n'\
                                  f'<b>├  Size : </b>{siz}\n'\
                                  f'<b>├  Speed : </b>{spe}\n'\
                                  f'<b>╰  Time Taken: </b>{str(datetime.now()-start_time).split(":")[2].split(".")[0]}\n\n'
                    if con != old:
                       #print(old,con)
                       app.edit_message_text(chat_id,st_id,text=con)
                       old = con
                       #print(old,con)

        process.wait()

        if process.returncode != 0:
            raise Exception(f"Error occurred: {process.stderr.strip()}")

        for i in os.listdir():
               if i.endswith("mp4") or i.endswith("mp3"):
                 thumbnail = f"{link.split('/')[-1].replace('.mp4', '.png')}"
                 os.system(f'vcsi "{link.split("/")[-1]}" -g 1x1 --metadata-position hidden -o "{thumbnail}"')
                 app.send_video(chat_id, video=link.split("/")[-1], caption=link.split("/")[-1], thumb=thumbnail)
               elif i.endswith("jpg") or i.endswith("png") :
                 app.send_photo(chat_id, photo=link.split("/")[-1], caption=link.split("/")[-1])

               try:
                  os.remove(link.split("/")[-1])
                  os.remove(link.split("/")[-1].replace('.mp4', '.jpg'))
                  os.remove(link.split("/")[-1].replace('.mp4', '.png'))
                 
               except:
                   pass

    except Exception as error:
        app.edit_message_text(chat_id,st_id,text=f"Error occurred: {error}")



def download_and_send_concurrently(links, chat_id,engine,formats):
    threads = []
    if engine=="y":
        for link in links:
           thread = threading.Thread(target=download_and_sendyt, args=(chat_id,formats,link))
           threads.append(thread)
           thread.start()
    else:
        for link in links:
          thread = threading.Thread(target=download_and_sendar, args=(link, chat_id))
          threads.append(thread)
          thread.start()


    for thread in threads:
        thread.join()









@app.on_message(filters.command(["start", "help"]))
def start_command(client, message):
    help_text = (
        "Send me links using the following commands:\n"
        "/dl <link> - Download using yt-dlp\n"
        "/leech <link1> <link2> ... - Bulk download using aria2c\n"
        "/speedtest - To Test Speed"
    )
    message.reply_text(help_text)

@app.on_message(filters.command("get"))
async def get_hrefs_handler(client,message):
    try:
        url = message.text.split()[1]
        hrefs = fetch_hrefs(url)
        with open("urls.txt","w+") as urls:
          for i in hrefs:
              urls.write(url+i+"\n")
        await app.send_document(message.chat.id,document="urls.txt")

    except IndexError:
        message.reply_text("Please provide a valid URL after the command.")


@app.on_message(filters.command("dl"))
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
async def start_command(client,message):
    result = internet_speed_test()
    text=""
    for category, data in result[0].items():
        text+=f"\t《 {category} 》\n"
        for key, value in data.items():
            text+=f"{key}: {value}\n"
    await app.send_photo(message.chat.id,photo=result[1],caption=text)


@app.on_message(filters.command("leech"))
def process_links(client, message):
    chat_id = message.chat.id
    links = message.text.split()[1:]

    if links:
        download_and_send_concurrently(links, chat_id,"a",None)


@app.on_message(filters.document)
def handle_document(client, message):
    chat_id = message.chat.id
    file_path = client.download_media(message.document)
    with open(file_path) as file:
      for link in file.readlines():
        download_and_sendar(link,chat_id)
        time.sleep(3)
      





app.run()
  
