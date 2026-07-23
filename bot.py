import os
import sqlite3
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ==================================================
# AlphaGrow - Core Bot
# ==================================================

TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = "alphagrow.db"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==================================================
# Database
# ==================================================

def get_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            points INTEGER DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            premium INTEGER DEFAULT 0,
            referred_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()
    db.close()


def create_user(user):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users
        (user_id, first_name, username)
        VALUES (?, ?, ?)
        """,
        (
            user.id,
            user.first_name or "",
            user.username or "",
        ),
    )

    db.commit()
    db.close()


def get_user(user_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,),
    )

    user = cursor.fetchone()
    db.close()

    return user


# ==================================================
# Main Menu
# ==================================================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton(
                "👤 پروفایل من",
                callback_data="profile",
            ),
            InlineKeyboardButton(
                "🏆 رتبه‌بندی",
                callback_data="leaderboard",
            ),
        ],
        [
            InlineKeyboardButton(
                "⭐ امتیاز و مأموریت‌ها",
                callback_data="missions",
            ),
            InlineKeyboardButton(
                "👥 دعوت دوستان",
                callback_data="referral",
            ),
        ],
        [
            InlineKeyboardButton(
                "💎 Premium",
                callback_data="premium",
            ),
            InlineKeyboardButton(
                "🎉 جشنواره‌ها",
                callback_data="events",
            ),
        ],
        [
            InlineKeyboardButton(
                "📢 کانال AlphaGrow",
                callback_data="channel",
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# ==================================================
# Start
# ==================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user = update.effective_user

    create_user(user)

    await update.message.reply_text(
        f"سلام {user.first_name} 👋\n\n"
        "🚀 به AlphaGrow خوش اومدی!\n\n"
        "اینجا می‌تونی با فعالیت، انجام مأموریت‌ها "
        "و دعوت دوستان امتیاز جمع کنی و در آینده "
        "از پاداش‌ها و امکانات ویژه استفاده کنی. 🎁\n\n"
        "از منوی زیر شروع کن 👇",
        reply_markup=main_menu(),
    )


# ==================================================
# Button Handler
# ==================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user = get_user(user_id)

    if not user:
                await query.edit_message_text("کاربر پیدا نشد.")
        return
