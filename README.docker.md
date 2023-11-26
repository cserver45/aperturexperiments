# Aperture Experiments
A General Purpose Discord Bot

## Install Instructions
- Download the container
``` docker run -d -v /path/to/your/config/:/app/config cserver45/aperturexperiments:latest ```

It will error out, that is because you need to add your own config

## Configure
- Open `bot.example.conf` whereever the config directory is `nano /path/to/your/config/bot.example.conf`
- add your token under `token`
- add your full mongodb url (with password and username) under `passwd`
- add your discord user id under `owner_ids`
- everything else is optional

- rename the file from `bot.example.conf` to `bot.conf`
- Now run the command again, and you should see the bot come alive


(I don't have a docker-compose `.yml` made yet, stay tuned)