import pandas as pd

# リストの入れ子でDataFrameを作る
df = pd.DataFrame([[1, 3, 5], [2, 4, 6], [8, 9, 10]])
print(df)

# columnsとindexを指定する
df1 = pd.DataFrame([[1, 3, 5],
                    [2, 4, 6],
                    [8, 9, 10]],
                   columns=['A', 'B', 'C'],
                   index=['C', 'E', 'F'])

print(df1)

# 辞書でcolumnsとリストを指定する
df2 = pd.DataFrame({'A': [1, 3, 5],
                   'B': [2, 4, 6],
                   'C': [7, 8, 9]},
                   index=[1, 2, 3])

print(df2)

