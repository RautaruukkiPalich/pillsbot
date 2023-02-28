This is my first REST project.
___
### **FastAPI + PostgreSQL + Aiogram + Docker**
___
This is a reminder bot.

If you forget to take your pills - this bot will help you.

You only need to register, add the pills you need, and set the reminder time.

At the specified time, the bot will remind you.


Starting the app:
1) clone repo
   ```bash
   clone https://github.com/RautaruukkiPalich/pillsbot
   ```
3) create .env file in . with parameters
    ```bash
    DB_NAME= #enter database name
    DB_HOST= database
    DB_PORT= #enter database port
    DB_USER= #enter database user
    DB_PASS= #enter database password
   
    HOST_ADD= 0.0.0.0
    HOST_PORT= #enter host port
    ```
4) create .env file in ./bot with parameters
    ```bash
    TG_TOKEN= #enter TG token
    HOST_ADD= web
    HOST_PORT= #enter host port
    ```
5) use command to create and start containers
    ```bash
    docker-compose up -d --build
    ```
6) use command to create migration
    ```bash
    docker-compose exec web alembic upgrade head
    ```

You can stop and start containers with commands:
```commandline
docker-compose start

docker-compose stop
```

be careful with command
```commandline
docker-compose down
```
