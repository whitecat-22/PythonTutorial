import tweepy
import datetime


def oath():
    """
    # 各種ツイッターのキーをセット
    """
    consumer_key = "****************************************"
    consumer_secret = "**************************************"
    access_key = "******************************************"
    access_secret = "******************************************"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)  # API利用制限にかかった場合、解除まで待機する
    return api


def search_key(screenname, item, count, api):
    """
    user_timeline
    ユーザー名（screenname)でツイートをサーチ
    itemにて検索個数
    いいね＋リツイートがcount以上の条件でサーチ
    """
    # ツイート取得
    tweet_data = []
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=screenname, exclude_replies=True, tweet_mode='extended',
                               lang='ja').items(item):
        if tweet.favorite_count + tweet.retweet_count >= count and 'RT @' not in tweet.full_text:
            tweet_data.append([tweet.user.name, tweet.favorite_count, tweet.retweet_count, tweet.created_at,
                               tweet.full_text.replace('\n', '')])
    for i in range(len(tweet_data)):
        print(str(i) + '番目' + str(tweet_data[i]))
    print('終了')


def main():
    """
    実行部分
    """
    API = oath()
    search_key('test', 100, 20, API)


if __name__ == '__main__':
    main()
