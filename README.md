# NFT Tracker Bot

A Discord bot that will track an NFT collection and send a message whenever a transaction is detected

# How to Run

Tested on Python Version 3.8.4

1.  Install dependencies

    Create a venv, then install the necessary libraries

    `pip install -r requirements.txt`


2. Set Configurations

    Fill up `.env_sample`
    ``` 
    ETHERSCAN_API_KEY = "Input Etherscan API Key Here"

    DISCORD_TOKEN = "Input Discord Bot Token Here"
    ```
    Rename `.env_sample` to `.env`


    Set NFT Collection Address in line 166 of `main.py`:

    `nft = 'INSERT NFT COLLECTION ADDRESS'`


3. Run the script

    `python main.py`

4. Start the bot with commands in Discord

    Use `\Start` to start the bot

    Use `\Stop` to stop the bot