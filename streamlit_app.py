# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title("🥤Customize Your Smoothie!🥤")
st.write(
    """Choose your fruits you want in your custom Smoothie!
    """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on your Smoothie will be: " +name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframes = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframes, use_container_width=True)
#st.stop()

pd_df = my_dataframes.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    my_dataframes,
    max_selections=5
)

if ingredients_list:
    #st.write("You selected:", ingredients_list)
    #st.text(ingredients_list)

    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string+= fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(f"{fruit_chosen} Nutrition Information")
        smoothiefroot_response  = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        sf_df = st.dataframe(data = smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                         values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')
    #st.write(my_insert_stmt)
    #st.stop()
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")    
