import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")

st.title("⚾ 打擊數據系統")

DATA_FILE="data.csv"
USER_FILE="users.csv"


# ======================
# ADMIN
# ======================

ADMINS=[

"洪仲平",
"楊振銓",
"張管理員"

]


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
# 登入
# ======================

username=st.sidebar.text_input("帳號")

password=st.sidebar.text_input("密碼",type="password")

login=user_df[
(user_df["帳號"]==username)&
(user_df["密碼"]==password)
]

if login.empty:

    st.warning("請登入")

    st.stop()


name=str(login.iloc[0]["姓名"]).strip()

team_default=login.iloc[0]["球隊"]

number_default=int(login.iloc[0]["背號"])

IS_ADMIN=name in ADMINS



# ======================
# CSV
# ======================

columns=[

"日期","球隊","背號","姓名",
"對戰球隊","投手",
"打席","打數","得分","打點","安打",
"1B","2B","3B","HR",
"BB","SF","SH","SB"

]

if os.path.exists(DATA_FILE):

    df=pd.read_csv(DATA_FILE)

else:

    df=pd.DataFrame(columns=columns)


for c in columns:

    if c not in df.columns:

        df[c]=0


# ⭐⭐⭐⭐⭐ 超重要

df["姓名"]=df["姓名"].astype(str).str.strip()

df=df.fillna(0)



# ======================
# 新增紀錄
# ======================

st.header("新增比賽紀錄")

c1,c2,c3=st.columns(3)

with c1:

    opponent=st.text_input("對戰球隊")

    pitcher=st.selectbox("投手",["左投","右投"])

with c2:

    PA=st.number_input("打席",0)

    AB=st.number_input("打數",0)

    R=st.number_input("得分",0)

    RBI=st.number_input("打點",0)

    H=st.number_input("安打",0)

with c3:

    single=st.number_input("1B",0)

    double=st.number_input("2B",0)

    triple=st.number_input("3B",0)

    HR=st.number_input("HR",0)

    BB=st.number_input("BB",0)

    SF=st.number_input("SF",0)

    SH=st.number_input("SH",0)

    SB=st.number_input("SB",0)



if st.button("新增紀錄"):

    today=datetime.now().strftime("%Y-%m-%d")

    new=pd.DataFrame([{

"日期":today,
"球隊":team_default,
"背號":number_default,
"姓名":name,

"對戰球隊":opponent,
"投手":pitcher,

"打席":PA,
"打數":AB,
"得分":R,
"打點":RBI,
"安打":H,

"1B":single,
"2B":double,
"3B":triple,
"HR":HR,

"BB":BB,
"SF":SF,
"SH":SH,
"SB":SB

}])

    df=pd.concat([df,new],ignore_index=True)

    df.to_csv(DATA_FILE,index=False)

    st.success("新增成功")



# ======================
# ⭐⭐⭐⭐⭐ 單場紀錄
# ======================

st.header("📅 單場比賽紀錄")


if IS_ADMIN:

    player_df=df.copy()

else:

    player_df=df[
    df["姓名"].astype(str).str.strip()==name
    ]


# ⭐ 沒資料提示

if player_df.empty:

    st.info("目前沒有比賽紀錄")

else:

    show_df=player_df.sort_values(
        "日期",
        ascending=False
    )

    for idx,row in show_df.iterrows():

        colA,colB=st.columns([9,1])

        with colA:

            st.markdown(f"""

### 📅 {row['日期']} ｜ {row['球隊']} #{int(row['背號'])} {row['姓名']}

vs {row['對戰球隊']} ｜ {row['投手']}

PA {int(row['打席'])} ｜ AB {int(row['打數'])} ｜ H {int(row['安打'])}

RBI {int(row['打點'])} ｜ R {int(row['得分'])}

1B {int(row['1B'])} ｜ 2B {int(row['2B'])} ｜ 3B {int(row['3B'])} ｜ HR {int(row['HR'])}

BB {int(row['BB'])} ｜ SF {int(row['SF'])} ｜ SH {int(row['SH'])} ｜ SB {int(row['SB'])}

---
""")

        with colB:

            if st.button("❌",key=f"del{idx}"):

                df=df.drop(idx)

                df.to_csv(DATA_FILE,index=False)

                st.success("刪除成功")

                st.rerun()