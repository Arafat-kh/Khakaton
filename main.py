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

# ===================== ФУНКЦИИ =====================

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


def select_stratified_vuz(combined_df, n_vuz=50):
    """Стратифицированная выборка ВУЗов по регионам"""
    if 'Region' not in combined_df.columns or 'VUZ' not in combined_df.columns:
        return combined_df['VUZ'].unique()[:n_vuz].tolist()
    
    region_groups = combined_df.groupby('Region')
    selected_vuz = []
    
    for region, group in region_groups:
        region_vuz = group['VUZ'].unique()
        region_quota = max(1, int(n_vuz * len(region_vuz) / len(combined_df['VUZ'].unique())))
        selected_vuz.extend(region_vuz[:region_quota])
    
    if len(selected_vuz) < n_vuz:
        region_sizes = combined_df.groupby('Region')['VUZ'].nunique().sort_values(ascending=False)
        for region in region_sizes.index:
            if len(selected_vuz) >= n_vuz:
                break
            region_vuz = combined_df[combined_df['Region'] == region]['VUZ'].unique()
            new_vuz = [v for v in region_vuz if v not in selected_vuz]
            selected_vuz.extend(new_vuz[:2])
    
    return selected_vuz[:n_vuz]

# ===================== ХРАНЕНИЕ СОСТОЯНИЯ =====================
if "results_df" not in st.session_state:
    st.session_state.results_df = None
if "filtered_df" not in st.session_state:
    st.session_state.filtered_df = None

# ===================== ИНТЕРФЕЙС =====================

uploaded_files = st.file_uploader(
    "Выберите Excel файлы:",
    type=['xlsx', 'xls'],
    accept_multiple_files=True,
    key="file_uploader"
)

if uploaded_files:
    st.success(f"✅ Загружено файлов: {len(uploaded_files)}")
    for i, file in enumerate(uploaded_files):
        st.write(f"{i+1}. {file.name}")

if uploaded_files and st.button("🚀 Построить прогноз на 2024 год", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("📁 Загружаем файлы...")
        all_data = []
        year_mapping = {
            '2015': 2014, '2014': 2014,
            '2020': 2019, '2019': 2019, 
            '2021': 2020, '2020': 2020,
            '2022': 2021, '2021': 2021
        }
        
        for file in uploaded_files:
            df = pd.read_excel(file)
            data_year = 2021
            for year_str, actual_year in year_mapping.items():
                if year_str in file.name:
                    data_year = actual_year
                    break
            df['data_year'] = data_year
            all_data.append(df)
        
        progress_bar.progress(30)
        status_text.text("📊 Объединяем данные...")
        
        combined_df = pd.concat(all_data, ignore_index=True)
        progress_bar.progress(50)
        status_text.text("🎯 Анализируем показатели...")

        numeric_cols = combined_df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [col for col in numeric_cols if col != 'data_year']

        col_quality = []
        for col in numeric_cols:
            filled_ratio = combined_df[col].notna().sum() / len(combined_df)
            if filled_ratio > 0.3:
                col_quality.append((col, filled_ratio))
        
        col_quality.sort(key=lambda x: x[1], reverse=True)
        target_columns = [col[0] for col in col_quality[:3]]
        progress_bar.progress(70)
        status_text.text("📈 Строим прогнозы...")

        results = []
        
        if 'VUZ' in combined_df.columns:
            selected_vuz_list = select_stratified_vuz(combined_df, n_vuz=50)

            for vuz in selected_vuz_list:
                vuz_data = combined_df[combined_df['VUZ'] == vuz]
                
                for col in target_columns:
                    yearly_data = vuz_data.groupby('data_year')[col].mean().reset_index()
                    yearly_data = yearly_data.dropna()
                    
                    if len(yearly_data) >= 2:
                        prediction, trend = simple_forecast(yearly_data, 'data_year', col)
                        
                        if prediction is not None:
                            trend_direction = "📈 Рост" if trend > 0 else "📉 Снижение" if trend < 0 else "➡️ Стабильно"
                            
                            results.append({
                                'ВУЗ': vuz,
                                'Показатель': col,
                                'Прогноз_2024': round(prediction, 2),
                                'Тренд': round(trend, 3),
                                'Направление': trend_direction,
                                'Лет_данных': len(yearly_data)
                            })
        
        progress_bar.progress(90)
        status_text.text("🎨 Готовим отчет...")

        if results:
            results_df = pd.DataFrame(results)
            st.session_state.results_df = results_df  # сохраняем
            progress_bar.progress(100)
            progress_bar.empty()
            status_text.empty()
        else:
            st.warning("❌ Не удалось построить прогноз.")
            
    except Exception as e:
        progress_bar.empty()
        status_text.empty()
        st.error(f"❌ Ошибка: {str(e)}")

# ===================== ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ =====================

if st.session_state.results_df is not None:
    results_df = st.session_state.results_df

    st.subheader("📊 Результаты прогноза на 2024 год")

    col1, col2 = st.columns(2)
    with col1:
        selected_indicator = st.selectbox(
            "Выберите показатель:",
            results_df['Показатель'].unique()
        )
    with col2:
        sort_by = st.selectbox(
            "Сортировать по:",
            ['Прогноз_2024', 'Тренд']
        )

    filtered_df = results_df[results_df['Показатель'] == selected_indicator]
    filtered_df = filtered_df.sort_values(sort_by, ascending=False)
    st.session_state.filtered_df = filtered_df  # сохраняем для скачивания

    st.dataframe(filtered_df.head(20), use_container_width=True)

    # ===================== СКАЧИВАНИЕ =====================
    st.subheader("📥 Скачать результаты")

    encoding_choice = st.radio(
        "Выберите кодировку файла:",
        ["UTF-8 (рекомендуется)", "Windows-1251 (для Excel)"],
        horizontal=True,
        key="encoding_radio"
    )

    if st.session_state.filtered_df is not None:
        filtered_df = st.session_state.filtered_df

        if encoding_choice == "UTF-8 (рекомендуется)":
            csv = filtered_df.to_csv(index=False, sep=';', encoding='utf-8-sig')
            filename = "прогноз_вузов_2024_utf8.csv"
        else:
            csv = filtered_df.to_csv(index=False, sep=';', encoding='cp1251')
            filename = "прогноз_вузов_2024_win1251.csv"

        st.download_button(
            label="💾 Скачать CSV-файл",
            data=csv,
            file_name=filename,
            mime="text/csv"
        )

        # 💡 Дополнительно: Excel-версия
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            filtered_df.to_excel(writer, index=False, sheet_name='Прогноз 2024')
        st.download_button(
            label="📘 Скачать Excel-файл (.xlsx)",
            data=buffer.getvalue(),
            file_name="прогноз_вузов_2024.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("""👆 Загрузите файлы и нажмите «Построить прогноз».""")

