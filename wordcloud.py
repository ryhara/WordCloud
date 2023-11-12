# -*- coding: utf-8 -*-
"""WordCloud.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pmLIjnJix2KGw30VigtM8Eisg2Tb5WYx

<font color = red><h2>※Google Colaboratoryで開いてください</h2></font>

# Googleドライブへの接続
"""

#※Google Colaboratoryでこのファイルを開いてください
#全てをまとめて実行する場合は上のメニューバーの「ランタイム」から全てのセルを実行
#Googleアカウントへのログインが必要
from google.colab import drive
drive.mount('/content/drive')

#Googleドライブ内に、使用するデータとコードを含んだディレクトリを作成し、そのパスを指定
import os

#ディレクトリ名を指定
project = 'directory'
#そのディレクトリへ移動
os.chdir(f'/content/drive/MyDrive/{project}/')

"""# コード

## 準備
"""

#現在のディレクトリ内のファイル一覧を表示
#分析したいtxtファイルはコードと同じディレクトリに置く
! ls

#現在のディレクトリ内のtxtファイルを指定してreadして出力
#　https://www.aozora.gr.jp/　内のtxtファイルであれば、以降の作業で本文のみの抽出が可能
with open('./gakumonno_susume.txt', mode='r', encoding='shift-jis') as f:
  content = f.read()
print(content)

#解析に必要のない部分を取り除き、本文のみを取り出す作業
import re
body = content
body = re.split(r'\--+', body)[2] # --が連続した部分で区切り、見出し以降を抽出
body = re.split(r'底本：', body)[0] # '底本'の部分で区切り、見出し、本文を抽出
body = re.sub(r'《.+?》', '', body) # 《》で囲まれた部分を削除
body = re.sub(r'［＃.+?］', '', body) # ［＃］で囲まれた部分を削除
body = ' '.join(body.split()) #スペース、改行、タブで分割して繋げることで1行の文章にする
body = body.strip() # 前後の余白を削除

print(body)

"""## 形態素解析


"""

#mecabのインストール 少し時間がかかります
!apt install -q \
  mecab \
  mecab-ipadic-utf8 \
  libmecab-dev
!pip install -q mecab-python3
!ln -s /etc/mecabrc /usr/local/etc/mecabrc


#インストールの確認
!pip list | grep mecab

import MeCab

tagger = MeCab.Tagger()
#parseでbodyを形態素解析したあと、splitで改行ごとに区切って形態素ごとに配列に格納
parsed = tagger.parse(body).split('\n')
parsed[:6]

print(parsed[-4:])
#末尾二つが必要のないデータであるので取り除く
parsed = parsed[:-2]
parsed[-4:]

#parsedの要素をsplitで\tまたはカンマの場合に区切って、配列に格納している。
#lamdaで定義した関数をmapによってparsedに適用している。
#*values, = はアンパックを表しており、可変長の配列に分割して格納している
*values, = map(lambda s: re.split(r'\t|,',s),parsed)
values[:4]

#mecabのカラム名を追加し、pandasでデータフレームに格納
import pandas as pd
columns =['表層形','品詞','品詞細分類1','品詞細分類2','品詞細分類3','活用型','活用形','原形','読み','発音']
mecab_df = pd.DataFrame(data=values,columns=columns)
print(len(mecab_df))
mecab_df

#単語の原形と品詞、その登場回数を多い順に出力
print(mecab_df.groupby(['原形','品詞']).size().sort_values(ascending=False))

#単語の品詞が名詞のものだけを出力
noun = mecab_df.loc[mecab_df['品詞']=='名詞']
noun

#名詞と動詞だけを出力
verb = mecab_df.loc[(mecab_df['品詞'] == '名詞')|(mecab_df['品詞'] == '動詞')]
verb

#名詞の出現回数を数えて、多い順に表示
count = noun.groupby('原形').size().sort_values(ascending=False)
count.name = 'count'
count = count.reset_index().head(10)
count

#分析に必要のない単語を取り除く
#取り除く単語は文章によって、臨機応変に変更する。
#本文の本質とは関係のない単語を取り除けばよい。
stop_words = ["これ","こと","もの","*","ところ","の","よう"]
noun = noun.loc[~noun['原形'].isin(stop_words)]
count = noun.groupby('原形').size().sort_values(ascending=False)
count.name = 'count'
count = count.reset_index().head(10)
count

#グラフの表示に必要なライブラリをインストール
!pip install -q japanize-matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import japanize_matplotlib

#グラフの表示
plt.figure(figsize=(10, 5))
sns.barplot(x=count['count'], y=count['原形'])

#フォントのインストールと確認
!apt-get -yq install fonts-ipafont-gothic
!ls /usr/share/fonts/opentype/ipafont-gothic

#ワードクラウドを用いて、単語の傾向を可視化する
#出現頻度の高い単語が大きく表示される。
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import japanize_matplotlib
font_path = 'usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf'
cloud = WordCloud(background_color='white', font_path=font_path).generate(' '.join(noun['原形'].values))
plt.figure(figsize=(10, 5))
plt.imshow(cloud)
plt.axis("off")
plt.savefig('./wc_noun.png') #画像で保存、パスと名前を指定
plt.show()