from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from bs4 import BeautifulSoup
import aiohttp
import aiosqlite3
import pickle


async def async_fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


class CheckAnons(Client):

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.db = "chats.db"
        super().__init__(
            "CheckAnons",
            bot_token="1391829242:AAErTbeoEQ4G_Hhh1fMJqMqVQdz9Lwb8EsY",
            workers=16,
            plugins=dict(root="CheckAnons/plugins"),
        )

    async def start(self):
        self.scheduler.add_job(self.check_url, "interval", minutes=5)
        self.scheduler.start()
        await super().start()
        print("Bot started")

    async def stop(self, block: bool = True):
        self.scheduler.shutdown()
        await super().stop(block)
        print("Bot stopped")

    async def check_url(self):
        chats_and_urls = await self.get_chat_and_url()
        for row in chats_and_urls:
            chat_id = row[0]
            url = row[1]
            try:
                with open(chat_id + "_html", 'rb') as f:
                    anons_html = pickle.load(f)
            except EOFError:
                anons_html = ""
            if url != "":
                if url.startswith("http://"):
                    pass
                else:
                    url = "http://" + url

                async with aiohttp.ClientSession() as session:
                    response = await async_fetch(session, url)
                soup = BeautifulSoup(response, 'html.parser').find("span", {"id": "lblFromAuthor"}).parent

                if anons_html != "" and soup != anons_html:
                    await self.send_message(chat_id, "Анонс " + url + "изменился, проверьте")

                with open(chat_id + '_html', 'wb') as f:
                    pickle.dump(soup, f)

    async def set_chat_and_url(self, chat_id, url):
        with open(chat_id + "_html", 'w'):
            pass
        query = 'REPLACE into chats (chat, url) values (' + chat_id + ', ' + url + ');'
        await self.exec_query(query)

    async def clear_url(self, chat_id):
        query = 'DELETE from chats where chat = ' + chat_id + ';'
        await self.exec_query(query)

    async def get_chat_and_url(self):
        query = 'SELECT chat, url from chats'
        result = await self.exec_query(query)
        return result

    async def exec_query(self, query):
        try:
            connect = await aiosqlite3.connect(self.db)
            cursor = await connect.cursor()
            await cursor.execute(query)
            result = await cursor.fetchall()
            await connect.commit()
            await connect.close()
            return result
        except aiosqlite3.DatabaseError as ex:
            template = "Произошла ошибка {0}. **Параметры ошибки**:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print(message)
