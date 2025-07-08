import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import base64

alt.themes.enable('dark')
st.set_page_config(page_title='검색', layout='wide', initial_sidebar_state='collapsed')


# URL
URL = 'https://github.com/SailingSnails/SailingSnails.github.io/raw/refs/heads/main/RawData.xlsx'
font_URL = './streamlit/fonts/Freesentation-6SemiBold.ttf'

# Font
def apply_custom_font(path):
    fm.fontManager.addfont(path)
    fontprop = fm.FontProperties(fname=path)
    plt.rcParams['font.family'] = fontprop.get_name()

    with open(path, 'rb') as f:
        font_base64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
        @font-face {{
            font-family: 'Freesentation';
            src: url('data:font/ttf;base64,{font_base64}') format('truetype');
        }}
        html, body, .stApp, div, p, span, section, label, button {{
            font-family: 'Freesentation', sans-serif !important;
        }}
        .stTextInput input {{
            font-family: 'Freesentation', sans-serif !important;
        }}
        .stSelectbox div {{
            font-family: 'Freesentation', sans-serif !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_font(font_URL)

# Tool Box
st.markdown(
    """
    <style>
    [data-testid="stElementToolbar"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Data
전체 = pd.read_excel(URL)
전체 = 전체.drop(columns=['횟수', '가격', '캐보', '후기', 'L1', 'L2', 'CB', 'RV'])
전체['시간'] = pd.to_datetime(전체['시간'], format='%H:%M:%S').dt.strftime('%H:%M')
전체['날짜'] = pd.to_datetime(전체['날짜']).dt.date

search_columns = ['날짜', '시간', '제작사', '시즌', '장르', '극', '자n', '캐슷', '극장']

# Layout
col1, col2, col3 = st.columns([2, 1, 4])

with col1:
    search = st.text_input('검색:')

with col2:
    selected_col = st.selectbox(
        '상세 검색:',
        options=[''] + search_columns,
        index=0
    )

def calc_height(num_rows, row_height=35, header_height=38, min_height=0, max_height=700):
    height = header_height + num_rows * row_height
    return min(max(height, min_height), max_height)

if search:
    if selected_col == '':
        filtered = 전체[전체.apply(lambda row: row.astype(str).str.contains(search, case=False, regex=False).any(), axis=1)]
    elif selected_col == '캐슷':
        keyword = f' {search} '
        filtered = 전체[전체['캐슷'].astype(str).str.contains(keyword, case=False, na=False, regex=False)]
    elif selected_col == '제작사':
        filtered = 전체[
            전체['제작사'].astype(str)
            .apply(lambda x: f"┃{x.replace(', ', '┃')}┃")
            .str.contains(f"┃{search}┃", case=False, na=False, regex=False)
        ]
    elif selected_col in ['극', '극장']:
        filtered = 전체[전체[selected_col].astype(str) == search]
        
    else:
        filtered = 전체[전체[selected_col].astype(str).str.contains(search, case=False, na=False, regex=False)]
else:
    filtered = 전체

본_횟수 = filtered.shape[0]
극_개수 = filtered['극'].nunique() if '극' in filtered.columns else 0

st.markdown(
    f"""
    <div style="margin-bottom: 10px; font-size: 1.5em;">
        <b>▶ {극_개수} 극 &nbsp; & &nbsp; {본_횟수} 회</b>
    </div>
    """,
    unsafe_allow_html=True
)

display_df = filtered.copy()
if '캐슷' in display_df.columns:
    display_df['캐슷'] = (
        display_df['캐슷']
        .astype(str)
        .str.strip()
        .str.replace(' ', ', ', regex=False)
        .str.replace('_', ' ', regex=False)
    )

height = calc_height(본_횟수)
st.dataframe(
    display_df,
    hide_index=True,
    height=height,
    column_config={
        "날짜": st.column_config.Column(width=45),
        "시간": st.column_config.Column(width=10),
        "제작사": st.column_config.Column(width=75),
        "시즌": st.column_config.Column(width=30),
        "장르": st.column_config.Column(width=70),
        "극": st.column_config.Column(width=185),
        "자n": st.column_config.Column(width=20),
        "캐슷": st.column_config.Column(width=450),
        "극장": st.column_config.Column(width=60),
    }
)