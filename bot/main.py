"""
Telegram Bot для Mini App
"""

import asyncio
import logging
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from app.core.config import settings
from app.services.telegram import TelegramService

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация сервисов
telegram_service = TelegramService()


class TelegramBot:
    """Telegram бот для Mini App"""
    
    def __init__(self):
        self.application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("models", self.models_command))
        self.application.add_handler(CommandHandler("my_tickets", self.my_tickets_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        
        # Создаем клавиатуру с WebApp
        keyboard = [
            [KeyboardButton("📱 Открыть приложение", web_app=WebAppInfo(url=settings.TELEGRAM_WEBAPP_URL))],
            [KeyboardButton("📋 Каталог моделей"), KeyboardButton("🎫 Мои тикеты")],
            [KeyboardButton("ℹ️ Помощь")]
        ]
        
        if user.id in settings.admin_user_ids_list:
            keyboard.append([KeyboardButton("⚙️ Админ-панель")])
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        welcome_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "Добро пожаловать в каталог моделей и службу поддержки.\n\n"
            "Здесь вы можете:\n"
            "• 📋 Просматривать каталог моделей\n"
            "• 📄 Скачивать инструкции и файлы\n"
            "• 🎫 Создавать тикеты поддержки\n"
            "• 📱 Использовать удобное веб-приложение\n\n"
            "Нажмите кнопку ниже, чтобы открыть приложение:"
        )
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def models_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /models"""
        # Создаем inline клавиатуру для открытия каталога
        keyboard = [
            [InlineKeyboardButton(
                "📋 Открыть каталог моделей",
                web_app=WebAppInfo(url=f"{settings.TELEGRAM_WEBAPP_URL}/models")
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 <b>Каталог моделей</b>\n\n"
            "Здесь вы можете найти нужную модель и скачать инструкции.\n\n"
            "Нажмите кнопку ниже, чтобы открыть каталог:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def my_tickets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /my_tickets"""
        # Создаем inline клавиатуру для открытия тикетов
        keyboard = [
            [InlineKeyboardButton(
                "🎫 Мои тикеты",
                web_app=WebAppInfo(url=f"{settings.TELEGRAM_WEBAPP_URL}/tickets")
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎫 <b>Мои тикеты</b>\n\n"
            "Здесь вы можете просматривать свои тикеты поддержки и создавать новые.\n\n"
            "Нажмите кнопку ниже, чтобы открыть тикеты:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /admin"""
        user = update.effective_user
        
        if user.id not in settings.admin_user_ids_list:
            await update.message.reply_text(
                "❌ У вас нет прав доступа к админ-панели.",
                parse_mode=ParseMode.HTML
            )
            return
        
        # Создаем inline клавиатуру для открытия админ-панели
        keyboard = [
            [InlineKeyboardButton(
                "⚙️ Админ-панель",
                web_app=WebAppInfo(url=f"{settings.TELEGRAM_WEBAPP_URL}/admin")
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ <b>Админ-панель</b>\n\n"
            "Здесь вы можете управлять моделями, файлами и тикетами.\n\n"
            "Нажмите кнопку ниже, чтобы открыть админ-панель:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /help"""
        help_text = (
            "ℹ️ <b>Помощь</b>\n\n"
            "<b>Доступные команды:</b>\n"
            "/start - Главное меню\n"
            "/models - Каталог моделей\n"
            "/my_tickets - Мои тикеты\n"
            "/help - Эта справка\n\n"
            "<b>Функции приложения:</b>\n"
            "• 📋 Просмотр каталога моделей с поиском и фильтрами\n"
            "• 📄 Скачивание инструкций и файлов\n"
            "• 🎫 Создание и отслеживание тикетов поддержки\n"
            "• 📱 Удобный веб-интерфейс\n\n"
            "<b>Поддержка:</b>\n"
            "Если у вас есть вопросы, создайте тикет через приложение."
        )
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text
        
        if text == "📱 Открыть приложение":
            keyboard = [
                [InlineKeyboardButton(
                    "🚀 Открыть приложение",
                    web_app=WebAppInfo(url=settings.TELEGRAM_WEBAPP_URL)
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "🚀 <b>Открыть приложение</b>\n\n"
                "Нажмите кнопку ниже, чтобы открыть веб-приложение:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            )
        
        elif text == "📋 Каталог моделей":
            await self.models_command(update, context)
        
        elif text == "🎫 Мои тикеты":
            await self.my_tickets_command(update, context)
        
        elif text == "⚙️ Админ-панель":
            await self.admin_command(update, context)
        
        elif text == "ℹ️ Помощь":
            await self.help_command(update, context)
        
        else:
            await update.message.reply_text(
                "Я не понимаю эту команду. Используйте /help для получения справки."
            )
    
    async def send_notification(self, user_id: int, message: str):
        """Отправка уведомления пользователю"""
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Failed to send notification to {user_id}: {e}")
    
    async def send_admin_notification(self, message: str):
        """Отправка уведомления всем админам"""
        for admin_id in settings.admin_user_ids_list:
            await self.send_notification(admin_id, message)
    
    def run(self):
        """Запуск бота"""
        logger.info("Starting Telegram bot...")
        self.application.run_polling()
    
    async def run_webhook(self, webhook_url: str):
        """Запуск бота с webhook"""
        logger.info(f"Starting Telegram bot with webhook: {webhook_url}")
        await self.application.bot.set_webhook(url=webhook_url)
        self.application.run_webhook(
            listen="0.0.0.0",
            port=8001,
            webhook_url=webhook_url
        )


# Глобальный экземпляр бота
bot = TelegramBot()


def main():
    """Главная функция для запуска бота"""
    if settings.TELEGRAM_WEBHOOK_URL:
        asyncio.run(bot.run_webhook(settings.TELEGRAM_WEBHOOK_URL))
    else:
        bot.run()


if __name__ == "__main__":
    main()
