# ブラウザを自動操作するためseleniumをimport
from selenium import webdriver
# seleniumでEnterキーを送信する際に使用するのでimport
from selenium.webdriver.common.keys import Keys
# seleniumでヘッドレスモードを指定するためにimport
from selenium.webdriver.chrome.options import Options
# 待ち時間を指定するためにtimeをimport
import time
# 正規表現にマッチする文字列を探すためにreをimport
import re

# Googleのトップページ
URL = 'https://www.google.co.jp'

# Googleのトップページに遷移したらタイトルに'Google'が含まれているか確認するために指定

def main():
    '''
    メインの処理
    Googleの検索エンジンでキーワードを検索
    指定されたドメインが検索結果の１ページ目に含まれていないキーワードをテキストファイルに出力
    '''

    with open('検索キーワードリスト.txt', encoding="utf-8") as f:  # '検索キーワードリスト.txt'ファイルを読み込み、リストにする
        keywords = [s.rstrip() for s in f.readlines()]  # １行ずつ読み込んで改行コードを削除してリストにする

    with open('ドメインリスト.txt', encoding="utf-8") as f:  # 'ドメインリスト.txt'ファイルを読み込み、リストにする
        domains = [s.rstrip() for s in f.readlines()]  # １行ずつ読み込んで改行コードを削除してリストにする

    # seleniumで自動操作するブラウザはGoogleChrome
    options = Options()  # Optionsオブジェクトを作成

    # ヘッドレスモードを有効にする
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)  # ChromeのWebDriverオブジェクトを作成

    # driver = webdriver.Chrome(options=options, executable_path=r"D:\Program\chromedriver_win32\chromedriver.exe")

    driver.get(URL)  # Googleのトップページを開く
    time.sleep(2)  # 2秒待機（読み込みのため）

    ok_keywordlist = []
    for keyword in keywords:  # 検索キーワードを１つずつ取り出す
        search(keyword, driver)  # search関数実行
        urls = get_url(driver)  # get_url関数を実行し、戻り値をurlsに代入
        weak_keywordlist = domain_checked(urls, domains, ok_keywordlist, keyword)  # domain_checked関数を実行し、戻り値をok_keywordlistに代入

    # '結果.txt'という名前を付けて、ドメインチェックしたキーワードをファイルに書き込む
    with open('結果.txt', 'w') as f:
        f.write('\n'.join(weak_keywordlist))  # ドメインチェック済みのキーワードを１行ずつ保存

    driver.quit()  # ブラウザーを閉じる

def search(keyword, driver):
    '''
    検索テキストボックスに検索キーワードを入力し、検索する
    '''
    input_element = driver.find_element_by_name('q')  # 検索テキストボックスの要素をname属性から取得

    input_element.clear()  # 検索テキストボックスに入力されている文字列を消去

    input_element.send_keys(keyword)  # 検索テキストボックスにキーワードを入力

    input_element.send_keys(Keys.RETURN)  # Enterキーを送信

    time.sleep(2)  # 2秒待機

　  # タイトルにkeywordが含まれていることを確認

def get_url(driver):
    '''
    検索結果ページの1位から10位までのURLを取得
    '''

    urls = []  # 各ページのURLを入れるためのリストを指定
    objects = driver.find_elements_by_css_selector('div.r > a')  # a要素（各ページの1位から10位までのURL）取得
    # objects = driver.find_elements_by_css_selector('.rc > .r > a')

    if objects:
        for object in objects:
            urls.append(object.get_attribute('href'))  # 各ページのURLをリストに追加
    else:
        print('URLが取得できませんでした')  # 各ページのURLが取得できなかった場合は警告を出す
    return urls  # 各ページのURLを戻り値に指定

def domain_checked(urls, domains, ok_keywordlist, keyword):
    '''
    URLリストからドメインを取得し、指定ドメインに含まれているかチェック
    '''
    # URLリストから各ページのURLを１つずつ取り出す
    for url in urls:
        m = re.search(r'//(.*?)/', url)  # '//〇〇/'に一致する箇所（ドメイン）を抜き出す
        domain = m.group(1)  # '//〇〇/'の'〇〇'に一致する箇所を抜き出し、domainに代入
        if 'www.' in domain:  # ドメインに'www.'が含まれているかチェック
            domain = domain[4:]  # 含まれているなら'www.'を除去
        if domain in domains:  # 各ページのドメインが指定ドメインに含まれているかチェック
            # 含まれているなら警告を出す
            print(f'キーワード「{keyword}」の検索結果には大手ドメインがありましたので除外します。')
            break  # １つでも含まれているなら他はチェックする必要がないので関数を終了
    else:
        ok_keywordlist.append(keyword)  # 指定ドメインに含まれていないならキーワードをokkeywordlistに追加
    return ok_keywordlist  # ドメインチェック済みのキーワードを戻り値に指定

if __name__ == "__main__":

    main()  # main関数を実行
