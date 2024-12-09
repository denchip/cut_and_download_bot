from aiogram import Bot, Dispatcher, types, executor
from aiogram.utils.executor import start_webhook
import yt_dlp
import ffmpeg
import os
import uuid


TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
DOMAIN = os.environ.get('DOMAIN')
ENVIRONMENT = os.environ.get('ENVIRONMENT')

# webhook settings
WEBHOOK_HOST = f'https://{DOMAIN}'
WEBHOOK_PATH = '/webhook'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = 8001

# bot initialization
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


# webhook startup & shutdown
async def on_startup(dp):
    if ENVIRONMENT == 'production':
        await bot.set_webhook(WEBHOOK_URL)
        print(f'Telegram servers now send updates to {WEBHOOK_URL}. Bot is online')
    else:
        print('Bot is online. Started polling')


async def on_shutdown(dp):
    await bot.delete_webhook()


# emain function for cut and convert
async def cut(message: types.Message):
    try:
        url, start, duration = message.text.split(' ')
        await message.reply(f'Start to download')
        filename = uuid.uuid4()
        ydl_opts = {
            'format': 'best',
            'outtmpl': f'media/{filename}.mp4',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await message.reply(f'Download complete. Cutting')
        ffmpeg.input(f'media/{filename}.mp4', ss=start).output(f'media/{filename}_cutted.mp4', t=duration, c='copy').run()
        await message.reply(f'File is ready. Sending')
        await bot.send_video(message.chat.id, open(f'media/{filename}_cutted.mp4', 'rb'))

    except Exception as e:
        pass


if __name__ == '__main__':
    dp.register_message_handler(cut, content_types=['text'])
    if ENVIRONMENT == 'production':
        start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,)
    else:
        executor.start_polling(dp, skip_updates=True)
