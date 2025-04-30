import asyncio
       from aiogram import Bot, Dispatcher, Router, types
       from aiogram.filters import CommandStart
       from aiogram.types import Message
       import logging
       from aiohttp import web

       # Настройка логирования
       logging.basicConfig(level=logging.INFO)

       # Инициализация бота и диспетчера
       bot = Bot(token="8150630981:AAEOcVcZOFKVSYbJBG0SJdXgMn0vmvULWws")
       dp = Dispatcher()
       router = Router()
       dp.include_router(router)

       # ID чата, куда будут перенаправляться запросы
       SUPPORT_CHAT_ID = -4645385426

       # Словарь для хранения первого сообщения от пользователя
       user_first_message = {}

       @router.message(CommandStart())
       async def start_command(message: Message):
           await message.answer(
               """Привет! Это горячая линия Тринити Харрогейт. 
       Мы принимаем обращения с 10:00 до 18:00 по МСК. Опишите вашу проблему (например, отсутствие товара, задержка доставки), и мы оперативно поможем!
       Обращения направляются в следующем формате:
       Проблема:
       Название спота:
       Город:
       Номер для оперативной связи:"""
           )

       @router.message()
       async def handle_message(message: Message):
           print(f"Получено сообщение: {message.text} от {message.from_user.id}")
           if message.chat.type == "private" and not message.from_user.is_bot:
               user_id = message.from_user.id
               if user_id not in user_first_message:
                   user_first_message[user_id] = message.message_id
                   forwarded = await message.forward(SUPPORT_CHAT_ID)
                   await bot.send_message(
                       SUPPORT_CHAT_ID,
                       f"Новый запрос от @{message.from_user.username or 'NoUsername'} (ID: {user_id}). Ответьте, процитировав это сообщение.",
                       reply_to_message_id=forwarded.message_id
                   )
               else:
                   await message.forward(SUPPORT_CHAT_ID)
           elif message.chat.id == SUPPORT_CHAT_ID and not message.from_user.is_bot:
               if message.reply_to_message and message.reply_to_message.forward_from:
                   original_user_id = message.reply_to_message.forward_from.id
                   await bot.send_message(
                       original_user_id,
                       f"Ответ от горячей линии Тринити Харрогейт: {message.text}"
                   )
                   await message.reply("Ответ отправлен партнеру.")

       async def webhook_handler(request):
           update = types.Update(**(await request.json()))
           await dp.feed_update(bot, update)
           return web.Response()

       async def set_webhook():
           webhook_url = f"https://YOUR_KOYEB_APP.koyeb.app/webhook"  # Замените на ваш URL после развертывания
           await bot.set_webhook(webhook_url)
           logging.info(f"Webhook установлен: {webhook_url}")

       async def on_startup():
           await set_webhook()

       async def on_shutdown():
           await bot.delete_webhook()
           logging.info("Webhook удален")

       async def main():
           app = web.Application()
           app.router.add_post('/webhook', webhook_handler)
           runner = web.AppRunner(app)
           await runner.setup()
           site = web.TCPSite(runner, '0.0.0.0', 8000)  # Порт 8000 для Koyeb
           await site.start()
           await on_startup()
           try:
               await asyncio.Event().wait()
           finally:
               await on_shutdown()
               await runner.cleanup()

       if __name__ == "__main__":
           asyncio.run(main())
