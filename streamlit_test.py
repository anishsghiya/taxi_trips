import  os
import  warnings
import  time
import  calendar

import  streamlit           as st
import  pandas              as pd
import  numpy               as np
import  matplotlib.pyplot   as plt
import  plotly.express      as px
import  pydeck              as pdk
import  seaborn             as sns

from    PIL                            import Image
from    yellowbrick.model_selection    import FeatureImportances
from    sklearn.linear_model           import Lasso

warnings.simplefilter("ignore")

@st.cache(persist = True)
def data_loader():
    data = pd.read_csv("E:/Vit/Sem - 5/Project/Data_viz/nyc_taxi_data_viz/train.csv", nrows=10000)
    data['counter'] = 0
    data['pickup_datetime'] = pd.DatetimeIndex(data['pickup_datetime'])
    data['pickup_dow'] = pd.DatetimeIndex(data['pickup_datetime']).weekday
    data['dropoff_dow'] = pd.DatetimeIndex(data['dropoff_datetime']).weekday
    data['pickup_hour'] = pd.DatetimeIndex(data['pickup_datetime']).hour
    data['dropoff_hour'] = pd.DatetimeIndex(data['dropoff_datetime']).hour
    data['pickup_month'] = pd.DatetimeIndex(data['dropoff_datetime']).month
    return data

st.beta_set_page_config(page_title='DV_Project')
st.sidebar.markdown("# Dv Project")
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("", ('Home', 'Datasets', 'EDA', 'ML', 'About Us'))

df = data_loader()
cwd = os.getcwd()

if page == 'Home':
    '''
    # Visualizing taxi trips
    '''
    
    path = cwd + '\Visualizations\img_home.jpg'
    image = Image.open(path)
    st.image(image, caption='', width = 500, use_column_width=False )

elif page == 'Datasets':
    '''
    ## Dataset
    '''
    is_check = st.checkbox("Display Complete Data")
    if is_check:
        st.write(df.head(15))
    teams = st.sidebar.selectbox("Enter Vendor", df['vendor_id'].unique())
    variables = st.sidebar.multiselect("Enter the variables to view the raw data", df.columns)
    selected_club_data = df[(df['vendor_id'] == teams)]
    two_clubs_data = selected_club_data[variables]
    club_data_is_check = st.checkbox("Display the data of selected variables of the particular vendor")
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
    '''
    ## Graph Visualiztions
    '''
    hour_choice = st.slider("Hour of choice", 0, 23)
    test_data = pd.DataFrame()
    test_data['latitude'] = df['pickup_latitude']
    test_data['longitude'] = df['pickup_longitude']
    test_data['date/time'] = df['pickup_datetime']
    test_data['pickup_hour'] = df['pickup_hour']
    test_data = test_data[test_data['pickup_hour'] == hour_choice]
    if st.checkbox("Show raw data", False):
        st.subheader("Raw data by minute between %i:00 and %i:00" % (hour_choice, (hour_choice + 1) % 24))
        st.write(test_data.head(15))
    
    # st.sidebar.write("Hello")
    if st.sidebar.button('Interesting Viz'):
        st.sidebar.write('Why hello there')
    '''
    ### 2D Visualization
    '''

    st.map(test_data)

    '''
    ### 3D Visualization
    '''
    midpoint = (np.average(test_data["latitude"]), np.average(test_data["longitude"]))
    st.write(pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state={
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 11,
            "pitch": 50,
        },
        layers=[
            pdk.Layer(
            "HexagonLayer",
            data=test_data[['date/time', 'latitude', 'longitude']],
            get_position=["longitude", "latitude"],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
            ),
            pdk.Layer(
                "TextLayer",
                test_data,
                pickable=True,
                get_position="coordinates",
                get_text="name",
                get_size=16,
                get_color=[255, 255, 255],
                get_angle=0,
                # Note that string constants in pydeck are explicitly passed as strings
                # This distinguishes them from columns in a data set
                get_text_anchor="'middle'",
                get_alignment_baseline="'center'",
            ),

        ],
    ))
    
    '''
    ## Correlation of various variables
    '''
    train = df.copy()
    train = train.drop(['counter'],axis=1)
    f,ax = plt.subplots(figsize = (10,10))
    sns.heatmap(train.corr(),annot=True,cmap='RdYlGn',linewidths=0.2,annot_kws={'size':10})
    fig=plt.gcf()
    fig.set_size_inches(18,15)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    st.pyplot(f)

elif page == 'ML' :
    '''
    # Machine Learning

    '''
    path_vis = cwd + '\Visualizations'
    path_lasso = path_vis + '\lasso'
    path_elasticnet = path_vis + '\elasticnet'
    plot_x = ['Lasso', 'ElasticNet']
    plot_var = st.selectbox("Enter the ML model which you would like to visualize", plot_x).lower()
    if plot_var == 'lasso':
        path_ftimp = path_lasso + '_ftimp.png'
        image = Image.open(path_ftimp)
        st.image(image, caption='Lasso Feature Importance', width = 500, use_column_width=True )
    if plot_var == 'elasticnet':
        path_ftimp = path_elasticnet + '_ftimp.png'
        image = Image.open(path_ftimp)
        st.image(image, caption='ElasticNet Feature Importance', width = 350, use_column_width=True )
    
    # # Create a new figure
    # fig = plt.figure()
    # ax = fig.add_subplot()

    # # Title case the feature for better display and create the visualizer
    # #labels = list(map(lambda s: s.title(), features))
    # viz = FeatureImportances(Lasso(), ax=ax, stack = False, relative=False)

    # # Fit and show the feature importances
    # viz.fit(x_train, y_train)
    # viz.poof()



elif page == 'About Us':
    st.write("Project developed by : ")
    image = Image.open('C:/Users/ANISH/Desktop/Facebook_profile.jpg')
    st.image(image, caption='Anish', width = 100, use_column_width=False )

