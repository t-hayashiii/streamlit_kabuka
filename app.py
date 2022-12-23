# 実行はターミナルで。streamlit run app.py

# ライブラリの読み込み
import pandas as pd
import yfinance as yf
import altair as alt
import streamlit as st

# タイトル
st.title('建設業株価可視化アプリ')

# side bar 複数行にわたる文字列
st.sidebar.write("""
# 主要ゼネコン株価
こちらは株価可視化ツールです。以下のオプションから表示日数を指定できます。
""")

st.sidebar.write("""
## 表示日数選択
""")

# 日付のスライダーを作成し、それを変数daysに代入
days = st.sidebar.slider('日数', 1, 50, 20)

# メイン
st.write(f"""
### 過去 **{days}日間** の主要ゼネコン株価
""")

# キャッシュに貯めることで高速に回せるおまじない
# キャッシュのクリアは st.cache.clear?? → 要検索
@st.cache(persist=False)
# get_dataの定義
def get_data(days, tickers):
    df = pd.DataFrame()  # pandasの空のデータを用意 
    for company in tickers.keys():
        # 株価の取得
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')

        # Date表示形式を変更
        # https://www.ibm.com/docs/en/cmofm/9.0.0?topic=SSEPCD_9.0.0/com.ibm.ondemand.mp.doc/arsa0257.html
        hist.index = hist.index.strftime('%Y-%m-%d')

        # 終値closeのみを使用
        hist = hist[["Close"]]  
        hist.columns = [company]

        # 表に合わせて行列を入替え
        hist = hist.T

        # index名にNameを入れる
        hist.index.name = 'Name'

        df = pd.concat([df, hist])  # panadasのデータにhistを順次追加していく★重要★

    return df


# エラー表示対応 try except
try:
    # サイドバー その2
    st.sidebar.write("""
    ## 株価の範囲指定
    """)

    ymin, ymax = st.sidebar.slider(
        '範囲を指定してください',
        0, 5000, (0, 5000)  # スライダーで2点を指定する方法
    )

    # 対象の会社ライブラリ
    tickers = {
        '矢作': '1870.T',
        '清水': '1803.T',
        '戸田': '1860.T',
        '大林': '1802.T',
        '鹿島': '1812.T',
        '大成': '1801.T'
    }

    df = get_data(days, tickers)

    # multiselect
    companies = st.multiselect(
        '会社名を選択してください。',
        list(df.index),
        ['矢作', '清水', '戸田', '大林', '鹿島', '大成']   # デフォルト
    )

    # エラー対応 → 最低でもひとつ選択させる
    # 問題なければグラフを表示させる
    if not companies:  # もしcompaniesにひとつも入っていなかったら
        st.error('少なくとも一社は選んで下さい。')
    else:
        data = df.loc[companies]
        st.write("### 株価(主要ゼネコン)", data.sort_index())
        # インデックスからデータを取り除いて通常のデータ型に変更
        data = data.T.reset_index()
        # Date列を基準に元の汚い形のデータに戻す 溶けるメルト
        data = pd.melt(data, id_vars=['Date']).rename(columns={'value': "株価"})  
        # グラフの表示
        # https://altair-viz.github.io/index.html
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True) # はみ出している線をクリップ
            .encode(
                x="Date:T",
                y=alt.Y("株価:Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),   #上限,下限
                color="Name:N"
            )
        )
        st.altair_chart(chart, use_container_width=True) # 枠サイズちょうどに表示

except:
    st.error(
        "おっと!なにかエラーが起きているようです。"
    )

