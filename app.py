import streamlit as st
import random
import pandas as pd

st.set_page_config(layout="wide")

# ---------------------------
# 초기화
# ---------------------------
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.stage = "decision"

    st.session_state.year = 2025
    st.session_state.quarter = 1

    st.session_state.cash = 10000
    st.session_state.tech = 1.0
    st.session_state.yield_rate = 0.7
    st.session_state.capacity = 100
    st.session_state.inventory = 20
    st.session_state.reputation = 50

    st.session_state.history = []

# ---------------------------
# 경쟁사 (간단)
# ---------------------------
competitors = {
    "BOE": {"price": 90},
    "LG Display": {"price": 100}
}

# ---------------------------
# 이벤트
# ---------------------------
def get_event():
    events = [
        ("🔥 반도체 Shortage", 1.3, 1.0),
        ("❄️ 경기 침체", 0.8, 0.9),
        ("⚠️ 고객사 스펙 변경", 0.9, 0.95),
        ("⏳ 개발 지연", 0.85, 0.9),
    ]
    return random.choice(events)

# ---------------------------
# 수요 계산
# ---------------------------
def calc_demand(price, tech, reputation):
    base = 100
    demand = base * tech * (reputation / 50)

    if price < 90:
        demand *= 1.2
    elif price > 110:
        demand *= 0.8

    return int(demand)

# ---------------------------
# 상단 상태바
# ---------------------------
st.title("📱 SSS Game V3")

st.write(f"📅 {st.session_state.year}년 {st.session_state.quarter}분기")
st.write(f"💰 Cash: {st.session_state.cash} | 🧠 Tech: {round(st.session_state.tech,2)} | 🏭 Yield: {round(st.session_state.yield_rate,2)}")

st.divider()

# ==================================================
# 1️⃣ 의사결정 화면
# ==================================================
if st.session_state.stage == "decision":

    st.header("📊 전략 선택")

    rd_choice = st.radio(
        "R&D 전략",
        ["보수적 투자 (500)", "균형 투자 (1000)", "공격 투자 (2000)"]
    )

    capex_choice = st.radio(
        "CAPEX 전략",
        ["축소 (500)", "유지 (1000)", "확대 (2000)"]
    )

    price_choice = st.radio(
        "가격 전략",
        ["프리미엄 (120)", "균형 (100)", "덤핑 (80)"]
    )

    st.info("💡 공격 투자 = 기술↑ but 현금 리스크 ↑")

    if st.button("➡️ 결정 완료"):
        st.session_state.rd_choice = rd_choice
        st.session_state.capex_choice = capex_choice
        st.session_state.price_choice = price_choice
        st.session_state.stage = "result"

# ==================================================
# 2️⃣ 결과 화면
# ==================================================
elif st.session_state.stage == "result":

    st.header("📉 분기 결과")

    # 선택값 매핑
    rd_map = {
        "보수적 투자 (500)": 500,
        "균형 투자 (1000)": 1000,
        "공격 투자 (2000)": 2000
    }

    capex_map = {
        "축소 (500)": 500,
        "유지 (1000)": 1000,
        "확대 (2000)": 2000
    }

    price_map = {
        "프리미엄 (120)": 120,
        "균형 (100)": 100,
        "덤핑 (80)": 80
    }

    rd = rd_map[st.session_state.rd_choice]
    capex = capex_map[st.session_state.capex_choice]
    price = price_map[st.session_state.price_choice]

    # 이벤트
    event, demand_mult, tech_mult = get_event()

    st.success(f"📢 이벤트: {event}")

    # 투자 반영
    st.session_state.cash -= (rd + capex)

    # 기술
    st.session_state.tech += rd * 0.0005
    st.session_state.yield_rate += rd * 0.0001
    st.session_state.tech *= tech_mult

    # 설비
    st.session_state.capacity += int(capex * 0.02)

    # 수요
    demand = calc_demand(price, st.session_state.tech, st.session_state.reputation)
    demand = int(demand * demand_mult)

    # 생산
    production = int(st.session_state.capacity * st.session_state.yield_rate)

    # 판매
    sales = min(production + st.session_state.inventory, demand)

    # 재고
    st.session_state.inventory = production + st.session_state.inventory - sales

    # 매출 / 비용
    revenue = sales * price
    cost = production * 60
    op_profit = revenue - cost

    st.session_state.cash += op_profit

    # 평판
    if sales < demand:
        st.session_state.reputation -= 2
    else:
        st.session_state.reputation += 1

    # 결과 출력
    st.write(f"📦 판매량: {sales}")
    st.write(f"💵 매출: {revenue}")
    st.write(f"📈 영업이익: {op_profit}")
    st.write(f"🏦 현금: {st.session_state.cash}")

    # 기록
    st.session_state.history.append({
        "Year": st.session_state.year,
        "Q": st.session_state.quarter,
        "Revenue": revenue,
        "Op Profit": op_profit,
        "Cash": st.session_state.cash
    })

    if st.button("📊 다음 단계"):
        st.session_state.stage = "summary"

# ==================================================
# 3️⃣ 요약 화면
# ==================================================
elif st.session_state.stage == "summary":

    st.header("📊 성과 요약")

    if len(st.session_state.history) > 0:
        df = pd.DataFrame(st.session_state.history)

        st.line_chart(df[["Revenue", "Op Profit"]])
        st.dataframe(df.tail(8))

    if st.button("➡️ 다음 분기 진행"):
        st.session_state.quarter += 1
        if st.session_state.quarter > 4:
            st.session_state.quarter = 1
            st.session_state.year += 1

        st.session_state.stage = "decision"

# ---------------------------
# 게임오버
# ---------------------------
if st.session_state.cash <= 0:
    st.error("💀 파산! 게임 종료")
