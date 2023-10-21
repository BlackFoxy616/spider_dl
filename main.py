from pyrogram import Client, filters
import time,csv,os
import yt_dlp
from hurry.filesize import size
from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup,
                            InlineKeyboardButton)





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



def extract(yturl):
    ydl = yt_dlp.YoutubeDL()
    with ydl:
        qualityList = []
        r = ydl.extract_info(yturl, download=False)
        """ with open ("dump.txt","w+") as file:
             file.write(str(r))"""
        for format in r['formats']:
            if not "dash" in str(format['format']).lower():
                if "filesize" in format and format['filesize'] != None and format['video_ext'] !="webm" :
                  qualityList.append(" ".join([str(format['format']),size(format['filesize']),str(format['video_ext'])]))

   
   
    return r["title"],qualityList





@app.on_message(filters.command("dl"))
async def start_command(client,message):
         query = message.text.split()
         button_list =[]
         info = extract(query[1])
         co=0
         temp = []
         for i in range(len(info[1])):
             X = info[1][i].split(" ")
             Y = X[3].replace("(","").replace(")","")+","+X[5]+","+X[4]
             if X[3] == "only":
                  Y = X[4].replace("(","").replace(")","")+", mp3 ,"+X[5]
             temp.append(InlineKeyboardButton( Y, info[1][i].split(" ")[0]+f"__{query[1]}"))
             co+=1
             if co%2==0 or i == len(info[1])-1:
               button_list.append(temp)
               temp=[]
          
         reply_markup=InlineKeyboardMarkup(button_list)
         choice = await app.send_message(
            message.chat.id,"Select The Format:",reply_markup=reply_markup)
        







def extract2(yturl):
    ydl = yt_dlp.YoutubeDL()
    with ydl:
        qualityList = []
        r = ydl.extract_info(yturl, download=False)
        with open ("dump.txt","w+") as file:
             file.write(str(r))

   
   
    return r




#G =  extract2("https://youtube.com/playlist?list=PLxnyxqL6KA4jO2gQBRj560DGCFH4b5tIe&si=pTTeEk292wd1Qvy0")
#print(G)

        




@app.on_callback_query()
async def answer(client, call):
         await app.delete_messages(call.message.chat.id,call.message.id)
         data = call.data.split("__")
         os.system(f"yt-dlp -f {data[0]} --downloader aria2c --download-archive music.txt {data[1]}")
         title = extract(data[1])[0]
         for i in os.listdir():
              if i.endswith('mp4') or i.endswith('mp3') or i.endswith('webm'):
                os.system(f'''vcsi """{i}""" -g 2x2 --metadata-position hidden -o """{i.replace('.mp4','.png')}""" ''')
                await app.send_video(call.message.chat.id,video=i,caption=title,thumb=i.replace(".mp4",".png"))
             
                


print("Bot Started ..!!")

app.run()
