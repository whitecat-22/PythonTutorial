import datetime
import requests
import time
import random
import os
from glob import glob
import warnings
from facenet_pytorch import MTCNN, InceptionResnetV1
from geopy.geocoders import Nominatim
from PIL import Image
import numpy as np
from numpy.core.fromnumeric import squeeze
import sys

warnings.simplefilter('ignore')

PROF_FILE = "./origin_images/original/profiles.txt"
TINDER_URL = "https://api.gotinder.com"
geolocator = Nominatim(user_agent="auto-tinder")

def get_latest_modified_file_path(dirname):
    target = os.path.join(dirname, '*')
    files = [(f, os.path.getmtime(f)) for f in glob(target)]
    latest_modified_file_path = sorted(files, key=lambda files: files[1])[-1]
    return latest_modified_file_path[0]

#### 2つのベクトル間のコサイン類似度を取得(cosine_similarity(a, b) = a・b / |a||b|)
def cosine_similarity(a, b):
    try:
        cosine_similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return cosine_similarity
    except TypeError:
        pass
    return

# Personクラスの作成
class Person(object):

    def __init__(self, data, api):
        self._api = api

        self.id = data["_id"]
        self.name = data.get("name", "Unknown")

        self.bio = data.get("bio", "")
        self.distance = data.get("distance_mi", 0) / 1.60934

        self.birth_date = datetime.datetime.strptime(data["birth_date"], '%Y-%m-%dT%H:%M:%S.%fZ') if data.get(
            "birth_date", False) else None
        self.gender = ["Male", "Female", "Unknown"][data.get("gender", 2)]

        self.images = list(map(lambda photo: photo["url"], data.get("photos", [])))

        self.jobs = list(
            map(lambda job: {"title": job.get("title", {}).get("name"), "company": job.get("company", {}).get("name")}, data.get("jobs", [])))
        self.schools = list(map(lambda school: school["name"], data.get("schools", [])))

        if data.get("pos", False):
            self.location = geolocator.reverse(f'{data["pos"]["lat"]}, {data["pos"]["lon"]}')


    def __repr__(self):
        return f"{self.id}  -  {self.name} ({self.birth_date.strftime('%d.%m.%Y')})"


    def like(self):
        return self._api.like(self.id)

    def dislike(self):
        return self._api.dislike(self.id)

    def prof_files(self):
        with open(PROF_FILE, "r") as f:
            lines = f.readlines()
            if self.id in lines:
                return
        with open(PROF_FILE, "a") as f:
            f.write(self.id+"\r\n")
    
    def download_images(self, image_url, folder=".", index = -1):
        #index = -1
        #for image_url in self.images:
        #index += 1
        req = requests.get(image_url, stream=True)
        if req.status_code == 200:
            with open(f"{folder}/{self.id}_{self.name}_{index}.jpg", "wb") as f:
                f.write(req.content)
        #time.sleep(random.random()*sleep_max_for)
    
TINDER_URL = "https://api.gotinder.com"

# APIラッパーの部分
class tinderAPI():

    def __init__(self, token):
        self._token = token

    def profile(self):
        data = requests.get(TINDER_URL + "/v2/profile?include=account%2Cuser", headers={"X-Auth-Token": self._token}).json()
        return Profile(data["data"], self)

    def matches(self, limit=10):
        data = requests.get(TINDER_URL + f"/v2/matches?count={limit}", headers={"X-Auth-Token": self._token}).json()
        return list(map(lambda match: Person(match["person"], self), data["data"]["matches"]))

    def like(self, user_id):
        data = requests.get(TINDER_URL + f"/like/{user_id}", headers={"X-Auth-Token": self._token}).json()
        return {
            "is_match": data["match"],
            "liked_remaining": data["likes_remaining"]
        }

    def dislike(self, user_id):
        requests.get(TINDER_URL + f"/pass/{user_id}", headers={"X-Auth-Token": self._token}).json()
        return True

    def nearby_persons(self):
        persons_list = []
        data = requests.get(TINDER_URL + "/v2/recs/core", headers={"X-Auth-Token": self._token}).json()
        try:
            persons_list = list(map(lambda user: Person(user["user"], self), data["data"]["results"]))
            return persons_list
        except KeyError:
            pass
        return persons_list
    
if __name__ == "__main__":
    # Tinderからダウンロードした画像を保存するパス
    dirname ="./faces/imface"
    # Tinderからダウンロードした画像を顔検出してトリミングした画像を保存するパス
    save_dirname = "./faces/save_imface"
    # Tinder APIのトークンを記述
    token = "4abdd6d7-2139-411f-a06a-a4a9856c5f6e"
    # TinderAPIのインスタンス化
    api = tinderAPI(token)
    # 顔検出のためのMTCNNの準備
    mtcnn = MTCNN()
    # 顔を推論するためのVGGFace2で事前学習されたInceptionResnetV1の準備
    resnet = InceptionResnetV1(pretrained='vggface2').eval()
    # 芸能人の名前とパスの辞書
    favorite_dict = {"川口春奈" : "./origin_images/croped/3.jpg",
    "新垣結衣" : "./origin_images/croped/0.jpg",
    "生田絵梨花" : "./origin_images/croped/1.jpg",
    "齋藤飛鳥" : "./origin_images/croped/2.jpg"}

    # 芸能人の画像の計算
    im_img = favorite_dict["川口春奈"]
    # 顔画像ファイルの読み込み
    img = Image.open(im_img)
    # 顔検出＋トリミングして画像テンソルの形にして保存
    img_cropped = mtcnn(img)
    # トリミングした画像テンソルを512個の数字に
    img1_fv = resnet(img_cropped.unsqueeze(0))
    # 512個の数字をテンソル型からnumpy型に変換
    img1_fv_np = img1_fv.squeeze().to('cpu').detach().numpy().copy()
    # while文でAPIリクエストを送るので、無限ループから抜けるためにtry-except
    try:    
        while True:
            # 近くのユーザーの呼び出し
            persons = api.nearby_persons()
            # for文で一人一人処理をしていく
            for person in persons:
                # personごとの複数枚の画像をダウンロードして、for文で一枚一枚処理する
                for i, image_url in enumerate(person.images):
                    person.download_images(image_url, folder=dirname, index=i)
                    # トリミングした画像のパスの指定
                    save_img = rf"./faces/save_imface/{person}.jpg"
                    # フォルダ中の最後に更新したファイルパスの取得
                    path = get_latest_modified_file_path(dirname)
                    # 画像ファイルの読み込み
                    img = Image.open(path)
                    try:
                        # 顔検出＋トリミングして画像テンソルの形にして保存
                        img_cropped = mtcnn(img, save_path=save_img)
                        # 顔が検出できなかった場合は次の画像へ
                        if img_cropped is None:
                            #print(f'{person}の結果は', img_cropped)
                            continue 
                    except Exception as e:
                        # 顔が検出できなかった場合は次の画像へ
                        #print(e)
                        continue
                    
                    # しっかりと顔を検出できた場合
                    # トリミングした画像テンソルを512個の数字に
                    img2_fv = resnet(img_cropped.unsqueeze(0))
                    # 512個の数字をテンソル型からnumpy型に変換
                    img2_fv_np = img2_fv.squeeze().to('cpu').detach().numpy().copy()
                    # コサイン類似度を計算
                    similarity = cosine_similarity(img1_fv_np, img2_fv_np)
                    # if文で類似度の条件分岐
                    if similarity * 100 > 30:
                        # 類似度が条件を超えていたらいいねをする
                        person.like()
                        # 名前、類似度、いいねの表示の順に出力
                        print(person)
                        print('川口春奈との類似度は', similarity * 100)
                        print('いいねしました。')
                        # いいねをしたら次の人に行く
                        # breakで内側のfor文を抜ける
                        break
                    # else節　類似度が低い場合⇨次の画像に行く
                    else:
                        #print(person)
                        #print(f'{select_img}との類似度', similarity * 100)
                        #print('類似度が低いのでパス')
                        continue
                # rondomスリープ
                time.sleep(random.random()*10)
    # Ctrl+Cを押した時にプログラム終了のためにexcept 
    except KeyboardInterrupt:
        pass
        sys.exit()
                    
