import glob
from facenet_pytorch import MTCNN
import os
from PIL import Image

image_dir = r"./origin_images/original"

# MTCNN()で顔認識＋トリミング
mtcnn = MTCNN()

# glob.glob(directory)⇨ファイル一覧をディレクトリとして取得
list = glob.glob(os.path.join(image_dir, "*.jpg"))
print(list)
print('トリミング開始')
for i, path in enumerate(list):
    img = Image.open(path)
    try:
        mtcnn(img, save_path=r"./origin_images/croped/{}.jpg".format(str(i))) # 画像と保存先を渡す
    except KeyError as e:
        print(e)
print('トリミング終了')
    