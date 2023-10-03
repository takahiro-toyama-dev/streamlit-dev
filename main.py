import streamlit as st
from PIL import Image
import time

st.title("Streamlit 超入門")

st.write("DataFrame")

"Start!!"

later_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    later_iteration.text(f"Iteration{i+1}")
    bar.progress(i + 1)
    time.sleep(0.1)

"Done!!!!!"


left_column, right_column = st.columns(2)
button = left_column.button("右カラムに文字を表示")
if button:
    right_column.write("ここは右カラム")

expander1 = st.expander("問合せ1")
expander1.write("問合せ内容1")
expander2 = st.expander("問合せ2")
expander2.write("問合せ内容2")
expander3 = st.expander("問合せ3")
expander3.write("問合せ内容3")
