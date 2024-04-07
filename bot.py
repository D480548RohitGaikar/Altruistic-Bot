from config import *
from telegram import Bot,Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters
from datetime import datetime
import os
import requests

# Telegram bot token
BOT_TOKEN = BOT_API

# Giphy API key
GIPHY_API_KEY = GIPHY_API

# Giphy project ID
PROJECT_ID = PROJECT_API

# Function to fetch total views from Giphy
def get_total_views():
    url = f"https://api.giphy.com/v1/projects/{PROJECT_ID}?api_key={GIPHY_API_KEY}"
    response = requests.get(url)
    data = response.json()
    total_views = data.get("data", {}).get("analytics", {}).get("total_views", 0)
    return total_views

# Command handler for /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the Giphy Views Tracker Bot! Send me the project name or ID to get started.')

# Command handler for receiving project name or ID
def track_project(update: Update, context: CallbackContext) -> None:
    project_id = update.message.text
    # Save the project ID in database or storage for daily tracking
    context.user_data["project_id"] = project_id
    update.message.reply_text(f'Project {project_id} is now being tracked.')

# Function to send daily updates
def send_daily_update(context: CallbackContext) -> None:
    project_id = context.user_data.get("project_id")
    if project_id:
        total_views = get_total_views()
        context.bot.send_message(context.job.context, f"Daily update: Project {project_id} has {total_views} views.")

def main() -> None:
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, track_project))

    # Job queue for daily updates
    job_queue = updater.job_queue
    job_queue.run_daily(send_daily_update, datetime.time(hour=12), context=updater.bot.username)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

