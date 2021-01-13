# 必要なライブラリのimport ※selenium,time,os,datetime,pandas
from selenium import webdriver
import time
import os
import datetime
import pandas as pd

def main():
    '''
    メインの実行部分
    '''
    # 何年前からのデータを取得するのかを入力
    year = 2015
    # 今年の西暦を取得
    this_year = datetime.date.today().year

    # 銘柄コードの入力
    stock_code = 6758
    # Seleniumでダウンロードするデフォルトディレクトリ
    download_directory = r"/Users/io/Desktop/prophet/stockdata"
    # CSVのダウンロードの実行
    download(stock_code, year, this_year, download_directory)
    # ダンロードしたデータフレームの結合
    df = concat_df(stock_code, year, this_year, download_directory)
    # 結合したデータフレームをCSVファイルで出力
    df.to_csv(f"{download_directory}/{stock_code}_{year}_{this_year}.csv")
    # 完成したデータフレームの出力
    print(df)

def download(stock_code, year, this_year, download_directory):
    '''
    特定の銘柄のCSVデータを各年ごとにダウンロード（デフォルトディレクトリの指定）
    '''
    options = webdriver.ChromeOptions()  # クロームオプションの設定
    prefs = {"download.default_directory" : download_directory}  # デフォルトのダウンロードディレクトリの指定
    options.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(options=options)  # オプションを指定してクロームドライバーの起動
    driver.implicitly_wait(30)  # 要素が見つからなかった時の待ち時間を指定
    
    # 各年のCSVデータのダウンロードをfor文で繰り返す
    for y in range(year, this_year + 1):
        driver.get(f"https://kabuoji3.com/stock/{stock_code}/")
        # ファイルがすでに存在している場合はcontinueで次のyへ行く
        if os.path.isfile(f"{download_directory}/{stock_code}_{y}.csv"):
            # 3秒待機
            time.sleep(3)
            continue
        # seleniumでy年のテキストをクリック
        driver.find_element_by_link_text(str(y)).click()
        # 3秒待機
        time.sleep(3)
        # クリックでCSVのダウンロード
        driver.find_element_by_name("csv").click()
        driver.find_element_by_name("csv").click()
        # 3秒待機
        time.sleep(3)
    # ブラウザを閉じて終了する
    driver.quit()
    
def concat_df(stock_code, year, this_year, download_directory):
    '''
    ダウンロードしたCSVをデータフレームとして結合
    '''
    # 結合するデータフレームを入れる空のリストを用意
    concat_list = []
    
    # データフレームの結合
    for y in range(year, this_year + 1):
        # データフレームの読み込み
        df = pd.read_csv(f"{download_directory}/{stock_code}_{y}.csv", encoding="cp932")
        # 日付行の削除
        df.drop(index='日付', inplace=True)
        # pd.concatで結合するためにリストにデータフレームを入れていく
        concat_list.append(df)
    # pd.concatでデータフレームの結合
    df = pd.concat(concat_list)
    return df

if __name__ == "__main__":
    main()