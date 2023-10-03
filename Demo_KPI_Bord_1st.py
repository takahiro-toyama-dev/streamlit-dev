#
# pandas : データ加工
#
import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
#from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, ColumnsAutoSizeMode, AgGridTheme
#from st_aggrid.grid_options_builder import GridOptionsBuilder

import matplotlib as mpl
import matplotlib.pyplot as plt

import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio

from numpy import pi, cos, sin


# 定数
## 最新年度
const_nendo_latest = [2022]
const_nendo_previous = [2021]
const_nendo_all = [2022,2021,2020,2019,2018,2017]
const_segment_id_all = ["A01","A02","A03","A04","A05"]

# ページ設定
st.set_page_config(
    page_title="streamlitテスト",
    page_icon="🗾",
    layout="wide"
)


# CSVデータの読み込み
def load_data():
    ## 売上
    in_csv_sales = pd.read_csv('kpiin_sales.csv')
    ## 営業利益
    in_csv_prof = pd.read_csv('kpiin_profit.csv')
    ## セグメント
    in_csv_seg = pd.read_csv('kpiin_segment.csv')
    ## セグメント辞書
    dict_segment = dict(zip(in_csv_seg["セグメントID"], in_csv_seg["セグメント名"]))
    ## 読んだCSVをDataFrameで返す
    return in_csv_sales, in_csv_prof, in_csv_seg, dict_segment

def get_segmenid_list_from_segmentname_list(segmentnames):
    dict_segment_name2id = dict(zip(in_csv_seg["セグメント名"], in_csv_seg["セグメントID"]))
    segment_id_list = []
    for name in segmentnames:
        segment_id_list.append( dict_segment_name2id[name] )
    return segment_id_list

# セグメント別売上
def get_sales_info_by_segments(selected_segment_id, selected_nendo):
    # 売上CSVから、引数の条件で絞込　引数：selected_segments, selected_nendo
    df_sales = in_csv_sales[(in_csv_sales["セグメントID"].isin(selected_segment_id)) & (in_csv_sales["年度"].isin(selected_nendo))]
    sales_info = df_sales.groupby(by="セグメントID").sum().sort_values(by="セグメントID", ascending=True).reset_index()
    sales_info['セグメント名'] = sales_info['セグメントID'].apply(lambda x: dict_segment[x])
    return sales_info

# セグメント別、年度別売上
def get_sales_info_by_segments_and_nendo(selected_segment_id, selected_nendo):
    # 売上CSVから、引数の条件で絞込　引数：selected_segments, selected_nendo
    df_sales = in_csv_sales[(in_csv_sales["セグメントID"].isin(selected_segment_id)) & (in_csv_sales["年度"].isin(selected_nendo))]
    sales_info = df_sales.groupby(by=["セグメントID","年度"]).sum().sort_values(by=["年度","セグメントID"], ascending=True).reset_index()
    sales_info['セグメント名'] = sales_info['セグメントID'].apply(lambda x: dict_segment[x])
    return sales_info

# 利益率算出
def func_profit_per_sales(df):
    return (df["営業利益[百万円]"] / df["売上高[百万円]"])

# 営業利益(地図用)
# 地図（バブルマップ）表示用に、営業利益を重みづけ
def func_profit_for_map(df):
    return (df["営業利益[百万円]"] * 0.0003)

# セグメント別営業利益
def get_sales_profit_info_by_segments_and_nendo(selected_segment_id, selected_nendo):
    # 売上CSVから、引数の条件で絞込　引数：selected_segments, selected_nendo
    ## 営業利益
    df_prof = in_csv_prof[(in_csv_prof["セグメントID"].isin(selected_segment_id)) & (in_csv_prof["年度"].isin(selected_nendo))]
    profit_info = df_prof.groupby(by=["セグメントID","年度"]).sum().sort_values(by=["年度","セグメントID"],ascending=True).reset_index()
    profit_info['セグメント名'] = profit_info['セグメントID'].apply(lambda x: dict_segment[x])

    ## 売上
    sales_info = get_sales_info_by_segments_and_nendo(selected_segment_id, selected_nendo)

    ## 売上と営業利益を連結
    return_info = profit_info.merge(sales_info, on=["年度","セグメントID"], how="outer")
    return_info.rename(columns={'セグメント名_y':'セグメント名_売上'})

    ## 営業利益率を算出して、列追加
    return_info['営業利益率'] = return_info.apply(lambda x: func_profit_per_sales(x),axis=1).astype(float)
    return_info['営業利益-マップ用'] = return_info.apply(lambda x: func_profit_for_map(x),axis=1)
    return return_info


# 全社　営業利益
def get_profit_sales_info_allsegments(arg_segment_id, arg_nendo):
    ## 営業利益
    df_profit = in_csv_prof[(in_csv_prof["セグメントID"].isin(arg_segment_id)) & (in_csv_prof["年度"].isin(arg_nendo))]
    all_profit_info = df_profit.groupby(by=["年度"]).sum().sort_values(by=["年度"],ascending=True).reset_index()
    ## 売上
    df_sales = in_csv_sales[(in_csv_sales["セグメントID"].isin(arg_segment_id)) & (in_csv_sales["年度"].isin(arg_nendo))]
    all_sales_info = df_sales.groupby(by=["年度"]).sum().sort_values(by=["年度"], ascending=True).reset_index()

    ## 売上と営業利益を連結
    all_sales_profit_info = all_profit_info.merge(all_sales_info, on=["年度"], how="outer")

    ## 営業利益率を算出して、列追加
    all_sales_profit_info['営業利益率'] = all_sales_profit_info.apply(lambda x: func_profit_per_sales(x),axis=1)

    return all_sales_profit_info


#--------

# CSV読み込み
in_csv_sales, in_csv_prof, in_csv_seg, dict_segment = load_data()

# Title
st.subheader('Streamlit KPIボードサンプル')


#
# サイドバー
#
with st.sidebar:
    st.subheader("表示条件")

    # セグメント選択
    ## セグメントCSVからセグメント読み込み
    segment_name_list = dict_segment.values()
    selected_segment_names = st.multiselect("表示するセグメントを選択"
                                       , options=segment_name_list, default=segment_name_list)
    selected_segment_ids = get_segmenid_list_from_segmentname_list(selected_segment_names)
#    st.dataframe(selected_segment_names)
#    st.write(selected_segment_ids)

    # 年度選択
    nendo_list = list(in_csv_sales["年度"].unique())
    selected_nendo = st.multiselect("表示する年度を選択"
                                    , options=nendo_list, default=nendo_list)
#    st.dataframe(selected_nendo)
   



#
# 表示部
#
## ３カラム表示
col1, col3 = st.columns([1,1])

# メーター（Gaugeチャート）
## 営業利益率前年比
col1.subheader('ゲージチャート')

### データ生成
### 今年度　営業利益
df_prof_latest = get_profit_sales_info_allsegments(selected_segment_ids, const_nendo_latest)
### 前年度　営業利益
df_prof_previous = get_profit_sales_info_allsegments(selected_segment_ids, const_nendo_previous)

# Gaugeの値　＝　今年度の営業利益率
_g_value = float( round(100*df_prof_latest["営業利益率"],1).iloc[0] )

# Gaugeのしきい値　＝　前年度の営業利益率
_g_threshold_value = float( round(100*df_prof_previous["営業利益率"],1).iloc[0] )

# Gaugeの基本設定
# グラフタイトル
_g_title_text = "営業利益率（状況＋前年比）"
# グラフ最大値
_g_range_max = 10
# 前年度ラベル
_g_threshold_label = "前年度"
# 前年度ラベル色
_g_threshold_color = "green"

# ゲージチャート設定
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number"
    ,value=_g_value
    ,number={'suffix':"%", 'font':{'size':36}}
    ,domain={'x':[0,1], 'y':[0,1]}
    ,title={'text':_g_title_text, 'font':{'size': 20}}
    ,delta={'reference':_g_threshold_value}
    ,gauge={
        'axis':{   'range':[None, _g_range_max]
                 , 'tickwidth':1 
                 , 'tickcolor': "darkblue"
                 , 'ticksuffix' : "%"
#                 , 'tickformat':".1%"
                }
        ,'bar':{'color':"darkblue"}
        ,'bgcolor': "white"
        ,'borderwidth': 2
        ,'bordercolor': "gray"
        ,'steps' : [
             {'range': [0,4], 'color':'red'}
            ,{'range': [4,6], 'color': 'cyan'}
            ,{'range': [6,10], 'color': 'royalblue'}
            ]
        ,'threshold': {
            'line': {'color': _g_threshold_color, 'width': 4}
            ,'thickness': 1.0
            ,'value': _g_threshold_value
        }
    }))
# 前年度のラベル表示
threshold_radians = pi * ((_g_range_max) - _g_threshold_value) / _g_range_max
r = 0.6
dx = r * cos(threshold_radians)
dy = r * sin(threshold_radians)
fig_gauge.add_annotation(
     x=0.5+dx
    ,y=0.08+dy
    ,xref='paper', yref='paper'
    ,text=_g_threshold_label + "：" + str(_g_threshold_value) +"%"
    ,font=dict(size=16,color=_g_threshold_color)
    ,showarrow=False
)
fig_gauge.update_layout( paper_bgcolor = "lavender"
                        ,font={'color': "darkblue", 'family': "Arial"}
                        ,height=340)
# ゲージチャート描画
col1.plotly_chart(fig_gauge, use_container_width=True)


# 円グラフ
##（セグメント別売上）
col1.subheader('円グラフ')
### グラフ設定
sales_info_by_segments = get_sales_info_by_segments(selected_segment_ids, const_nendo_latest)
fig_pie = go.Figure(data=[
                          go.Pie(labels=sales_info_by_segments['セグメント名']
                                ,values=sales_info_by_segments['売上高[百万円]']
                                ,hole=.3)
                  ])
fig_pie.update_layout(title="セグメント別売上（最新年度）"
                      ,showlegend=False
                      ,height=400)
fig_pie.update_traces(textposition="inside"
                                    , textinfo="label+percent")
### グラフ描画
col1.plotly_chart(fig_pie, use_container_width=True)


# 棒＋折れ線グラフ
## 全社　営業利益、営業利益率
col3.subheader('棒＋折れ線グラフ')
profit_sales_info_all = get_profit_sales_info_allsegments(selected_segment_ids, selected_nendo)
#profit_sales_info_all = get_profit_info_by_segments_and_nendo(selected_segment_ids, selected_nendo)

fig_bl = go.Figure()
fig_bl.add_trace(go.Bar(x=profit_sales_info_all["年度"]
                       ,y=profit_sales_info_all["営業利益[百万円]"]
                       ,width=0.5
                       ,name="営業利益"
                       ,yaxis="y1"))
fig_bl.add_trace(go.Scatter(x=profit_sales_info_all["年度"]
                            ,y=profit_sales_info_all["営業利益率"]
                            ,name="営業利益率"
                            ,yaxis="y2"))
fig_bl.update_layout(title="営業利益と営業利益率の推移"
                     ,height=400
                     ,yaxis1=dict(side="left", title="営業利益[百万円]")
                     ,yaxis2=dict(side="right",title="営業利益率",tickformat=".1%",range=(0,0.1),overlaying="y")
                     )
### グラフ描画
col3.plotly_chart(fig_bl, use_container_width=True)


# 積み上げ棒グラフ
##（セグメント別売上）
col3.subheader('積み上げ棒グラフ')
### グラフ設定
sales_info_by_segments_and_nendo = get_sales_info_by_segments_and_nendo(selected_segment_ids, selected_nendo)
fig_bar = px.bar(sales_info_by_segments_and_nendo, x="年度", y="売上高[百万円]", color="セグメント名")
fig_bar.update_layout(title="セグメント別売上の推移"
                      ,showlegend=False, height=400)
### グラフ描画
col3.plotly_chart(fig_bar, use_container_width=True)



# セグメント別営業利益
st.subheader("地図")
st.write("セグメント別営業利益  ")
profit_info_by_segments = get_sales_profit_info_by_segments_and_nendo(selected_segment_ids, const_nendo_latest)

# マップ用のDataframe
map_columns = ["セグメントID","セグメント名","latitude","longitude","color"]
map_index = ["A01","A02","A03","A04","A05"]
map_list = [["A01","日本",35.689634,139.692101,'#ff0088']
           ,["A02","北米",38.895450,-77.015870,'#aaaa00']
           ,["A03","欧州",51.504827,-0.078626,'#0000ff']
           ,["A04","アジア",1.306704,103.843100,'#118888']
           ,["A05","その他",1.328054,172.977292,'#777777']
             ]
df_map = pd.DataFrame(data=map_list, index=map_index, columns=map_columns)

#営業利益データにセグメント毎の経度緯度、色情報を追加
df_map_data = profit_info_by_segments.merge(df_map, on=["セグメントID"], how="outer")
#st.write(df_map_data)


#st.map(
#    df_map_data
#    ,latitude="latitude"
#    ,longitude="longitude"
#    ,size="営業利益-マップ用"
#    ,color="color"
#    ,zoom=0
#    ,use_container_width=True
#)

# マップ（folium）
## 基本設定
#st.write("【folium版】")
m = folium.Map(
     attr='セグメント別営業利益'
    ,zoom_start=2
    ,tiles="OpenStreetMap"
#    ,tiles="Stamen Watercolor"
#    ,tiles='https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png'
    # 地図の中心設定
#    ,location=[35.689634,139.692101] # 東京
    ,location=[35.0,125.0] # いい感じに全データが見えるところ
)

## マップに円形マーカー表示
for i, row in df_map_data.iterrows():
    ### ポップアップ
    pop=f"セグメント：{row['セグメント名']}<br> (営業利益：{row['営業利益[百万円]']} 百万円)"
    folium.CircleMarker(
        # 緯度と経度
         location=[row['latitude'], row['longitude']]
        # 円
        ,radius=row['営業利益-マップ用']
        # ポップアップ
        ,popup=folium.Popup(pop, max_width=300)
        # 色
        ,color=row['color']
        ,fill_color=row['color']
    ).add_to(m)

st_data = st_folium(m, width=1200, height=600)

# バブルチャート
# 3つのデータの関係性を一つのグラフで見ることができる
st.subheader("バブルチャート")
#st.write("セグメント別、営業利益率、売上前年比")

# データ生成
# 今年度売上、営業利益率
_df_sales_prof_info_latest = get_sales_profit_info_by_segments_and_nendo(selected_segment_ids, const_nendo_latest)
_df_sales_prof_info_latest.drop(columns=['セグメント名_y','営業利益-マップ用'], inplace=True)
_df_sales_prof_info_latest.rename(columns={ '年度':'年度_latest'
                                           ,'営業利益[百万円]':'営業利益[百万円]_latest'
                                           ,'売上高[百万円]':'売上高[百万円]_latest'
                                           ,'営業利益率':'営業利益率_latest'
                                           ,'セグメント名_x':'セグメント名'
                                           }, inplace=True)

# 前年度売上
_df_sales_prof_info_previous = get_sales_profit_info_by_segments_and_nendo(selected_segment_ids, const_nendo_previous)
_df_sales_prof_info_previous.drop(columns=['セグメント名_y','セグメント名_x','営業利益-マップ用'], inplace=True)
_df_sales_prof_info_previous.rename(columns={ '年度':'年度_previous'
                                           ,'営業利益[百万円]':'営業利益[百万円]_previous'
                                           ,'売上高[百万円]':'売上高[百万円]_previous'
                                           ,'営業利益率':'営業利益率_previous'
                                           }, inplace=True)

# 今年度の情報に、前年度売上の列を追加
_df_bubble_chart = _df_sales_prof_info_latest.merge(_df_sales_prof_info_previous, on=["セグメントID"], how="outer")

# 今年度の情報に、前年度売上との差額の列を追加
_df_bubble_chart["売上高[百万円]_前年比"] = _df_bubble_chart.apply(lambda x: x['売上高[百万円]_latest'] - x['売上高[百万円]_previous'], axis=1)


fig_bubble = px.scatter(_df_bubble_chart
                        ,y="売上高[百万円]_前年比"
                        ,x="営業利益率_latest"
                        ,size="売上高[百万円]_latest"
                        ,color="セグメント名"
                        ,hover_name="セグメント名"
                        ,size_max=60
                        )
fig_bubble.update_layout(
    title="セグメント別 営業利益率、売上高前年比"
    ,width=1200
    ,xaxis=dict(title='営業利益率 [%]'
               ,showline=True
               ,tickformat=".0%"
               ,ticks="inside"
               ,ticklen=5
               ,tickwidth=2
               ,tickcolor="lightgrey"
               )
    ,yaxis=dict(title='売上高（前年比）[百万円]'
               ,showline=True
               ,side="bottom"
               ,tickformat=","
               ,ticks="inside"
               ,ticklen=5
               ,tickwidth=2
               ,tickcolor="lightgrey"
                )
)
#fig_bubble.update_xaxes(
#    tick0=0
#    ,dtick=1000000
#)
st.write(fig_bubble)
