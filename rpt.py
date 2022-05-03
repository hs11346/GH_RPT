#-------
#Importing & Cleaning Data
#_______

import pyairtable as py
import pandas as pd
import numpy as np
import streamlit as st
import yagmail as yg
import re
import seaborn as sns
import matplotlib.pyplot as plt
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
def cate(x):
    exception = ['Sets',"Liners"]
    if x["Product Name"] in exception:
        return " ".join([x["Product Name"].split()[-2],x])
    else:
        return x["Product Name"].split()[-1]
products["Updated Category"]=products.apply(cate,axis=1)
Food_and_Beverages_Containers=[ 'Bowl Sets', 'Bowls','Containers','Lids','Lunchbox','Packagings','Plate Sets','Plates','Platter Sets', 'Platters']
Cutlery=['Chopsticks','Knives', 'Spoons', 'Stirrers', 'Straws', 'Tongs', 'Dinnerwares', 'Forks', 'Cups' ,'Cutlery']
Amenities=['Napkins', 'Towels']
Films=['Half-Tube Films','Stretch Films','Tube Films']
Others=[ 'Aprons','Bags','Bin Liners', 'Box Liners', 'Boxes', 'Buds', 'Can Liners','Cards', 'Clamshells', 'Cleaners','Covers', 'Detergent', 'Fresh', 'Gloves', 'Holders','Pads', 'Pouches', 'Sacks', 'Sheets', 'Skewers', 'Sleeves', 'Sticks', 'Storages', 'Tablets', 'Tapes', 'Tissues', 'Toothpicks', 'Trays','Tumblers', 'Wraps']
def cate_dict(x):
    if x in Food_and_Beverages_Containers:
        return "Food and Beverages Containers"
    elif x in Cutlery:
        return "Cutlery"
    elif x in Amenities:
        return "Amenities"
    else:
        return "Others"
products["Updated Category"]=products["Updated Category"].apply(cate_dict)
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

pages = st.selectbox("Select Page",options = ["Supplier Database","Products Databse"])
st.markdown("\n")
if pages == "Supplier Database":
    supplier_data = st.container()
    with supplier_data:
        st.subheader("Supplier Database")
        left, right = st.columns(2)
        with left:
            country = st.selectbox("Select Country of Copmany", options = [x for x in supplier["Country"].dropna().unique() if x == x])
            ihg = st.slider("Select minimum IHG score",0,100,0,1)
        #word = st.text_input("Any comments?","Hi")
        with right:
            st.write(pd.DataFrame(supplier.drop(columns = "id")[((supplier["Score Ranked by the IHG"]>=ihg) | (supplier["Score Ranked by the IHG"]!=supplier["Score Ranked by the IHG"])) & (supplier["Country"]==country)].index.to_list(),columns = ["Name"]))
        st.markdown("\n")

    description = st.container()
    with description:
        st.subheader("Company Details")
        comp = st.selectbox("Select Company", options=list(supplier.drop(columns = "id")[((supplier["Score Ranked by the IHG"]>=ihg) | (supplier["Score Ranked by the IHG"]!=supplier["Score Ranked by the IHG"])) & (supplier["Country"]==country)].index.values))
        st.markdown(supplier["Company description"].loc[comp])
        if supplier["Description of products/services"].loc[comp] == supplier["Description of products/services"].loc[comp]:
            st.markdown("**Description of Product:**\n"+"* "+supplier["Description of products/services"].loc[comp])
        else:
            st.text("Information unavailable")
        st.markdown("\nProduct Categories include:")
        st.markdown("* "+"\n* ".join(supplier["Type of Products"].loc[comp]))
    

  
elif pages == 'Products Databse':
    head_container = st.container()
    with head_container:
        st.subheader("Product Databse")
        product_category = st.selectbox("Category of Product", options = [x for x in products["Updated Category"].unique() if x == x])
        st.write(products[products["Updated Category"]==product_category])
        product_name = st.selectbox("Select product", options = [x for x in products[products["Updated Category"]==product_category]["Product Name"] if x == x])
        st.subheader(product_name+"\n")
        
        image,description_2 = st.columns(2)
        with image:
            if products.set_index("Product Name")["Photo"].loc[product_name] == products.set_index("Product Name")["Photo"].loc[product_name]:
                st.image(products.set_index("Product Name")["Photo"].loc[product_name],caption = "Source from company website", use_column_width = True)
            else:
                st.markdown("No photo available")
        with description_2:
            st.subheader("Product Description\n")
            st.markdown("This product is produced by "+products.set_index("Product Name")["Company"].loc[product_name])
            st.markdown("\nContact Method:")
            if products.set_index("Product Name")["Contact email"].loc[product_name] == products.set_index("Product Name")["Contact email"].loc[product_name]:
                st.markdown(products.set_index("Product Name")["Contact email"].loc[product_name])
                email = products.set_index("Product Name")["Contact email"].loc[product_name]
                quick_container = st.container()
                with quick_container:
                    st.header("Quick Contact")
                    org = st.text_input("Your Organisation")
                    email = st.text_input("Your Receiving Email")
                    message = st.text_input("Your Message")
            
            else:
                st.markdown("Information unavailable")
                
with st.sidebar:
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    st.title("Contact Us")
    org = st.text_input("Your Organisation")
    email = st.text_input("Email")
    message = st.text_input("Your Message")
    send_button = st.button("Send")
    if send_button:
        if re.fullmatch(regex, email):
            user = yg.SMTP(user='hbgwjti@gmail.com',password = st.secrets['pw'])
            user.send(to=email,subject = 'Enquiry Recieved (noreply)', contents = """
            To {},
            We have recieved your enquiry, and we will get back to you soon!
            
            Best Regards,
            GREEN Hospitality Responsible Procurement Tool Team               
            """.format(org))
            st.markdown("Received, thanks!")
         else:
            st.markdown("Error: Invalid Email")                

