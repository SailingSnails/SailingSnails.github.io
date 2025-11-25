from dash import Dash, html, dash_table, dcc, Input, Output
import pandas as pd
import dash_bootstrap_components as dbc

data_URL = 'https://github.com/SailingSnails/SailingSnails.github.io/raw/refs/heads/main/RawData.xlsx'
전체A = pd.read_excel(data_URL)

year_options = ['전체'] + sorted([str(x) for x in 전체A['날짜'].dt.year.unique()], reverse=True)
dropdown_options = [{'label': y + '년' if y != '전체' else '전체', 'value': y} for y in year_options]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                zoom: 75%;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id='year-dropdown',
                options=dropdown_options,
                value='전체',
                clearable=False,
                style={'marginBottom': '30px', 'width': '150px'}
            ),
            width="auto"
        ),
        dbc.Col(
            dcc.RadioItems(
                id='mode-selector',
                options=[
                    {'label': '구분X', 'value': '구분X'},
                    {'label': '구분O', 'value': '구분O'}
                ],
                value='구분X',
                inline=True,
                style={'marginBottom': '30px', 'marginLeft': '10px', 'fontSize': '16'},
                labelStyle={'marginRight': '20px'}
            ),
            width="auto",
            style={'display': 'flex', 'alignItems': 'center'}
        ),
    ], align='center'),
    html.Div(id='table-content')
], fluid=True, style={'padding': 50})


table_style = {
    "style_header": {
        "backgroundColor": "#71AD47",
        "color": "white",
        "fontWeight": "bold",
        "border": "none"
    },
    "style_table": {
        "overflowX": "auto",
        "border": "2px solid black"
    },
    "style_cell": {
        "textAlign": "center",
        "font-family": "Arial",
        "fontSize": 12,
        "borderTop": "1px solid #71AD47",
        "borderRight": "1px solid #D4D4D4",
        "color": "black",
        "padding": "0 10px"        
    }
}


def create_table(title, text, df, base_table_style):
    table_style = base_table_style.copy()

    column_width = [
            {'if': {'column_id': df.columns[0]}, 'width': '60%', 'minWidth': '60%', 'maxWidth': '60%'},
            {'if': {'column_id': df.columns[1]}, 'width': '40%', 'minWidth': '40%', 'maxWidth': '40%'},
        ]

    return html.Div([
        html.H3(title, style={'fontSize': 22}),
        html.P(text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_action='none',
            **table_style,
            style_cell_conditional=column_width,
            css=[{
                "selector": ".dash-spreadsheet tr",
                "rule": "height: 22px; min-height: 22px; max-height: 22px;"
            }]
        )
    ], style={'marginBottom': '50px'})


def create_table_3(title, text, df, base_table_style, use_622=True,
                   style_data_conditional=None, extra_components=None,
                   hidden_columns=None, extra_css=None):
    table_style = base_table_style.copy()

    if use_622:
        column_width = [
            {'if': {'column_id': df.columns[0]}, 'width': '60%', 'minWidth': '60%', 'maxWidth': '60%'},
            {'if': {'column_id': df.columns[1]}, 'width': '20%', 'minWidth': '20%', 'maxWidth': '20%'},
            {'if': {'column_id': df.columns[2]}, 'width': '20%', 'minWidth': '20%', 'maxWidth': '20%'},
        ]
    else:
        column_width = [
            {'if': {'column_id': df.columns[0]}, 'width': '50%', 'minWidth': '50%', 'maxWidth': '50%'},
            {'if': {'column_id': df.columns[1]}, 'width': '25%', 'minWidth': '25%', 'maxWidth': '25%'},
            {'if': {'column_id': df.columns[2]}, 'width': '25%', 'minWidth': '25%', 'maxWidth': '25%'},
        ]

    css_list = [{
        "selector": ".dash-spreadsheet tr",
        "rule": "height: 22px; min-height: 22px; max-height: 22px;"
    }]

    if extra_css:
        css_list.extend(extra_css)

    children_list = [
        html.H3(title, style={'fontSize': 22}),
        html.P(text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict('records'),
            page_action='none',
            **table_style,
            hidden_columns=hidden_columns if hidden_columns else [],
            style_data_conditional=style_data_conditional if style_data_conditional else [],
            style_cell_conditional=column_width,
            css=css_list
        )
    ]

    if extra_components:
        children_list.extend(extra_components)

    return html.Div(children_list, style={'marginBottom': '50px'})


def compute_tables(selected_year, selected_mode):
    if selected_year == "전체":
        전체 = 전체A.copy()
    else:
        전체 = 전체A[전체A['날짜'].dt.year == int(selected_year)].copy()
    
    #-----------
    연도 = 전체['날짜'].dt.year.value_counts(sort=False).to_frame().reset_index()
    연도.columns = ['연도', '횟수']

    연도2 = 연도.copy()
    연도2['극'] = 연도2['연도'].apply(lambda y: 전체[전체['날짜'].dt.year == y]['극'].nunique())
    연도2 = 연도2[['연도', '극', '횟수']]
    연도2_text = f'▶︎ {전체['극'].nunique()} 편, {연도2["횟수"].sum()} 회'

    전체_직관 = 전체[전체['장르'].isin(['연극', '뮤지컬', '기타'])]
    전체_집관 = 전체[전체['장르'].str.contains('중계|DVD')]
    years = 전체['날짜'].dt.year.sort_values().unique()
    연도3 = pd.DataFrame({
        '연도': years,
        '직관': 전체_직관.groupby(전체_직관['날짜'].dt.year).size().reindex(years, fill_value=0).values,
        '집관': 전체_집관.groupby(전체_집관['날짜'].dt.year).size().reindex(years, fill_value=0).values
    })
    연도3_text = html.P([
        "▶︎ 직관: ",
        html.Span(f"{연도3["직관"].sum()}", style={'color': '#0F80FF'}),
        " 회, 집관: ",
        html.Span(f"{연도3["집관"].sum()}", style={'color': '#E91E63'}),
        " 회"
    ], style={'margin': '0 0 5px 0'})

    연도2['연도'] = 연도2['연도'].astype(str) + ' 년'
    연도3['연도'] = 연도3['연도'].astype(str) + ' 년'

    표_연도2 = create_table_3("【 연도 】", 연도2_text, 연도2, table_style)
    표_연도3 = create_table_3("【 횟수 】", 연도3_text, 연도3, table_style)

    #-----------
    review_list = ['극호', '호', '평타', '불호', '극불']
    counts = 전체['RV'].value_counts().to_dict()
    show_counts = 전체.groupby('RV')['극'].nunique().to_dict()
    review_data = []
    for review in review_list:
        review_data.append({
            '후기': review,
            '횟수': counts.get(review, 0),
            '극': show_counts.get(review, 0)
        })
    후기 = pd.DataFrame(review_data)
    후기_text = f'▶︎ {후기["횟수"].sum()} 회  ({(전체['RV'].isin(['극호', '호', '평타']).mean() * 100).round(1)}%)'

    표_후기 = create_table_3("【 후기 】", 후기_text, 후기, table_style, use_622=True)

    #-----------      
    def theater(x):
        idx = x.find("(")
        return x[:idx].strip() if idx >= 0 else x.strip()
    극장 = 전체.copy()
    극장['극장'] = 극장['극장'].apply(theater)
    theater_list = 극장['극장'].unique()
    theatre = []
    for x in theater_list:
        filtered = 극장[극장['극장'] == x]
        count = filtered.shape[0]
        show = filtered['극'].nunique()
        theatre.append({'극장': x, '횟수': count, '극': show})
    극장 = pd.DataFrame(theatre).sort_values(by=['횟수', '극'], ascending=[False, False])
    dash = 극장[극장['극장'] == '-']
    if not dash.empty:
        dash_row = dash.iloc[0]
    else:
        dash_row = {'극장': '-', '횟수': '0', '극': '0'}
    dash_values = [dash_row['극장'], dash_row['횟수'], dash_row['극']]
    others = 극장[극장['극장'] != '-']
    극장 = pd.concat([others])
    극장_text = [
        "▶︎ ",
        html.Span(f"{극장.shape[0] - 1}"),
        " 곳, ",
        html.Span(f"{극장['횟수'].sum() - 극장[극장['극장'] == '-']['횟수'].sum()}", style={'color': '#0F80FF'}),
        " 회"
    ]
    max_value = 극장.loc[극장['극장'] != '-', '극'].max()
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{극}} = {}'.format(max_value),
            },
            'backgroundColor': '#FFF4DF'
        },
        {
            'if': {
                'filter_query': '{{극}} = {}'.format(max_value),
                'column_id': '극'
            },
            'fontWeight': 'bold',
            'color': '#FF6F3C',
            'backgroundColor': '#FFF4DF'
        }
    ]

    표_극장_부분 = create_table_3("【 극장 】", 극장_text, 극장, table_style, style_data_conditional=style_data_conditional, use_622=True)

    dash_row_table = html.Table(
        style={'marginTop': '-28px', 'borderCollapse': 'collapse', 'width': '100%', 'maxWidth': '400px', 'height': '22px', 'tableLayout': 'fixed'},
        children=[
            html.Tbody([
                html.Tr(
                    children=[
                        html.Td(value, style={
                            'border': '1px solid #808080',
                            'color': '#808080',
                            'fontSize': 11,
                            'padding': '0 0',
                            'textAlign': 'center',
                            'width': ['60%', '20%', '20%'][i]
                        }) for i, value in enumerate(dash_values)])])])

    표_극장 = html.Div([
        표_극장_부분,
        dash_row_table
    ], style={'marginBottom': '50px'})

    #-----------
    직관_counts = 전체_직관['RV'].value_counts().to_dict()
    직관_show_counts = 전체_직관.groupby('RV')['극'].nunique().to_dict()
    
    직관_review_data = []
    for review in review_list:
        직관_review_data.append({
            '후기': review,
            '횟수': 직관_counts.get(review, 0),
            '극': 직관_show_counts.get(review, 0)
        })
    직관후기 = pd.DataFrame(직관_review_data)

    직관후기['후기'] = pd.Categorical(직관후기['후기'], categories=review_list, ordered=True)
    직관후기 = 직관후기.sort_values('후기').reset_index(drop=True)
    
    직관후기_text = html.P([
        "▶︎ ",
        html.Span(f"{직관후기['횟수'].sum()}", style={'color': '#0F80FF'}),
        " 회 (",
        html.Span(f"{(전체_직관['RV'].isin(['극호', '호', '평타']).mean() * 100).round(1)}%"),
        ")"
    ], style={'margin': '0 0 5px 0'})

    표_직관후기 = create_table_3("【 직관 후기 】", 직관후기_text, 직관후기, table_style)

    #-----------
    집관_counts = 전체_집관['RV'].value_counts().to_dict()
    집관_show_counts = 전체_집관.groupby('RV')['극'].nunique().to_dict()
    
    집관_review_data = []
    for review in review_list:
        집관_review_data.append({
            '후기': review,
            '횟수': 집관_counts.get(review, 0),
            '극': 집관_show_counts.get(review, 0)
        })
    집관후기 = pd.DataFrame(집관_review_data)
    집관후기['후기'] = pd.Categorical(집관후기['후기'], categories=review_list, ordered=True)
    집관후기 = 집관후기.sort_values('후기').reset_index(drop=True)
    
    if not 전체_집관.empty:
        집관후기_percent = round(전체_집관['RV'].isin(['극호', '호', '평타']).mean() * 100, 1)
    else:
        집관후기_percent = 0.0
    
    집관후기_text = html.P([
        "▶︎ ",
        html.Span(f"{집관후기['횟수'].sum()}", style={'color': '#E91E63'})," 회  (",
        html.Span(f"{집관후기_percent}%)")
    ], style={'margin': '0 0 5px 0'})

    표_집관후기 = create_table_3("【 집관 후기 】", 집관후기_text, 집관후기, table_style)

    #-----------
    genre_list = ['연극', '뮤지컬', '기타']
    genre = []
    for x in genre_list:
        filtered = 전체[전체['장르'].str.contains(x)]
        count = filtered.shape[0]
        show = filtered['극'].nunique()
        genre.append({'장르': x, '극': show, '횟수': count})
    장르 = pd.DataFrame(genre)
    전체['장르0'] = 전체['장르'].apply(
        lambda x: '연극' if '연극' in x else (
            '뮤지컬' if '뮤지컬' in x else '기타')
    )
    test = 전체.groupby('극')['장르0'].nunique()
    겹 = test[test > 1]
    겹극 = 겹.index.tolist()
    장르_text = (f'▶︎ {장르['극'].sum() - 겹.shape[0]} 편, {장르['횟수'].sum()} 회')
    장르겹_text = f'   ※ 겹치는 극: {겹.shape[0]} 편'
    겹목록_text = ""
    for x in 겹극:
        겹목록_text += f"                - {x}\n"

    표_장르 = create_table_3("【 장르 】", 장르_text, 장르, table_style, use_622=True,
        extra_components=[
            html.Pre(장르겹_text, style={'fontSize': 12, 'marginBottom': '0px', 'marginTop': '5px'}),
            html.Pre(겹목록_text, style={'fontSize': 10, 'color': "#989898", 'marginTop': '3px'})
        ]
    )

    #-----------
    company_list = 전체['제작사'].str.split(', ').explode().unique()
    
    company = []
    for x in company_list:
        filtered = 전체['제작사'].apply(lambda y: x in y.split(', '))
        count = filtered.sum()
        show = 전체[filtered]['극'].nunique()
        company.append({'제작사': x, '횟수': count, '극': show})
    제작사 = pd.DataFrame(company).sort_values(by=['횟수', '극'], ascending=[False, False], ignore_index=True)
    dash = 제작사[제작사['제작사'] == '-']
    if not dash.empty:
        dash_row = dash.iloc[0]
    else:
        dash_row = {'제작사': '-', '횟수': '0', '극': '0'}
    dash_values = [dash_row['제작사'], dash_row['횟수'], dash_row['극']]
    others = 제작사[제작사['제작사'] != '-']
    제작사 = pd.concat([others], ignore_index= True)
    제작사_text = f'▶︎ {others.shape[0]} 곳'
    if '극' in 제작사.columns:
        max_value = 제작사.loc[제작사['제작사'] != '-', '극'].max()
    else:
        max_value = 0
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{극}} = {}'.format(max_value),
            },
            'backgroundColor': '#FFF4DF'
        },
        {
            'if': {
                'filter_query': '{{극}} = {}'.format(max_value),
                'column_id': '극'
            },
            'fontWeight': 'bold',
            'color': '#FF6F3C',
            'backgroundColor': '#FFF4DF'
        }
    ]

    표_제작사_부분 = create_table_3("【 제작사 】", 제작사_text, 제작사, table_style, use_622=True,
        style_data_conditional=style_data_conditional
    )

    dash_row_table = html.Table(
        style={'marginTop': '-28px', 'borderCollapse': 'collapse', 'width': '100%', 'maxWidth': '400px', 'height': '22px', 'tableLayout': 'fixed'},
        children=[
            html.Tbody([
                html.Tr(
                    children=[
                        html.Td(value, style={
                            'border': '1px solid #808080',
                            'color': '#808080',
                            'fontSize': 11,
                            'padding': '0 0',
                            'textAlign': 'center',
                            'width': ['60%', '20%', '20%'][i]
                        }) for i, value in enumerate(dash_values)])])])

    표_제작사 = html.Div([
        표_제작사_부분,
        dash_row_table
    ], style={'marginBottom': '50px'})

    #-----------
    offgen = []
    for x in genre_list:
        filtered = 전체_직관[전체_직관['장르'] == x]
        show = filtered['극'].nunique()
        count = filtered.shape[0]
        offgen.append({'직관 장르': x, '극': show, '횟수': count})
    직관_장르 = pd.DataFrame(offgen)
    전체_직관 = 전체_직관.copy()
    전체_직관['장르0'] = 전체_직관['장르'].apply(
        lambda x: '연극' if '연극' in x else (
            '뮤지컬' if '뮤지컬' in x else '기타'
        )
    )
    offtest = 전체_직관.groupby('극')['장르0'].nunique()
    직겹 = offtest[offtest > 1]
    직겹극 = 직겹.index.tolist()
    직관_장르_text = [
        "▶︎ ",
        html.Span(f"{직관_장르['극'].sum() - 직겹.shape[0]}", style={'color': "#0F80FF"}),
        " 편, ",
        html.Span(f"{직관_장르['횟수'].sum()}", style={'color': "#0F80FF"}),
        " 회"
    ]
    직관_장르겹_text = f'   ※ 겹치는 극: {직겹.shape[0]} 편'
    직관_겹목록_text = ""
    for x in 직겹극:
        직관_겹목록_text += f"                - {x}\n"

    표_직관_장르 = create_table_3("【 직관 장르 】", 직관_장르_text, 직관_장르, table_style, use_622=False,
        extra_components=[
            html.Pre(직관_장르겹_text, style={'fontSize': 12, 'marginBottom': '0px', 'marginTop': '5px'}),
            html.Pre(직관_겹목록_text, style={'fontSize': 10, 'color': "#989898", 'marginTop': '3px'})
        ]
    )

    #-----------
    list = 전체['제작사'].str.split(', ').explode().unique()
    com = []
    for x in list:
        off_filtered = 전체_직관['제작사'].apply(lambda y: x in y.split(', '))
        on_filtered = 전체_집관['제작사'].apply(lambda y: x in y.split(', '))
        
        off_count = off_filtered.sum()
        on_count = on_filtered.sum()
        
        off_show = 전체_직관[off_filtered]['극'].nunique()
        if not 전체_집관.empty and '극' in 전체_집관.columns:
            on_show = 전체_집관[on_filtered]['극'].nunique()
        else:
            on_show = 0
        
        count_str = f"{off_count} (+{on_count})"
        show_str = f"{off_show} (+{on_show})"
        
        com.append({
            '제작사': x,
            '횟수': count_str,
            '극': show_str,
            '직관': off_count,
            '집관': on_count,
            '직관극': off_show,
            '집관극': on_show
        })
    onfc = pd.DataFrame(com)
    onfc = onfc.sort_values(by=['직관', '집관', '직관극', '집관극'], ascending=False)
    dash = onfc[onfc['제작사'] == '-']
    if not dash.empty:
        dash_row = dash.iloc[0]
    else:
        dash_row = {'제작사': '-', '횟수': '0 (+0)', '극': '0 (+0)'}
    dash_values = [dash_row['제작사'], dash_row['횟수'], dash_row['극']]
    others = onfc[onfc['제작사'] != '-']
    직집제작사 = pd.concat([others], ignore_index=True)[['제작사', '횟수', '직관극', '극']]
    직집제작사_text = (f'▶︎ 직관: {(others["직관"] >= 1).sum()} 곳')

    max_value = 직집제작사.loc[직집제작사['제작사'] != '-', '직관극'].max()
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{직관극}} = {}'.format(max_value),
            },
            'backgroundColor': '#FFF4DF'
        },
        {
            'if': {
                'filter_query': '{{직관극}} = {}'.format(max_value),
                'column_id': '극'
            },
            'fontWeight': 'bold',
            'color': '#FF6F3C',
            'backgroundColor': '#FFF4DF'
        }
    ]

    표_직집제작사_부분 = create_table_3("【 제작사 】", 직집제작사_text, 직집제작사, table_style, use_622=False,
        style_data_conditional=style_data_conditional,
        hidden_columns=['직관극'],
        extra_css=[{
            "selector": ".show-hide",
            "rule": "display: none"
        }]
    )

    dash_row_table = html.Table(
        style={'marginTop': '-28px', 'borderCollapse': 'collapse', 'width': '100%', 'maxWidth': '400px', 'height': '22px', 'tableLayout': 'fixed'},
        children=[
            html.Tbody([
                html.Tr(
                    children=[
                        html.Td(value, style={
                            'border': '1px solid #808080',
                            'color': '#808080',
                            'fontSize': 11,
                            'padding': '0 0',
                            'textAlign': 'center',
                            'width': ['50%', '25%', '25%'][i]
                        }) for i, value in enumerate(dash_values)])])])

    표_직집제작사 = html.Div([
        표_직집제작사_부분,
        dash_row_table
    ], style={'marginBottom': '50px'})

    #-----------
    극 = 전체['극'].value_counts(sort = False).to_frame().reset_index()
    극.columns = ['극', '횟수']
    극 = 극.sort_values(by= ['횟수'], ascending=False)
    극_text = (f'▶︎ {극.shape[0]} 편, {극['횟수'].sum()} 회')

    unique_sorted = 극['횟수'].drop_duplicates().sort_values(ascending=False).values
    max_value = unique_sorted[0] if len(unique_sorted) > 0 else None
    second_value = unique_sorted[1] if len(unique_sorted) > 1 else None
    third_value = unique_sorted[2] if len(unique_sorted) > 2 else None

    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{횟수}} = {}'.format(max_value),
            },
            'backgroundColor': '#FEA3A3'
        },
        {
            'if': {
                'filter_query': '{{횟수}} = {}'.format(second_value),
            },
            'backgroundColor': '#FECC66'
        },
        {
            'if': {
                'filter_query': '{{횟수}} = {}'.format(third_value),
            },
            'backgroundColor': '#FFF4DF'
        },
    ]

    표_극 = html.Div([
        html.H3("【 극 】", style={'fontSize': 22}),
        html.P(극_text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in 극.columns],
            data=극.to_dict('records'),
            page_action='none',
            css=[{
                "selector": ".dash-spreadsheet tr",
                "rule": "height: 22px; min-height: 22px; max-height: 22px;"
            }],
            **table_style,
            style_data_conditional=style_data_conditional
        )
    ], style={'marginBottom': '50px'})

    #-----------
    show_list = 전체['극'].unique()
    onfshow = []
    for x in show_list:
        off = 전체_직관['극'].apply(lambda y: x == y).sum()
        on = 전체_집관['극'].apply(lambda y: x == y).sum()
        onoff = f'{off} (+{on})'
        onfshow.append({'극': x, '직관': off, '집관': on, '직관 (+집관)': onoff})
    직집극 = pd.DataFrame(onfshow).sort_values(by= ['직관', '집관'], ascending=False)
    직집극_text = [
        "▶︎ ",
        html.Span(f"{(직집극['직관'] > 0).sum()}", style={'color': '#0F80FF'}),
        " 편, ",
        html.Span(f"{직집극['직관'].sum()}", style={'color': '#0F80FF'}),
        " 회"
    ]

    unique_sorted = 직집극['직관'].drop_duplicates().sort_values(ascending=False).values
    max_value = unique_sorted[0] if len(unique_sorted) > 0 else None
    second_value = unique_sorted[1] if len(unique_sorted) > 1 else None
    third_value = unique_sorted[2] if len(unique_sorted) > 2 else None

    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{직관}} = {}'.format(max_value),
            },
            'backgroundColor': '#FEA3A3'
        },
        {
            'if': {
                'filter_query': '{{직관}} = {}'.format(second_value),
            },
            'backgroundColor': '#FECC66'
        },
        {
            'if': {
                'filter_query': '{{직관}} = {}'.format(third_value),
            },
            'backgroundColor': '#FFF4DF'
        },
    ]

    표_직집극 = html.Div([
        html.H3("【 극 】", style={'fontSize': 22}),
        html.P(직집극_text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in 직집극.columns],
            data=직집극.to_dict('records'),
            page_action='none',
            hidden_columns=['직관', '집관'],
            css=[{
                "selector": ".dash-spreadsheet tr",
                "rule": "height: 22px; min-height: 22px; max-height: 22px;"
            }, {
                "selector": ".show-hide",
                "rule": "display: none"
            }],
            **table_style,
            style_data_conditional=style_data_conditional
        )
    ], style={'marginBottom': '50px'})

    #-----------
    actor_list = 전체['캐슷'].str.strip().str.split(' ').explode().unique().tolist()
    actor = []
    for x in actor_list:
        filtered = 전체['캐슷'].apply(lambda y: (' '+x+' ') in y)
        count = filtered.sum()
        nshow = 전체[filtered]['극'].nunique()
        show = ' \u00A0|\u00A0 '.join(전체[filtered]['극'].unique())
        actor.append({'배우': x, '횟수': count, '필모': nshow, '전체 필모': show})
    배우 = pd.DataFrame(actor).sort_values(by=['횟수', '필모'], ascending=False)
    배우['배우'] = 배우['배우'].str.replace('_', ' ').str.replace(r'\s*\[.*?\]', '', regex=True)
    배우_text = (f'▶︎ {배우.shape[0]} 명')

    max_value = 배우['필모'].max()
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{필모}} = {}'.format(max_value),
            },
            'backgroundColor': '#FFF4DF'
        },
        {
            'if': {
                'filter_query': '{{필모}} = {}'.format(max_value),
                'column_id': '필모'
            },
            'fontWeight': 'bold',
            'color': '#FF6F3C',
            'backgroundColor': '#FFF4DF'
        }
    ]

    style_cell_conditional = [
        {'if': {'column_id': '전체 필모'},
         'textAlign': 'left',
         'fontSize' : 10
        },
        {'if': {'column_id': 배우.columns[0]}, 'width': '20%', 'minWidth': '20%', 'maxWidth': '20%'},
        {'if': {'column_id': 배우.columns[1]}, 'width': '5%', 'minWidth': '5%', 'maxWidth': '5%'},
        {'if': {'column_id': 배우.columns[2]}, 'width': '5%', 'minWidth': '5%', 'maxWidth': '5%'},
        {'if': {'column_id': 배우.columns[3]}, 'width': '70%', 'minWidth': '70%', 'maxWidth': '70%'},
    ]

    표_배우 = html.Div([
        html.H3("【 배우 】", style={'fontSize': 22}),
        html.P(배우_text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in 배우.columns],
            data=배우.to_dict('records'),
            page_action='none',
            css=[{
                "selector": ".dash-spreadsheet tr",
                "rule": "height: 22px; min-height: 22px; max-height: 22px;"
            }, {
                "selector": ".show-hide",
                "rule": "display: none"
            }],
            **table_style,
            style_data_conditional=style_data_conditional,
            style_cell_conditional=style_cell_conditional
        )
    ], style={'marginBottom': '50px'})

    #-----------
    list = 전체['캐슷'].str.strip().str.split(' ').explode().unique().tolist()
    onfactor = []
    for x in list:
        off_filtered = 전체_직관['캐슷'].apply(lambda y: (' '+x+' ') in y) 
        on_filtered = 전체_집관['캐슷'].apply(lambda y: (' '+x+' ') in y)
        s1 = off_filtered.sum()
        s2 = on_filtered.sum()
        onoff = f'{s1} (+{s2})'
        s3 = 전체_직관[off_filtered]['극'].nunique()
        filtered_df = 전체_집관[on_filtered]
        s4 = filtered_df['극'].nunique() if not filtered_df.empty and '극' in filtered_df.columns else 0

        nonfshow = f'{s3} (+{s4})'
        offshows = ' \u00A0|\u00A0 '.join(전체_직관[off_filtered]['극'].unique())
        if not filtered_df.empty and '극' in filtered_df.columns:
            onshows = ', '.join(filtered_df['극'].unique())
        else:
            onshows = ''

        if onshows:
            onfshows = f"{offshows} ( + {onshows} )"
        else:
            onfshows = offshows 
        s = s1*1000000000+s2*1000000+s3*1000+s4
        onfactor.append({
            '배우': x, 
            '직관 (+집관)': onoff, 
            '직관 필모' : s3,
            '필모': nonfshow, 
            '전체 필모': onfshows,
            '소팅용' : s
            })
    onfactor = pd.DataFrame(onfactor).sort_values('소팅용', ascending=False)
    직집배우 = onfactor[['배우', '직관 (+집관)', '직관 필모', '필모', '전체 필모']]
    직집배우['배우'] = 직집배우['배우'].str.replace('_', ' ').str.replace(r'\s*\[.*?\]', '', regex=True)
    직집배우_text = (f'▶︎ 직관: {(onfactor['소팅용']>1000000000).sum()} 명')

    max_value = 직집배우['직관 필모'].max()
    style_data_conditional = [
        {
            'if': {
                'filter_query': '{{직관 필모}} = {}'.format(max_value),
            },
            'backgroundColor': '#FFF4DF'
        },
        {
            'if': {
                'filter_query': '{{직관 필모}} = {}'.format(max_value),
                'column_id': '필모'
            },
            'fontWeight': 'bold',
            'color': '#FF6F3C',
            'backgroundColor': '#FFF4DF'
        }
    ]

    style_cell_conditional = [
        {'if': {'column_id': '전체 필모'},
         'textAlign': 'left',
         'fontSize' : 10
        },
        {'if': {'column_id': 직집배우.columns[0]}, 'width': '20%', 'minWidth': '20%', 'maxWidth': '20%'},
        {'if': {'column_id': 직집배우.columns[1]}, 'width': '5%', 'minWidth': '5%', 'maxWidth': '5%'},
        {'if': {'column_id': 직집배우.columns[3]}, 'width': '5%', 'minWidth': '5%', 'maxWidth': '5%'},
        {'if': {'column_id': 직집배우.columns[4]}, 'width': '70%', 'minWidth': '70%', 'maxWidth': '70%'},
    ]

    표_직집배우 = html.Div([
        html.H3("【 배우 】", style={'fontSize': 22}),
        html.P(직집배우_text, style={'fontSize': 16, 'margin': 5}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in 직집배우.columns],
            data=직집배우.to_dict('records'),
            page_action='none',
            hidden_columns=['직관 필모'],
            css=[{
                "selector": ".dash-spreadsheet tr",
                "rule": "height: 22px; min-height: 22px; max-height: 22px;"
            }, {
                "selector": ".show-hide",
                "rule": "display: none"
            }],
            **table_style,
            style_data_conditional=style_data_conditional,
            style_cell_conditional=style_cell_conditional
        )
    ], style={'marginBottom': '50px'})

    #-----------
    nth_list = ['자첫자막', '자둘', '자셋 이상']
    nth = []
    for x in nth_list:
        filtered = 극['횟수'].apply(
            lambda x: '자첫자막' if x == 1 else ('자둘' if x == 2 else '자셋 이상'))
        show = (filtered == x).sum()
        count = 극[filtered == x]['횟수'].sum()
        nth.append({
            '회전': x,
            '극': show,
            '횟수': count
        })
    회전 = pd.DataFrame(nth)
    회전_text = (f'▶︎ {회전['극'].sum()} 편, {회전['횟수'].sum()} 회')

    표_회전 = create_table_3("【 회전 】", 회전_text, 회전, table_style, use_622=False)

    #-----------
    창작초 = 전체['시즌'].str.contains('창작 초연|창작 트아').sum()
    창작재 = 전체['시즌'].str.contains('창작 재연').sum()
    창작삼 = 전체['시즌'].str.contains('창작').sum() - 창작초 - 창작재
    라센초 = 전체['시즌'].str.contains('라센 초연|라센 트아').sum()
    라센재 = 전체['시즌'].str.contains('라센 재연').sum()
    라센삼 = 전체['시즌'].str.contains('라센').sum() - 라센초 - 라센재
    season = [
        {'시즌': '초연 & 트아', '창작': 창작초, '라센': 라센초},
        {'시즌': '재연', '창작': 창작재, '라센': 라센재},
        {'시즌': '삼연 이상', '창작': 창작삼, '라센': 라센삼}
    ]
    시즌 = pd.DataFrame(season)
    시즌_text = (f'▶︎ {시즌['창작'].sum()+시즌['라센'].sum()} 회')

    표_시즌 = create_table_3("【 시즌 】", 시즌_text, 시즌, table_style, use_622=False)

    #-----------
    직관극 = 전체_직관['극'].nunique()
    직관횟수 = 전체_직관.shape[0]
    집관극 = 전체_집관['극'].nunique()
    집관횟수 = 전체_집관.shape[0]
    onfline = [
        ['직관', 직관극, 직관횟수],
        ['집관', 집관극, 집관횟수]
    ]
    유형 = pd.DataFrame(onfline)
    유형.columns = ['유형', '극', '횟수']
    직집겹극 = 직집극[직집극['직관'] * 직집극['집관'] >0].sort_index()['극']
    유형_text = (f'▶︎ {유형['극'].sum()-직집겹극.shape[0]} 편, {유형['횟수'].sum()} 회')
    직관겹_text = (f'   ※ 겹치는 극: {직집겹극.shape[0]} 편')
    직관겹목록_text = ""
    for x in 직집겹극:
        직관겹목록_text += f"           - {x}\n"

    style_data_conditional = [
        {
            'if': {
                'filter_query': '{유형} = "직관"',
                'column_id': '횟수'
            },
            'color': '#0F80FF'
        }
    ]

    표_유형 = create_table_3("【 유형 】", 유형_text, 유형, table_style, use_622=False,
        style_data_conditional=style_data_conditional,
        extra_components=[
            html.Pre(직관겹_text, style={'fontSize': 12, 'marginBottom': '0px', 'marginTop': '5px'}),
            html.Pre(직관겹목록_text, style={'fontSize': 10, 'color': "#989898", 'marginTop': '3px'})
        ]
    )

    style_data_conditional = [
        {
            'if': {
                'filter_query': '{유형} = "직관"',
                'column_id': '극'
            },
            'color': '#0F80FF'
        },
        {
            'if': {
                'filter_query': '{유형} = "직관"',
                'column_id': '횟수'
            },
            'color': '#0F80FF'
        },
        {
            'if': {
                'filter_query': '{유형} = "집관"',
                'column_id': '극'
            },
            'color': '#E91E63'
        },
        {
            'if': {
                'filter_query': '{유형} = "집관"',
                'column_id': '횟수'
            },
            'color': '#E91E63'
        }
    ]

    표_유형2 = create_table_3("【 유형 】", 유형_text, 유형, table_style, use_622=False,
        style_data_conditional=style_data_conditional,
        extra_components=[
            html.Pre(직관겹_text, style={'fontSize': 12, 'marginBottom': '0px', 'marginTop': '5px'})
        ]
    )

    #-----------
    직관극 = 직집극[직집극['직관']>0].sort_index()
    직관극['직관회전'] = 직관극['직관'].apply(
            lambda x: '자첫자막' if x == 1 else ( '자둘' if x == 2 else '자셋 이상')
        )
    offnth = []
    for x in nth_list:
        show = (직관극['직관회전'] == x).sum()
        count = 직관극[(직관극['직관회전'] == x)]['직관'].sum()
        offnth.append({
            '직관 회전': x,
            '극': show,
            '횟수': count
        })
    직관회전 = pd.DataFrame(offnth)
    직관회전_text = html.P([
        "▶︎ ",
        html.Span(f"{직관회전['극'].sum()}", style={'color': '#0F80FF'}),
        " 편, ",
        html.Span(f"{직관회전['횟수'].sum()}", style={'color': '#0F80FF'}),
        " 회"
    ], style={'fontSize': 16, 'margin': 5})

    표_직관회전 = create_table_3("【 직관 회전 】", 직관회전_text, 직관회전, table_style, use_622=False)

    #-----------
    창작초 = 전체_직관['시즌'].str.contains('창작 초연|창작 트아').sum()
    창작재 = 전체_직관['시즌'].str.contains('창작 재연').sum()
    창작삼 = 전체_직관['시즌'].str.contains('창작').sum() - 창작초 - 창작재
    라센초 = 전체_직관['시즌'].str.contains('라센 초연|라센 트아').sum()
    라센재 = 전체_직관['시즌'].str.contains('라센 재연').sum()
    라센삼 = 전체_직관['시즌'].str.contains('라센').sum() - 라센초 - 라센재
    offseason = [
        {'시즌': '초연 & 트아', '창작': 창작초, '라센': 라센초},
        {'시즌': '재연', '창작': 창작재, '라센': 라센재},
        {'시즌': '삼연 이상', '창작': 창작삼, '라센': 라센삼}
    ]
    직관시즌 = pd.DataFrame(offseason)
    직관시즌_text = 직관시즌_text = html.P([
        "▶︎ ",
        html.Span(f"{직관시즌['창작'].sum() + 직관시즌['라센'].sum()}", style={'color': '#0F80FF'}),
        " 회"
    ], style={'margin': '0 0 5px 0'})

    표_직관시즌 = create_table_3("【 직관 시즌 】", 직관시즌_text, 직관시즌, table_style, use_622=False)

    #-----------
    online_list = ['무료 중계', '유료 중계', 'DVD']
    online = []
    for x in online_list:
        filtered = 전체_집관[전체_집관['장르'].str.contains(x)]
        count = filtered.shape[0]
        show = filtered['극'].nunique()
        online.append({'집관': x, '극': show, '횟수': count})
    집관 = pd.DataFrame(online)
    전체_집관 = 전체_집관.copy()
    전체_집관['장르0'] = 전체_집관['장르'].apply(
        lambda x: '무료 중계' if '무료 중계' in x else (
            '유료 중계' if '유료 중계' in x else 'DVD')
    )
    ontest = 전체_집관.groupby('극')['장르0'].nunique()
    집겹 = ontest[ontest > 1]
    집겹극 = 집겹.index.tolist()
    집관_text = html.P([
        "▶︎ ",
        html.Span(f"{집관['극'].sum() - 집겹.shape[0]}", style={'color': '#E91E63'}),
        " 편, ",
        html.Span(f"{집관['횟수'].sum()}", style={'color': '#E91E63'}),
        " 회"
    ], style={'margin': '0 0 5px 0'})
    집겹_text = f'   ※ 겹치는 극: {집겹.shape[0]} 편'
    집겹목록_text = ""
    for x in 집겹극:
        집겹목록_text += f"              - {x}\n"

    표_집관 = create_table_3("【 집관 】", 집관_text, 집관, table_style, use_622=False,
        extra_components=[
            html.Pre(집겹_text, style={'fontSize': 12, 'marginBottom': '0px', 'marginTop': '5px'}),
            html.Pre(집겹목록_text, style={'fontSize': 10, 'color': "#989898", 'marginTop': '3px'})
        ]
    )

    #-----------
    if selected_mode == '구분X':
        return [
            dbc.Row([
                dbc.Col([표_연도2, 표_후기, 표_극장], style={'minWidth': '240px', 'maxWidth': '240px', 'width': '240px'}),
                dbc.Col([표_장르, 표_제작사], style={'minWidth': '270px', 'maxWidth': '270px', 'width': '270px'}),
                dbc.Col([표_유형, 표_회전, 표_시즌], style={'minWidth': '250px', 'maxWidth': '250px', 'width': '250px'}),
                dbc.Col([표_극], style={'minWidth': '330px', 'maxWidth': '330px', 'width': '330px'}),
                dbc.Col([표_배우], style={'minWidth': '730px', 'maxWidth': '730px', 'width': '730px'}),
            ], style={"overflowX": "auto", "flexWrap": "nowrap"})
        ]
    else:
        return [
            dbc.Row([
                dbc.Col([표_연도3, 표_직관후기, 표_집관후기], style={'minWidth': '240px', 'maxWidth': '240px', 'width': '240px'}),
                dbc.Col([표_직관_장르, 표_직집제작사], style={'minWidth': '270px', 'maxWidth': '270px', 'width': '270px'}),
                dbc.Col([표_유형2, 표_직관회전, 표_직관시즌, 표_집관], style={'minWidth': '250px', 'maxWidth': '250px', 'width': '250px'}),
                dbc.Col([표_직집극], style={'minWidth': '330px', 'maxWidth': '330px', 'width': '330px'}),
                dbc.Col([표_직집배우], style={'minWidth': '730px', 'maxWidth': '730px', 'width': '730px'}),
            ], style={"overflowX": "auto", "flexWrap": "nowrap"})
        ]

@app.callback(
    Output('table-content', 'children'),
    [Input('year-dropdown', 'value'),
     Input('mode-selector', 'value')]
)

def update_tables(selected_year, selected_mode):
    return compute_tables(selected_year, selected_mode)

if __name__ == "__main__":
    app.run(debug=True)