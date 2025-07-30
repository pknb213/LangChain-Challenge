import streamlit as st

st.set_page_config(
    page_title="Happy Birthday",
    page_icon="🎉",
)

select_event = st.sidebar.selectbox(
    "Select a page",
    [
        "고",
        "차",
        "장",
        "님",
    ],
    index=0,
)

if select_event == "고":
    st.title("고차장님 생일 축하드립니다 !!")
    st.image("https://github.com/pknb213/LangChain-Challenge/blob/master/image1.jpg?raw=true", caption="Celebrate your special day!", use_column_width=True)

elif select_event == "차":
    st.title("더운데 일찍 집에 가셔서")
    st.image("https://github.com/pknb213/LangChain-Challenge/blob/master/image2.jpg?raw=true")

elif select_event == "장":
    st.title("맛있는거 많이 드시고")
    st.image("https://github.com/pknb213/LangChain-Challenge/blob/master/image3.png?raw=true")

elif select_event == "님":
    st.title("칼퇴 축하드립니다~")
    st.image("https://github.com/pknb213/LangChain-Challenge/blob/master/image4.png?raw=true")