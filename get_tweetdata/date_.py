import datetime

# 今日の日時
today = datetime.datetime.today()
print(today)

# 日付の作成
date = datetime.datetime(2020,7,1)
print(date)

# datetimeオブジェクトを文字列に変換　.strftimeを使う
print(today.strftime('%Y-%m-%d-%H:%M:%S'))


