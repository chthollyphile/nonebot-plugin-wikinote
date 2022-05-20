from nonebot import on_command, on_regex
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters import Message
from urllib import parse
import re
import asyncio
import aiohttp
import json

# custom setting
# use of main account for login is not supported. 
# Obtain credentials via Special:BotPasswords
# (https://www.mediawiki.org/wiki/Special:BotPasswords) for account & password

account = "" 
password = ""
quicknote = ""
URL = "https://yourwiki.tld/api.php"

record = on_command("记录", priority=5, block=True)
write = on_command("写入", priority=5, block=True)
search_mev = on_command("搜索wiki", priority=5, block=True) # search mediawiki
snippet = on_command("典中典", priority=5, block=True)
write_snippet = on_command("典",priority=5, block=True)

# /记录
@record.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()  # 输入预处理，e.g."/记录 123 234" -> "123 234"
    if args:
        state["args"] = args
@record.got("args", prompt="请告知需要记录到"+quicknote+"的内容") # get state["arg"] in case user sends an empty msg.
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args_record = await page_insert(args,title = quicknote)
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
    args_write = await embed_page_insert_with_p(args, title)
    await write.finish(args_write)

async def get_write(args: str, title: str): # mediaWiki API
    async with aiohttp.ClientSession() as session:
        PARAMS_0 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        async with session.get(URL, params=PARAMS_0) as R0:
            DATA = await R0.json()
            LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
        PARAMS_1 = {
            "action": "login",
            "lgname": account,
            "lgpassword": password,
            "lgtoken": LOGIN_TOKEN,
            "format": "json"
        }
        await session.post(URL, data=PARAMS_1)
        PARAMS_2 = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        async with session.get(URL, params=PARAMS_2) as R2:
            DATA = await R2.json()
            CSRF_TOKEN = DATA['query']['tokens']['csrftoken']
            Hello = args
            content = "<p>" + Hello + "</p>"
        PARAMS_3 = {
            "action": "edit",
            "title": title,
            "token": CSRF_TOKEN,
            "format": "json",
            "appendtext": content
        }
        await session.post(URL, data=PARAMS_3)

async def page_insert(args: str, title: str):
    await asyncio.gather(get_write(args,title))

async def get_write1(args: str, title: str): # mediaWiki API
    async with aiohttp.ClientSession() as session:
        PARAMS_0 = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        async with session.get(URL, params=PARAMS_0) as R0:
            DATA = await R0.json()
            LOGIN_TOKEN = DATA['query']['tokens']['logintoken']
        PARAMS_1 = {
            "action": "login",
            "lgname": account,
            "lgpassword": password,
            "lgtoken": LOGIN_TOKEN,
            "format": "json"
        }
        await session.post(URL, data=PARAMS_1)
        PARAMS_2 = {
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }
        async with session.get(URL, params=PARAMS_2) as R2:
            DATA = await R2.json()
            CSRF_TOKEN = DATA['query']['tokens']['csrftoken']
            content = args
        PARAMS_3 = {
            "action": "edit",
            "title": title,
            "token": CSRF_TOKEN,
            "format": "json",
            "appendtext": content
        }
        await session.post(URL, data=PARAMS_3)

# /搜索wiki
@search_mev.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args
@search_mev.got("args", prompt="搜索什么内容？") # get state["arg"] in case user sends an empty msg.
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args_search_mev = await ssearch_mev(args) # 防重名
    await search_mev.finish(args_search_mev)

async def ssearch_mev(args):
    async with aiohttp.ClientSession() as session:
        PARAMS = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srsearch": args,
                    "srwhat": "text",
                }
        async with session.get(url=URL, params=PARAMS) as S:
            DATA = await S.json()
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

# /典中典
@write_snippet.handle()
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

@write_snippet.got("title", prompt="请告知典中典的标题")
@write_snippet.got("args", prompt="请告知典中典的内容")
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    title = state["title"]
    args_write = await embed_page_insert(args,title)
    await write_snippet.finish(args_write)

async def embed_page_insert(args: str, title: str): # notion API
    await asyncio.gather(get_write1(args,title))

async def embed_page_insert_with_p(args: str, title: str): # notion API
    await asyncio.gather(get_write(args,title))

@snippet.handle()
async def handle_first_receive(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if args:
        state["args"] = args
@snippet.got("args", prompt="要看哪篇典中典？") # get state["arg"] in case user sends an empty msg.
async def handle_args(bot: Bot, event: Event, state: T_State):
    args = state["args"]
    args_search = await snippets_mev(args)
    await snippet.finish(args_search)

async def snippets_mev(args):
    async with aiohttp.ClientSession() as session:
        PARAMS = {
                    "action": "parse",
                    "page": args,
                    "prop": "wikitext",
                    "formatversion":"2",
                    "format":"json"
                }
        async with session.get(URL, params=PARAMS) as S:
            DATA = await S.json()
            try:
                dict = DATA['parse']
            except KeyError:
                pf = await pfsearch(args)
                return f'没有找到标题为"'+args+'"的词条' + pf
            result = dict['wikitext']
            if len(result)<=1665:
                return result.strip()
            else:
                uri = parse.quote(args)
                return f'词条过长，请自行前往 https://chamomilepasta.ml/index.php?title='+uri 

async def pfsearch(args):
    async with aiohttp.ClientSession() as session:
        PARAMS = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": args,
        "srwhat": "title"
        }
        async with session.get(url=URL, params=PARAMS) as R:
            DATA = R.json()
            result = ""
            list = DATA['query']['search']
            for item in list:
                result = result + item['title'] + " | "
            if not result:
                return result
            else:
                return ",也许您要找的是："+result.strip()
