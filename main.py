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
def simple_forecast(df, years_col, values_col):
    """Простой прогноз на основе линейного тренда"""
    if len(df) < 2:
        return None, 0
    
    x = df[years_col].values
    y = df[values_col].values
    
    n = len(x)
    sum_x = np.sum(x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    sum_x2 = np.sum(x ** 2)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
    intercept = (sum_y - slope * sum_x) / n
    
    prediction = slope * 2024 + intercept
    return prediction, slope
