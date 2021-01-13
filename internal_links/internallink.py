# プログラム終了のためのsysのimport
import sys
# 正規表現を使うためのreをimport
import re
# HTTPリクエストを送るためのrequestsをimport
import requests
# BeautifulSoupをimport
from bs4 import BeautifulSoup
# URLからドメインを取得する為にurlparseをimport
from urllib.parse import urlparse
# ネットワーク図を作成する為にnetworkxをimport
import networkx as nx
# ネットワーク図を描画する為にmatplotlibをimport
import matplotlib.pyplot as plt

def main():
    """
    メインの実行部分:調べたいURLはanl_urlに入力する
    """

    pages = set()  #空のセットを用意
    anl_url = "https://hashikake.com/import"  # 内部リンクを調べたいURL
    
    match_url = re.match("https?://.*?/", anl_url)  # https://またはhttp://からはじまる基準のホームページのURL
    base_url = match_url.group()  # match_urlはマッチオブジェクトなので、そこからURLだけを取り出す
    base_domain = urlparse(anl_url).netloc  # 正規表現で使うためにドメイン名の取得
    innerlinks = get_links(anl_url, pages, base_url, base_domain)  #　内部リンクの取得
    if innerlinks:  # 内部リンクが存在するなら
        print(f"内部リンクは全部で{len(innerlinks)}個あります。")  # 内部リンクの数を表示
        print("内部リンクの表示", innerlinks)  # 内部リンクの表示
        short_links = []  # 関数内で使われるshort_linksを定義
        short_links = shape_url(innerlinks, short_links, base_url, base_domain)  # 内部リンクとして価値の薄いものの除外
        print(f"重要な内部リンクは全部で{len(short_links)}個あります。")  # 内部リンクとして価値が高いものの数を表示
        print("short_linksの表示", short_links)
        show_network(short_links)
    else:
        print("ページ情報が取得できませんでした。")
        sys.exit()

    return innerlinks

def get_links(anl_url:str, pages:set, base_url:str, base_domain:str) -> set:
    """
    /で始まるものと、base_urlから始まるもの//ドメインから始まるもの
    全ての内部リンクを取得して、重複を除去してpagesに収集する＋
    内部リンク数を出力
    """
    # 正規表現の中で変数を使う時はf文字列またはformatを使う
    my_regex = rf"^(/[^/].*?)|^({base_url}.*)|^(//{base_domain}.*)" # /で始まって//を含まないURLと、https://ドメインから始まるもの
    pattern = re.compile(my_regex)  # re.compileによる正規表現パターンの生成
    html = requests.get(anl_url)  # URLにGETリクエストを送る
    soup = BeautifulSoup(html.content, "html.parser")  # BeautifulSoupによるsoupの作成
    for link in soup.find_all("a", href=pattern):  # URLがパターンに一致するaタグを取得
        if "href" in link.attrs:  # リンクタグの属性辞書をattrsによって作成
            print(link.attrs["href"])
            if link.attrs["href"] not in pages:  # セットの中にリンクが入っていないことを確認
                new_page = link.attrs["href"]  # 新しいページとしておく
                # print(new_page)  # 新しいページを表示
                pages.add(new_page)  # セットの中に内部リンクとして追加
    return pages

def show_network(pages:list):
    """
    調査URLを中心としたネットワーク図の作成
    """
    pages = list(pages)
    pages.insert(0, "start_url")  # indexの0に文字列"start_url"を追加
    G = nx.DiGraph()  #　空のグラフの作成　有向グラフ
    nx.add_star(G, pages)  # リストの最初の要素を中心として放射状に頂点と辺の追加
    pos = nx.spring_layout(G, k=0.3)  # レイアウトを決める スプリングレイアウト
    nx.draw_networkx_nodes(G, pos, node_size=300, node_color='c', alpha=0.6)  # ノードの様式
    nx.draw_networkx_labels(G, pos, font_size=10)  # ラベル文字の様式
    nx.draw_networkx_edges(G, pos, alpha=0.4, edge_color='c')  # エッジの様式
    #nx.draw_networkx(G)
    plt.axis('off')  # 座標軸の非表示
    plt.show()

def shape_url(innerlinks, short_links, base_url, base_domain):

    """
    URLのhttp://を省略してネットワーク図を見やすくするための調整
    privacyページやcontactページなどの無駄な内部リンクページの除去
    """    

    for url in innerlinks:  # 内部リンクのURLから効果の薄い内部リンクをre.sub()で消していく
        rel_path = re.sub(rf"^{base_url}|^(//{base_domain})|.*tag.*|.*feed.*|.*about.*", "", url)
        short_links.append(rel_path)  # short_links（空のリスト）に追加
        s_links = set(short_links)  # short_linksをセットに変更(重複の削除)
        s_links.discard("")  # ""を削除　# discardだとキーがなくてもエラーにはならない。removeだとエラーになる。
    return s_links

if __name__ == '__main__':
    main()
