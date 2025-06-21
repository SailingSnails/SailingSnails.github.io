import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import base64
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from st_aggrid import AgGrid, GridOptionsBuilder


#URL
URL = 'https://github.com/SailingSnails/summary/raw/refs/heads/main/RawData.xlsx'
font_URL = './fonts/Freesentation-6SemiBold.ttf'

review_URL = {
    2018: "https://docs.google.com/document/d/1ngNlvLkkbjqr2dKBcf6GSFSng658vXWsZWSRmY0p_EI/edit?tab=t.0",
    2019: "https://docs.google.com/document/d/1ngNlvLkkbjqr2dKBcf6GSFSng658vXWsZWSRmY0p_EI/edit?tab=t.0#heading=h.cgexjii66zaa",
    2020: "https://docs.google.com/document/d/1IJKj28WSmB43cowlF19ppH67wi0aAqRkUBKykEZYuqo/edit?tab=t.0",
    2021: "https://docs.google.com/document/d/11HkLPS0i1BaHYxd_nrXF-DIXJddcswiEALKDXXaMLyk/edit?tab=t.0",
    2022: "https://docs.google.com/document/d/14ko3jNxFIZktf9Vp6kEA59ANtVfHfnph4zFvlagN6m8/edit?tab=t.0",
    2023: "https://docs.google.com/document/d/1Lp8e0cK20w1skw57uWFSe5gkgxcq_WRyIVKUViLO08c/edit?tab=t.0",
    2024: "https://docs.google.com/document/d/1PlCMWPXI8RFP3FU5QmjoMivZdmflKNWw6sUZKOcfaEE/edit?tab=t.0",
    2025: "https://docs.google.com/document/d/151p6Aup0qZki6hvL_E73D-XKB7jHAqBNW0_aKy_5m9w/edit?tab=t.0"
}

cast_URL = {
    2018: "https://x.com/playnmusical_Q/status/1499335369652772864",
    2019: "https://x.com/playnmusical_Q/status/1499341967087394817",
    2020: "https://x.com/playnmusical_Q/status/1219481959170068480",
    2021: "https://x.com/playnmusical_Q/status/1352549590537408513",
    2022: "https://x.com/playnmusical_Q/status/1478714300579876866",
    2023: "https://x.com/playnmusical_Q/status/1681233081586552834",
    2024: "https://x.com/playnmusical_Q/status/1742747279763648953",
    2025: "https://x.com/playnmusical_Q/status/1875163614967202161"
}

회전극_링크 = "https://x.com/playnmusical_Q/status/1900853298317742414"


#Setting
alt.themes.enable('dark')
st.set_page_config(page_title='관극 정산', layout='wide', initial_sidebar_state="collapsed")
color_presets = {
    'default': ['#A13E4A', '#C56874', '#E9A8AE'],
    2019: ['#FD6666', '#FEA3A3', '#FFDFDF'],
    2020: ['#4A7FB0', '#5B9BD5', '#ADC6E5'],
    2021: ['#666666', '#888888', '#BABABA'],
    2022: ['#E68AA9', '#FFA0C5', '#FFD1D4'],
    2023: ['#703C3C', '#8E5656', '#C49A9A'],
    2024: ['#228B22', '#5DC35D', '#A4FBA6'],
    2025: ['#9258A8', '#BD7CCF', '#D9B3E6'],
}


#Font
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
        </style>
        """,
        unsafe_allow_html=True
    )

apply_custom_font(font_URL)


#Filter
전체 = pd.read_excel(URL)
전체['날짜'] = pd.to_datetime(전체['날짜'])
years = sorted(전체['날짜'].dt.year.unique(), reverse=True)
display_list = ['전체'] + [f"{y}년 관극 정산" for y in years]

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    selected_option = st.selectbox(' ', display_list, index=0)

is_all = selected_option == '전체'
selected_year = None
후기_링크 = 캐보_링크 = ''

if is_all:
    df_selected_year = df_year_before = 전체.copy()
else:
    selected_year = years[display_list.index(selected_option) - 1]
    df_selected_year = 전체[전체['날짜'].dt.year == selected_year].copy()
    df_year_before = 전체[전체['날짜'].dt.year == (selected_year - 1)]


#Buttons
if not is_all:
    selected_year = int(selected_option.split('년')[0])
    후기_링크 = review_URL.get(selected_year, '')
    캐보_링크 = cast_URL.get(selected_year, '')

with col3:
    col_btn1, col_btn2 = st.columns([1, 3.8])
    with col_btn1:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        st.link_button("회전극" if is_all else "캐슷 보드", 회전극_링크 if is_all else 캐보_링크)

    with col_btn2:
        if not is_all:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            st.link_button("후기", 후기_링크)


if is_all:
    col_or = color_presets.get('default')
else:
    col_or = color_presets.get(selected_year, color_presets['default'])  # fallback to default if year not in dict


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


#연별/월별 정산
df_selected_year['가격'] = df_selected_year['가격'].replace(',', '', regex=True)
df_selected_year['년도'] = df_selected_year['날짜'].dt.year
df_selected_year['월'] = df_selected_year['날짜'].dt.month

기준표 = pd.DataFrame([
    {'년도': y, '월': m}
    for y in df_selected_year['년도'].unique()
    for m in range(1, 13)
])

집계표 = (
    df_selected_year
    .groupby(['년도', '월'])
    .agg(횟수=('극', 'count'), 극=('극', 'nunique'), 비용=('가격', 'sum'))
    .reset_index()
)

월별정산 = pd.merge(기준표, 집계표, on=['년도', '월'], how='left').fillna(0)
월별정산[['횟수', '극', '비용']] = 월별정산[['횟수', '극', '비용']].astype(int)
월별정산 = 월별정산.sort_values(by=['년도', '월']).reset_index(drop=True)

연별정산 = df_selected_year.groupby('년도').agg(
    극=('극', 'nunique'),
    횟수=('극', 'count'),
    비용=('가격', 'sum')
).reset_index()

#그래프
if is_all:
    x = np.arange(len(연별정산))
    x_labels = [f'\n{y}년' for y in 연별정산['년도'].values]
    횟수 = 연별정산['횟수'].values
    극 = 연별정산['극'].values
    비용 = 연별정산['비용'].values
else:
    x = np.arange(1, 13)
    x_labels = [f'\n{m}월' for m in x]
    횟수 = 월별정산['횟수'].values
    극 = 월별정산['극'].values
    비용 = 월별정산['비용'].values

fig0, ax0 = plt.subplots(figsize=(13.6, 3.8))
fig0.patch.set_facecolor('none')
ax0.set_facecolor('none')

bar_width = 0.48
cmap = LinearSegmentedColormap.from_list("bar_grad", ['#E7E6E6', col_or[1], col_or[0]])

#횟수
for xi, y in zip(x, 횟수):
    grad = np.linspace(0, 1, 100).reshape(-1, 1)
    ax0.imshow(grad, aspect='auto', extent=(xi - bar_width/2, xi + bar_width/2, 0, y),
               origin='lower', cmap=cmap, zorder=2)

#극
for xi, y in zip(x, 극):
    ax0.bar(xi, y, width=bar_width, fill=False, edgecolor='#F0F0F0',
            linewidth=1.5, linestyle=(0, (5, 5)), zorder=3)

#비용
ax01 = ax0.twinx()
ax01.plot(x, 비용, color=col_or[2], linewidth=2.25, zorder=4)
ax01.set_ylim(bottom=0)

#Axis
ax01.set_xticks(x)
ax0.set_xticklabels(x_labels, fontsize=12, color='#AFABAB')
ax0.tick_params(axis='x', length=0, colors='#AFABAB')
ax0.tick_params(axis='y', left=False, labelleft=False)
ax01.tick_params(axis='y', right=False, labelright=False)

for ax in [ax0, ax01]:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
ax0.spines['bottom'].set_color('#C0C0C0')
ax01.spines['bottom'].set_visible(False)
ax0.grid(False)
ax01.grid(False)

#Legend
legend_elements = [
    Patch(facecolor=col_or[0], label='횟수'),
    Patch(facecolor='none', edgecolor='#F0F0F0', linewidth=1, linestyle=(0, (5, 5)), label='극'),
    Line2D([0], [0], color='#C0C0C0', lw=2.25, label='비용')
]
ax0.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.3),
           ncol=3, frameon=False, fontsize=10, labelcolor='#AFABAB')

#Data Label
for xi, y in zip(x, 횟수):
    if y > 0:
        ax0.text(xi, y + max(횟수)*0.07, f"{y}", ha='center', fontsize=8, color='#E0E0E0', zorder=10)

for xi, y in zip(x, 극):
    if y > 0:
        ax0.text(xi, 0.5, f"{y}", ha='center', fontsize=8, color='#404040', zorder=10)

plt.subplots_adjust(left=0.12, right=0.93, bottom=0.18, top=0.83)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


#Donut Chart
def draw_donut(ax, values, labels, center_label, diff_label=None, diff_color='#BFBFBF'):
    fig = ax.figure
    fig.patch.set_facecolor('none')

    ax.pie(
        values,
        autopct='%.0f%%',
        counterclock=False,
        startangle=90,
        radius=1,
        colors=col_or,
        pctdistance=0.82,
        wedgeprops=dict(width=0.35, edgecolor='#3B3838', linewidth=2),
        textprops=dict(color='#4D4D4D', fontsize=11, fontweight='bold')
    )

    if selected_option == '전체':
        ax.text(0, -0.02, center_label, ha='center', va='center', fontsize=44, fontweight='bold', color='white')
    else:
        ax.text(0, 0.04, center_label, ha='center', va='center', fontsize=44, fontweight='bold', color='white')
        if diff_label:
            ax.text(0, -0.26, diff_label, ha='center', va='center', fontsize=20, fontweight='bold', color=diff_color)

    ax.legend(
        labels,
        loc='lower center',
        bbox_to_anchor=(0.5, -0.15),
        ncol=len(labels),
        frameon=False,
        fontsize=12,
        labelcolor='#D9D9D9'
    )


#장르
genre_list = ['연극', '뮤지컬', '기타']

장르 = pd.DataFrame([{
    '장르': g,
    '횟수': df_selected_year['장르'].str.contains(g, na=False).sum()
} for g in genre_list])
장르 = 장르[장르['횟수'] > 0].reset_index(drop=True)

올해횟수 = 장르['횟수'].sum()
작년횟수 = 0
if selected_year is not None:
    작년횟수 = 전체[전체['날짜'].dt.year == (selected_year - 1)].shape[0]

차이 = 올해횟수 - 작년횟수
if 차이 > 0:
    차이표시, 색상 = f'▲ {차이}', '#FD6666'
elif 차이 < 0:
    차이표시, 색상 = f'▼ {abs(차이)}', '#6FB3FF'
else:
    차이표시, 색상 = '-', '#BFBFBF'

#그래프
fig1, ax1 = plt.subplots(figsize=(5, 5))
draw_donut(ax1, 장르['횟수'], 장르['장르'], f'{올해횟수}회', None if selected_option == '전체' else 차이표시, 색상)


# ---------------------------------------------------------------------------


#회전
극 = df_selected_year['극'].value_counts().to_frame().reset_index()
극.columns = ['극', '횟수']

nth = pd.DataFrame([{
    '회전': '자첫자막' if 횟수 == 1 else ('자둘' if 횟수 == 2 else '자셋+'),
    '극': 극명
} for 극명, 횟수 in zip(극['극'], 극['횟수'])])

nth['회전'] = pd.Categorical(nth['회전'], categories=['자첫자막', '자둘', '자셋+'], ordered=True)

회전 = nth['회전'].value_counts().to_frame().reset_index()
회전.columns = ['회전', '극']
회전 = 회전.sort_values(by='회전')

올해극 = 회전['극'].sum()
작년극 = 0
if selected_year is not None:
    작년극 = 전체[전체['날짜'].dt.year == (selected_year - 1)]['극'].nunique()

차이 = 올해극 - 작년극
if 차이 > 0:
    차이표시, 색상 = f'▲ {차이}', '#FD6666'
elif 차이 < 0:
    차이표시, 색상 = f'▼ {abs(차이)}', '#6FB3FF'
else:
    차이표시, 색상 = '-', '#BFBFBF'

#그래프
fig2, ax2 = plt.subplots(figsize=(5, 5))
draw_donut(ax2, 회전['극'], 회전['회전'], f'{올해극}극', None if selected_option == '전체' else 차이표시, 색상)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


#시즌
def count_season(df, keyword):
    return df['시즌'].str.contains(keyword, na=False).sum()

창초 = count_season(df_selected_year, '창작 초연|창작 트아')
창재 = count_season(df_selected_year, '창작 재연')
창삼 = count_season(df_selected_year, '창작') - 창초 - 창재
라초 = count_season(df_selected_year, '라센 초연|라센 트아')
라재 = count_season(df_selected_year, '라센 재연')
라삼 = count_season(df_selected_year, '라센') - 라초 - 라재

시즌 = pd.DataFrame([
    {'회차': '초연', '창작': 창초, '라센': 라초},
    {'회차': '재연', '창작': 창재, '라센': 라재},
    {'회차': '삼연+', '창작': 창삼, '라센': 라삼}
])

#그래프
labels = ['창작', '라센']
categories = 시즌['회차'].tolist()

창작_values = 시즌['창작'].values.tolist()
라센_values = 시즌['라센'].values.tolist()

fig3, ax3 = plt.subplots(figsize=(5, 5))
fig3.patch.set_facecolor('none')
ax3.set_facecolor('none')

bar_width = 0.45
y = np.arange(len(labels))


colors = col_or
stacked_data = [창작_values, 라센_values]
cumulative = np.zeros(2)

for i, (label, color) in enumerate(zip(categories, colors)):
    values = [row[i] for row in stacked_data]
    bars = ax3.barh(labels, values, bar_width, left=cumulative, label=label,
                    color=color, edgecolor='#3B3838', linewidth=2)
    cumulative += values

    ax3.bar_label(
        bars,
        labels=[f'{int(v)}' if v != 0 else '' for v in values],
        label_type='center',
        color='#4D4D4D',
        fontsize=12,
        fontweight='bold'
    )

#Axis & Legend
ax3.set_ylim(-0.5, len(labels) - 0.5)
ax3.set_yticks(y)
ax3.set_yticklabels([label + '  ' for label in labels], color='#D9D9D9', fontsize=18, fontweight='bold')
ax3.invert_yaxis()
ax3.set_xticks([])

ax3.legend(categories, loc='lower center', bbox_to_anchor=(0.5, -0.326), ncol=3, frameon=False, fontsize=14, labelcolor='#D9D9D9')

for spine in ['top', 'right', 'bottom']:
    ax3.spines[spine].set_visible(False)
ax3.spines['left'].set_color('#C0C0C0')



#-------------------------------------------------------------------------------------------------------------------------------------------------------------


#배우
actor_list = (df_selected_year['캐슷'].fillna('').str.strip().str.split(' ').explode())
actor_list = actor_list[actor_list != ''].unique()  # 빈 문자열 제거

actor = []
for x in actor_list:
    filtered = df_selected_year['캐슷'].apply(lambda y: (' ' + x + ' ') in f' {y} ')
    count = filtered.sum()
    nshow = df_selected_year[filtered]['극'].nunique()
    actor.append({'배우': x, '횟수': count, '필모': nshow})

배우 = pd.DataFrame(actor)
배우['배우'] = pd.Categorical(배우['배우'], categories=actor_list, ordered=True)
배우 = 배우.sort_values(by=['횟수', '필모', '배우'], ascending=[False, False, True])
배우['배우'] = 배우['배우'].apply(lambda x: x.replace('_', ' ').replace('[', ' [').replace('(', ' ('))


actor_diff = 배우.shape[0] - df_year_before['캐슷'].str.strip().str.split().explode().nunique()

if actor_diff > 0:
    차이표시, 색상 = f'▲ {actor_diff}', '#FD6666'
elif actor_diff < 0:
    차이표시, 색상 = f'▼ {abs(actor_diff)}', '#6FB3FF'
else:
    차이표시, 색상 = '-', '#BFBFBF'

배우_text = (
    f'<p style="font-size: 17px;">{"&nbsp;" * 2}{배우.shape[0]}명</p>'
    if selected_option == '전체'
    else f'<p style="font-size: 17px;">{"&nbsp;" * 2}{배우.shape[0]}명  (<span style="font-size: 13px; color: {색상};">{차이표시}</span>)</p>'
)


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


# 극
극 = df_selected_year['극'].value_counts().reset_index()
극.columns = ['극', '횟수']

show_order = df_selected_year['극'].unique()
극['극'] = pd.Categorical(극['극'], categories=show_order, ordered=True)
극 = 극.sort_values(by=['횟수', '극'], ascending=[False, True])


장르극 = {
    '연극': df_selected_year[df_selected_year['장르'].str.contains('연극', na=False)]['극'].nunique(),
    '뮤지컬': df_selected_year[df_selected_year['장르'].str.contains('뮤지컬', na=False)]['극'].nunique(),
    '기타': df_selected_year[df_selected_year['장르'].str.contains('기타', na=False)]['극'].nunique()
}
기타극 = f", 기타 {장르극['기타']}편" if 장르극['기타'] > 0 else ''

극_text = f"<p style='font-size: 17px;'>{'&nbsp;' * 2}: 연극 {장르극['연극']}편, 뮤지컬 {장르극['뮤지컬']}편{기타극}</p>"


#-------------------------------------------------------------------------------------------------------------------------------------------------------------


연월 = '연별 정산' if selected_option == '전체' else '월별 정산'

def grid(df, column_widths):
    builder = GridOptionsBuilder.from_dataframe(df)
    for col, width in column_widths.items():
        builder.configure_column(
            col,
            width=width,
            filter=True,
            cellStyle={"fontFamily": "Freesentation, sans-serif"},
            headerStyle={"fontFamily": "Freesentation, sans-serif"}
        )
    return builder.build()

actor_grid_options = grid(배우, {'배우': 160, '횟수': 70, '필모': 70})
show_grid_options = grid(극, {'극': 230, '횟수': 70})


#Layout
left, right = st.columns([3, 2])

with left:
    with st.container():
        st.markdown(f'<p style="font-size: 22px;">《 {연월} 》</p>', unsafe_allow_html=True)
        st.pyplot(fig0)
        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<p style="font-size: 22px;">《 장르 》</p>', unsafe_allow_html=True)
        st.pyplot(fig1)
    
    with col2:
        st.markdown('<p style="font-size: 22px;">《 회전 》</p>', unsafe_allow_html=True)
        st.pyplot(fig2)

    with col3:
        st.markdown('<p style="font-size: 22px;">《 시즌 》</p>', unsafe_allow_html=True)
        st.pyplot(fig3)

fixed_height = 555
with right:
    up1, up2 = st.columns(2)
    with up1:
        st.markdown('<p style="font-size: 22px;">《 배우 》</p>', unsafe_allow_html=True)
        st.markdown(배우_text, unsafe_allow_html=True)
        AgGrid(
            배우,
            height=fixed_height,
            fit_columns_on_grid_load=True,
            theme='streamlit',
            gridOptions=actor_grid_options
        )

    with up2:
        st.markdown('<p style="font-size: 22px;">《 작품 》</p>', unsafe_allow_html=True)
        st.markdown(극_text, unsafe_allow_html=True)
        AgGrid(
            극,
            height=fixed_height,
            fit_columns_on_grid_load=True,
            theme='streamlit',
            gridOptions=show_grid_options
        )