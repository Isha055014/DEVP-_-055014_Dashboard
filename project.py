import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pydeck as pdk

# The set_page_config() must be the first Streamlit command.
st.set_page_config(layout="wide")

import streamlit as st
from PIL import Image
import pandas as pd
import requests
from io import BytesIO

# Define the raw URLs of the files on GitHub
csv_url = "https://raw.githubusercontent.com/Isha055014/DEVP-_-055014_Dashboard/main/IE.csv"
image_url = "https://raw.githubusercontent.com/Isha055014/DEVP-_-055014_Dashboard/main/i.webp"

# Load CSV directly from GitHub
@st.cache
def load_data():
    df = pd.read_csv(csv_url)
    return df

# Load Image directly from GitHub
@st.cache
def load_image():
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    return img

# Display the data
# st.write("Displaying data from GitHub:")
df = load_data()
# st.write(df.head())  # Display first few rows of the DataFrame

# Display the image



# # Upload CSV file
# uploaded_file = st.file_uploader(r"IE.csv", type="csv")
# if uploaded_file is not None:
#     data = pd.read_csv(uploaded_file)
#     st.write("CSV uploaded successfully!")
#     df = data.sample(n=3001, random_state=55014)
#     st.write(df.head(1))

# # Layout adjustments
# st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# # Upload Image file
# uploaded_image = st.file_uploader("i.webp", type="webp")
# if uploaded_image is not None:
#     image = Image.open(uploaded_image)
#     # st.image(image, width=100)
# else:
#     st.write("Please upload an image.")

col1, col2 = st.columns([0.1, 0.9])
with col1:
    # st.write("Displaying image from GitHub:")
    image = load_image()
    st.image(image, width=100)
        # if uploaded_image is not None:
        #    st.image(image, width=100)
        # else:
        #    st.write("No image to display.")

html_title = """
    <style>
    .title-test {
        font-weight:bold;
        padding:5px;
        border-radius:6px;
    }
    </style>
    <center><h1 class="title-dash">Trade Data Dashboard</h1><center>"""

with col2:
    st.markdown(html_title, unsafe_allow_html=True)

st.sidebar.header("Please Filter here")
country = st.sidebar.multiselect(
    "Select the Country here",
    options=df['Country'].unique(),
)

shipping = st.sidebar.radio(
    "Select the Shipping_method:",
    options=df['Shipping_Method'].unique(),
)

category = st.sidebar.multiselect(
    "Select the Category:",
    options=df['Category'].unique(),
)

# Apply the sidebar selections to the dataframe
df_select = df.query(
    "Country== @country & Shipping_Method ==@shipping & Category ==@category"
)

# Halt execution if no data based on filter settings
if df_select.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop()

average_value = int(df_select['Value'].mean())
average_weight = int(df_select['Weight'].mean())
average_quantity = int(df_select['Quantity'].mean())

first_col, second_col, third_col = st.columns(3)
with first_col:
    st.subheader('Average Value')
    st.subheader(f"US $ {average_value:,}")
with second_col:
    st.subheader('Average Weight')
    st.subheader(f"{average_weight:,}")
with third_col:
    st.subheader('Average Quantity')
    st.subheader(f"{average_quantity:,}")

st.divider()

col3, col4 = st.columns([0.6, 0.4])
with col3:
    seat_make_dist = df.groupby(by=["Category"])[['Quantity']].agg('count').sort_values(by='Category')

    fig_seat_dist = px.pie(
        seat_make_dist,
        values="Quantity",
        title="Category Distribution",
        names=seat_make_dist.index,
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.4
    )

    fig_seat_dist.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    left_column, middle_column, right_column = st.columns([0.2, 0.5, 0.3])
    with left_column:
        min_price = df_select['Quantity'].min()
        left_column.metric(
            label="Min Category Quantity Selected: ",
            value=int(min_price / 1000)
        )

    with left_column:
        max_price = df_select['Quantity'].max()
        left_column.metric(
            label="Max Category Quantity Selected: ",
            value=int(max_price / 1000)
        )

    with left_column:
        median_price = df_select['Quantity'].median()
        left_column.metric(
            label="Median Category Quantity Selected: ",
            value=int(median_price / 1000)
        )

    middle_column.plotly_chart(fig_seat_dist, use_container_width=True)

with col4:
    df_grouped = df.groupby(["Payment_Terms", "Category"]).agg({"Quantity": "count"}).reset_index()
    make_price_fig = px.bar(
        df_grouped,
        x="Category",
        y="Quantity",
        color="Payment_Terms",
        title="<b>Payment Terms vs Category</b>",
        template="seaborn"
    )

    make_price_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
    )

    col4.plotly_chart(make_price_fig)

col5, col6 = st.columns([0.4, 0.6])

violin_fig = px.violin(df, x="Shipping_Method", y="Weight", box=True, points="all", title="Weight Distribution by Shipping Method", template="ggplot2")
col5.plotly_chart(violin_fig)

with col6:
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    year_list = sorted(df['Date'].dt.year.unique(), reverse=True)
    selected_year = st.selectbox('Select a year', year_list)

    df_selected_year = df[df['Date'].dt.year == selected_year]
    
    if country:
        df_selected_year = df_selected_year[df_selected_year['Country'].isin(country)]
    
    def format_value(val):
        return f"${val / 1e6:.1f}M" if val > 1e6 else f"${val / 1e3:.1f}K"

    def calculate_transaction_difference(input_df, input_year):
        selected_year_data = input_df[input_df['Date'].dt.year == input_year].reset_index()
        previous_year_data = input_df[input_df['Date'].dt.year == input_year - 1].reset_index()
        selected_year_data['value_difference'] = selected_year_data.Value.sub(previous_year_data.Value, fill_value=0)
        return pd.concat([selected_year_data.Country, selected_year_data.Value, selected_year_data.value_difference], axis=1).sort_values(by="value_difference", ascending=False)

    df_transaction_diff_sorted = calculate_transaction_difference(df, selected_year)

    first_country = df_transaction_diff_sorted.Country.iloc[0] if selected_year > df['Date'].dt.year.min() else '-'
    first_country_value = format_value(df_transaction_diff_sorted.Value.iloc[0])
    first_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[0]) if selected_year > df['Date'].dt.year.min() else '-'

    last_country = df_transaction_diff_sorted.Country.iloc[-1] if selected_year > df['Date'].dt.year.min() else '-'
    last_country_value = format_value(df_transaction_diff_sorted.Value.iloc[-1])
    last_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[-1]) if selected_year > df['Date'].dt.year.min() else '-'

    line_chart = alt.Chart(df_selected_year).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='Transaction Value')),
        color=alt.Color('Category:N', legend=alt.Legend(title="Category"))
    ).properties(width=600, height=400)
    st.altair_chart(line_chart, use_container_width=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("##### Created by Isha Gupta | Trade Data (Import-Export) Dashboard © 2024", unsafe_allow_html=True)



