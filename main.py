from pyrogram import Client, filters
import time,csv,os
import speedtest
import yt_dlp
import subprocess
import threading
from hurry.filesize import size
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)
import asyncio


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





"""
@app.on_message(filters.command("dl"))
async def start_command(client,message):
      try:
         global query 
         query = message.text.split()
         button_list =[]
         co=0
         temp = []
         for i in ['144', '240', '360', '480', '720', '1080', '1440', '2160','Audio','Cancel']:
             temp.append(InlineKeyboardButton(i, callback_data =i))
             co+=1
             if co%2==0 or i == len(['144', '240', '360', '480', '720', '1080', '1440', '2160','Audio'])-1:
               button_list.append(temp)
               temp=[]
          
         reply_markup=InlineKeyboardMarkup(button_list)
         choice = await app.send_message(
            message.chat.id,"Select The Format:",reply_markup=reply_markup)        
      except Exception as error:
          await app.send_message(
            message.chat.id,f"Error Occurred Contact Owner About This ,\n{error}")

"""





def download_and_sendar(link, chat_id):
    download_path = "downloads"
    os.makedirs(download_path, exist_ok=True)

    file_name = link.split("/")[-1]  # Extracting the filename from the link
    file_path = os.path.join(download_path, file_name)
    command = ["aria2c", "--seed-time=0", "--summary-interval=1", "-x", "16", "-s", "16", "-d", download_path, link]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    for line in process.stdout:
        app.send_message(chat_id, text=f"Downloading: {line.strip()}")
    process.wait()
    if process.returncode == 0:
        app.send_message(chat_id, text=f"Download completed: {file_name}")
        app.send_document(chat_id, document=file_path)
        os.remove(file_path)
        print(f"File deleted: {file_path}")
    else:
        error_message = f"Download failed for link: {link}"
        app.send_message(chat_id, text=error_message)




async def download_and_sendyt(chat_id, format_option, link):
    try:
        download_path = "downloads"
        os.makedirs(download_path, exist_ok=True)

        format_arg = (
            f'-f "bv*[height<=?{format_option}][ext=mp4]+ba[ext=m4a]/b[height<=?{format_option}]"'
            if format_option in ['144', '240', '360', '480', '720', '1080', '1440', '2160']
            else '--extract-audio --audio-format mp3' if format_option == 'Audio'
            else ''
        )

        cmd = f'./yt-dlp {link} --downloader aria2c {format_arg} '
        print(cmd)

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"Error occurred: {result.stderr.strip()}")

        thumbnail = f"{link.split('/')[-1].replace('.mp4', '.png')}"
        os.system(f'vcsi "{link.split("/")[-1]}" -g 1x1 --metadata-position hidden -o "{thumbnail}"')
        await app.send_video(chat_id, video=link.split("/")[-1], caption=link.split("/")[-1], thumb=thumbnail)

        try:
            os.remove(link.split("/")[-1])
            os.remove(link.split("/")[-1].replace('.mp4', '.jpg'))
            os.remove(link.split("/")[-1].replace('.mp4', '.png'))
        except:
            pass

    except Exception as error:
        await app.send_message(chat_id, text=f"Error occurred: {error}")


def download_and_send_concurrently(links, chat_id):
    threads = []

    for link in links:
        thread = threading.Thread(target=download_and_send, args=(link, chat_id))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()









@app.on_message(filters.command(["start", "help"]))
def start_command(client, message):
    help_text = (
        "Send me links using the following commands:\n"
        "/dl <link> - Download using yt-dlp\n"
        "/leech <link1> <link2> ... - Bulk download using aria2c"
    )
    message.reply_text(help_text)




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
    try:
        await app.delete_messages(call.message.chat.id, call.message.id)
        data = call.data.split("__")

        if len(data) >= 2 and data[0] != 'Cancel':
            format_option = data[0]
            unique_id = data[1]

            # Retrieve link from shared_data
            link = shared_data[int(unique_id)]
            print(link)

            # Download asynchronously
            await asyncio.gather(download_and_sendyt(call.message.chat.id, format_option, link))

    except Exception as error:
        print(error)



             
                
@app.on_message(filters.command("speedtest"))
async def start_command(client,message):
    st = speedtest.Speedtest()
    download_speed = st.download()
    upload_speed = st.upload()
    await app.send_photo(message.chat.id,photo=st.results.share(),caption=f"Download Speed: {download_speed / 10**6:.2f} Mbps\nUpload Speed: {upload_speed / 10**6:.2f} Mbps\nPing:{st.results.ping}")


@app.on_message(filters.command("leech"))
def process_links(client, message):
    chat_id = message.chat.id
    links = message.text.split()[1:]

    if links:
        download_and_send_concurrently(links, chat_id)







app.run()
