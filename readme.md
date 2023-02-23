Hey. This is my first REST project.
___
### **FastAPI + PostgreSQL + Aiogram + Docker**
___
This is a reminder bot.

If you forget to take your pills - this bot will help you.

You only need to register, add the pills you need, and set the reminder time.

At the specified time, the bot will remind you.


Starting the app:
1) clone repo
2) edit "docker-compose.yaml" -> service - tg_bot - environment - TG_TOKEN -> use your telegram bot token
3) use command: "docker-compose up -d --build"
4) use command: "docker-compose exec web alembic upgrade head"


