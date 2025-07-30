import streamlit as st

st.set_page_config(
    page_title="Happy Birthday",
    page_icon="🎉",
)

select_event = st.sidebar.selectbox(
    "Select a page",
    ["Happy Birthday", "Happy Birthday with Name", "Happy Birthday with Name and Age"],
    index=0,
)

if select_event == "Happy Birthday":
    st.title("Happy Birthday!")
    st.write("🎂🎉 Wishing you a wonderful birthday filled with joy and happiness! 🎉🎂")

elif select_event == "Happy Birthday with Name":
    st.title("Happy Birthday!")
    name = st.text_input("Enter your name:")
    if name:
        st.write(f"🎂🎉 Happy Birthday, {name}! Wishing you a wonderful day filled with joy and happiness! 🎉🎂")
    else:
        st.write("Please enter your name to receive a personalized birthday wish.")

elif select_event == "Happy Birthday with Name and Age":
    st.title("Happy Birthday!")
    name = st.text_input("Enter your name:")
    age = st.number_input("Enter your age:", min_value=0, max_value=120, step=1)

    if name and age:
        st.write(f"🎂🎉 Happy Birthday, {name}! You are now {age} years old! Wishing you a wonderful day filled with joy and happiness! 🎉🎂")
    else:
        st.write("Please enter your name and age to receive a personalized birthday wish.")


st.image("https://github.com/pknb213/pknb213/blob/main/45507892b4f48b2b3d4a6386f6dae20c28376a8ef5dfb68c7cc95249ec358e3e68df77594766021173b2e6acf374b79ce02e9eeef61fcdf316659e30289e123fbddf6e5ec3492eddbc582ee5a59a2ff5d6ee84f57ad19277d179b613614364ad.jpeg?raw=true", caption="Celebrate your special day!", use_column_width=True)