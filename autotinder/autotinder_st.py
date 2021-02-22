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
import streamlit as st
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
    token = "4abdd6d7-2139-411f-a06a-a4a9856c5f6e"
    # インスタンス化
    api = tinderAPI(token)
    mtcnn = MTCNN()
    resnet = InceptionResnetV1(pretrained='vggface2').eval()
    dirname ="./faces/imface"
    
    save_dirname = "./faces/save_imface"
    st.title('Auto like Tinder')
    st.sidebar.header("Adjust parameters")
    
    add_slider = st.sidebar.slider(
        "Determine the similarity", min_value=30, max_value=70, step=5
    )
    favorite_dict = {"川口春奈" : "./origin_images/croped/3.jpg",
    "新垣結衣" : "./origin_images/croped/0.jpg",
    "生田絵梨花" : "./origin_images/croped/1.jpg",
    "齋藤飛鳥" : "./origin_images/croped/2.jpg"}
    
    select_img = st.sidebar.selectbox(
    "Who do you like",
    ("川口春奈", "新垣結衣", "生田絵梨花", "齋藤飛鳥")
    )
    
    image = Image.open(favorite_dict[select_img])
    st.image(favorite_dict[select_img], width=300)
    st.write(f'{select_img}と{add_slider}%以上顔が似ている人にいいね')

    # 芸能人の画像の計算
    im_img = favorite_dict[select_img]
    #im_img = r"./origin_images/original/2764183_ext_col_03_1.jpg"
    img = Image.open(im_img)
    img_cropped = mtcnn(img)
    img1_fv = resnet(img_cropped.unsqueeze(0))
    img1_fv_np = img1_fv.squeeze().to('cpu').detach().numpy().copy()

    # 実行ボタン
    if st.button('今すぐ近くの異性を探す'):
        try:    
            while True:
                # 近くのユーザーの呼び出し
                persons = api.nearby_persons()
                for person in persons:
                    # personごとに画像をダウンロードして、保存
                    for i, image_url in enumerate(person.images):
                        person.download_images(image_url, folder=dirname, index=i)
                        # トリミングした画像のパスの指定
                        save_img = rf"faces/save_imface/{person}.jpg"
                        path = get_latest_modified_file_path(dirname)
                        img = Image.open(path)
                        try:
                            img_cropped = mtcnn(img, save_path=save_img)
                            # 顔が検出できなかった場合は次の画像へ
                            if img_cropped is None:
                                #st.write(f'{person}の結果は', img_cropped)
                                #st.image(img, width=300)
                                continue 
                        except Exception as e:
                            # 顔が検出できなかった場合は次の画像へ
                            #st.write(e)
                            continue
                        
                        # しっかりと顔を検出できた時
                        img2_fv = resnet(img_cropped.unsqueeze(0))
                        img2_fv_np = img2_fv.squeeze().to('cpu').detach().numpy().copy()
                        similarity = cosine_similarity(img1_fv_np, img2_fv_np)

                        # 類似度の判定
                        if similarity * 100 > add_slider:
                            image = Image.open(save_img)
                            st.image(save_img, width=300)
                            person.like()
                            st.write(person)
                            st.write(f'{select_img}との類似度', similarity * 100)
                            st.write('いいねしました。')
                            # 類似度が高ければもう次の人に行っていい
                            break
                        # 類似度が低い場合?次の画像に行く
                        else:
                            #image = Image.open(save_img)
                            #st.image(save_img, width=300)
                            #st.write(person)
                            #st.write(f'{select_img}との類似度', similarity * 100)
                            #st.write('類似度が低いのでパス')
                            continue
                    time.sleep(random.random()*10)    
        except KeyboardInterrupt:
            pass
            sys.exit()
                    

