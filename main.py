import asyncio
import os
import time,re,datetime,sqlite3,hashlib,logging,traceback
from telethon import TelegramClient, sync,errors


#########################################
api_id = 0
api_hash = '???'
channel_="channel"
user_id="your_id_for_errors"
path_to_save="/var/www/html/folder/" #save to nginx folder
#########################################
client = TelegramClient('session_name', api_id, api_hash)
client.start()
cgcool=client.get_entity(channel_)
time_edit=0

dem2 = lambda list,where:[l[where] for l in list]


from_date = datetime.datetime.strptime(f'11.11.2000 14:00:00', '%d.%m.%Y %H:%M:%S').replace(tzinfo=datetime.timezone.utc)

pre_first_msg = client.get_messages(cgcool, offset_date=from_date, limit=2,reverse=True)
pre_first_msg=pre_first_msg[1]

async def callback(current, total):
   global time_edit
   global pre_first_msg
   dsd=int(100*(current/total))
   if time.time()-time_edit>3:
      try:await client.edit_message(pre_first_msg,f"down: {dsd}%")
      except errors.rpcerrorlist.MessageNotModifiedError:pass
      time_edit=time.time()

def get_files(path=path_to_save):
   allofthem=[]
   for file in os.listdir(path):
      
      opj=os.path.join(path, file)
      if os.path.isfile(opj):
         allofthem.append(re.sub(path_to_save,"",opj))
      elif os.path.isdir(opj):
         if len(os.listdir(opj)) == 0:
            os.rmdir(opj)
         else:
            [ allofthem.append(_d) for _d in get_files(opj)]
         
   return allofthem

def main():

   global pre_first_msg
   global path_to_save

   to_date = datetime.datetime.strptime('15.05.2026 14:00:00', '%d.%m.%Y %H:%M:%S').replace(tzinfo=datetime.timezone.utc)

   last_msg = client.get_messages(cgcool, offset_date=to_date, limit=1)[0]
   shit=client.get_messages(cgcool, min_id=pre_first_msg.id, max_id=last_msg.id,reverse=True)
   messages_between = [m for m in [pre_first_msg]+[sh for sh in shit ]+[last_msg]]
   # print([(m.text,messages_between.index(m)) for m in messages_between])
   f_names=[(m.text.strip("-/"),messages_between.index(m)) for m in messages_between if str(m.text).startswith("-/")]
   d_names=[d for d in get_files()]

   # print(d_names,f_names)

   for d in d_names:
      if re.sub("\..+","",d) not in dem2(f_names,0):
         os.remove(os.path.join(path_to_save,d))

   for f in f_names:
      if f[0] not in [re.sub("\..+","",d) for d in d_names] and len(messages_between)>f[1]+1:
         try:
            nm=messages_between[f[1]+1]
            nname=f[0]+re.findall(".*(\.[^\.]+)",nm.file.name)[0]
         except:
            #client.send_message(client.get_entity(user_id),traceback.format_exc()+"++++++++++++++"+str(nm.file.name))
            nname=f[0]

         
         filemsg=messages_between[f[1]+1]
         filemsg.download_media(file=os.path.join(path_to_save,nname),progress_callback=callback)
         
         
while True:
   try:
      time.sleep(3)
      main()
   except:
      client.send_message(client.get_entity(user_id),traceback.format_exc())
      time.sleep(60)
