import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
import pydeck as pdk


data = pd.read_csv(r"IE.csv")
df = data.sample(n = 3001 , random_state = 55014)

st.set_page_config(layout = "wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html = True)
image = Image.open(r"C:\Users\ishud\Downloads\zarla-smart-cargo-1x1-2400x2400-20220325-fjbg9qbqh67tppwvvg6r.webp")



col1, col2 = st.columns([0.1,0.9])
with col1:
    st.image(image,width=100)
    
html_title = """
    <style>
    .title-test {
        font-wight:bold;
        padding:5px;
        border-radius:6px;
    }
    </style>
    <center><h1 class="title-dash">Trade Data Dashboard</h1><center>"""
    
with col2:
    st.markdown(html_title, unsafe_allow_html = True)
    

st.sidebar.header("Please Filter here")
country = st.sidebar.multiselect(
    "Select the Country here",
    options = df['Country'].unique(),
    # default = df["Country"].unique()
)

# st.dataframe(df)

shipping = st.sidebar.radio(
    "Select the Shipping_method :",
    options = df['Shipping_Method'].unique(),
    #default = df['Automation'].unique()
)

category = st.sidebar.multiselect(
    "Select the Category:",
    options = df['Category'].unique(),
    #default = df['Automation'].unique()
)


#apply the sidebar selections to the dataframe
df_select = df.query(
    "Country== @country & Shipping_Method ==@shipping & Category ==@category"
)

#if dataframe is empty == throw an error
if df_select.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() ##-- halt streamlit from further execution

# st.dataframe(df_select)

average_value = int(df_select['Value'].mean())
average_weight = int(df_select['Weight'].mean())
average_quantity = int(df_select['Quantity'].mean())

first_col,second_col,third_col = st.columns(3)
with first_col:
    st.subheader('Average Value')
    st.subheader(f"US $ {average_value:,}")
with second_col:
    st.subheader('Average Weight')
    st.subheader (f"{average_weight:,}")
with third_col:
    st.subheader('Average Quantity')
    st.subheader(f"{average_quantity:,}")
    
st.divider()


col3, col4 = st.columns([0.6,0.4])

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
    
    #calculate max and minimum price in selection
    max_price = df_select['Category'].max()
    min_price = df_select['Category'].min()
    
    
    left_column, middle_column, right_column = st.columns([0.2,0.5,0.3])
    with left_column:
        min_price = df_select['Quantity'].min()
        left_column.metric(
            label = "Min Category Quantity Selected: ",
            value = int(min_price/1000)
        
    )

    
    with left_column:
        max_price = df_select['Quantity'].max()
        left_column.metric(
            label = "Max Category Quantity Selected: ",
            value = int(max_price/1000)
        
    )

    
    with left_column:
        median_price = df_select['Quantity'].median()
        left_column.metric(
            label = "Median Category Quantity Selected: ",
            value = int(median_price/1000)
        
    )

    #middle plot
    middle_column.plotly_chart(fig_seat_dist, use_container_width=True)
    
with col4:
    # st.bar_chart(df, x = "Payment_Terms", y = "Category", horizontal = True)
    #plot manufacturer distribution
    
    # price_per_make = df_select.groupby(by=["Payment_Terms"])[["Category"]].sum().sort_values(by="")
    df_grouped = df.groupby(["Payment_Terms", "Category"]).agg({"Value": "count"}).reset_index()
    make_price_fig = px.bar(
        df_grouped,
        x = "Category",
        y="Value",
        color ="Payment_Terms",
        # orientation="h",
        title="<b>Payment Terms vs Category</b>",
        # color_discrete_sequence=["#0083B8"],
        template="seaborn",
        # hover_data={"count": True}
        
)

    make_price_fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=(dict(showgrid=False))
)


    # left_column, right_column = st.columns(2)
    # left_column.plotly_chart(fig_color_price, use_container_width=True)
    col4.plotly_chart(make_price_fig)

# st.divider()
    
    
col5,col6 = st.columns([0.4,0.6])

violin_fig = px.violin(df, x="Shipping_Method", y="Weight", box=True, points="all", title="Weight Distribution by Shipping Method", template = "ggplot2")
col5.plotly_chart(violin_fig)


with col6:
#     data = {
#         'X_values': df['Category'],
#         'Y_values': df['Weight'],
#         'Category': ['A', 'B', 'A', 'B', 'A']
#     }
#     df = pd.DataFrame(data)

# # Scatter plot using Altair
#     scatter_plot = alt.Chart(df).mark_circle(size=60).encode(
#         x='X_values',
#         y='Y_values',
#         color='Category',
#         tooltip=['X_values', 'Y_values', 'Category']
#     ).properties(
#         title='Scatter Plot of X vs Y',
#         width=600,
#         height=400
#     )

# # Streamlit: Display the plot
#     st.altair_chart(scatter_plot, use_container_width=True)

# Filter by year
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    year_list = sorted(df['Date'].dt.year.unique(), reverse=True)
    selected_year = st.selectbox('Select a year', year_list)

# Filter data based on the selected year
    df_selected_year = df[df['Date'].dt.year == selected_year]
    
    if country:
        df_selected_year = df_selected_year[df_selected_year['Country'].isin(country)]
    
    # Helper Functions
    def format_value(val):
        return f"${val / 1e6:.1f}M" if val > 1e6 else f"${val / 1e3:.1f}K"

    def calculate_transaction_difference(input_df, input_year):
        selected_year_data = input_df[input_df['Date'].dt.year == input_year].reset_index()
        previous_year_data = input_df[input_df['Date'].dt.year == input_year - 1].reset_index()
        selected_year_data['value_difference'] = selected_year_data.Value.sub(previous_year_data.Value, fill_value=0)
        return pd.concat([selected_year_data.Country, selected_year_data.Value, selected_year_data.value_difference], axis=1).sort_values(by="value_difference", ascending=False)



# Display key metrics in card layout
    df_transaction_diff_sorted = calculate_transaction_difference(df, selected_year)

    first_country = df_transaction_diff_sorted.Country.iloc[0] if selected_year > df['Date'].dt.year.min() else '-'
    first_country_value = format_value(df_transaction_diff_sorted.Value.iloc[0])
    first_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[0]) if selected_year > df['Date'].dt.year.min() else '-'

    last_country = df_transaction_diff_sorted.Country.iloc[-1] if selected_year > df['Date'].dt.year.min() else '-'
    last_country_value = format_value(df_transaction_diff_sorted.Value.iloc[-1])
    last_country_delta = format_value(df_transaction_diff_sorted.value_difference.iloc[-1]) if selected_year > df['Date'].dt.year.min() else '-'

# Line chart for transactions over time
    line_chart = alt.Chart(df_selected_year).mark_line().encode(
        x=alt.X('Date:T', axis=alt.Axis(title='Date')),
        y=alt.Y('Value:Q', axis=alt.Axis(title='Transaction Value')),
        color=alt.Color('Category:N', legend=alt.Legend(title="Category"))
    ).properties(width=600, height=400)
    st.altair_chart(line_chart, use_container_width=True)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("##### Created by Isha Gupta | Import-Export Dashboard © 2024", unsafe_allow_html=True)



