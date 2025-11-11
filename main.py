import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

st.set_page_config(
    page_title="Прогноз ВУЗов 2024",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Прогноз показателей ВУЗов на 2024 год")
st.markdown("Загрузите данные мониторинга за 2015, 2020, 2021, 2022 годы")
