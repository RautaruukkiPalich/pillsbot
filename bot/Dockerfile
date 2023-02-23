FROM python:3.10
# set work directory
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot
# copy project
COPY . /usr/src/bot
# install dependencies
RUN pip install --user aiogram requests aioschedule python-dotenv
# run app
CMD ["python", "bot.py"]