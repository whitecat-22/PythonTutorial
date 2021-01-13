# pandasのimport
import pandas as pd
# fbprophetのimport
from fbprophet import Prophet

# データの読み込み
df = pd.read_csv("NoCode_2020-05-28-23-25.csv")

# 最初の5行を取得
df.head()

# 行数・列数を取得
df.shape

# データの整形
# 日時といいね数の列を取り出して新しいDataFrameを作る。
df = df.loc[:,['日時','いいね数']]

# 日時をdatetime型にする
df['日時'] = pd.to_datetime(df['日時'])

#　日付が同じデータを足してまとめる
df = df.resample('D', on='日時').sum()
print(df)

# 通常の0から始まるindexを追加
df = df.reset_index()

# prophetの予測のために、dsとyをカラム名に設定
df = df.rename(columns={'日時':'ds', 'いいね数':'y'})
print(df)
m = Prophet()

# データを元に学習
m.fit(df)

# 予測する分のデータフレームの作成
future = m.make_future_dataframe(periods=60)

# 最後の5行を表示する
print(future.tail())

# 予測する
forecast = m.predict(future)

# 予測データの描画
m.plot(forecast)

# plotlyのimport
#from fbprophet.plot import plot_plotly
#import plotly.offline as py

# 予測データをインタラクティブに描画
#fig1 = plot_plotly(m, forecast)
#py.plot(fig1)

# 予測データのトレンドや周期性を描画
fig2 = m.plot_components(forecast)