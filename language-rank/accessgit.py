# 必要なライブラリのimport
import json
import requests
import pandas as pd

def main():
    '''
    メインの実行部分
    '''
    
    # 言語リストからデータフレームの作成
    df = get_stars_repos()
    
    # 言語でグループ化して、スター数の多さで並べ替え
    grouped = df.groupby('language')
    print(grouped.sum().sort_values(by = 'stars', ascending=False))
    
    df = grouped.sum().sort_values(by = 'stars', ascending=False)

def get_api_repos(endpoint):
    '''
    エンドポイントにGETリクエストを送って得られたデータから
    言語ごとのスター数をまとめたデータフレームを作る
    '''

    # エンドポイントにGETリクエストを送ってデータを取得
    r = requests.get(endpoint)
    # ステータスコードが200じゃない（アクセスできない）場合の
    if r.status_code != 200:
        print(f'次のエンドポイントにアクセスできません。{endpoint}')
    # json文字列をjson.loads()でPythonで扱える辞書形式に変換する
    repos_dict = json.loads(r.content)
    
    # 辞書からアイテムを取り出す
    repos = repos_dict['items']
    
    # language(言語)とstargazers_count(スター数)のリストを作成する
    languages = []
    stars = []
    for repo in repos:
        languages.append(repo['language'])
        stars.append(repo['stargazers_count'])
    
    # languagesとstarsのリストからデータフレームの作成
    df = pd.DataFrame({'language': languages, 'stars': stars})
    return df

def get_access_token():
    '''
    アクセストークンをテキストファイルから取得する
    '''
    with open('token.txt', 'r', encoding='utf-8') as f:
        return f.read().strip()

def get_stars_repos():
    '''
    スター数が多いリポジトリの集計を取る
    '''
    # アクセストークンの取得
    token = get_access_token()
    
    # リポジトリーを検索するエンドポイントを指定する
    repo_stars_api = 'https://api.github.com/search/repositories?q=stars:>0&sort=stars&per_page=100&access_token={}'.format(token)
    
    # エンドポイントを引数にget_api_repos関数でスターが多いリポジトリ数のデータフレームを取得
    print("言語情報をリポジトリのスター数が多い順に取得します。...")
    repos_stars = get_api_repos(repo_stars_api)
    print("取得が完了しました!\n")
    
    return repos_stars

if __name__ == '__main__':
    main()