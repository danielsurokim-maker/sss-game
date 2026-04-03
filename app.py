import streamlit as st
import random
import pandas as pd
import json
import os

st.set_page_config(layout="wide")

# ---------------------------
# 저장/불러오기
# ---------------------------
def save_game(user_id):
    data = dict(st.session_state)
    with open(f"{user_id}.json", "w") as f:
        json.dump(data, f)

def load_game(user_id):
    if os.path.exists(f"{user_id}.json"):
        with open(f"{user_id}.json") as f:
            data = json.load(f)
            for k, v in data.items():
                st.session_state[k] = v

# ---------------------------
# 로그인
# ---------------------------
if "login" not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("🔐 SSS Game Login")

    user_id = st.text_input("ID 입력 (아무거나 가능)")

    if st.button("시작"):
        st.session_state.user_id = user_id
        load_game(user_id)
        st.session_state.login = True
        st.rerun()

    st.stop()

# ---------------------------
# 초기화
# ---------------------------
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.stage = "decision"

    st.session_state.year = 2025
    st.session_state.quarter = 1

    st.session_state.cash = 10000
    st.session_state.debt = 0

    st.session_state.tech = 1.0
    st.session_state.yield_rate = 0.7
    st.session_state.capacity = 100
    st.session_state.inventory = 20
    st.session_state.reputation = 50

    st.session_state.history = []

# ---------------------------
# 경쟁사
# ---------------------------
def competitor_price(player_price):
    if player_price < 90:
        return 80
    return 95

# ---------------------------
# 고객사 수주
# ---------------------------
def win_apple(price, tech, reputation):
    score = tech * 0.4 + reputation * 0.3 - price * 0.3
    return score > random.uniform(0, 50)

# ---------------------------
# 이벤트
# ---------------------------
def get_event():
    events = [
        ("🔥 반도체 Shortage", 1.3),
        ("❄️ 경기 침체", 0.8),
        ("⏳ 개발 지연", 0.9),
    ]
    return random.choice(events)

# ---------------------------
# UI 상단
# ---------------------------
st.title(f"📱 SSS Game V4 - {st.session_state.user_id}")

st.write(f"{st.session_state.year}년 Q{st.session_state.quarter}")
st.write(f"💰 Cash: {st.session_state.cash} | 💸 Debt: {st.session_state.debt}")

st.divider()

# ---------------------------
# 의사결정
# ---------------------------
if st.session_state.stage == "decision":

    st.header("📊 전략 선택")

    rd_choice = st.radio("R&D", ["보수(500)", "균형(1000)", "공격(2000)"])
    capex_choice = st.radio("CAPEX", ["축소(500)", "유지(1000)", "확대(2000)"])
    price_choice = st.radio("가격", ["프리미엄(120)", "균형(100)", "덤핑(80)"])

    if st.button("결정"):
        st.session_state.rd_choice = rd_choice
        st.session_state.capex_choice = capex_choice
        st.session_state.price_choice = price_choice
        st.session_state.stage = "result"

# ---------------------------
# 결과
# ---------------------------
elif st.session_state.stage == "result":

    rd_map = {"보수(500)": 500, "균형(1000)": 1000, "공격(2000)": 2000}
    capex_map = {"축소(500)": 500, "유지(1000)": 1000, "확대(2000)": 2000}
    price_map = {"프리미엄(120)": 120, "균형(100)": 100, "덤핑(80)": 80}

    rd = rd_map[st.session_state.rd_choice]
    capex = capex_map[st.session_state.capex_choice]
    price = price_map[st.session_state.price_choice]

    # 이벤트
    event, demand_mult = get_event()
    st.success(event)

    # 투자
    st.session_state.cash -= (rd + capex)

    # 기술
    st.session_state.tech += rd * 0.0005
    st.session_state.yield_rate += rd * 0.0001

    # 생산
    production = int(st.session_state.capacity * st.session_state.yield_rate)

    # 고객사 수주
    apple_win = win_apple(price, st.session_state.tech, st.session_state.reputation)

    if apple_win:
        demand = 150
        st.success("🍎 Apple 수주 성공!")
    else:
        demand = 80
        st.warning("❌ Apple 수주 실패")

    demand = int(demand * demand_mult)

    # 판매
    sales = min(production + st.session_state.inventory, demand)

    # 재고
    st.session_state.inventory = production + st.session_state.inventory - sales

    # 재고 리스크
    if st.session_state.inventory > 100:
        st.session_state.cash -= 500
        st.error("📦 재고 손실 발생!")

    # 매출
    revenue = sales * price
    cost = production * 60
    op_profit = revenue - cost

    st.session_state.cash += op_profit

    # 차입
    if st.session_state.cash < 0:
        st.session_state.debt += 2000
        st.session_state.cash += 2000
        st.warning("💸 자동 대출 발생")

    # 이자
    interest = int(st.session_state.debt * 0.05)
    st.session_state.cash -= interest

    st.write(f"매출: {revenue}")
    st.write(f"영업이익: {op_profit}")
    st.write(f"이자: {interest}")

    # 저장
    save_game(st.session_state.user_id)

    if st.button("다음"):
        st.session_state.quarter += 1
        if st.session_state.quarter > 4:
            st.session_state.quarter = 1
            st.session_state.year += 1

        st.session_state.stage = "decision"

# ---------------------------
# 게임오버
# ---------------------------
if st.session_state.cash <= -5000:
    st.error("💀 파산! 게임 종료")
