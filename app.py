from curses import tigetflag
import random
import numpy as np
import pandas as pd

import base64
import plotly.express as px


# ========
# GET DATA
# ========

def create_plotting_df(df_obj, c_light, distance_col: str='aphelion', timeout_col: str='minutes', light_size: float=1):
    """
    Return a pandas dataframe w/ the data to plot.
    """
    # farthest object
    max_dist = df_obj[distance_col].max()
    # time for light to reach farthest object
    # adding 2 time points at 0 and n+1
    times = int(max_dist/c_light)+2
    # 
    light_dist = [i*c_light for i in range(0, times)]
    
    n_object = len(df_obj)
    df_con = pd.concat([df_obj]*times)
    df_con[timeout_col] = sum([[i]*n_object for i in range(0,times)],[])
    df_con['Y_axis'] = [0]*len(df_con)
    
    # df light
    light_size = df_con['radius'].median()*light_size
    df_light = pd.DataFrame(zip(['Light']*times,
                                light_dist,
                                [light_size]*times,
                                range(0,times),
                                [0.1]*times),
                            columns = df_con.columns)
    df_plot = pd.concat([df_con, df_light], axis=0)
    df_plot.sort_values(by = [timeout_col], inplace=True)
    df_plot.reset_index(drop=True, inplace=True)
    
    # calculate plot marker areas
    df_plot['area'] = df_plot.radius.apply(lambda r: np.pi*(r**2))
    sun_st = df_plot.area.max()
    df_plot['area'] = [i if i >= sun_st*0.9 else i*500 for i in iter(df_plot['area'])]
    
    # calculate AU
    au = 149597871
    df_plot['AU'] = [i/au for i in df_plot[distance_col]]

    # create a text column for annotation
    keep_text = []
    for e,s,a,m in zip(df_plot.object, df_plot.aphelion, df_plot.AU, df_plot.minutes):
        if e not in ['Sun', 'Light']:
            keep_text.append(e+'<br>'+str(round(s/c_kmm,2))+' m'+'<br>'+str(round(a,1))+' AU')
        elif e == 'Light':
            keep_text.append(e+'<br>'+str(m)+' m')
        else:
            keep_text.append(e)
    df_plot['text'] = keep_text
    
    return df_plot

# =================
# INTERACTIVE PLOT
# =================

def interactive_plot(df_plot):
    """
    Return a plotly figure object.
    """
    fig = px.scatter(df_plot, x="aphelion", y="Y_axis", animation_group="object",
                    size = "area", animation_frame="minutes",
                    hover_name="object", text = "text",
                    range_x=[df_plot['aphelion'].min()-df_plot['aphelion'].max()*0.06,
                            df_plot['aphelion'].max()*1.04],
                    range_y=[-0.2, 0.25],
                    color = 'object',
                    color_discrete_map=dict_colors,
                    labels={"aphelion": "Distance(km)"}
                    )
    #update text and marker lines
    fig.update_traces(textposition='bottom center',
                    textfont_color='white',
                    marker=dict(opacity=1, line=dict(width=0))
                    )
    #insert wallpaper
    image_filename = 'images/wallpaper.jpeg'
    plotly_logo = base64.b64encode(open(image_filename, 'rb').read())
    fig.update_layout(xaxis=dict(showgrid=False, visible=True, zeroline=False),
                    yaxis=dict(showgrid=False, visible=False),
                    images= [dict(source='data:image/png;base64,{}'.format(plotly_logo.decode()),
                                    xref="paper", yref="paper",
                                    x=0, y=1,
                                    sizex=1, sizey=1,
                                    xanchor="left", yanchor="top",
                                    sizing="stretch",
                                    opacity = 0.99,
                                    layer="below")],
                    legend_title = 'Object',
                    title='<b>Aphelion Distance</b>')
    # play speed
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 500
    fig.show()



if __name__ == '__main__':
        
    dict_colors = {'Sun':'#FFC404', 'Light':'white',
                'Mercury':'#BeBeBe', 'Venus':'#F9AB46', 
                'Earth':'#0494cc', 'Mars':'#D14734', 
                'Jupiter':'#FE9C37', 'Saturn':'#FDA369', 
                'Uranus':'#3B97B6', 'Neptune':'#1a5fa1'}


    inner_planets = pd.DataFrame(zip(
        ['Sun', 'Mercury', 'Venus', 'Earth', 'Mars'],
        [0, 69817445, 108942780, 152098233, 249232432],
        [696340, 2440, 6052, 6371, 3390, ]),
        columns = ['object', 'aphelion', 'radius'])

    outter_planets = pd.DataFrame(zip(
        ['Sun', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
        [0, 816001807, 1503509229, 3006318143, 4537039826],
        [696340, 69911, 58232, 25362, 24622 ]),
        columns = ['object', 'aphelion', 'radius'])


    # df_obj = random.choice([inner_planets, outter_planets])
    # df_obj = inner_planets
    df_obj = outter_planets
    df_obj


    # light speed in meter/second
    c = 299792458
    c_kmm = (c/1000)*60         # >>  kilometer/minute

    df_plot = create_plotting_df(df_obj, c_kmm, 'aphelion', 'minutes', 1)

    interactive_plot(df_plot)