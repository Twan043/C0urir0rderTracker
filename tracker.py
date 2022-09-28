from cgitb import reset
import csv
import time
from tkinter import E
from pyparsing import line
import requests
import json
from discord_webhook import DiscordWebhook, DiscordEmbed, webhook

headers = {
    'authority': 'api.shipup.co',
    'accept': 'application/vnd.api+json',
    'accept-language': 'nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': 'Bearer psjuWukt7xZALCREwhUgYg',
    'content-type': 'application/vnd.api+json',
    'origin': 'https://www.courir.com',
    'referer': 'https://www.courir.com/',
    'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
}

with open('config.json') as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()
delay = int(jsonObject['delay'])
hook = jsonObject['webhook']

with open('courir.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            line_count += 1
            time.sleep(1)
        else:
            while True:
                try:
                    line_count += 1
                    email = row[0]
                    zip = row[1]
                except Exception as e:
                    print(e)
                else:
                    break
            while True:
                try:
                    print(zip)
                    link = f'https://api.shipup.co/v1/orders/tracking_page_order?address_zip={zip}&email={email}'
                    s = requests.Session()
                    response = s.get(link, headers=headers)
                except Exception as e:
                    print(e)
                if response.status_code == 200:
                    break
            while True:
                try:
                    status = json.loads(response.text)['included'][0]['attributes']['statusCode']
                    item = json.loads(response.text)['included'][1]['attributes']['title']
                    sku = json.loads(response.text)['included'][1]['attributes']['sku']
                    pic = json.loads(response.text)['included'][1]['attributes']['thumbnail']['src']
                    if status == 'shipped':
                        trackinglink = json.loads(response.text)['included'][2]['attributes']['trackingLink']
                    else:
                        break
                except Exception as e:
                    print(e)
                else:
                    break
            while True:
                try:
                    web_hook = DiscordWebhook(url=f'{hook}', username='Courir Order Tracker')
                    embed = DiscordEmbed(title=f'Succesfully tracked courir order', url=f'https://www.courir.com/en/track-my-orders', color=65280)
                    embed.add_embed_field(name='Status', value=f'{status}', inliEne=False)
                    embed.add_embed_field(name='item', value=f'{item}', inline=False)
                    embed.add_embed_field(name='sku', value=f'{sku}', inline=False)
                    if status == 'shipped':
                        embed.add_embed_field(name='TrackingLink', value=f'{trackinglink}', inline=False)
                    else:
                        break
                    embed.set_footer(text=f'Courir Order Tracker')
                    web_hook.add_embed(embed)
                    web_hook.execute()
                except Exception as e:
                    print(e)
                else:
                    print('Succesfully tracked order')
                    time.sleep(delay)
                    break
