import json
import requests 
import csv 
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os, sys, stat 
import os.path
import termcolor
import re

key = get_random_bytes(32) 
key_slack_scan_file = 'key.key'

if os.path.isfile(key_slack_scan_file):
    os.remove(key_slack_scan_file)
my_protected_key = open(key_slack_scan_file, "wb")
my_protected_key.write(key)
my_protected_key.close()
os.chmod(key_slack_scan_file, stat.S_IRWXU) 

my_slack_token = os.environ.get("my_slack_token")


with open('keywords.txt') as wordlist, open('temp.csv', 'w', newline='') as excel:
    fieldnames = ['Shared Channel?','Channel name', 'Private channel?', 'Message author', 'Message', 'Date', 'Channel members']
    writer = csv.DictWriter(excel, fieldnames=fieldnames)
    writer.writeheader()
    for i in wordlist:
        url_msg = 'https://slack.com/api/search.messages?token=' + my_slack_token + '&query=' + i + '&pretty=1'
        r_msg = requests.get(url_msg).json()
        try:
            for b in r_msg["messages"]["matches"]:
                message = b["text"]
                ts = int(float(b["ts"]))
                tshumano = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                shared = b["channel"]["is_org_shared"]
                channelname = b["channel"]["name"]
                channelid = b["channel"]["id"]
                private = b["channel"]["is_private"]
                userid = b["user"]
                url_users = 'https://slack.com/api/users.profile.get?token=' + my_slack_token + '&user=' + userid + '&pretty=1'
                r_users = requests.get(url_users).json()
                usermail = r_users["profile"]["email"]
                print(15*"=")
                print("Channel:",termcolor.colored(channelname, "magenta"))
                print("Private:",termcolor.colored(private, "magenta"))
                print("Message:",termcolor.colored(message, "red"))
                print("Message author:",termcolor.colored(usermail, "cyan"),termcolor.colored("at " + tshumano + " UTC", "cyan"))
                url_members = 'https://slack.com/api/conversations.members?token=' + my_slack_token + '&channel=' + channelid + '&pretty=1'
                r_members = requests.get(url_members).json()
                memberid = r_members["members"]
                print("Channel members:")
                for individuals in memberid:

                    url_membermail = 'https://slack.com/api/users.profile.get?token=' + my_slack_token + '&user=' + individuals + '&pretty=1'
                    r_membermail = requests.get(url_membermail).json()
                    membermail = r_membermail["profile"]["email"]
                    print(termcolor.colored(membermail, "yellow"))
                    writer.writerow({'Shared Channel?': shared, 'Channel name': channelname, 'Private channel?': private, 'Channel members': membermail })
                writer.writerow({'Shared Channel?': shared, 'Channel name': channelname, 'Private channel?': private, 'Message author': usermail, 'Message': message, 'Date': tshumano, 'Channel members': membermail })
        except:
                print("keyword not found in others channels.")

buffer_size = 65536 
input_file = open('temp.csv', 'rb')
output_file = open('results.csv', 'wb')
cipher_encrypt = AES.new(key, AES.MODE_CFB)
output_file.write(cipher_encrypt.iv)
buffer = input_file.read(buffer_size)
while len(buffer) > 0:
    ciphered_bytes = cipher_encrypt.encrypt(buffer)
    output_file.write(ciphered_bytes)
    buffer = input_file.read(buffer_size)
input_file.close()
output_file.close()
os.remove('temp.csv')
os.chmod('results.csv', stat.S_IRWXU) 


