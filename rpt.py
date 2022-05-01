#-------
#Importing & Cleaning Data
#_______

import pyairtable as py
import pandas as pd
import numpy as np
import streamlit as st
import yagmail as yg
import re

# arg1 = API key, arg2 = table key, arg3 = table name


def tableX():
    return py.Table(st.secrets["api_key"],st.secrets["table_key"],"List of Suppliers")
table = tableX()
table = table.all()



list2 = []
#changing column names
@st.cache
def renamer(name):
    if name[0:7] == "fields_":
        return name[7:]
    else:
        return name

#flattening dataframe
for i in range(len(table)):
    flat = pd.json_normalize(table[i], sep = "_")
    list2.append(flat.to_dict(orient='records')[0])
supplier = pd.DataFrame(list2)
supplier = supplier.rename(columns = {"fields_Company Name":"Company"})
supplier = supplier.rename(mapper = renamer, axis = 'columns').set_index("Company").drop("createdTime",axis=1).rename(columns={"Country of Company":"Country"})

#cleaning the photo column to show only the url
@st.cache
def photo(val):
    if val == val:
        return val[0]['url']
    else:
        return np.NaN
supplier["Photo"] = supplier['Photo'].apply(photo)

def convert_int(i):
    if i == i:
        return int(i)
    else:
        return i
supplier["Score Ranked by the IHG"] = supplier["Score Ranked by the IHG"].apply(convert_int)

id_dict = {}
def make_pair(series):
    id_dict[series['id']] = series["Company"]
supplier.reset_index().apply(make_pair,axis = 1)


def table_2():
    return py.Table(st.secrets["api_key"],st.secrets["table_key"],"Products Database")

table2 = table_2()
table2 = table2.all()

list2 = []
#changing column names
@st.cache
def renamer(name):
    if name[0:7] == "fields_":
        return name[7:]
    else:
        return name

#flattening dataframe

for i in range(len(table2)):
    flat = pd.json_normalize(table2[i], sep = "_")
    list2.append(flat.to_dict(orient='records')[0])
products = pd.DataFrame(list2)
products = products.rename(mapper = renamer, axis = 'columns').drop("createdTime",axis=1)

#Linking the products databse to the supplier list
for i in range(len(products["Company"])):
    if products['Company'][i] == products['Company'][i]:
        products['Company'][i] = id_dict[products['Company'][i][0]]
    else:
        pass
    
#cleaning the photo column to show only the url
@st.cache
def photo(val):
    if val == val:
        return val[0]['url']
    else:
        return np.NaN
products["Photo"] = products['Photo'].apply(photo)
#products.set_index("Company")
products.set_index("Product Name")


def table_3():
    return py.Table(st.secrets["api_key"],st.secrets['table_key'],"List of Country")
table3 = table_3()
table3 = table3.all()

list2 = []
#changing column names
@st.cache
def renamer(name):
    if name[0:7] == "fields_":
        return name[7:]
    else:
        return name

#flattening dataframe 
for i in range(len(table3)):
    flat = pd.json_normalize(table3[i], sep = "_")
    list2.append(flat.to_dict(orient='records')[0])
country = pd.DataFrame(list2)
country = country.rename(mapper = renamer, axis = 'columns').drop("createdTime",axis=1).rename(columns = {"Name":"Country"})


id_dict2 = []
id_value2 = []
def make_pair_country(series):
    id_dict2.append(series["id"])   
    id_value2.append(series["Country"])
country.apply(make_pair_country,axis = 1)
supplier["Country"] = supplier["Country"].apply(lambda x: x[0] if x == x else x)
supplier = supplier.replace(id_dict2,id_value2).sort_values("Country")
#supplier["Country"] = supplier["Country"].fillna("Unspecified")

#--------
#Creating Webapp
#--------



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
    left, right = st.columns(2)
    with left:
        country = st.selectbox("Select Country of Copmany", options = [x for x in supplier["Country"].dropna().unique() if x == x])
        ihg = st.slider("Select minimum IHG score",0,100,0,1)
    #word = st.text_input("Any comments?","Hi")
    with right:
        st.write(supplier.drop(columns = "id")[(supplier["Score Ranked by the IHG"]>=ihg) & (supplier["Country"]==country)])
    st.markdown("\n")

description = st.container()
with description:
    st.subheader("Company Details")
    comp = st.selectbox("Select Company", options=list(supplier.drop(columns = "id")[(supplier["Score Ranked by the IHG"]>=ihg) & (supplier["Country"]==country)].index.values))
    st.markdown(supplier["Company description"].loc[comp])
    st.markdown("\nProduct Categories include:")
    st.markdown(" ".join(supplier["Type of Products"].loc[comp]))
yg.register('hbgwjti@gmail.com', st.secrets['pw']
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
with st.sidebar:
    st.title("Contact Us")
    org = st.text_input("Your Organisation")
    email = st.text_input("Email")
    message = st.text_input("Your Message")
    send_button = st.button("Send")
    if send_button:
        if re.fullmatch(regex, email):
            user = yg.SMTP(user='hbgwjti@gmail.com',password = st.secrets['pw'])
            user.send(to=email,subject = 'Webapp trial email from '+org, contents = message)
            org, email, message = st.empty()
        else:
            st.markdown("Error: Invalid Email")
        


    


