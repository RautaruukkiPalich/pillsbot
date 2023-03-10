import os
from dotenv import load_dotenv

load_dotenv()

HOST_ADD = os.environ.get("HOST_ADD", "web")
HOST_PORT = os.environ.get("HOST_PORT", 8000)
HOST_URL = f"http://{HOST_ADD}:{HOST_PORT}"
TOKEN = os.environ.get("TG_TOKEN")

CANCEL = "\n\nДля отмены заполнения этого поля можно нажать /cancel"

TIME_4ZONE = {
    1: "0:00 - 5:30",
    2: "6:00 - 11:30",
    3: "12:00 - 17:30",
    4: "18:00 - 23:30",
}
TIME_SELECT = {
    1: {
        1: "0:00", 2: "0:30", 3: "1:00", 4: "1:30", 5: "2:00", 6: "2:30",
        7: "3:00", 8: "3:30", 9: "4:00", 10: "4:30", 11: "5:00", 12: "5:30",
    },
    2: {
        1: "6:00", 2: "6:30", 3: "7:00", 4: "7:30", 5: "8:00", 6: "8:30",
        7: "9:00", 8: "9:30", 9: "10:00", 10: "10:30", 11: "11:00", 12: "11:30",
    },
    3: {
        1: "12:00", 2: "12:30", 3: "13:00", 4: "13:30", 5: "14:00", 6: "14:30",
        7: "15:00", 8: "15:30", 9: "16:00", 10: "16:30", 11: "17:00", 12: "17:30",
    },
    4: {
        1: "18:00", 2: "18:30", 3: "19:00", 4: "19:30", 5: "20:00", 6: "20:30",
        7: "21:00", 8: "21:30", 9: "22:00", 10: "22:30", 11: "23:00", 12: "23:30",
    },
}
TIMEZONE = {
    1: "-1 МСК (Калининград)",
    2: "0 МСК (Москва)",
    3: "+1 МСК (Самара)",
    4: "+2 МСК (Екатеринбург)",
    5: "+3 МСК (Омск)",
    6: "+4 МСК (Новосибирск)",
    7: "+5 МСК (Иркутск)",
    8: "+6 МСК (Якутск)",
    9: "+7 МСК (Владивосток)",
    10: "+8 МСК (Магадан)",
    11: "+9 МСК (Камчатка)",
}
