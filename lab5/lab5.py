import streamlit as st
import pandas as pd
import plotly.express as px


# НАЛАШТУВАННЯ СТОРІНКИ
# Встановлюємо назву сторінки та режим відображення (wide — на всю ширину)
st.set_page_config(
    page_title="Аналіз VCI, TCI, VHI",
    layout="wide"
)


# ЗАВАНТАЖЕННЯ ТА ПІДГОТОВКА ДАНИХ

@st.cache_data
def load_data():
    """
    Функція завантажує очищений датасет з CSV-файлу з другої лаби.
     кешування використовується для оптимізації роботи додатку, щоб
     дані не перечитувались при кожній взаємодії користувача.
    """

    df = pd.read_csv("noaa_cleaned.csv")

    # Перетворення типів даних
    df["Year"] = pd.to_numeric(df["Year"])
    df["Week"] = pd.to_numeric(df["Week"])

    # Перетворення індексів до числового типу
    for col in ["VCI", "TCI", "VHI"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Видалення рядків з пропущеними значеннями
    df = df.dropna(subset=["VCI", "TCI", "VHI"])

    return df


# Завантаження датафрейму
df = load_data()

# ПОЧАТКОВІ ЗНАЧЕННЯ ФІЛЬТРІВ

# Список доступних індексів
index_options = ["VCI", "TCI", "VHI"]

# Список областей
province_options = sorted(df["Province_Name"].unique())

# Межі для слайдерів
min_week = int(df["Week"].min())
max_week = int(df["Week"].max())

min_year = int(df["Year"].min())
max_year = int(df["Year"].max())

# Значення за замовчуванням
default_index = "VHI"
default_province = province_options[0]
default_weeks = (min_week, max_week)
default_years = (min_year, max_year)


# SESSION STATE (збереження стану віджетів)

# Якщо значення ще не існує, встановлюємо його
if "selected_index" not in st.session_state:
    st.session_state.selected_index = default_index

if "selected_province" not in st.session_state:
    st.session_state.selected_province = default_province

if "selected_weeks" not in st.session_state:
    st.session_state.selected_weeks = default_weeks

if "selected_years" not in st.session_state:
    st.session_state.selected_years = default_years

if "sort_ascending" not in st.session_state:
    st.session_state.sort_ascending = False

if "sort_descending" not in st.session_state:
    st.session_state.sort_descending = False


def reset_filters():
    """
    Функція для скидання всіх фільтрів до початкових значень,
    використовується при натисканні кнопки Reset.
    """
    st.session_state.selected_index = default_index
    st.session_state.selected_province = default_province
    st.session_state.selected_weeks = default_weeks
    st.session_state.selected_years = default_years
    st.session_state.sort_ascending = False
    st.session_state.sort_descending = False


# ІНТЕРФЕЙС КОРИСТУВАЧА

st.title("Веб-додаток для аналізу VCI, TCI та VHI")

# Розбиваємо екран на 2 колонки: ліва — фільтри, права — результати
left_col, right_col = st.columns([1, 3])

with left_col:
    st.header("Фільтри")

    # Dropdown для вибору індексу
    st.selectbox(
        "Оберіть часовий ряд:",
        index_options,
        key="selected_index"
    )

    # Dropdown для вибору області
    st.selectbox(
        "Оберіть область:",
        province_options,
        key="selected_province"
    )

    # Слайдер для вибору тижнів
    st.slider(
        "Оберіть інтервал тижнів:",
        min_value=min_week,
        max_value=max_week,
        key="selected_weeks"
    )

    # Слайдер для вибору років
    st.slider(
        "Оберіть інтервал років:",
        min_value=min_year,
        max_value=max_year,
        key="selected_years"
    )

    # Checkbox для сортування
    st.checkbox("Сортувати за зростанням", key="sort_ascending")
    st.checkbox("Сортувати за спаданням", key="sort_descending")

    # Кнопка скидання фільтрів
    st.button("Скинути фільтри", on_click=reset_filters)

    # Обробка конфлікту сортування
    if st.session_state.sort_ascending and st.session_state.sort_descending:
        st.warning(
            "Обрано обидва варіанти сортування. "
            "Сортування не застосовується."
        )

# ОТРИМАННЯ ВИБОРУ КОРИСТУВАЧА

selected_index = st.session_state.selected_index
selected_province = st.session_state.selected_province

week_start, week_end = st.session_state.selected_weeks
year_start, year_end = st.session_state.selected_years

# ФІЛЬТРАЦІЯ ДАНИХ

# Відбір даних за обраними параметрами
filtered_df = df[
    (df["Province_Name"] == selected_province) &
    (df["Week"] >= week_start) &
    (df["Week"] <= week_end) &
    (df["Year"] >= year_start) &
    (df["Year"] <= year_end)
].copy()

# Сортування
if st.session_state.sort_ascending and not st.session_state.sort_descending:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=True)

elif st.session_state.sort_descending and not st.session_state.sort_ascending:
    filtered_df = filtered_df.sort_values(by=selected_index, ascending=False)

else:
    # Стандартне сортування по часу
    filtered_df = filtered_df.sort_values(by=["Year", "Week"])

# ПІДГОТОВКА ДАНИХ ДЛЯ ПОРІВНЯННЯ ОБЛАСТЕЙ

comparison_df = df[
    (df["Week"] >= week_start) &
    (df["Week"] <= week_end) &
    (df["Year"] >= year_start) &
    (df["Year"] <= year_end)
].copy()

# Обчислення середнього значення для кожної області
comparison_df = (
    comparison_df
    .groupby("Province_Name", as_index=False)[selected_index]
    .mean()
    .rename(columns={selected_index: f"Average_{selected_index}"})
)

# Позначаємо обрану область
comparison_df["Type"] = comparison_df["Province_Name"].apply(
    lambda x: "Обрана область" if x == selected_province else "Інші області"
)

# Сортування
comparison_df = comparison_df.sort_values(
    by=f"Average_{selected_index}",
    ascending=False
)

# ВІДОБРАЖЕННЯ РЕЗУЛЬТАТІВ

with right_col:
    st.subheader("Результати аналізу")

    # Відображення вибраних параметрів
    st.write(
        f"Обрано: **{selected_index}**, область: **{selected_province}**, "
        f"тижні: **{week_start}-{week_end}**, роки: **{year_start}-{year_end}**"
    )

    # Вкладки
    tab1, tab2, tab3 = st.tabs([
        "Таблиця",
        "Графік часового ряду",
        "Порівняння областей"
    ])

    # ТАБЛИЦЯ

    with tab1:
        st.subheader("Відфільтровані дані")

        if filtered_df.empty:
            st.info("За вибраними фільтрами дані відсутні.")
        else:
            st.dataframe(filtered_df.reset_index(drop=True))

            # Базова статистика
            st.write("Кількість записів:", len(filtered_df))
            st.write("Мінімум:", round(filtered_df[selected_index].min(), 2))
            st.write("Максимум:", round(filtered_df[selected_index].max(), 2))
            st.write("Середнє:", round(filtered_df[selected_index].mean(), 2))
            st.write("Медіана:", round(filtered_df[selected_index].median(), 2))


    # ГРАФІК ЧАСОВОГО РЯДУ

    with tab2:
        st.subheader(f"Графік {selected_index} для області {selected_province}")

        if not filtered_df.empty:
            plot_df = filtered_df.sort_values(by=["Year", "Week"]).copy()

            # Формування осі часу
            plot_df["Year_Week"] = (
                plot_df["Year"].astype(str)
                + "-W"
                + plot_df["Week"].astype(str).str.zfill(2)
            )

            fig = px.line(
                plot_df,
                x="Year_Week",
                y=selected_index,
                markers=True
            )

            st.plotly_chart(fig, use_container_width=True)


    # ПОРІВНЯННЯ ОБЛАСТЕЙ

    with tab3:
        st.subheader(f"Порівняння {selected_index} по областях")

        if not comparison_df.empty:
            fig = px.bar(
                comparison_df,
                x="Province_Name",
                y=f"Average_{selected_index}",
                color="Type"
            )

            st.plotly_chart(fig, use_container_width=True)