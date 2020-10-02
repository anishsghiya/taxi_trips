import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import plotly.express as px
import time
import calendar


# data_loc = ("E:/Vit/Sem - 5/Project/Data_viz/nyc_taxi_data_viz/train.csv", nrows=10000)
@st.cache(persist = True)
def data_loader():
    data = pd.read_csv("E:/Vit/Sem - 5/Project/Data_viz/nyc_taxi_data_viz/train.csv", nrows=10000)
    data['counter'] = 0
    data['pickup_dow'] = pd.DatetimeIndex(data['pickup_datetime']).weekday
    data['dropoff_dow'] = pd.DatetimeIndex(data['dropoff_datetime']).weekday
    #Extracting hour
    data['pickup_hour'] = pd.DatetimeIndex(data['pickup_datetime']).hour
    data['dropoff_hour'] = pd.DatetimeIndex(data['dropoff_datetime']).hour
    return data

st.beta_set_page_config(page_title='DV_Project')
st.sidebar.markdown("# Dv Project")
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("", ('Home', 'Datasets', 'EDA', 'ML', 'About Us'))

df = data_loader()

if page == 'Home':
    '''
    # Visualizing taxi trips
    '''
    image = Image.open('img_home.jpg')
    st.image(image, caption='', width = 500, use_column_width=False )

elif page == 'Datasets':
    '''
    ## Dataset
    '''
    is_check = st.checkbox("Display Complete Data")
    if is_check:
        st.write(df.head())
    teams = st.sidebar.multiselect("Enter clubs", df['vendor_id'].unique())
    variables = st.sidebar.multiselect("Enter the variables", df.columns)

    selected_club_data = df[(df['vendor_id'].isin(teams))]
    two_clubs_data = selected_club_data[variables]
    club_data_is_check = st.checkbox("Display the data of selected clubs")
    if club_data_is_check:
        st.write(two_clubs_data)

elif page == 'EDA':
    '''
    ## Variable plotting
    '''
    plot_x = ['Number of rides', '']
    plot_var = st.selectbox("Enter variable to be plotted", plot_x)

    if plot_var == 'Number of rides':
        plot_ys = ['Vendor', 'Passenger', 'Day,hour', 'Month']

        plot_y = st.selectbox("Enter variable to be plotted", plot_ys)

        if plot_y == 'Passenger':
            passenger_dist = df.groupby(by='passenger_count',as_index=False).counter.count()
            fig = px.bar(passenger_dist, 
                        x="passenger_count", y="counter", 
                        title='Number of rides based on number of passengers', 
                        text='counter',
                        width=800, height=700)
            fig.update_traces(marker_color='#008000', opacity=0.8)

            # fig.update_layout(template = 'plotly_dark')
            st.plotly_chart(fig)

        elif plot_y == 'Day,hour':
            pickup_time = df.groupby(['pickup_dow','pickup_hour'],as_index=False)[['counter']].count()
            pickup_time['pickup_dow'] = pickup_time['pickup_dow'].apply(lambda x: calendar.day_abbr[x])
            fig = px.treemap(pickup_time, path=['pickup_dow','pickup_hour'], values='counter',
                            color='counter', hover_data=['pickup_hour','counter'],
                            color_continuous_scale='Blues', title='Number of rides per hour')
            st.plotly_chart(fig)

        elif plot_y == 'Month':
            image = Image.open('C:/Users/ANISH/Desktop/Dev/Nyc_taxi/Data_Vis_NYCabs/Visualizations/Rides_vs_Month_Line.png')
            st.image(image, caption='Rides_vs_Month_Line', use_column_width=False )

        elif plot_y == 'Vendor':
            df = data_loader()
            vendor_distributions = df.groupby(by='vendor_id',as_index=False).counter.count()
            sizes = [vendor_distributions.counter[0],vendor_distributions.counter[1]]
            labels = ['Vendor 1','Vendor 2']
            explode = (0.1, 0)
            colors = ['#66b3ff','yellow']
            fig = plt.figure(figsize= (8,8))
            plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                    shadow=True, startangle=90)
            plt.title('Distribution of rides based on vendor',fontsize = 20)
            plt.axis('equal')
            plt.tight_layout()
            st.pyplot(fig)

            '''
            Data visualization is the graphic representation of data. It involves producing images that communicate relationships among 
            the represented data to viewers of the images. This communication is achieved through the use of a systematic mapping between graphic 
            marks and data values in the creation of the visualization
            '''
    st.markdown("## Graph visualisations")
    test_data = pd.DataFrame()
    test_data['lat'] = df['pickup_latitude']
    test_data['lon'] = df['pickup_longitude']
    st.map(test_data)

elif page == 'ML' :
    '''
    # Machine Learning

    '''

elif page == 'About Us':
    st.write("Project developed by : ")
    image = Image.open('C:/Users/ANISH/Desktop/Facebook_profile.jpg')
    st.image(image, caption='Anish', width = 100, use_column_width=False )

 st.pydeck_chart(pdk.Deck(
     map_style='mapbox://styles/mapbox/light-v9',
     initial_view_state=pdk.ViewState(
         latitude=37.76,
         longitude=-122.4,
         zoom=11,
         pitch=50,
     ),
     layers=[
         pdk.Layer(
            'HexagonLayer',
            data=df,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
         ),
         pdk.Layer(
             'ScatterplotLayer',
             data=df,
             get_position='[lon, lat]',
             get_color='[200, 30, 0, 160]',
             get_radius=200,
         ),
     ],
 ))