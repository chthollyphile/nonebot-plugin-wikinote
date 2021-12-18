from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

import requests
import re

# custom setting
# use of main account for login is not supported. 
# Obtain credentials via Special:BotPasswords
# (https://www.mediawiki.org/wiki/Special:BotPasswords) for account & password

account = "" 
password = ""
quicknote = "" # quicknote页面标题
URL = "" # https://www.mediawiki.org/api.php
record = on_command("记录", priority=5)
write = on_command("写入", priority=6)
search = on_command("搜索", priority=4)

# /记录
@record.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 输入预处理，e.g."/记录 123 234" -> "123 234"
    if args:
        state["args"] = args
@record.got("args", prompt="请告知需要记录到"+quicknote+"的内容") # get state["arg"] in case user sends an empty msg.
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args_record = await get_write(args,title = quicknote)
    await record.finish(args_record)

# /写入  
@write.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    raw = str(event.get_message()).strip()
    titles = re.match("#(.+?)#", raw)  # 使用 #标题# 来传入词条标题
    if titles:
        titles = titles.group()
        title = re.sub("#","",titles)
        args = raw.replace(titles,"")
    else:
        title  = None
    if title:
        state["args"] = args
        state["title"] = title

@write.got("title", prompt="请告知写入的词条标题")
@write.got("args", prompt="请告知需要写入的内容")
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    title = state["title"] 
    args_write = await get_write(args,title)
    await write.finish(args_write)

async def get_write(args: str, title: str): # mediaWiki API
    S = requests.Session() 
    # Step 1: GET request to fetch login token
    PARAMS_0 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }
    R = S.get(url=URL, params=PARAMS_0)
    DATA = R.json()
    LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
    # Step 2: POST request to log in. 
    PARAMS_1 = {
        "action": "login",
        "lgname": account,
        "lgpassword": password,
        "lgtoken": LOGIN_TOKEN,
        "format": "json"
    }
    R = S.post(URL, data=PARAMS_1)
    # Step 3: GET request to fetch CSRF token
    PARAMS_2 = {
        "action": "query",
        "meta": "tokens",
        "format": "json"
    }
    R = S.get(url=URL, params=PARAMS_2)
    DATA = R.json()
    CSRF_TOKEN = DATA['query']['tokens']['csrftoken']

    Hello = args
    content = "<br><br>" + Hello

    # Step 4: POST request to edit a page
    PARAMS_3 = {
        "action": "edit",
        "title": title,
        "token": CSRF_TOKEN,
        "format": "json",
        "appendtext": content
    }
    R = S.post(URL, data=PARAMS_3)

# /搜索
@search.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args
@search.got("args", prompt="搜索什么内容？") # get state["arg"] in case user sends an empty msg.
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args_search = await ssearch(args) # 防重名
    await search.finish(args_search)

async def ssearch(args):
    S = requests.Session()
    PARAMS = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": args,
                "srwhat": "text",
            }
    DATA = S.get(url=URL, params=PARAMS).json()
    result = ""
    list = DATA['query']['search']
    for item in list:
        result = result + item['title'] + " : " + item["snippet"]
    result = re.sub(r'<.*?>', "", result)
    if not result:
        return f"未找到结果"
    else:
        results = result.replace("&lt;/p&gt;&lt;p&gt;","...")
        return results.strip()