import streamlit as st
import random
import pandas as pd

st.set_page_config(layout="wide")

# ---------------------------
# 초기 상태
# ---------------------------
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.year = 2025
    st.session_state.quarter = 1
    st.session_state.cash = 10000
    st.session_state.debt = 0
    st.session_state.tech_node = 10  # nm
    st.session_state.ddi_perf = 1.0
    st.session_state.yield_rate = 0.7
    st.session_state.capacity = 100
    st.session_state.inventory = 20
    st.session_state.reputation = 50
    st.session_state.history = []

# ---------------------------
# 경쟁사
# ---------------------------
competitors = {
    "BOE": {"price": 90, "tech": 1.0},
    "LG Display": {"price": 100, "tech": 1.2},
}

# ---------------------------
# UI
# ---------------------------
st.title("📱 Samsung Semiconductor Survival (SSS) Game")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 현재 상태")
    st.write(f"Year: {st.session_state.year} Q{st.session_state.quarter}")
    st.write(f"Cash: {st.session_state.cash}")
    st.write(f"Debt: {st.session_state.debt}")
    st.write(f"Tech Node: {st.session_state.tech_node}nm")
    st.write(f"DDI 성능: {round(st.session_state.ddi_perf,2)}")
    st.write(f"Yield: {round(st.session_state.yield_rate,2)}")
    st.write(f"Capacity: {st.session_state.capacity}")
    st.write(f"Inventory: {st.session_state.inventory}")
    st.write(f"Reputation: {st.session_state.reputation}")

with col2:
    st.subheader("🏭 의사결정 (3개)")
    rd = st.slider("R&D 투자", 0, 3000, 1000)
    capex = st.slider("CAPEX 투자", 0, 3000, 1000)
    price = st.slider("제품 가격", 50, 150, 100)

# ---------------------------
# 이벤트
# ---------------------------
def get_event():
    events = [
        ("반도체 Shortage 🔥", 1.3, 1.1),
        ("경기 침체 ❄️", 0.8, 0.9),
        ("고객사 스펙 변경 ⚠️", 0.9, 0.95),
        ("개발 지연 ⏳", 0.85, 0.9),
        ("중국 보조금 확대 🇨🇳", 0.9, 1.0),
    ]
    return random.choice(events)

# ---------------------------
# 수요 계산
# ---------------------------
def calc_demand(price, tech, reputation):
    base = 100
    demand = base * (tech) * (reputation/50)

    if price < 90:
        demand *= 1.2
    elif price > 110:
        demand *= 0.8

    return int(demand)

# ---------------------------
# 실행
# ---------------------------
if st.button("➡️ 다음 분기 진행"):

    event, demand_mult, tech_mult = get_event()

    # 투자 반영
    st.session_state.cash -= (rd + capex)

    # 기술 향상
    st.session_state.ddi_perf += rd * 0.0005
    st.session_state.yield_rate += rd * 0.0001

    # 설비 증가
    st.session_state.capacity += int(capex * 0.02)

    # 이벤트 반영
    st.session_state.ddi_perf *= tech_mult

    # 수요 계산
    demand = calc_demand(price, st.session_state.ddi_perf, st.session_state.reputation)
    demand = int(demand * demand_mult)

    # 생산
    production = int(st.session_state.capacity * st.session_state.yield_rate)

    # 판매
    sales = min(production + st.session_state.inventory, demand)

    # 재고 업데이트
    st.session_state.inventory = production + st.session_state.inventory - sales

    # 매출
    revenue = sales * price

    # 비용
    cost = production * 60

    operating_profit = revenue - cost

    # 현금 반영
    st.session_state.cash += operating_profit

    # 평판 변화
    if sales < demand:
        st.session_state.reputation -= 2
    else:
        st.session_state.reputation += 1

    # 기록
    st.session_state.history.append({
        "Year": st.session_state.year,
        "Q": st.session_state.quarter,
        "Revenue": revenue,
        "Op Profit": operating_profit,
        "Cash": st.session_state.cash
    })

    # 시간 흐름
    st.session_state.quarter += 1
    if st.session_state.quarter > 4:
        st.session_state.quarter = 1
        st.session_state.year += 1

    st.success(f"이벤트 발생: {event}")

# ---------------------------
# 재무 출력
# ---------------------------
st.subheader("📈 현금흐름 / 성과")

if len(st.session_state.history) > 0:
    df = pd.DataFrame(st.session_state.history)
    st.line_chart(df.set_index(df.index)[["Revenue", "Op Profit"]])
    st.dataframe(df.tail(10))

# ---------------------------
# 게임 오버
# ---------------------------
if st.session_state.cash <= 0:
    st.error("💀 파산! 게임 종료")
