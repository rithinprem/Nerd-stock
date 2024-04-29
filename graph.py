import plotly.express as px
import plotly.io as pio
import pandas as pd

def plot(df, flag):
    fig = px.line(df,
                  x='Timestamp',
                  y='Price',
                  title='Stock Price Chart',
                  labels={'Price': 'Price (Rs)', 'Timestamp': 'Time'},
                  template='plotly_white',  # Clean, good for financial charts
                  range_x=[df['Timestamp'].min(), df['Timestamp'].max()],  # Set x-axis range
                  range_y=[df['Price'].min(), df['Price'].max()]  # Set y-axis range
                  )

    fig.update_layout(  
        plot_bgcolor='white',  # Clean background
        xaxis=dict(spikecolor="#8f919d",
                   showline=True,
                   showgrid=True,
                   showticklabels=True,
                   linecolor='#8f919d',  # Adds line bordering the x-axis
                   linewidth=1,
                   ticks='outside',
                   tickfont=dict(
                       family='GrowwSans, NotoSans, system-ui',
                       size=12,
                       color='#44475b')
                   ),

        yaxis=dict(spikecolor="#8f919d",
                   showgrid=True,  # Turn off the grid lines
                   showline=True,
                   showticklabels=True,
                   linecolor='#8f919d',
                   linewidth=1,
                   ticks='outside',
                   tickfont=dict(
                       family='GrowwSans, NotoSans, system-ui',
                       size=12,
                       color='#44475b')
                   ),

        autosize=True,
        margin=dict(autoexpand=True,
                    l=100,
                    r=20,
                    t=110,
                    ),
        showlegend=False,
        hoverlabel=dict(bgcolor='rgba(205, 255, 205, 0.5)',
                        font_family="GrowwSans, NotoSans, system-ui",
                        font_color='black',
                        bordercolor='rgb(255,255,255,0)',
                        namelength=-1,  # Prevent name truncation
                        align='left',  # Align label to the left
                        )
    )

    hover_template = '<b>Date</b>: %{x}<br>'+'<b>Price:</b> \u20B9%{y:.2f}'
    fig.update_xaxes(spikemode="across", spikethickness=0.5,spikecolor='black')
    fig.update_yaxes(spikemode="across", spikethickness=0.5,spikecolor='black')
    fig.update_traces(hovertemplate=hover_template,
                      line_color=('red' if flag == -1 else '#00b386'),  # Set line color
                      fill='tozeroy',  # Fill area under the curve
                      fillcolor=('rgba(255,0,0,0.3)' if flag == -1 else 'rgba(0,179,134,0.3)'),  # Set fill color
                      )

    print(flag)
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    graphHTML = pio.to_html(fig, full_html=False)

    return graphHTML

