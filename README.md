# Discord Mercari Bot

This is a Discord bot that monitors Mercari for new listings based on specified search terms and sends notifications to a designated Discord channel.

## Features

- Activate a Discord channel to receive notifications
- Add and remove search terms
- List current search terms
- Automatically check for new listings every 30 seconds

## Prerequisites
1. You will need [python](https://www.python.org/downloads/)
2. An application on the [Discord Developers Page](https://discord.com/developers/applications)
3. An editor, I use VSCode
4. Access to a cloud service or VPS (current one in Makefile)

## Setup

1. Clone the repository:
    ```sh
    git clone https://github.com/jastreet/mercaribot.git
    cd mercaribot
    ```

2. Create a [.env](https://www.geeksforgeeks.org/how-to-create-and-use-env-files-in-python/) file with your Discord bot token from [Discord Developers Page](https://discord.com/developers/applications)

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the bot:
    ```sh
    python bot.py
    ```

## Docker

You can also run the bot using Docker:

1. Build the Docker image:
    ```sh
    docker build -t mercari-discord-bot:latest .
    ```

2. Run the Docker container:
    ```sh
    docker run -it --rm --env-file .env mercari-discord-bot:latest
    ```

## Makefile

The Makefile provides several useful commands for building, saving, running, and deploying the Docker container. (Requires Linux)

- `make build`: Build the Docker image.
- `make save`: Save the Docker image to a tar file.
- `make run`: Run the Docker container.
- `make push`: Push the Docker image and .env file to a remote server.
- `make load`: Load the Docker image from a tar file.
- `make build-save`: Build the Docker image and save it to a tar file.
- `make build-run`: Build the Docker image and run the container.


## Commands

- `~activate-channel`: Activate the current channel to receive notifications.
- `~add-search-term <term>`: Add a new search term.
- `~remove-search-term <term>`: Remove an existing search term.
- `~list-search-terms`: List all current search terms.
