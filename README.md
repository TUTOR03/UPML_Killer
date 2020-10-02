# UPML_Killer
### This is a telegram bot for the killer game in [my school](https://ugrafmsh.ru/)
### You can test it here [UPML_killer](https://t.me/UPML_Killer_bot)
## Instalation
To set up the bot use `docker`. Firstly create a `virtualenv` and install all requirements.
```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
Then just configure `Dockerfile`, `docker-compose.yml`, `settings.py` as you need and run it with `docker-compose`.
```bash
docker-compose up -d --build
```
Also you need to configure the `url_shortener.conf` and put it into `etc/nginx/sites-enabled/`\
Do not forget to fill `bot token` in `/back/views.py`
