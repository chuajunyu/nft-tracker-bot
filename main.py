import os
import time
from collections import defaultdict
from datetime import datetime

import requests
import discord
from dotenv import load_dotenv  # For loading env variables

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

URL = "https://api.etherscan.io/api"  # URL to do api calls to get nft information
CHECK_DELAY = 30  # Interval between api calls, in seconds


def get_log(nft_address, from_block, to_block='latest'):
    """Runs a GET request to return transaction logs of an nft address"""
    
    query = {
        "module": "logs",
        "action": "getLogs",
        "fromBlock": from_block,
        "toBlock": to_block,
        "address": nft_address,
        "apikey": ETHERSCAN_API_KEY
    }

    response = requests.request("GET", URL, params=query)
    data = response.json()
    
    # TODO: Add error checking (request error)
    # TODO: Add logging

    return data["result"]


def get_latest_block():
    """Returns block number of the latest block mined"""

    query = {
        "module": "proxy",
        "action": "eth_BlockNumber",
        "apikey": ETHERSCAN_API_KEY
    }
    response = requests.request("GET", URL, params=query)
    data = response.json()

    # TODO: Add error checking (request error)
    # TODO: Add logging

    block_num = int(data["result"], 16)  # Convert from hexadecimal to decimal
    return block_num


def find_transactions(logs):
    """Takes in logs (return value of get_log) to find nft transactions

    Returns a list of nft transactions
    """

    confirmed_senders = defaultdict(dict)
    possible_receivers = defaultdict(dict)
    """Above dictionaries have the following format:
    E.G:
    confirmed_senders/possible_receivers = {
        token_id: {timestamp_1: address, timestamp_2:address},
        token_id: {timestamp_1: address}
    }
    This format allows for multiple transactions of the same token to be differentiated by their timestamp"""

    for log in logs:
        topics = log["topics"]

        if not len(topics) == 4:  # Filter 1: Transactions all have 4 topics in their logs
            continue
        
        timestamp = int(log["timeStamp"], 16) 
        sender, receiver, token_id = topics[1:]  
        token_id = int(token_id, 16)

        if int(receiver, 16) == 0:  # Filter 2: 0x000...000 is associated with token minting and transfers
            # This is a transaction with sender address!
            confirmed_senders[token_id][timestamp] = sender
        else:
            # This could contain receiver address information
            possible_receivers[token_id][timestamp] = receiver

    confirmed_transactions = []
    for token in confirmed_senders:
        for timestamp in confirmed_senders[token]:
            sender = confirmed_senders[token][timestamp]
            receiver = possible_receivers[token][timestamp]

            # TODO: Add checks in case there is assymetry in the timestamps between dictionaries

            sender = "0x" + sender[-40:]  # Take out extra 0s
            receiver = "0x" + receiver[-40:]
            transaction = [token, sender, receiver, timestamp]
            confirmed_transactions.append(transaction)

    return confirmed_transactions


client = discord.Client()


@client.event
async def on_ready():
    print("we have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    global running  # Each condition seems to be running in a different frame, hence running variable has to be globalised to work
    if message.author == client.user:
        return

    if message.content == '/About':
        await message.channel.send('Hi, this bot will send live transaction receipts of Blockchain miners club nft that was transacted')

    if message.content == '/Start':
        running = True
        last_checked = get_latest_block()
        print("Initialised: ", last_checked)
        await message.channel.send("Bot Started")
        
        while running:
            latest = get_latest_block()
            logs = get_log(nft, last_checked, latest)
            
            if logs:
                transactions = find_transactions(logs)

                for trans in transactions:
                    token_id, sender, receiver, timestamp = trans
                    timestamp = datetime.utcfromtimestamp(timestamp).strftime(r'%Y-%m-%d %H:%M:%S')
                    alert_message = """
                    ----TRANSACTION DETECTED----
                    @ {} UTC
                    NFT Collection Contract Address: {}
                    Token ID: {}
                    Sender Address: {}
                    Receiver Address: {}\n
                    """.format(timestamp, nft, token_id, sender, receiver)
                    print(alert_message)
            else:
                pass # No transactions detected

            await message.channel.send(alert_message)
            print("Latest Block Checked: {}".format(latest))
            
            last_checked = latest
            time.sleep(CHECK_DELAY)
        print('Stopped')

    if message.content == '/Stop':
        running = False
        await message.channel.send('Bot Stopped')


if __name__ == "__main__":
    nft = "0x49cF6f5d44E70224e2E23fDcdd2C053F30aDA28B"
    client.run(DISCORD_TOKEN)
    