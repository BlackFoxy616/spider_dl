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
from threading import Thread
import shutil
import hashlib 
from time import sleep

terminate_flag = False 
file_ids={}


def snaper(file_path):
            file=file_path.split("/")
            thumbnail = f"""{file.replace('.mp4', '.png')}"""
            os.system(f'''vcsi "{file_path}" -g 2x1 --metadata-position hidden -o "{thumbnail}"''')
            return thumbnail

def zip_and_split_folder(input_folder, output_folder,file_name,chunk_size_mb=2000):
    # Create a temporary directory to store the zip file
    temp_dir = "temp_zip"
    os.makedirs(temp_dir, exist_ok=True)
    os.makedirs("Zips", exist_ok=True)

    # Zip the contents of the folder
    zip_filename = os.path.join(temp_dir, "archive.zip")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(input_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, input_folder)
                zipf.write(file_path, arcname)

    # Split the zip file into chunks
    chunk_size_bytes = chunk_size_mb * 1024 * 1024
    with open(zip_filename, 'rb') as zip_file:
        chunk_num = 1
        while True:
            chunk_data = zip_file.read(chunk_size_bytes)
            if not chunk_data:
                break

            chunk_filename = os.path.join(output_folder, f"{file_name}{chunk_num}.zip")
            with open(chunk_filename, 'wb') as chunk:
                chunk.write(chunk_data)
            
            chunk_num += 1
        


    # Clean up temporary directory
    shutil.rmtree(temp_dir)
    files = []
    for i in range(1,chunk_num):
        files.append(os.path.join(output_folder, f"{file_name}{i}.zip"))
        
        
    return files






def send_file(app,file_path, chat_id):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in {'.jpg', '.jpeg', '.png', '.gif'}:
        app.send_photo(chat_id=chat_id, photo=file_path,caption=file_path.split("/")[-1])
    elif file_extension in {'.mp3', '.ogg', '.wav'}:
        app.send_audio(chat_id=chat_id, audio=file_path,caption=file_path.split("/")[-1])
    elif file_extension in {'.mp4', '.mkv', '.avi'}:
        app.send_video(chat_id=chat_id, video=file_path,thumb=snaper(file_path),caption=file_path.split("/")[-1])
    else:
        app.send_document(chat_id=chat_id, document=file_path,caption=file_path.split("/")[-1])
    deltry(file_path)


def send_files(app, local_directory, chat_id):
    global terminate_flag
    files = [f for f in os.listdir(local_directory) if os.path.isfile(os.path.join(local_directory, f))]
    for file_name in files:
        if terminate_flag:
            break
        Thread(target=send_file, args=(app,file_path, chat_id)).start()
   


def shah(str):
    return hashlib.sha1(str.encode()).hexdigest()

        



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






def download_and_sendar(app,link, chat_id):
    download_path = "downloads"
    os.makedirs(download_path, exist_ok=True)
    file_name = link.split("&")[1][4:] if link.startswith("magnet") else link.split("/")[-1]
    file_path = os.path.join(download_path, file_name)
    sts = app.send_message(chat_id,text=f"Download Started....")
    Thread(target=send_files, args=(app, ".", chat_id,shah(link))).start()
    print(file_name)
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
    st_id = sts.id
    old = ""
    for line in process.stdout:
        print(line)
        if 'MiB' in line:
               spe=line.strip().split()[-2][3:].replace('MiB','MiB/s')
               siz=line.strip().split()[1].replace("/"," of ")[:-5]
               con = stats = f'<b>├  FileName : </b>{file_name}\n'\
                             f'<b>├  Engine : </b>Aria2c\n'\
                             f'<b>├  Size : </b>{siz}\n'\
                             f'<b>├  Speed : </b>{spe}\n'\
                             f'<b>╰  Time Taken: </b>{str(datetime.now()-start_time)}\n\n'
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
       pass
    else:
        error_message = f"Download failed for link: {link}"
        app.send_message(chat_id, text=error_message)







def deltry(j):
        ext=j.split(".")[-1]
        try:
            os.remove(j)
            os.remove(j.replace(ext, 'jpg'))
            os.remove(j.replace(ext,'png'))
        except:
            pass

def leng(name):
    with open(f"{name}.txt") as file:
        return len(file.read().split())

def bulker(app,chat_id,url,iszip=False):
    try:  
        download_path = f"downloads/{str(shah(url))}/"
        os.makedirs(download_path, exist_ok=True)
        files=[]
        sts = app.send_message(chat_id,text=f"Processing Links......\nTime:{str(datetime.now())[:23]}")
        hrefs = fetch_hrefs(url)
        with open(f"{str(shah(url))}.txt","w+") as urls:
                for i in hrefs:
                    urls.write(url+i+"\n")
                urls.seek(0)
                urls = urls.read().split()
        file_path = f"{str(shah(url))}.txt"
        app.edit_message_text(chat_id,sts.id,text=f"Processed Links......\nTotal Links:{len(hrefs)}\nTime:{str(datetime.now())[:23]}")
        total,rm,up =len(urls),len(urls),0
        #sts = app.send_message(chat_id,text=f"Download Status:\nTotal:{total}\nDownloaded:{up}\nDownloading:{rm}\nTime:{str(datetime.now())[:23]}")
        app.edit_message_text(chat_id,sts.id,text=f"Started Download......\nTime:{str(datetime.now())[:23]}")
        cmd = ["aria2c" ,"-i" ,file_path,"--continue=true","-d", download_path]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        if not iszip:
            Thread(target=send_files, args=(app,download_path, chat_id,shah(link))).start()
        for line in process.stdout:
                print(line)
                if 'MiB' in line:
                   spe=line.strip().split()[-2][3:].replace('MiB','MiB/s')
                   siz=line.strip().split()[1].replace("/"," of ")[:-5]
                   con = stats = f'<b>├  FileName : </b>{file_name}\n'\
                             f'<b>├  Engine : </b>Aria2c\n'\
                             f'<b>├  Size : </b>{siz}\n'\
                             f'<b>├  Speed : </b>{spe}\n'\
                             f'<b>╰  Time Taken: </b>{str(datetime.now()-start_time)}\n\n'
                  print(con)
                  if con != old:
                     #print(old,con)
                     #app.edit_message_text(chat_id,st_id,text=con)
                     old = con
                     print(old)
        
                  # Extract download speed
                  match = re.search(r'Speed: ([0-9.]+)MiB/s', line)
                  if "MiB/s" in line :
                    print(con)
                    speed = line.split("|")[2].strip()
                    #sp = app.edit_message_text(chat_id,st_id,text=f"Average Download Speed: {speed}")
            

        process.wait()
        #print(leng(),len(os.listdir(download_path)))
        while leng(str(shah(url))) != len(os.listdir(download_path)):
            app.edit_message_text(chat_id,sts.id,text=f"Download Status:\nTotal:{leng(str(shah(url)))}\nDownloaded:{len(os.listdir(download_path))}\nDownloading:{leng(str(shah(url)))-len(os.listdir(download_path))}\nTime:{str(datetime.now())[:23]}") 
            sleep(2)
        app.edit_message_text(chat_id,sts.id,text=f"Download Status:\nUploading Files...\nTime:{str(datetime.now())[:23]}")
        if iszip:
            zip_files = zip_and_split_folder(download_path,"Zips","_".join(url.split("/")[3:]))
            #print(zip_files)
            for file in zip_files:
                    #print(file)
                    app.send_document(chat_id, document=file, caption=file[6:])
                    os.remove(file)
            else:
                os.system(f"rm -r {download_path}")
        else:
            while total!=up :
                    if not iszip:
                        for file in os.listdir(download_path):
                                Thread(target=send_file, args=(app,download_path+file,chat_id)).start()
                                rm-=1
                                up+=1
                                app.edit_message_text(chat_id,sts.id,text=f"Download Status:\nTotal:{leng(str(shah(url)))}\nUploaded:{leng(str(shah(url)))-len(os.listdir(download_path))}\nUploading:{len(os.listdir(download_path))}\nTime:{str(datetime.now())[:23]}")
        app.edit_message_text(chat_id,sts.id,text=f"Download Status:\nDownload Completed..\nTime:{str(datetime.now())[:23]}")  
    except Exception as err:   
        print(err)


def download_and_send_concurrently(app,links, chat_id,engine,formats):
    threads = []
    if engine=="y":
        for link in links:
           thread = threading.Thread(target=download_and_sendyt, args=(app,chat_id,formats,link))
           threads.append(thread)
           thread.start()
    else:
        for link in links:
          thread = threading.Thread(target=download_and_sendar, args=(app,link, chat_id))
          threads.append(thread)
          thread.start()


    for thread in threads:
        thread.join()

    
