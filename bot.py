import os
import logging
import requests
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# تحميل المتغيرات من ملف البيئة
load_dotenv()

# إعدادات التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# المتغيرات الأساسية
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]

class VideoDownloaderBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        # handler للرسائل في القناة
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_channel_message
        ))
        
        # handler للأوامر
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "مرحباً! أنا بوت تحميل الفيديوهات 🎬\n"
            "فقط أرسل رابط فيديو من:\n"
            "• Instagram • TikTok • YouTube\n"
            "وسأقوم بتحميله وإرساله لك!"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "كيفية الاستخدام:\n"
            "1. أرسل رابط فيديو من أي منصة\n"
            "2. سأقوم بتحميله تلقائياً\n"
            "3. سأرسل لك الفيديو مع حذف الرابط الأصلي\n\n"
            "المنصات المدعومة: Instagram, TikTok, YouTube, Twitter, Facebook"
        )
    
    def extract_video_info(self, url):
        """استخراج معلومات الفيديو باستخدام yt-dlp"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best[ext=mp4]/best',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    'url': info['url'],
                    'title': info.get('title', 'video'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', '')
                }
        except Exception as e:
            logging.error(f"Error extracting video: {e}")
            return None
    
    async def handle_channel_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة الرسائل في القناة"""
        try:
            message = update.message
            text = message.text.strip()
            
            # التحقق إذا كان النص يحتوي على روابط
            if not any(domain in text for domain in [
                'instagram.com', 'tiktok.com', 'youtube.com', 
                'youtu.be', 'twitter.com', 'facebook.com'
            ]):
                return
            
            # إرسال رسالة انتظار
            wait_msg = await message.reply_text("⏳ جاري تحميل الفيديو...")
            
            # استخراج وتحميل الفيديو
            video_info = self.extract_video_info(text)
            
            if video_info:
                # إرسال الفيديو
                await message.reply_video(
                    video=video_info['url'],
                    caption=f"🎬 {video_info['title']}\n\nتم التحميل بواسطة @LinkVDownbot"
                )
                
                # حذف الرسالة الأصلية (الرابط)
                await message.delete()
                
                # حذف رسالة الانتظار
                await wait_msg.delete()
                
                logging.info(f"Video processed successfully: {video_info['title']}")
            else:
                await wait_msg.edit_text("❌ تعذر تحميل الفيديو. تأكد من صحة الرابط.")
                
        except Exception as e:
            logging.error(f"Error in handle_channel_message: {e}")
            try:
                await message.reply_text("❌ حدث خطأ أثناء معالجة الفيديو.")
            except:
                pass
    
    def run(self):
        """تشغيل البوت"""
        print("🤖 البوت يعمل الآن...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = VideoDownloaderBot()
    bot.run()