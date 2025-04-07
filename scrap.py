import os
import asyncio
from json import dump
from colorama import init, Fore
from datetime import datetime,timedelta
from time import sleep
from pytz import timezone
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import PhoneNumberBannedError
from telethon.tl.types import UserStatusRecently, UserStatusLastMonth, UserStatusLastWeek, UserStatusOffline, UserStatusOnline, PeerChannel, ChannelParticipantsAdmins, User
import webbrowser

webbrowser.open('http://github.com/Mr-Spect3r/My-Tools', new=2)

init()

def clear():
    os.system("cls || clear")

colors = {
    "red": '\033[00;31m',
    "green": '\033[00;32m',
    "light_green": '\033[01;32m',
    "yellow": '\033[01;33m',
    "light_red": '\033[01;31m',
    "blue": '\033[94m',
    "purple": '\033[01;35m',
    "cyan": '\033[00;36m',
    "grey": '\033[90m',
    "reset": Fore.RESET,
    "light_green_ex": Fore.LIGHTGREEN_EX,
    "white": Fore.WHITE,
}

messages = {
    "info": f"{colors['red']}[{colors['light_green']}+{colors['red']}] {colors['light_green']}",
    "error": f"{colors['red']}[{colors['light_red']}-{colors['red']}] {colors['light_red']}",
}

api_id = '1'
api_hash = '1'

if not os.path.exists('sessions'):
    os.makedirs('sessions')

today = datetime.now()
yesterday = today - timedelta(days=1)

async def get_user_messages(group_link, user_id, phone):
    async with TelegramClient(f'sessions/{phone}', api_id, api_hash) as client:
        try:
            group = await client.get_entity(group_link)
            messages_data = []

            async for message in client.iter_messages(group):
                if message.sender_id == user_id:
                    message_date = message.date.strftime('%Y-%m-%d %H:%M:%S')
                    message_info = {
                        'date': message_date,
                        'text': message.text
                    }
                    messages_data.append(message_info)

            filename = f'user_{user_id}_messages.json'
            with open(filename, 'w', encoding='utf-8') as f:
                dump(messages_data, f, ensure_ascii=False, indent=4)

            print(f"{messages['info']}Messages saved to {filename}")

        except Exception as e:
            print(f"{messages['error']}Error: {e}")
async def get_group_messages(group_link,phone):
    async with TelegramClient(f'sessions/{phone}', api_id, api_hash) as client:
        group = await client.get_entity(group_link)
        
        if isinstance(group, PeerChannel):
            print(f'Group Title: {group.title}')
        
        iran_tz = timezone('Asia/Tehran')  
        
        filename = f'{group.title.replace(" ", "_")}_{group.id}_messages.json'
        
        async for message in client.iter_messages(group):
            sender = message.sender_id
            if sender:
                user = await client.get_entity(sender)
                
                if isinstance(user, User):
                    name = f'{user.first_name or ""} {user.last_name or ""}'.strip()
                    username = f'@{user.username}' if user.username else 'No username'
                else:
                    name = "Unknown Sender"
                    username = "No username"

                message_date = message.date.astimezone(iran_tz).strftime('%Y-%m-%d %H:%M:%S')  
                
                message_data = {
                    'date': message_date,
                    'name': name,
                    'username': username,
                    'user_id': user.id,
                    'text': message.text
                }

                with open(filename, 'a', encoding='utf-8') as f:
                    dump(message_data, f, ensure_ascii=False)
                    f.write('\n')  
        print (f"{colors['green']} Saved! File Name {colors['yellow']} {filename}")
                

async def get_member_info(member, is_admin):
    name = f'{member.first_name or ""} {member.last_name or ""}'.strip()
    username = f'@{member.username}' if member.username else 'No username'
    bio = getattr(member, 'bio', 'Bio not available')
    user_id = member.id
    access_hash = member.access_hash
    status = member.status

    return {
        'name': name,
        'username': username,
        'bio': bio,
        'user_id': user_id,
        'access_hash': access_hash,
        'status': status,
        'is_admin': is_admin  
    }

async def get_group_members(group_link, filter_choice, phone):
    async with TelegramClient(f'sessions/{phone}', api_id, api_hash) as client:
        group = await client.get_entity(group_link)
        members = await client.get_participants(group, aggressive=True)
        admins = await client.get_participants(group, filter=ChannelParticipantsAdmins)
        admin_ids = {admin.id for admin in admins}

        member_info_tasks = [
            get_member_info(member, member.id in admin_ids) for member in members
        ]
        member_infos = await asyncio.gather(*member_info_tasks)

        filtered_members = filter_members(member_infos, filter_choice)
        write_to_json(filtered_members, group.title, group.id)


def filter_members(members, choice):
    filtered = []
    for member in members:
        if isinstance(member['status'], UserStatusOffline):
            was_online = member['status'].was_online
            if choice == 1 and was_online and (was_online.date() == today.date() or was_online.date() == yesterday.date()):
                filtered.append(member)
            elif choice == 4:
                continue
        elif isinstance(member['status'], (UserStatusOnline, UserStatusRecently)):
            if choice in [0, 1, 2, 3]:
                filtered.append(member)
        elif isinstance(member['status'], UserStatusLastWeek):
            if choice in [0, 2, 3]:
                filtered.append(member)
        elif isinstance(member['status'], UserStatusLastMonth):
            if choice in [0, 3]:
                filtered.append(member)

    return filtered

def write_to_json(members, group_title, group_id):
    data_to_save = [{
        'name': member['name'],
        'username': member['username'],
        'user_id': member['user_id'],
        'access_hash': member['access_hash'],
        'group': group_title,
        'group_id': group_id,
        'status': type(member['status']).__name__,
        'is_admin': member['is_admin'] 
    } for member in members]

    with open(f"{group_title}.json", "w", encoding='UTF-8') as f:
        dump(data_to_save, f, ensure_ascii=False, indent=4)

    print (f"{messages['info']}Saved! File Name: {colors['yellow']}{group_title}.json")

async def select_session():
    session_files = [f for f in os.listdir('sessions') if f.endswith('.session')]
    if not session_files:
        return None
    clear()
    print (f'''{colors["white"]}
▀▄    ▄ ████▄   ▄  
  █  █  █   █    █ 
   ▀█   █   █ █   █
   █    ▀████ █   █
 ▄▀           █▄ ▄█
               ▀▀▀ 
''')
    for idx, session in enumerate(session_files):
        async with TelegramClient(f'sessions/{session}', api_id, api_hash) as client:
            me = await client.get_me()
            username = f'{colors["yellow"]}@{me.username}' if me.username else f'{colors["red"]}None'

            print(f"{colors['red']}[{colors['light_green']}{idx + 1}{colors['red']}] {colors['light_green_ex']}{session[:-8]} {colors['red']}({colors['cyan']}ID: {colors['yellow']}{me.id}{colors['white']}, {colors['cyan']}Username: {username}{colors['white']}, {colors['cyan']}Name:{colors['yellow']} {me.first_name}{colors['red']})") 
    while True:
        choice = input(f"\n\n{messages['info']}Choose a session by number or type '0' for a new account: {colors['yellow']}")
        if choice.lower() == '0':
            return None
        try:
            choice_index = int(choice) - 1
            if 0 <= choice_index < len(session_files):
                return session_files[choice_index][:-8]  
        except ValueError:
            print(f"{messages['error']}Invalid input. Please enter a valid number or 'new'.")

async def authenticate_user(phone, api_id, api_hash):
    async with TelegramClient(f'sessions/{phone}', api_id, api_hash) as client:
        await client.start(phone)
        clear()
        print(f"{messages['info']}Authentication successful!")
        sleep(3)

async def main():
    phone = await select_session()
    clear()
    if phone is None:
        clear()
        phone = input(f"{messages['info']}Enter your phone number (with country code): {colors['cyan']}")
        id = input(f"{messages['info']}Enter your api id: {colors['cyan']}")
        hash = input(f"{messages['info']}Enter your api hash: {colors['cyan']}")
        await authenticate_user(phone, id, hash)
    print (f'''{colors["grey"]}                                                                                                                                                                              
                ..........                                                             
              .*#########+..                                                           
            -#**###########+.                                                          
           *:*=*+*##########+..                                                        
         .+*=.:##=###########+.                                                        
         .**+..+:*###########*: {colors["red"]}Telegram Scraper{colors["grey"]}                                                         
         .*##-:+#######*######+.                                                       
          .##########-....#####. {colors["red"]}Telegram: @MrEsfelurm{colors["grey"]}                                                      
            .+#%%*-..   ..+####:                                                       
                        ..+####-.       .:=:.                                          
                        ..*####-.   ..+#######:.                                       
                        ..*####=.  :###########*..         ... ....                    
                         .*#####*#######*=#######*.... .*#######:..    .*              
                         .*###########*.  ..#####################-.    .*:             
                         .=##########:.     .=##########=.. ..*###:.   =#......        
........  ........::::::::--#######+============#####-----::::::+###*##+..    ..  .    
.......:::--===+++**************###################**************++++=---:::......                                                                                      
''')
    choice = int(input(f"{colors['red']}[{colors['light_green']}1{colors['red']}] {colors['light_green_ex']} Scrap group members\n{colors['red']}[{colors['light_green']}2{colors['red']}] {colors['light_green_ex']} Get user information\n{colors['red']}[{colors['light_green']}3{colors['red']}] {colors['light_green_ex']} Receive all messages of a user in the group\n{colors['red']}[{colors['light_green']}4{colors['red']}] {colors['light_green_ex']} Receive all group messages\n\n\t{messages['info']}Select operation: {colors['cyan']}"))
    clear()
    if choice == 1:
        group_link = input(f"{messages['info']}Enter the group link (e.g., https://t.me/your_group): {colors['cyan']}")
        clear()
        print (f'''{colors["yellow"]}
 ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌
▐░█▄▄▄▄▄▄▄▄▄ ▐░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌
▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
 ▀▀▀▀▀▀▀▀▀█░▌▐░▌          ▐░█▀▀▀▀█░█▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ 
          ▐░▌▐░▌          ▐░▌     ▐░▌  ▐░▌       ▐░▌▐░▌          
 ▄▄▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌      ▐░▌ ▐░▌       ▐░▌▐░▌          
▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          
 ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀         ▀  ▀    \n\n       
''')
        filter_choice = int(input(f"{colors['red']}[{colors['light_green']}0{colors['red']}] {colors['light_green_ex']}All users\n{colors['red']}[{colors['light_green']}1{colors['red']}] {colors['light_green_ex']}Active today/yesterday\n{colors['red']}[{colors['light_green']}2{colors['red']}] {colors['light_green_ex']}Active last week\n{colors['red']}[{colors['light_green']}3{colors['red']}] {colors['light_green_ex']}Active last month\n{colors['red']}[{colors['light_green']}4{colors['red']}] {colors['light_green_ex']}Inactive\n\n\t{messages['info']}Select filter: {colors['cyan']}"))
        await get_group_members(group_link, filter_choice, phone)
    elif choice == 2:
        username = input(f"{messages['info']}Enter the username (without @): {colors['cyan']}")
        await get_user_info(username, phone) 
    elif choice == 3:
        group_link = input(f"{messages['info']}Enter the group link (e.g., https://t.me/your_group): {colors['cyan']}")
        user_id = int(input(f"{messages['info']}Enter the user ID whose messages you want to retrieve: {colors['cyan']}"))
        clear()
        print (f'''{colors["yellow"]}
  █████████                                        
 ███░░░░░███                                       
░███    ░░░   ██████  ████████   ██████   ████████ 
░░█████████  ███░░███░░███░░███ ░░░░░███ ░░███░░███
 ░░░░░░░░███░███ ░░░  ░███ ░░░   ███████  ░███ ░███
 ███    ░███░███  ███ ░███      ███░░███  ░███ ░███
░░█████████ ░░██████  █████    ░░████████ ░███████ 
 ░░░░░░░░░   ░░░░░░  ░░░░░      ░░░░░░░░  ░███░░░  
                                          ░███     
                                          █████    
                                         ░░░░░     \n\n       
''')
        await get_user_messages(group_link, user_id, phone)
    elif choice == 4:
        group_link = input(f"{messages['info']}Enter the group link (e.g., https://t.me/your_group): {colors['cyan']}")
        clear()
        print (f'''{colors["green"]}
   ▄████████  ▄████████    ▄████████    ▄████████    ▄███████▄
  ███    ███ ███    ███   ███    ███   ███    ███   ███    ███
  ███    █▀  ███    █▀    ███    ███   ███    ███   ███    ███
  ███        ███         ▄███▄▄▄▄██▀   ███    ███   ███    ███
▀███████████ ███        ▀▀███▀▀▀▀▀   ▀███████████ ▀█████████▀ 
         ███ ███    █▄  ▀███████████   ███    ███   ███       
   ▄█    ███ ███    ███   ███    ███   ███    ███   ███       
 ▄████████▀  ████████▀    ███    ███   ███    █▀   ▄████▀     
                          ███    ███                          \n\n
''')
        await get_group_messages(group_link,phone)
    else:
        print(f"{messages['error']}Invalid choice. Please select either 1, 2,3 or 4")

async def get_user_info(username, phone):
    async with TelegramClient(f'sessions/{phone}', api_id, api_hash) as client:
        entity = await client.get_entity(username)
        clear()
        print (f'''{colors["yellow"]}
 _____        ___      
(_____)      / __)     
   _   ____ | |__ ___  
  | | |  _ \|  __) _ \ 
 _| |_| | | | | | |_| |
(_____)_| |_|_|  \___/   
''')
        response = ""

        if hasattr(entity, 'first_name'):
            response += f"{messages['info']}Account Name: {colors['yellow']}{entity.first_name} {entity.last_name or ''}\n"
            response += f"{messages['info']}Numeric ID: {colors['yellow']}{entity.id}\n"
            response += f"{messages['info']}ID: {colors['yellow']}@{username}\n"
            response += f"{messages['info']}Phone: {colors['yellow']}{entity.phone or 'No'}\n"
            response += f"{messages['info']}Bot: {colors['yellow'] + 'Yes' if entity.bot else colors['red'] + 'No'}\n"
        elif hasattr(entity, 'title'):
            response += f"{messages['info']}Channel/Group Name: {colors['yellow']}{entity.title}\n"
            response += f"{messages['info']}Numeric ID: {colors['yellow']}{entity.id}\n"
            response += f"{messages['info']}ID: {colors['yellow']}@{username}\n"
            res = await client(functions.channels.GetFullChannelRequest(entity))
            response += f"{messages['info']}Member Count: {colors['yellow']}{res.full_chat.participants_count}\n"
        else:
            print(f"{messages['error']}This username does not correspond to a user or channel/group.")
            return
        
        print(response)  

if __name__ == '__main__':
    asyncio.run(main())
