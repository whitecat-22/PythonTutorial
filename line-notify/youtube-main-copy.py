# 必要なモジュールをimport
import requests
import pandas as pd
from apiclient.discovery import build
import datetime as dt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import math


def main():
    # 2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # 認証情報設定
    # ダウンロードしたjsonファイル名をクレデンシャル変数に設定
    credentials = ServiceAccountCredentials.from_json_keyfile_name("*********************************.json", scope)
    # OAuth2の資格情報を使用してGoogle APIにログインします。
    gc = gspread.authorize(credentials)
    # 共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
    SPREADSHEET_KEY = '********************************************'

    # 共有設定したスプレッドシートの検索キーワードシートを開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('検索キーワード')
    keyword_list = worksheet.col_values(1)
    # Youtube APIキーの記入
    api_key = '***************************************'
    # 今から24時間前の時刻をfromtimeとする（今の時刻のタイムゾーンはYoutubeに合わせて協定世界時刻のutcにする)
    fromtime = (dt.datetime.utcnow()-dt.timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ')
    videourl = 'https://www.youtube.com/watch?v='
    # データを入れる空のリストを作成
    data = []
    # キーワードリストを元に検索
    for keyword in keyword_list:
        nextpagetoken = ''
        youtube = build('youtube', 'v3', developerKey=api_key)
        # while文でnextPageTokenがあるまで動画データを取得
        while True:
            # youtube.search().listで動画情報を取得。結果は辞書型
            result = youtube.search().list(
                # 必須パラメーターのpart
                part='snippet',
                # 検索したい文字列を指定
                q=keyword,
                # 1回の試行における最大の取得数
                maxResults=50,
                #視聴回数が多い順に取得
                order='viewCount',
                #いつから情報を検索するか？
                publishedAfter=fromtime,
                #動画タイプ
                type='video',
                #地域コード
                regionCode='JP',
                #ページ送りのトークンの設定
                pageToken=nextpagetoken
            ).execute()

            # もしも動画数が50件以下ならば、dataに情報を追加してbreak
            if len(result['items']) <= 50:
                for i in result['items']:
                    data.append([i['id']['videoId'], i['snippet']['publishedAt'], i['snippet']['title'], keyword])
                break
            # もしも動画数が50件より多い場合はページ送りのトークン(result['nextPageToken']を変数nextpagetokenに設定する
            else:
                for i in result['items']:
                    data.append([i['id']['videoId'], i['snippet']['publishedAt'], i['snippet']['title'], keyword])
                nextpagetoken = result['nextPageToken']

            # data = [[videoId, 投稿日, 動画タイトル, 検索キーワード], [videoId, 投稿日, 動画タイトル, 検索キーワード], ...]
            # datalength = len(data)

    # videoidリストを作成
    videoid_list = []
    for i in data:
        videoid_list.append(i[0])
    # videoidリストの中の重複を取り除く
    videoid_list = sorted(set(videoid_list), key=videoid_list.index)
    # 50のセットの数(次のデータ取得で最大50ずつしかデータが取れないため、50のセットの数を数えている)
    # math.ceilは小数点以下は繰り上げの割り算　例　math.ceil(3.4) = 4
    data_length = len(data)
    _set_50 = math.ceil(data_length/50)

    _id_list = []
    for i in range(_set_50):
        _id_list.append(','.join(videoid_list[i*50:(i*50+50)]))
    # 再生回数データを取得して、再生回数リストを作成
    viewcount_list = []
    for videoid in _id_list:
        viewcount = youtube.videos().list(
            part='statistics',
            maxResults=50,
            id=videoid
        ).execute()
        for i in viewcount['items']:
            viewcount_list.append([i['id'], i['statistics']['viewCount']])
    # 動画情報を入れたデータフレームdf_dataの作成
    df_data = pd.DataFrame(data, columns=['videoid', 'publishtime', 'title', 'keyword'])
    # 重複の削除 subsetで重複を判定する列を指定,inplace=Trueでデータフレームを新しくするかを指定,
    df_data.drop_duplicates(subset='videoid', inplace=True)
    # 動画のURL
    df_data['url'] = videourl + df_data['videoid']
    # 調査した日
    df_data['search_day'] = dt.date.today().strftime('%Y/%m/%d')
    # 再生回数データを入れたデータフレームdf_viewcountの作成
    df_viewcount = pd.DataFrame(viewcount_list, columns=['videoid', 'viewcount'])
    # 2つのデータフレームのマージ
    df_data = pd.merge(df_viewcount, df_data, on='videoid', how='left')
    # viewcountの列のデータを条件検索のためにint型にする(元データも変更)
    df_data['viewcount'] = df_data['viewcount'].astype(int)
    # データフレームのviewcountに記載されている、再生回数が条件を満たす行だけを抽出
    df_data = df_data.query('viewcount>=100000')
    # viewcountの列のデータをint型から文字列型に戻している
    df_data['viewcount'] = df_data['viewcount'].astype(str)
    df_data = df_data[['search_day', 'keyword', 'title', 'url', 'viewcount']]


    # postリクエストをline notify APIに送るためにrequestsのimport
    # token.txtからトークンの読み込み
    with open('token.txt', 'r') as f:
        token = f.read().strip()
    print(token)

    # lineに通知したいメッセージを入力
    youtube_list = []
    for i in range(df_data.shape[0]):
        youtube_list.append('\n'.join(df_data.iloc[i]))

    notification_message = '\n\n'.join(youtube_list)


    # line notify APIのトークンの読み込み
    line_notify_token = token
    # line notify APIのエンドポイントの設定
    line_notify_api = 'https://notify-api.line.me/api/notify'
    # ヘッダーの指定
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    # 送信するデータの指定
    data = {'message': f'{notification_message}'}
    # line notify apiにpostリクエストを送る
    requests.post(line_notify_api, headers=headers, data=data)


    #共有設定したスプレッドシートの検索結果シートを開く
    worksheet = gc.open_by_key(SPREADSHEET_KEY).worksheet('検索結果')
    # ワークシートに要素が書き込まれているかを確認
    last_row = len(worksheet.get_all_values())
    # 見出し行（1行目)がない場合
    if last_row == 0:
        cell_columns = worksheet.range('A1:E1')
        cell_columns[0].value = '検索日'
        cell_columns[1].value = '検索キーワード'
        cell_columns[2].value = '検索Title'
        cell_columns[3].value = 'URL'
        cell_columns[4].value = '再生回数（検索時）'
        worksheet.update_cells(cell_columns)
        last_row += 1

    # もしdf_dataにデータが入っていない場合は書き込みをpass（Youtube APIで情報が取得されなかった場合)
    length = df_data.shape[0]  # df_dataの行数
    if length == 0:
        pass
    # df_dataにデータが入っている場合（Youtube APIで情報が見つかった場合)
    else:
        cell_list = worksheet.range(f'A{last_row+1}:E{last_row+length}')
        for cell in cell_list:
            cell.value = df_data.iloc[cell.row-last_row-1][cell.col-1]
        # スプレッドシートに書き出す
        worksheet.update_cells(cell_list)

if __name__ == '__main__':
    main()
