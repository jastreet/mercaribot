build:
	docker build -t mercari-discord-bot:latest .

save:
	docker save mercari-discord-bot:latest > mercari-discord-bot.tar

run:
	docker run -it --rm --env-file .env mercari-discord-bot:latest

push:
	scp -r mercari-discord-bot.tar .env root@45.56.69.241:/root/

load:
	docker load < mercari-discord-bot.tar

build-save: build save

build-run: build run
