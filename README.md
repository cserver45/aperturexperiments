# Aperture Experiments Discord Bot

This is the github page for the Aperture Experiments discord bot.

## This project has been archived, and no new development/support will be given
## Last (tested) working build was using discord.py v2.3.2, and on debian 12.

#### Some of the features include:

- Economy system
- Moderation
- Fun commands
- And more!

If you would like to contribute, open a PR and we might consider adding your idea.

## Installation:

### Via Docker, see instructions there or in README.docker.md: (https://hub.docker.com/r/cserver45/aperturexperiments) 

### Manual install:
(these are instructions for setting up on a debian system)
- Download the bot: `git clone https://github.com/cserver45/aperturexperiments.git`
  - For people using MongoDB Atlas, skip the step below. 
- Install MongoDB: (instructions are here)[https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-debian/]

- Add a user to mongodb (name it anything, but remember its username and password) (tutorial on that)[https://www.mongodb.com/docs/manual/tutorial/create-users/]
- make a database (again, name it anything, but remember it), with the collection named `economy_data` (tutorial on that)[https://www.mongodb.com/docs/manual/core/databases-and-collections/]
- Rename the `bot.example.conf` file to `bot.conf`, and add in your discord bot token under `protoken`, your discord userid under `owner_ids`, and your full MongoDB authentication string under `passwd`
   - It lookes something like this: `mongodb+srv://<USERNAME_HERE>:<PASSWORD_HERE>@<SERVER_ENDPOINT>/` (server endpoint would be `127.0.0.1` if it is a local install)
