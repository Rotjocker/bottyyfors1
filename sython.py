from telethon import TelegramClient, events, Button, errors
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.sessions import StringSession
import asyncio, json, os, re
 
api_id_bot = 23910531 # اب ايدي
api_hash_bot = "8c2802db0b56c6bd29282bd8fff933ef" # اب هاش
bot = TelegramClient("Bot", api_id_bot, api_hash_bot).start(bot_token="6299081551:AAGvumouIsJdFG3j7zLRLW6C4xSopzIkkFc")


owner_id = [1308075085] # ايديك
collect, bots_to_collect, start_earn = True, [], False


sessions = json.load(open("sessions/sython.json"))




async def ToJson(user, path):
    with open(path, 'w') as file:
        json.dump(user, file) 
        


async def Add_NUMBER(event, api_id, api_hash, phone_number):      
    try:
        phone_number = phone_number.replace('+','').replace(' ', '')
        somy = TelegramClient("sessions/"+phone_number+".session", api_id, api_hash)
        await somy.connect()
        
        if not await somy.is_user_authorized():
            request = await somy.send_code_request(phone_number)
            
            async with bot.conversation(event.chat_id, timeout=300) as conv:

                verification_code_msg = await conv.send_message("ارسل الكود الذي وصلك 🌝")
                response_verification_code = await conv.get_response()
                verification_code = str(response_verification_code.message).replace('-', '')

                try:
                    login = await somy.sign_in(phone_number, code=int(verification_code))
                except errors.SessionPasswordNeededError:
                    password_msg = await conv.send_message("ارسل كلمه تحقق بخطوتين ⚙️")
                    password = await conv.get_response()
                    
                    login = await somy.sign_in(phone_number, password=password.text)

           
                count = f"session_{phone_number}"
                New_item = {count: {"phone": phone_number, "api_id": api_id, "api_hash": api_hash}}
                sessions.update(New_item)

                await ToJson(sessions, "sessions/sython.json")
        return "تـم اضافة الرقم الى البوت"
    except Exception as error:
        return str(error)


async def StartButtons(event, role):
    if role == 2:
        buttons = [[Button.inline("ااضافـة حسـاب", "add_number")]]
    elif role == 1:
        buttons = [[Button.inline("ااضافـة حسـاب", "add_number")], [Button.inline("ازالـة رقـم", "remove_number")]]
    await event.reply("اختر احد الازرار التالية اما اذا كنت تريد بدء الجنيع فأرسل الامر .بدء الجمع مع يوزر البوت بدون @", buttons=buttons)

 

@bot.on(events.NewMessage(pattern='/start'))
async def BotOnStart(event):
    
    if event.chat_id in owner_id:
        await StartButtons(event, 1)
    else:
        await StartButtons(event, 2)


@bot.on(events.CallbackQuery(data="back_to_menu"))
async def Callbacks__(event):

    if event.chat_id in owner_id:
        await StartButtons(event, 1)
    else:
        await StartButtons(event, 2)


@bot.on(events.CallbackQuery(data="remove_number"))
async def Callbacks_(event):
    global sessions
    
    delete, sessions, in_session = await event.delete(), json.load(open("sessions/sython.json")), False
    try:
        async with bot.conversation(event.chat_id, timeout=200) as conv:
            
            get_number= await conv.send_message("__ارسل الرقم لحذفه__")
            remove_number = await conv.get_response()
            remove_number = (remove_number.text).replace('+', '').replace(' ', '')
            for session in sessions:
                session_number = sessions.get(session).get("phone")
                if remove_number == session_number:
                    del sessions[session]
                    await ToJson(sessions, "sessions/sython.json")
                    in_session = True
                    break
        
    except Exception as error:
        print (error)
        
    if in_session == True:
        await event.reply("تـم التخلص من الرقم")
        sessions = json.load(open("sessions/sython.json"))
    else:
        await event.reply("عذرا ولكن رقم الهاتف الذي ارسلته غير موجود")
        
    if event.chat_id in owner_id:
        await StartButtons(event, 1)
    else: 
        await StartButtons(event, 2)


@bot.on(events.CallbackQuery(data="add_number"))
async def Callbacks(event):
    
    await event.delete()    
    try:
        
        async with bot.conversation(event.chat_id, timeout=300) as conv:
            await conv.send_message('ارسل الايبي ايدي')
            api_id_msg = await conv.get_response()
            api_id = api_id_msg.text
            
            await conv.send_message('ارسل ايبي هاش')
            api_hash_msg = await conv.get_response()
            api_hash_msg = api_hash_msg.text
            
            await conv.send_message('ارسل رقم هاتف')
            phone_number_msg = await conv.get_response()
            phone_number_msg = phone_number_msg.text

            

        result = await Add_NUMBER(event, int(api_id), api_hash_msg, phone_number_msg)
        await event.reply(result)
    except Exception as error:
        pass
 
    if event.chat_id in owner_id:
        await StartButtons(event, 1)
    else:
        await StartButtons(event, 2)
    
    
#####################################################################################



@bot.on(events.NewMessage(pattern=r'.بدء الجمع ?(.*)'))
async def StartCollectPoints(event):
    global start_earn
    
    if event.chat_id in owner_id:
        bot_username = (event.message.message).replace('.بدء الجمع', '').strip()
        start_collect, collect = await event.reply('**تم بدأ الجمع**'), True
        

        if start_earn == False:
            start_earn = True
            task = asyncio.create_task(StartCollect(event, bot_username))
            await task
        
        order = await event.reply('**تم انتهاء الجمع**')


async def JoinChannel(client, username):
    try:
        Join = await client(JoinChannelRequest(channel=username))
        return [True, '']
    except errors.FloodWaitError as error:
        return [False, f'تم حظر هذا الحساب من الانضمام للقنوات لمدة : {error.seconds} ثانية']
    except errors.ChannelsTooMuchError:
        return [False, 'هذا الحساب وصل للحد الاقصى من القنوات التي يستطيع الانضمام لها']
    except errors.ChannelInvalidError:
        return [False, False]
    except errors.ChannelPrivateError:
        return [False, False]
    except errors.InviteRequestSentError:
        return [False, False]
    except Exception as error:
        return [False, f'{error}']
    


async def JoinChannelPrivate(client, username):
    try:
        Join = await client(ImportChatInviteRequest(hash=username))
        return [True, '']
    except errors.UserAlreadyParticipantError:
        return [True, '']
    except errors.UsersTooMuchError:
        return [False, False]
    except errors.ChannelsTooMuchError:
        return [False, 'هذا الحساب وصل للحد الاقصى من القنوات التي يستطيع الانضمام لها']
    except errors.InviteHashEmptyError:
        return [False, False]
    except errors.InviteHashExpiredError:
        return [False, False]
    except errors.InviteHashInvalidError:
        return [False, False]
    except errors.InviteRequestSentError:
        return [False, False]
    except Exception as error:
        return [False, f'{error}']
    


async def StartCollect(event, bot_username):
    
    
    sessions = json.load(open("sessions/sython.json"))
    while collect != False:
        for session in sessions:
            try:
                if collect == False:
 
                    try:
                        await client.disconnect()
                    except Exception as error:
                        pass
                    break
                
                api_id = int(sessions[session]["api_id"])
                api_hash = str(sessions[session]["api_hash"])
                phone = str(sessions[session]["phone"])
                
                client = TelegramClient("sessions/"+(phone), api_id, api_hash)
                
                await client.connect()
                user = await client.get_me()
                if user == None:
                    await bot.send_message(entity=owner_id[0] ,message=f"**الرقم :** {phone}\n\nهذا الرقم لا يعمل")
                else:
                    async with client.conversation(bot_username, timeout=20) as conv:
                        try:
                            while True:
                                start_msg1 = await conv.send_message("/start")
                                resp = await conv.get_response()
                                

                                if "عذراً يجب" in resp.text or "عذرا عزيزي" in resp.text:
                                    link_pattern = re.compile(r'(https?://\S+)')
                                    link = re.search(link_pattern, resp.message).group(1)
                                    
                                    print (link)
                                    if link.startswith('https://t.me/+') or link.startswith('https://t.me/joinchat/+'):
                                        link = link.replace('https://t.me/joinchat/+', '')
                                        link = link.replace('https://t.me/+', '')
                                        result = await JoinChannelPrivate(client, link.strip())
                                    else:
                                        get_entity_must_join = await client.get_entity(link)
                                        result = await JoinChannel(client, get_entity_must_join.id)
                                else:
                                    break
 
                            click_collect = await resp.click(2)
                            resp2 = await conv.get_edit()
                            click_collect = await resp2.click(0)
                    
                            for x in range(6):
                                if collect == False:

                                    try:
                                        await client.disconnect()
                                    except Exception as error:
                                        pass
                                    break
                                try:
                                    channel_details = await conv.get_edit()       
                                    

                                    number_str = (channel_details.message).split('نقاطك الحاليه :')[1].strip()
                                    if int(number_str.strip()) >= 2000:
                                        await bot.send_message(entity=owner_id[0] ,message=f"**الرقم :** {phone}\n\n__لقد وصل هذا الحساب الى {number_str} نقطة__")
                                        break
                                                             
                                    channel_url = (channel_details.reply_markup.rows[0].buttons[0].url).replace('https://t.me/', '')
                                    if "+" in channel_url:
                                        channel_url = channel_url.replace('+', '')
                                        result = await JoinChannelPrivate(client, channel_url)
                                    else:
                                        result = await JoinChannel(client, channel_url)

                                    if result[0] == True:
                                        await channel_details.click(2)
                                    else:
                                        if result[1] == False:
                                            await channel_details.click(1)
                                        else:
                                            await bot.send_message(entity=owner_id[0] ,message=f"**الرقم :** {phone}\n\n__{result[1]}__")

                                            try:
                                                await client.disconnect()
                                            except Exception as error:
                                                pass
                                            break
                                        
                                    await asyncio.sleep(3)
                                    
                                except Exception as error:
                                    await bot.send_message(entity=owner_id[0] ,message=f"**الرقم :** {phone}\n\n__{error}__")

                                    try:
                                        await client.disconnect()
                                    except Exception as error:
                                        pass
                                    break
                    
                        except Exception as error:
                            if str(error) == "":
                                await bot.send_message(entity=owner_id[0] ,message=f"**الرقم :** {phone}\n\nالبوت لا يستجيب بسرعه. تم تخطي هذا الرقم")
                
               
                try:
                    await client.disconnect()
                except Exception as error:
                    pass
                
                sessions = json.load(open("sessions/sython.json"))
            except Exception as error:
                pass

bot.run_until_disconnected()
