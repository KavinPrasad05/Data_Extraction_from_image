import streamlit as st  # Import the Streamlit library for building the app UI
import easyocr  # Import the EasyOCR library for extracting text from the image
import cv2  # Import the OpenCV library for image processing
import numpy as np  # Import the NumPy library for numerical operations
import pandas as pd  # Import the Pandas library for data manipulation
from PIL import Image  # Import the Python Imaging Library for image handling
import re  # Import the re library for regular expression pattern matching
import sqlite3  # Import the SQLite library for database operations

# Set up the page title and description
st.set_page_config(page_title='Business Card Extractor', page_icon=':credit_card:', layout='wide')
st.title('Business Card Extractor')
st.write('Upload an image of a business card to extract its information')

# Create a file uploader widget
uploaded_file = st.file_uploader(label='Upload a business card image', type=['jpg', 'jpeg', 'png'])

# Define a function to extract the business card information
def extract_info(image):
    # Load the image using OpenCV
    image = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)

    # Use EasyOCR to extract text from the image
    read = easyocr.Reader(['en'])
    l = read.readtext(image, detail=0, paragraph=False)

    # Create a dictionary to store the extracted information
    k = {'Name': "", 'Designation': "", 'Number': "", 'Email': "", 'Website': "", 'Area': "", 'Pincode': ""}

    # Parse the text to extract the relevant information
    k['Name'] = l[0]
    k['Designation'] = l[1]
    for i in range(len(l)):
        if re.findall("[a-zA-Z0-9]+ [a-zA-Z0-9]+ [ St]+", l[i]):
            k['Area'] = (l[i])
        if re.search('[^- +a-zA-z]{6}', l[i]):
            res = l[i]
            result = [int(l[i]) for l[i] in res.split() if l[i].isdigit()]
            k['Pincode'] = result[0]
        if re.findall("[^A-Z0-9.-_+~!@#$ %&*()]+@+[a-zA-Z0-9]+.[a-z]+", l[i]):
            k['Email'] = l[i]
        if re.findall("[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", l[i]):
            k['Number'] = l[i]
        if re.findall('[^ ,0-9!@#$%&*()_+]+[A-Za-z]+.com', l[i]):
            k["Website"] = l[i]

    return k

# Create a button to extract the business card information
if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded business card', use_column_width=True)
    k = extract_info(uploaded_file)
    if st.button('Extract information'):
        st.write('Extracted information:')
        st.write(k)

    # Create a button to save the extracted information to a SQLite database
    if st.button("Save data to database!"):
        # Connect to the SQLite database
        conn = sqlite3.connect('Bizxcard.sqlite')
        table_name = k['Name']
        # Define the table schema and create the table if it doesn't exist
        query = f'''Create table if not Exists 
                 {table_name} (Name text,Designation text,Number text, Email text, Website text,Area text,
                state text,pincode integer)'''
        conn.execute(query)
        new_df = pd.DataFrame(k, index=[1])
        new_df['Website'] = new_df['Website'].apply(lambda x: x.replace(" ", "."))
        new_df['Area'] = new_df['Area'].apply(lambda x: x.replace(";", "."))
        new_df['Area'] = new_df['Area'].apply(lambda x: x.replace(" ", ""))
        new_df['Area'] = new_df['Area'].apply(lambda x: x.replace(",,", ","))
        new_df.to_sql(table_name, conn, if_exists='replace', index=False)
        st.write("done")
        conn.commit()
        conn.close()

    if st.button("view data"):
        table_name = k['Name']
        conn = sqlite3.connect('Bizxcard.sqlite')
        query = f'''select * from {table_name} '''
        r_df = pd.read_sql(query, conn)
        st.table(r_df)
        conn.commit()
        conn.close()

    if st.button("Delete data "):
        table_name= st.text_input(
        "Enter some text 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,)

        conn = sqlite3.connect('Bizxcard.sqlite')
        query = f'''drop table {table_name} '''
        pd.read_sql(query, conn)
        st.write("Information deleted")
