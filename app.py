import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(layout="wide")

st.title("⚾ 打擊數據系統")

DATA_FILE="data.csv"
USER_FILE="users.csv"


# ========= 管理員 =========

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
# ⭐ 登入 / 註冊
# ======================

mode=st.sidebar.radio("帳號",["登入","註冊"])


# ========= 註冊 =========

if mode=="註冊":

    st.header("建立帳號")

    acc=st.text_input("帳號")

    pw=st.text_input("密碼",type="password")

    real=st.text_input("姓名")

    team_reg=st.text_input("球隊")

    num_reg=st.number_input("背號",0)

    if st.button("建立帳號"):

        if acc in user_df["帳號"].values:

            st.error("帳號已存在")

        else:

            new=pd.DataFrame([{

"帳號":acc,
"密碼":pw,
"姓名":real.strip(),
"球隊":team_reg,
"背號":num_reg

}])

            user_df=pd.concat(
                [user_df,new],
                ignore_index=True)

            user_df.to_csv(USER_FILE,index=False)

            st.success("✅ 註冊成功")

    st.stop()



# ========= 登入 =========

st.sidebar.header("登入")

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


df["姓名"]=df["姓名"].astype(str).str.strip()

df=df.fillna(0)



# ======================
# ⭐ ADMIN 帳號管理
# ======================

if IS_ADMIN:

    st.header("👤 帳號管理")

    st.dataframe(
        user_df[["帳號","姓名","球隊","背號"]],
        use_container_width=True
    )

    delete_acc=st.selectbox(
        "刪除帳號",
        user_df["帳號"]
    )

    if st.button("❌ 刪除帳號"):

        if delete_acc=="admin":

            st.warning("不能刪admin")

        else:

            delete_name=str(
            user_df[
            user_df["帳號"]==delete_acc
            ].iloc[0]["姓名"]
            ).strip()

            user_df=user_df[
            user_df["帳號"]!=delete_acc
            ]

            user_df.to_csv(USER_FILE,index=False)

            df=df[
            df["姓名"]!=delete_name
            ]

            df.to_csv(DATA_FILE,index=False)

            st.success(f"{delete_name}帳號與全部紀錄已刪除")

            st.rerun()



# ======================
# ADMIN全部球員
# ======================

if IS_ADMIN and not df.empty:

    st.header("🏆 後台全部球員")

    summary=df.groupby(
["球隊","背號","姓名"],
as_index=False
).sum(numeric_only=True)

    st.dataframe(
summary.sort_values("安打",ascending=False),
use_container_width=True)



# ======================
# 新增紀錄
# ======================

st.header("新增比賽紀錄")

c1,c2,c3=st.columns(3)

with c1:

    opponent=st.text_input("對戰球隊")

    pitcher=st.selectbox(
        "投手",
        ["左投","右投"]
    )

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
# 累積統計
# ======================

st.header("📊 累積統計")

player_df=df if IS_ADMIN else df[df["姓名"]==name]

if not player_df.empty:

    total=player_df.sum(numeric_only=True)

    TB=(
total["1B"]
+total["2B"]*2
+total["3B"]*3
+total["HR"]*4)

    AVG=round(total["安打"]/total["打數"],3) if total["打數"]>0 else 0

    OBP=round(
(total["安打"]+total["BB"])/
(total["打數"]+total["BB"]+total["SF"])
,3) if (total["打數"]+total["BB"]+total["SF"])>0 else 0

    SLG=round(TB/total["打數"],3) if total["打數"]>0 else 0

    OPS=round(OBP+SLG,3)

    m1,m2,m3,m4=st.columns(4)

    m1.metric("打席",int(total["打席"]))
    m2.metric("安打",int(total["安打"]))
    m3.metric("AVG",AVG)
    m4.metric("OPS",OPS)



# ======================
# ⭐ 單場紀錄（可刪）
# ======================

st.header("📅 單場比賽紀錄")

if player_df.empty:

    st.info("目前沒有紀錄")

else:

    show_df=player_df.sort_values(
        "日期",
        ascending=False)

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

                if not IS_ADMIN:

                    if df.loc[idx,"姓名"]!=name:

                        st.warning("只能刪自己的")

                        st.stop()

                df=df.drop(idx)

                df.to_csv(DATA_FILE,index=False)

                st.success("刪除成功")

                st.rerun()



# ======================
# Excel統計
# ======================

st.divider()

st.header("📊 總數據統計")

summary=player_df.groupby(
["球隊","背號","姓名"],
as_index=False
).sum(numeric_only=True)

st.dataframe(summary,use_container_width=True)

