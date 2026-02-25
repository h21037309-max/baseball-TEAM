import streamlit as st
import pandas as pd
from datetime import datetime
import os
import uuid

st.set_page_config(layout="wide")

st.title("⚾ 打擊數據系統 V9.5")

DATA_FILE="data.csv"
USER_FILE="users.csv"

ADMINS=["洪仲平","楊振銓","張管理員"]


# ======================
# users 初始化
# ======================

if not os.path.exists(USER_FILE):

    pd.DataFrame([{

"帳號":"admin",
"密碼":"admin123",
"姓名":"洪仲平",
"球隊":"ADMIN",
"背號":0

}]).to_csv(USER_FILE,index=False)


user_df=pd.read_csv(USER_FILE)


# ======================
# 登入 / 註冊
# ======================

mode=st.sidebar.radio("帳號",["登入","註冊"])

if mode=="註冊":

    st.header("建立帳號")

    acc=st.text_input("帳號")

    pw=st.text_input("密碼",type="password")

    real=st.text_input("姓名")

    team_reg=st.text_input("球隊")

    num_reg=st.number_input("背號",0)

    if st.button("建立帳號"):

        if acc in user_df["帳號"].values:

            st.error("帳號存在")

        else:

            new=pd.DataFrame([{

"帳號":acc,
"密碼":pw,
"姓名":real.strip(),
"球隊":team_reg,
"背號":num_reg

}])

            user_df=pd.concat([user_df,new])

            user_df.to_csv(USER_FILE,index=False)

            st.success("註冊成功")

    st.stop()


username=st.sidebar.text_input("帳號")

password=st.sidebar.text_input("密碼",type="password")

login=user_df[
(user_df["帳號"]==username)&
(user_df["密碼"]==password)
]

if login.empty:

    st.warning("請登入")

    st.stop()


login_name=str(login.iloc[0]["姓名"]).strip()

IS_ADMIN=login_name in ADMINS


# ======================
# CSV
# ======================

columns=[

"紀錄ID","日期","球隊","背號","姓名",
"對戰球隊","投手",
"打席","打數","得分","打點","安打",
"1B","2B","3B","HR",
"BB","SF","SH","SB"

]

df=pd.read_csv(DATA_FILE) if os.path.exists(DATA_FILE) else pd.DataFrame(columns=columns)

df=df.fillna(0)

df["姓名"]=df["姓名"].astype(str).str.strip()


# ======================
# ADMIN 排行榜
# ======================

if IS_ADMIN and not df.empty:

    st.header("🏆 全隊排行榜")

    summary=df.groupby(
["球隊","背號","姓名"],
as_index=False).sum(numeric_only=True)

    TB=summary["1B"]+summary["2B"]*2+summary["3B"]*3+summary["HR"]*4

    summary["打擊率"]=(summary["安打"]/summary["打數"]).round(3)

    summary["上壘率"]=(
(summary["安打"]+summary["BB"])/
(summary["打數"]+summary["BB"]+summary["SF"])
).round(3)

    summary["長打率"]=(TB/summary["打數"]).round(3)

    summary["OPS"]=(summary["上壘率"]+summary["長打率"]).round(3)

    st.dataframe(
summary.sort_values("OPS",ascending=False),
use_container_width=True)



# ======================
# ADMIN 選球員查看
# ======================

if IS_ADMIN:

    select_player=st.selectbox(

"查看球員",

["全部球員"]+
sorted(user_df["姓名"].tolist())

)

else:

    select_player=login_name



player_df=df if select_player=="全部球員" else df[df["姓名"]==select_player]


# ======================
# 新增紀錄
# ======================

st.header("新增比賽紀錄")

record_name=login_name

team_default=login.iloc[0]["球隊"]

number_default=int(login.iloc[0]["背號"])


if IS_ADMIN:

    player_select=st.selectbox("新增給球員",user_df["姓名"])

    info=user_df[user_df["姓名"]==player_select].iloc[0]

    record_name=player_select

    team_default=info["球隊"]

    number_default=int(info["背號"])



c1,c2,c3=st.columns(3)

with c1:

    opponent=st.text_input("對戰球隊")

    pitcher=st.selectbox("投手",["左投","右投"])

with c2:

    PA=st.number_input("打席",0)

    AB=st.number_input("打數",0)

    H=st.number_input("安打",0)

with c3:

    HR=st.number_input("HR",0)

    BB=st.number_input("BB",0)



if st.button("新增紀錄"):

    new=pd.DataFrame([{

"紀錄ID":str(uuid.uuid4()),

"日期":datetime.now().strftime("%Y-%m-%d"),

"球隊":team_default,

"背號":number_default,

"姓名":record_name,

"對戰球隊":opponent,

"投手":pitcher,

"打席":PA,

"打數":AB,

"安打":H,

"HR":HR,

"BB":BB

}])

    df=pd.concat([df,new])

    df.to_csv(DATA_FILE,index=False)

    st.rerun()



# ======================
# 個人累積
# ======================

st.header("📊 個人累積統計")

if not player_df.empty:

    total=player_df.sum(numeric_only=True)

    AB=total["打數"]

    H=total["安打"]

    TB=total["HR"]*4

    AVG=round(H/AB,3) if AB>0 else 0

    OPS=round(TB/AB,3) if AB>0 else 0

    c1,c2,c3=st.columns(3)

    c1.metric("打席",int(total["打席"]))

    c2.metric("安打",int(H))

    c3.metric("打擊率",AVG)



# ======================
# 單場紀錄
# ======================

st.header("📅 單場紀錄")

for _,row in player_df.sort_values("日期",ascending=False).iterrows():

    colA,colB=st.columns([9,1])

    with colA:

        st.markdown(

f"📅 {row['日期']} ｜ {row['姓名']} H {int(row['安打'])}"

)

    with colB:

        if st.button("❌",key=row["紀錄ID"]):

            df=df[df["紀錄ID"]!=row["紀錄ID"]]

            df.to_csv(DATA_FILE,index=False)

            st.rerun()
