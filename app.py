import streamlit as st
import random

# 초기화
if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.cash = 10000
    st.session_state.tech = 1.0
    st.session_state.reputation = 50
    st.session_state.stage = "decision"
    st.session_state.year = 2025
    st.session_state.q = 1

st.title("🍎 SSS Game V5 - Apple War")

st.write(f"{st.session_state.year} Q{st.session_state.q}")
st.write(f"💰 Cash: {st.session_state.cash}")
st.write(f"🧠 Tech: {round(st.session_state.tech,2)} | ⭐ Reputation: {st.session_state.reputation}")

st.divider()

# --------------------
# 의사결정
# --------------------
if st.session_state.stage == "decision":

    st.header("📊 Apple 입찰 전략")

    rd_choice = st.radio("R&D", ["보수(500)", "균형(1000)", "공격(2000)"])
    price_choice = st.radio("가격", ["프리미엄(120)", "균형(100)", "덤핑(80)"])

    st.warning("⚠️ Apple 수주 실패 시 매출 급감")

    if st.button("입찰 진행"):
        st.session_state.rd_choice = rd_choice
        st.session_state.price_choice = price_choice
        st.session_state.stage = "result"

# --------------------
# 결과
# --------------------
elif st.session_state.stage == "result":

    rd_map = {"보수(500)": 500, "균형(1000)": 1000, "공격(2000)": 2000}
    price_map = {"프리미엄(120)": 120, "균형(100)": 100, "덤핑(80)": 80}

    rd = rd_map[st.session_state.rd_choice]
    price = price_map[st.session_state.price_choice]

    # 경쟁사 (BOE)
    competitor_price = random.choice([80, 90, 100])
    competitor_tech = random.uniform(0.9, 1.2)

    # 투자
    st.session_state.cash -= rd
    st.session_state.tech += rd * 0.0005

    # 점수 계산
    my_score = (
        st.session_state.tech * 0.5 +
        st.session_state.reputation * 0.3 -
        price * 0.2
    )

    comp_score = (
        competitor_tech * 0.5 +
        50 * 0.3 -
        competitor_price * 0.2
    )

    # 결과
    if my_score > comp_score:
        st.success("🔥 Apple 수주 성공!")
        revenue = 8000
        st.session_state.reputation += 3
    else:
        st.error("💀 Apple 수주 실패...")
        revenue = 1000
        st.session_state.reputation -= 5

    # 이벤트 (치명적)
    if random.random() < 0.2:
        st.error("⚠️ 개발 지연! 경쟁력 하락")
        st.session_state.tech *= 0.9

    profit = revenue - rd
    st.session_state.cash += profit

    st.write(f"매출: {revenue}")
    st.write(f"이익: {profit}")

    if st.button("다음 분기"):
        st.session_state.q += 1
        if st.session_state.q > 4:
            st.session_state.q = 1
            st.session_state.year += 1

        st.session_state.stage = "decision"

# --------------------
# 게임오버
# --------------------
if st.session_state.cash < 0:
    st.error("💀 파산! 게임 종료")
