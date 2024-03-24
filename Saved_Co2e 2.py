import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import csv
import altair as alt

# Set page title and favicon
st.set_page_config(
    page_title="CO2e Saved Through Recycling",
    page_icon="🌱",
    layout="wide"
)

np.set_printoptions(threshold=np.inf)
pd.set_option('display.width', 300)  # Setting the character display width
pd.set_option('display.max_rows', None)  # Setting the maximum lines to be displayed
pd.set_option('display.max_columns', None)  # Set to show maximum columns, None to show all columns.


# Load your dataset
@st.cache_data
def load_data():
    # with open('co2e_saved_data.csv', 'r', encoding='utf-8') as f:
    data = pd.read_csv("DataSource-Based on bins.csv")
    # data['Date'] = pd.to_datetime(data['Date'])  # Convert 'Date' column to datetime
    return data


data = load_data()
print(data)

st.title("𓊆𓊆𓊆⇨ Trash CO2e Calculator ⇦𓊇𓊇𓊇 ")

st.markdown(
    """
   <style>
   [data-testid="stSidebar"][aria-expanded="true"]{
       min-width: 250px;
       max-width: 400px;
   }
   """,
    unsafe_allow_html=True,
)
# Sidebar layout options
with st.sidebar:
    st.markdown('Tip：You can see a basic overview of the data included in our project by selecting the spam category.')
    # Categories
    Category = data['Categories'].unique().tolist()
    select_value = st.selectbox(label='Choose waste category', options=Category)
    Category_data = data.loc[data['Categories'] == select_value]
    Bins = Category_data['Type of bin'].unique().tolist()
    st.markdown('### Type of bin : ' + str(Bins))
    Saved_Co2 = Category_data['Saved Co2e(kg)/Per tonne recycled'].sum()
    st.markdown('### Saved_Co2 all : ' + str(Saved_Co2))
    Waste_amount = Category_data.shape[0]
    st.markdown('### Waste_amount : ' + str(Waste_amount))

# # Call the method directly on the container object:：
tab1, tab2, tab3 = st.tabs(["🗃 DataSet", "📈 Charts", "♻︎ Recycle"])
with tab1:
    tab1.subheader("Shown below is our dataset:")
    # tab1.write(data)
    use_container_width = 'false'
    df = pd.DataFrame(data)
    # List all columns
    columns = df.columns.tolist()
    # Let the user select which columns to display
    selected_columns = st.multiselect('Select data columns:', columns, default=columns)

    # st.properties(width=500, height=300)
    # Displays the appropriate data table according to the user's selection
    tab1.write(df[selected_columns])

    # st.expander - Expandable/collapsible multi-element containers
    with st.expander("Check notes on the use of this project's data."):
        st.write("""
            You can download our data as needed, but please do not use it for commercial purposes!
        """)
        # File Download Link
        # file_url = "http://www.example.com/DataSource-Based on bins.csv"
        # st.write() Add a link to download the file in
        # st.write(f"Click[here]({file_url})download the file")
with tab2:
    tab2.subheader("Shown below is a visualisation of our data:")

    # Setting up legend colour customisation
    data = pd.read_csv("DataSource-Based on bins.csv")
    scale = alt.Scale(
        domain=["Blue bin", "Brown bin", "Yellow bin", "Glass containers"],
        range=["#0055ff", "#494936", "#ffd439", "#aec7e8"],
    )
    color = alt.Color("Type of bin:N", scale=scale)

    # Create two selectors：
    # - brush，Brush selection for top panel
    # - click，Multi-click for bottom panel
    brush = alt.selection_interval(encodings=["x"])
    click = alt.selection_multi(encodings=["color"])
    # use_container_width=True
    points = (
        alt.Chart()
        .mark_circle()
        .encode(
            alt.X("Waste", title="Waste"),
            alt.Y(
                "Saved Co2e(kg)/Per tonne recycled:Q",
                title="Saved Co2e(kg)/Per tonne recycled",
                scale=alt.Scale(domain=[0, 30]),
            ),
            color=alt.condition(brush, color, alt.value("lightgray")),
            size=alt.Size("Saved Co2e(kg)/Per tonne recycled:Q", scale=alt.Scale(range=[50, 200])),
        )
        .properties(width=550, height=300)
        .add_selection(brush)
        .transform_filter(click)
    )

    bars = (
        alt.Chart(title="Click on the bars to see their details!")
        .mark_bar()
        .encode(
            x="count()",
            y="Type of bin:N",
            color=alt.condition(click, color, alt.value("lightgray")),
        )
        .transform_filter(brush)
        .properties(
            width=600,
        )
        .add_selection(click)
    )

    chart2 = alt.vconcat(points, bars, data=data, title="Saved Co2e(kg) of bins").interactive()
    st.altair_chart(chart2, theme="streamlit", use_container_width=True)


    def get_chart(data):
        # The hover in the function defines a selection set for determining the closest rubbish on mouse hover.
        hover = alt.selection_single(
            fields=["Waste"],
            nearest=True,
            on="mouseover",
            empty="none",
        )
        # The LINES section creates a line graph
        # where the x-axis represents the name of the waste and the y-axis represents the amount of CO2 saved
        lines = (
            alt.Chart(data, title="Save Co2e(kg) of waste")
            .mark_line()
            .encode(
                x="Waste",
                y="Saved Co2e(kg)/Per tonne recycled",
                color="Categories",
            )
        )

        # Draw points on the line, and highlight based on selection
        points = lines.transform_filter(hover).mark_circle(size=80)

        # Draw a rule at the location of the selection
        tooltips = (
            alt.Chart(data)
            .mark_rule()
            .encode(
                x="Waste",
                y="Saved Co2e(kg)/Per tonne recycled",
                # scale=alt.Scale(domain=[0, 30]),
                opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
                tooltip=[
                    alt.Tooltip("Waste", title="Waste"),
                    alt.Tooltip("Saved Co2e(kg)/Per tonne recycled", title="Saved Co2e(kg)"),
                ],
            )
            .add_selection(hover)
            .properties(width=600, height=450)
        )
        # Combine all charts together and enable interactive features.
        return (lines + points + tooltips).interactive()

    chart = get_chart(data)
    st.altair_chart(
        # (chart + annotation_layer).interactive(),
        chart.interactive(),
        use_container_width=True
    )
with tab3:
    col1, col2 = st.columns(2)
    # use_container_width = 'false'
    with col1:
        Bin_list = data['Type of bin'].unique()
        Bin_type = st.selectbox(
            "Which kind of bin do you want to explore?",
            Bin_list
        )
        part_df = data[data['Type of bin'] == Bin_type]
        st.write(f"You selected {Bin_type},the data contains {len(part_df)} rows")
        # st.write(part_df)
        # st.write('You selected {}.'.format(Bin_type))
        st.write(f"According to your filter, the waste of {Bin_type} are below")
        sub_df = part_df[['Saved Co2e(kg)/Per tonne recycled', 'Waste']]
        bars = (
            alt.Chart(sub_df)
            .mark_bar().encode(
                y="Saved Co2e(kg)/Per tonne recycled",
                x="Waste:N",
                # color=alt.condition(click, color, alt.value("lightgray")),
            ).properties(
                width=200,
                height=400
            )
        ).interactive()
        st.altair_chart(bars, use_container_width=True)
    with col2:
        waste_list = data['Waste'].unique()
        waste = st.selectbox(
            "Choose your waste:",
            waste_list
        )
        # title = st.text_input()
        part_df = data[data['Waste'] == waste]
        st.write(f"The details of {waste} are here:")
        st.write(part_df)
        ca = part_df['Saved Co2e(kg)/Per tonne recycled']
        n = np.double(ca.values)
        # st.write(f"The Categories of  {waste} is {ca.values}")
        # st.text_input('Input the weight of waste(kg):', value='', key=None)
        number = n * st.number_input('Input the weight of waste(tonne):', min_value=0.0)
        # st.write('The amount of Co2e(kg) saved is ', number)
        st.write('The amount of Co2e(kg) saved is ')
        # st.title(number)
        st.markdown(
            "<h2 style='color: #55ff00; text-align: center; font-size:65px'>"+str(number)+"kg</h2>",
            unsafe_allow_html=True
        )
