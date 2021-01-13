# 必要なモジュールのimport
import datetime
import pandas as pd
import tweepy

# 各種ツイッターのキーをセット　consumer_key, consumer_secret, access_key, access_secret
consumer_key = "*******************************"
consumer_secret = "*******************************"
access_key = "*******************************"
access_secret = "*******************************"

# 認証のためのAPIキーをセット
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)  # API利用制限にかかった場合、解除まで待機する


def main():
    '''
    メインの実行部分
    ツイートデータの取得からデータの出力まで
    '''

    # ツイートデータの取得 日付の指定は 2020-7-30のみでもOK,
    # 日本時間で取得したい場合は2020-7-30_00:00:00_JSTのように指定
    # JSTをつけないと時間がUTCになる UTCは協定世界時間-> JST＋9:00(日本時間よりも9時間進んでいる)
    data = get_search_tweet('Python', 100, 1, "2020-7-30_00:00:00_JST", "2020-7-31_00:00:00_JST")

    # ツイートデータを番号順に出力
    oup_put_tweets(data)

    # ツイートデータをDataframeにする
    df = make_df(data)
    # Dataframeの出力
    print(f"データフレーム{df}")
    # ツイートデータのCSVへの出力
    df.to_csv('tweet_data.csv')


# ツイートを収集する関数
def get_search_tweet(s, items_count, rlcount, since, until):
    '''
    ツイート情報を期間指定で収集
    取得できるのデータは1週間以内の分だけ
    リツイート数＋いいね数の合計でツイートを絞り込める
    '''

    searchkey = s + '-filter:retweets'  # 検索キーワードの設定、 リツイートは除く

    # ツイートデータ取得部分
    # tweepy.CursorのAPIのキーワードサーチを使用(api.search)
    # qがキーワード, sinceがいつから, untilがいつまで, tweet_modeでつぶやきの省略ありなし, langで言語, .itemes(数)と書いてツイート数を指定
    tweets = tweepy.Cursor(api.search, q=searchkey, exclude_replies = True, since=since, until=until, tweet_mode='extended', lang='ja').items(items_count)

    # ツイートのデータを取り出して、リストにまとめていく部分
    tweet_data = []  # ツイートデータを入れる空のリストを用意
    for tweet in tweets:
        if tweet.favorite_count + tweet.retweet_count >= rlcount:  # いいねとリツイートの合計がrlcuont以上の条件
            tweet_data.append([tweet.user.name, tweet.user.screen_name, tweet.retweet_count,  # 空のリストにユーザーネーム、スクリーンネーム、RT数、いいね数、日付などを入れる
                               tweet.favorite_count, tweet.created_at.strftime('%Y-%m-%d-%H:%M:%S_JST'), tweet.full_text.replace('\n', '')])
    return tweet_data

def oup_put_tweets(tweetdata):
    '''
    ツイートのリストを順番をつけて出力する関数の作成
    '''
    for i in range(len(tweetdata)):
        print(f"{i} 番目{tweetdata[i]}")

def make_df(data):
    '''
    ツイートデータからDataframeを作成する
    '''
    # データを入れる空のリストを用意(ユーザー名、ユーザーid、RT数、いいね数、日付け、ツイート本文)
    list_username = []
    list_userid = []
    list_rtcount = []
    list_favorite = []
    list_date = []
    list_text = []

    # ツイートデータからユーザー名、ユーザーid、RT数、いいね数、日付け、ツイート本文のそれぞれをデータごとにまとめたリストを作る
    for i in range(len(data)):
        list_username.append(data[i][0])
        list_userid.append(data[i][1])
        list_rtcount.append(data[i][2])
        list_favorite.append(data[i][3])
        list_date.append(data[i][4])
        list_text.append(data[i][5])

    # 先ほど作ったデータごとにまとめたリストからDataframeの作成
    df = pd.DataFrame({'ユーザー名': list_username,
                       'ユーザーid': list_userid,
                       'RT数': list_rtcount,
                       'いいね数': list_favorite,
                       '日時': list_date,
                       '本文': list_text})
    return df

# 実行部分
if __name__ == '__main__':
    main()

