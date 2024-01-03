import os
import requests
from dotenv import load_dotenv

load_dotenv()

commands = {
  "name": os.environ['COMMAND_NAME'], # コマンド
  "type": os.environ['COMMAND_INPUT'], # CHAT_INPUT
  "description": os.environ['COMMAND_DESCRIPTION'] # コマンドの説明
}

url=f"https://discord.com/api/v8/applications/{os.environ['APPLICATION_ID']}/commands"
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bot {os.environ['TOKEN']}"
}

if os.environ['EXECUTION']:
  response = requests.post(
    url=url,
    headers=headers,
    json=commands
  )
  print(f"status: {response.status_code}")
else:
  print("現在登録できません")