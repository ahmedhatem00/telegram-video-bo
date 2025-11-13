import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import yt_dlp
import requests

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# التوكن الخاص بك - سيتم تعيينه من متغير البيئة
BOT_TOKEN = os.getenv('BOT_TOKEN')

class VideoBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """إعداد معالجات الرسائل"""
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    def download_video(self, url):
        """تحميل الفيديو باستخدام yt-dlp"""
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'downloaded_video.%(ext)s',
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return 'downloaded_video.mp4'
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل الواردة"""
        try:
            message = update.message
            text = message.text
            
            # التحقق من وجود روابط
            if any(domain in text for domain in ['tiktok.com', 'instagram.com', 'youtube.com', 'youtu.be']):
                await message.reply_text("⏳ جاري تحميل الفيديو...")
                
                # تحميل الفيديو
                video_path = self.download_video(text)
                
                if video_path:
                    # إرسال الفيديو
                    with open(video_path, 'rb') as video_file:
                        await message.reply_video(
                            video=video_file,
                            caption="تم التحميل بنجاح ✅"
                        )
                    # حذف الملف المؤقت
                    os.remove(video_path)
                    
                    # حذف الرسالة الأصلية (إذا كان البوت مشرف)
                    try:
                        await message.delete()
                    except:
                        pass
                else:
                    await message.reply_text("❌ تعذر تحميل الفيديو")
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.reply_text("❌ حدث خطأ أثناء المعالجة")
    
    def run(self):
        """تشغيل البوت"""
        logger.info("🤖 البوت يعمل الآن...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = VideoBot()
    bot.run()