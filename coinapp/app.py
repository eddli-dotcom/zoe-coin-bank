import streamlit as st
import json
import os
import random
import time
from datetime import datetime
import base64
import mimetypes

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Zoe's Coin Bank", page_icon="💰", layout="centered")

# --- 2. 徹底封鎖深色模式 + 金幣動態特效 CSS ---
st.markdown("""
<style>
    .stApp { background-color: #fffaf0 !important; }
    html, body, p, h1, h2, h3, h4, span, label, div { color: #333333 !important; }

    .zoe-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 0; }
    .zoe-circular { width: 160px; height: 160px; border-radius: 50%; object-fit: cover; border: none !important; display: block; box-shadow: 0 0 20px rgba(255, 215, 0, 0.4) !important; }

    @keyframes coin-pulse {
        0% { transform: scale(1); text-shadow: 0 0 5px rgba(255,215,0,0.2); }
        50% { transform: scale(1.08); text-shadow: 0 0 20px rgba(255,215,0,0.8); }
        100% { transform: scale(1); text-shadow: 0 0 5px rgba(255,215,0,0.2); }
    }
    .animated-coins { animation: coin-pulse 2s infinite ease-in-out; display: inline-block; }

    div.stButton > button {
        background-color: #ffffff !important; color: #B8860B !important; border: 2px solid #FFD700 !important;
        border-radius: 14px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        font-weight: bold !important; font-size: 1rem !important; height: 45px !important; transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    div.stButton > button:active {
        transform: scale(0.92) !important; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #ffffff !important; box-shadow: 0 0 15px rgba(255, 165, 0, 0.6) !important;
    }

    div[data-testid="stSelectbox"] > div, div[data-testid="stTextInput"] > div, div[data-testid="stNumberInput"] > div {
        background-color: #ffffff !important; border: 2px solid #FFD700 !important; border-radius: 12px !important;
    }
    div[data-testid="stSelectbox"] *, div[data-baseweb="select"] * { color: #333333 !important; background-color: #ffffff !important; }

    div[data-testid="stTabs"] button[role="tab"] { flex: 1 1 auto; padding: 10px 2px !important; }
    div[data-testid="stTabs"] button[role="tab"] p { font-size: 15px !important; font-weight: 800; color: #B8860B !important; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] { background-color: #FFD700 !important; border-radius: 12px 12px 0 0; }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] p { color: #fffaf0 !important; }

    .coin-badge {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); color: white !important; padding: 4px 10px;
        border-radius: 20px; font-weight: bold; font-size: 1rem; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); display: inline-block; margin-left: 8px;
    }
    .chore-name { font-size: 1.1rem; font-weight: bold; color: #2c3e50 !important; }

    .metric-container {
        background: white; padding: 15px; border-radius: 15px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 8px 16px rgba(255,215,0,0.15);
    }
    .goal-text { text-align: center; font-size: 1.2rem; font-weight: 800; color: #B8860B !important; }
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #FFD700 0%, #FDB931 100%); }

    /* 轉盤動畫文字區塊 */
    .spin-box {
        background: linear-gradient(135deg, #FFD700 0%, #FDB931 100%);
        color: white !important; font-size: 2rem; font-weight: bold; text-align: center;
        padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(255,215,0,0.5);
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 數據庫初始化 ---
DATA_FILE = "coin_data_v4.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"老公": 0, "老婆": 0, "history": [], "goal_name": "吃頓好的 Omakase", "goal_target": 200}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

app_data = load_data()
ZOE_PRAISES = ["Zoe 開心地轉了三個圈圈！🐾", "Zoe 給你一個超萌的燦笑！🐶✨", "Zoe 跑過來瘋狂搖尾巴！❤️", "Zoe 覺得你是世界上最棒的主人！👑", "金幣叮噹響，Zoe 給你一個大大的擁抱！🪙", "Zoe 用崇拜的眼神看著你！👀✨"]

# --- 4. 頂部視覺：置中 Zoe 本尊相片 (終極雲端路徑相容版) ---
st.markdown('<div class="zoe-container">', unsafe_allow_html=True)
possible_photos = ["zoe.png", "zoe.jpg", "zoe.jpeg", "ZOE.JPG", "zoe.JPG", "ZOE.PNG"]
found_photo = None

# 獲取目前 app.py 所在的絕對資料夾路徑
current_dir = os.path.dirname(__file__)

for photo in possible_photos:
    # 組合出絕對路徑，確保雲端伺服器 100% 找得到
    full_path = os.path.join(current_dir, photo)
    if os.path.exists(full_path):
        found_photo = full_path
        break

if found_photo:
    try:
        with open(found_photo, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        mime_type, _ = mimetypes.guess_type(found_photo)
        st.markdown(f'<img src="data:{mime_type or "image/png"};base64,{encoded_string}" class="zoe-circular">', unsafe_allow_html=True)
        st.markdown('<p style="color:#B8860B; font-weight:bold; margin-top:10px; font-size:1.1rem;">🐾 首席金幣監督員：Zoe 🐾</p>', unsafe_allow_html=True)
    except Exception as e:
        st.caption(f"圖片載入失敗: {e}")
else:
    # 如果還是找不到，把伺服器當前的目錄結構印出來，方便除錯
    st.image("https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400&q=80", width=160)
    st.caption("⚠️ 雲端找不到 zoe.png，請確認照片與 app.py 放在同一個資料夾內。")

# --- 5. 總分儀表板 (加入動態呼吸燈) ---
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""<div class="metric-container">
        <p style="margin:0; font-size:0.95rem; color:#666 !important; font-weight:bold;">🏦 👨 老公專屬金庫</p>
        <h2 class="animated-coins" style="margin:0; color:#B8860B !important;">🪙 {app_data['老公']}</h2>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""<div class="metric-container">
        <p style="margin:0; font-size:0.95rem; color:#666 !important; font-weight:bold;">🏦 👩 老婆專屬金庫</p>
        <h2 class="animated-coins" style="margin:0; color:#B8860B !important;">🪙 {app_data['老婆']}</h2>
    </div>""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- 6. 共同目標 ---
total_coins = app_data["老公"] + app_data["老婆"]
st.markdown(f'<p class="goal-text">🎯 終極大賞：{app_data["goal_name"]} 🎯</p>', unsafe_allow_html=True)
st.progress(min(total_coins / app_data["goal_target"], 1.0), text=f"💰 財富累積：{total_coins} / {app_data['goal_target']} 🪙")
st.divider()

# --- 7. 功能分頁 ---
tab1, tab2, tab3, tab4 = st.tabs(["💰 賺金幣", "🎲 抽籤", "🎯 目標", "📜 存摺"])
CHORES = {"🐶 放狗 (Zoe)": 4, "🧼 擦狗": 3, "🍚 喂狗吃飯": 1, "🪥 幫狗刷牙": 3, "✂️ 剪指甲": 7, "👕 洗衣服": 2, "🧺 收晾衣服": 2, "🗑️ 扔垃圾": 2, "🫖 煲水": 1, "🧹 拖/掃地": 4, "🚽 洗厠所": 10, "🛁 洗浴缸": 5, "🏠 收拾家居": 4, "🛍️ 買菜/飯": 4}

def handle_chore_completion(person, chore, coins):
    app_data[person] += coins
    app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": chore, "coins": coins})
    save_data(app_data)
    st.toast(f"入帳 {coins} 幣！{random.choice(ZOE_PRAISES)}", icon="🪙")
    if coins >= 5: st.balloons()

with tab1:
    for chore, coins in CHORES.items():
        c_name, c_h, c_w = st.columns([2.2, 1, 1])
        c_name.markdown(f"<span class='chore-name'>{chore}</span> <span class='coin-badge'>+{coins}</span>", unsafe_allow_html=True)
        if c_h.button("👨 我做", key=f"h_{chore}", use_container_width=True):
            handle_chore_completion("老公", chore, coins)
            st.rerun()
        if c_w.button("👩 我做", key=f"w_{chore}", use_container_width=True):
            handle_chore_completion("老婆", chore, coins)
            st.rerun()
        st.markdown("<hr style='border:none; border-top:1px dashed #FFD700; margin:10px 0;'>", unsafe_allow_html=True)

# [分頁 2：命運轉盤動畫版]
with tab2:
    st.markdown("<p style='font-weight:bold; color:#B8860B !important;'>不知道誰該去？讓 Zoe 幫你們選：</p>", unsafe_allow_html=True)
    chore_to_draw = st.selectbox("", list(CHORES.keys()), label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🎰 啟動命運金幣轉盤", use_container_width=True):
        # 1. 建立一個空的佔位符用來播放動畫
        wheel_placeholder = st.empty()
        options = ["👨 老公", "👩 老婆"]
        
        # 2. 模擬轉盤動畫 (跑馬燈效果)
        sleep_time = 0.03 # 初始旋轉速度 (很快)
        for i in range(25): # 總共跳動 25 次
            current_focus = options[i % 2]
            # 渲染閃爍的黃金卡片
            wheel_placeholder.markdown(f"""
            <div class="spin-box">
                🌀 轉盤旋轉中...<br><span style="font-size:3rem;">{current_focus}</span>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(sleep_time)
            sleep_time += 0.012 # 每次迴圈增加等待時間，產生「減速」的物理阻力感
            
        # 3. 動畫結束，抽出最終結果
        winner = random.choice(options)
        
        # 清除轉盤動畫
        wheel_placeholder.empty()
        
        # 顯示最終結果並噴發氣球
        st.error(f"🎉 叮叮叮！ Zoe 的肉墊停在了...\n\n### {winner}！\n快去執行【{chore_to_draw}】吧！")
        st.balloons()

with tab3:
    st.markdown("<p style='font-weight:bold;'>👑 終極大賞名稱：</p>", unsafe_allow_html=True)
    new_goal = st.text_input("Goal Name", value=app_data["goal_name"], label_visibility="collapsed")
    st.markdown("<p style='font-weight:bold;'>💰 兌換所需金幣：</p>", unsafe_allow_html=True)
    new_target = st.number_input("Goal Target", min_value=10, value=app_data["goal_target"], label_visibility="collapsed")
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 鎖定金庫目標", use_container_width=True):
        app_data["goal_name"] = new_goal
        app_data["goal_target"] = new_target
        save_data(app_data)
        st.success("銀行目標已更新！大家一起努力賺金幣！💰")
        st.rerun()

with tab4:
    if app_data["history"]:
        for i, r in enumerate(app_data["history"][:30]):
            col_text, col_undo = st.columns([3.8, 1.4])
            icon = "👨" if r["person"] == "老公" else "👩"
            col_text.markdown(f"<span style='color:#888; font-size:0.8rem;'>{r['time']}</span><br><span style='color:#333 !important;'>{icon} **{r['person']}** 完成了 {r['chore']}</span> <span style='color:#B8860B; font-weight:bold;'>🪙 +{r['coins']}</span>", unsafe_allow_html=True)
            if col_undo.button("退回 💸", key=f"del_{i}", use_container_width=True):
                app_data[r['person']] -= r['coins']
                app_data["history"].pop(i)
                save_data(app_data)
                st.rerun()
            st.markdown("<div style='border-bottom:1px solid #eee; margin-bottom:10px;'></div>", unsafe_allow_html=True)
    else:
        st.write("金庫目前空空如也，快去賺金幣吧！")
