from pyrogram import filters

from CheckAnons import CheckAnons


@CheckAnons.on_message(filters.command('set_url'))
async def url_handler(client, message):
    await client.set_chat_and_url(message.chat.id, message.command[1])
    await message.reply("Слежение за URL " + message.command[1] + " запущено")


@CheckAnons.on_message(filters.command('clear_url'))
async def url_handler(client, message):
    await client.clear_url(message.chat.id)
    await message.reply("Слежение за URL остановлено")
