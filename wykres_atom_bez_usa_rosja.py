import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np

pio.templates.default = "plotly_dark"

file_path = 'Nuclear_warheads_modified_PL.csv'
data_long = pd.read_csv(file_path, encoding='ISO-8859-2')
data_long['Year'] = data_long['Year'].astype(int)

data_long = data_long[~data_long['Country'].isin(['USA', 'Rosja'])]
data_long.reset_index(drop=True, inplace=True)
data_long.fillna(0, inplace=True)

nuclear_events = {
    "1945": "USA zrzuca<br> bomby atomowe na<br> Hiroszimę i Nagasaki.",
    "1947": "Początek zimnej wojny",
    "1949": "ZSRR testuje pierwszą<br> bombę atomową <br>'Pierwszy Błysk'.",
    "1952": "Wielka Brytania przeprowadza pierwszy<br> test nuklearny na Wyspach Montebello.",
    "1960": "Francja eksploduje swoją <br>pierwszą bombę atomową na Saharze.",
    "1962": "Kryzys kubański, <br>napięty konflikt między USA a ZSRR.",
    "1964": "Chiny testują swoją pierwszą<br> bombę atomową 'Projekt 596'.",
    "1968": "Otwarcie do podpisu Traktatu<br> o nierozprzestrzenianiu broni jądrowej (NPT).",
    "1974": "Indie przeprowadzają test nuklearny<br> 'Uśmiechnięty Budda' w Pokhran.",
    "1986": "Izrael prawdopodobnie posiada nawet do 200 głowic nuklearnych, <br>według informacji Mordechaja Vanunu.",
    "1991": "Koniec zimnej wojny",
    "2006": "Korea Północna zaczyna testować broń nuklearną."
}

fig = go.Figure()
colors = fig.layout.template.layout.colorway

frames = []
for year in sorted(data_long['Year'].unique()):
    frame_data = data_long[data_long['Year'] <= year]

    if str(year) in nuclear_events:
        shapes = []
        event_points = []
        annotations = []
        annotations.append(dict(
            x=year,
            y=data_long['Warheads'].max() * 1.05,
            xref="x",
            yref="y",
            yanchor="bottom",
            text=nuclear_events[str(year)],
            showarrow=False,
            font=dict(size=14, color="white"),
            align="center",
            bgcolor="black",
            bordercolor="white"
        ))
        annotations.append(dict(
            x=year,
            y=data_long['Warheads'].max() * 1.05,
            xref="x",
            yref="y",
            yanchor="top",
            text='<b>' + str(year) + '<b>',
            showarrow=False,
            font=dict(size=18, color="white"),
            align="center",
            bgcolor="black"
        ))
        shapes.append(dict(
            type="line",
            x0=year,
            y0=0,
            x1=year,
            y1=data_long['Warheads'].max() * 1.05,
            line=dict(color="lightgrey", width=2, dash="dash")
        ))

        event_data = frame_data[frame_data['Year'] == year]
        max_warheads_country = event_data.sort_values(by='Warheads', ascending=False).iloc[0]
        event_points.append(go.Scatter(
            x=[year],
            y=[max_warheads_country['Warheads']],
            mode='markers',
            marker=dict(color="lightgrey", size=10, symbol="diamond"),
            text='Największa liczba głowic nuklearncyh',
            hoverinfo='text',
            showlegend=False
        ))
    last_points = []

    country_annotations = []
    for country in frame_data[frame_data['Year'] == year].sort_values(by='Warheads', ascending=True)['Country'].unique():
        country_data = frame_data[frame_data['Country'] == country]
        final_warheads = country_data.iloc[-1]['Warheads']
        if np.isnan(final_warheads):
            continue

        offset = 0
        while any(abs(final_warheads + offset - y) < 30 for y in last_points):
            offset += 20

        last_points.append(final_warheads + offset)
        max_warheads_country_data = frame_data[frame_data['Year'] == year].sort_values(by='Warheads', ascending=False).iloc[0]
        max_warheads_country = max_warheads_country_data['Country'] if max_warheads_country_data['Warheads'] != 0.0 else ''
        country_annotations.append(dict(
            x=year,
            y=final_warheads,
            xref="x",
            yref="y",
            xanchor="left",
            yanchor="middle",
            text=country,
            showarrow=True,
            arrowhead=0,
            arrowwidth=2,
            arrowcolor='black',
            ax=50,
            ay=-offset,
            font=dict(size=12, color=colors[frame_data[frame_data['Country'] == country]['Color'].index[0]]),
            bgcolor="black",
            bordercolor="yellow" if country == max_warheads_country else "black",
            borderwidth=1.5
        ))

    frames.append(go.Frame(
        data=[go.Scatter(x=frame_data[frame_data['Country'] == country]['Year'],
                         y=frame_data[frame_data['Country'] == country]['Warheads'],
                         mode='lines+markers', name=country, customdata=[country]*len(frame_data['Country']),
                         hovertemplate='<b>Kraj</b>: %{customdata}<br>' + '<b>Rok</b>: %{x}<br>' + '<b>Liczba głowic</b>: %{y}<extra></extra>')
              for country in frame_data['Country'].unique()] + event_points,
        name=str(year),
        layout=go.Layout(annotations=annotations + country_annotations, shapes=shapes)
    ))

initial_year = sorted(data_long['Year'].unique())[0]
initial_data = data_long[data_long['Year'] == initial_year]
for country in initial_data['Country'].unique():
    country_data = initial_data[initial_data['Country'] == country]
    fig.add_trace(go.Scatter(x=country_data['Year'], y=country_data['Warheads'], mode='lines+markers', name=country))

if str(initial_year) in nuclear_events:
    event_data = initial_data
    max_warheads_country = event_data.loc[event_data['Warheads'].idxmax()]
    fig.add_trace(go.Scatter(
        x=[initial_year],
        y=[max_warheads_country['Warheads']],
        mode='markers',
        marker=dict(color="lightgrey", size=10, symbol="diamond"),
        text=[nuclear_events[str(initial_year)]],
        hoverinfo="text",
        showlegend=False
    ))

max_warheads = data_long['Warheads'].max()

rounded_max = np.ceil(max_warheads / 100) * 100

tickvals = np.linspace(0, rounded_max, 5)

fig.update_layout(
    title=dict(text='Liczba głowic jądrowych w czasie według kraju (bez Rosji i USA)', y=0.96, yref='container', yanchor='bottom'),
    xaxis=dict(title='', range=[data_long['Year'].min(), data_long['Year'].max()], showticklabels=False, showgrid=False),
    yaxis=dict(title='', range=[0, data_long['Warheads'].max() * 1.05], tickmode='array', tickvals=tickvals),
    font_family="Courier New",
    showlegend=False,
    margin=dict(r=200),
    updatemenus=[dict(type='buttons', showactive=False,
                      buttons=[dict(label='Odtwórz',
                                    method='animate',
                                    args=[None, dict(frame=dict(duration=1000, redraw=True),
                                                     fromcurrent=True, mode='immediate')]),
                               dict(label='Pauza',
                                    method='animate',
                                    args=[[None], dict(frame=dict(duration=0, redraw=True),
                                                       mode='immediate')])],
                y=0.9, yanchor='top')],
    sliders=[dict(steps=[dict(method='animate',
                              args=[[str(year)], dict(mode='immediate',
                                                      frame=dict(duration=3000 if str(year) in nuclear_events else 1000, redraw=False),
                                                      transition=dict(duration=500))],
                              label=str(year)) for year in sorted(data_long['Year'].unique())],
                transition=dict(duration=500, easing="linear-in-out"), currentvalue=dict(visible=False),
                x=0, xanchor='left', y=0.02, yanchor='top')]
)

fig.frames = frames

linear_animated_line_html_file_path = "Nuclear_Warheads_Line_Chart_Without_USA_Russia.html"
fig.write_html(linear_animated_line_html_file_path, auto_open=False)

print(f"Animated line chart saved to {linear_animated_line_html_file_path}")
