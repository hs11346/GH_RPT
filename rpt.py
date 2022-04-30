#-------
#Importing & Cleaning Data
#_______

import pyairtable as py
import pandas as pd
import numpy as np

# arg1 = API key, arg2 = table key, arg3 = table name

table = py.Table("keyEP820cEIv0tZfJ","appVjXnuY1AZLe9HC","List of Suppliers")
table = table.all()

list = []
#changing column names
def renamer(name):
    if name[0:7] == "fields_":
        return name[7:]
    else:
        return name

#flattening dataframe 
for i in range(len(table)):
    flat = pd.json_normalize(table[i], sep = "_")
    list.append(flat.to_dict(orient='records')[0])
supplier = pd.DataFrame(list)
supplier = supplier.rename(columns = {"fields_Company Name":"Company"})
supplier = supplier.rename(mapper = renamer, axis = 'columns').set_index("Company").drop("createdTime",axis=1)

#cleaning the photo column to show only the url
def photo(val):
    if val == val:
        return val[0]['url']
    else:
        return np.NaN
supplier["Photo"] = supplier['Photo'].apply(photo)

id_dict = {}
def make_pair(series):
    id_dict[series['id']] = series["Company"]
supplier.reset_index().apply(make_pair,axis = 1)

table2 = py.Table("keyEP820cEIv0tZfJ","appVjXnuY1AZLe9HC","Products Database")
table2 = table2.all()

list = []
#changing column names
def renamer(name):
    if name[0:7] == "fields_":
        return name[7:]
    else:
        return name

#flattening dataframe 
for i in range(len(table2)):
    flat = pd.json_normalize(table2[i], sep = "_")
    list.append(flat.to_dict(orient='records')[0])
products = pd.DataFrame(list)
products = products.rename(mapper = renamer, axis = 'columns').drop("createdTime",axis=1)

#Linking the products databse to the supplier list
for i in range(len(products["Company"])):
    if products['Company'][i] == products['Company'][i]:
        products['Company'][i] = id_dict[products['Company'][i][0]]
    else:
        pass
    
#cleaning the photo column to show only the url
def photo(val):
    if val == val:
        return val[0]['url']
    else:
        return np.NaN
products["Photo"] = products['Photo'].apply(photo)
#products.set_index("Company")
products.set_index("Product Name")

#--------
#Creating Webapp
#--------

import streamlit as st

header = st.container()
with header:
    st.title("Responsible Procurement Tool Webapp Prototype")
    st.markdown("Developed by **See Yat Nam Harry:**")
    st.markdown("Purpose of this prototype:")
    st.markdown("* To demonstrate the viability of a connected webapp")
    st.markdown("* To enhance user-friendliness")

supplier_data = st.container()
with supplier_data:
    st.subheader("Supplier Database")
    country = st.selectbox("Select Country of Copmany", options = ["US","UK","Others"])
    price = st.slider("Select max price",10,100,50,10)
    word = st.text_input("Any comments?","Hi")
    st.write(supplier.head().drop(columns = "id"))

products_data = st.container()
with products_data:
    st.subheader("Products Database")
    st.write(products.head().drop(columns = "id"))
