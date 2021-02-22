# postリクエストをline notify APIに送るためにrequestsのimport
import requests

# token.txtからトークンの読み込み
with open('token.txt', 'r') as f:
	token = f.read().strip()
print(token)

list = ['apple', 'orange', 'pineapple']
notification_message = '\n'+'\n'.join(list)

# lineに通知したいメッセージを入力
# notification_message = 'テスト'

# line notify APIのトークンの読み込み
line_notify_token = token
# line notify APIのエンドポイントの設定
line_notify_api = 'https://notify-api.line.me/api/notify'
# ヘッダーの指定
headers = {'Authorization': f'Bearer {line_notify_token}'}
# 送信するデータの指定
data = {'message': f'{notification_message}'}
# line notify apiにpostリクエストを送る
requests.post(line_notify_api, headers = headers, data = data)
