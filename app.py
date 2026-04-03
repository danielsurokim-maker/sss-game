import streamlit as st
import random

# 초기값 설정
if "year" not in st.session_state:
    st.session_state.year = 2025
    st.session_state.cash = 10000
    st.session_state.tech = 1.0
    st.session_state.share = 20.0

st.title("📱 Samsung Semiconductor Survival (SSS) Game")

st.write(f"📅 Year: {st.session_state.year}")
st.write(f"💰 Cash: {st.session_state.cash}")
st.write(f"🧠 Tech Level: {round(st.session_state.tech,2)}")
st.write(f"📊 Market Share: {round(st.session_state.share,2)}%")

st.divider()

# 투자 선택
rd = st.slider("R&D 투자", 0, 5000, 1000)
capex = st.slider("설비 투자", 0, 5000, 1000)

# 이벤트
event_text = ""

def random_event():
    events = [
        ("AI 수요 폭발!", 1.2),
        ("경기 침체...", 0.8),
        ("중국 경쟁 심화", 0.9),
        ("신기술 성공!", 1.3),
    ]
    return random.choice(events)

# 다음 해 진행
if st.button("➡️ 다음 해로"):
    multiplier_text, multiplier = random_event()
    event_text = multiplier_text

    # 돈 차감
    st.session_state.cash -= (rd + capex)

    # 기술 성장
    st.session_state.tech += rd * 0.001

    # 점유율 변화
    st.session_state.share *= multiplier
    st.session_state.share += st.session_state.tech * 0.2

    # 수익 (간단 모델)
    revenue = st.session_state.share * 100
    st.session_state.cash += int(revenue)

    st.session_state.year += 1

    st.success(f"이벤트 발생: {event_text}")

# 게임 오버 조건
if st.session_state.cash <= 0:
    st.error("💀 파산! 게임 종료")
