import io
import sqlite3
import re
import easyocr as ocr
import streamlit as st
from PIL import Image
import numpy as np
st. set_page_config(layout="wide")

conn = sqlite3.connect('business_cards.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS business_cards (id INTEGER PRIMARY KEY AUTOINCREMENT, 
               website_url TEXT, email TEXT, pin_code TEXT, phone_numbers TEXT, address TEXT, card_holder_details TEXT, card_id TEXT, image_data BLOB)''')


def format_title(title: str):
    formatted_title = f"<div style='padding:10px;background-color:rgb(230, 0, 172, 0.3);border-radius:10px'><h1 style='color:rgb(0, 0, 0);text-align:center;'>{title}</h1></div>"
    return formatted_title


st.markdown(format_title(
    "Text Extraction From Business-Card Image With OCR"), unsafe_allow_html=True)
st.write(" ")
st.write(" ")
st.write(" ")
st.write("## UPLOAD ANY BUSINESS CARD IMAGE TO EXTRACT INFORMATION ")
CD, col1, col2, col3 = st.columns([0.5, 5, 1, 5])
with col1:
    st.write("#### SELECT IMAGE")  # upload
    image = st.file_uploader(label="", type=['png', 'jpg', 'jpeg'])


@ st.cache_data
def load_model():
    reader = ocr.Reader(['en'])
    return reader


reader = load_model()  # load model
if image is not None:
    input_image = Image.open(image)  # read image
    with col1:
        st.image(input_image)  # display image
        st.write(" ")
    result = reader.readtext(np.array(input_image))
    result_text = []  # empty list for results
    for text in result:
        result_text.append(text[1])

    PH = []
    PHID = []
    ADD = set()
    AID = []
    EMAIL = ''
    EID = ''
    PIN = ''
    PID = ''
    WEB = ''
    WID = ''
    for i, string in enumerate(result_text):
        if re.search(r'@', string.lower()):  # email
            EMAIL = string.lower()
            EID = i
        match = re.search(r'\d{6,7}', string.lower())  # pincode
        if match:
            PIN = match.group()
            PID = i
        match = re.search(
            r'(?:ph|phone|phno)?\s*(?:[+-]?\d\s*[\(\)]*){7,}', string)
        if match and len(re.findall(r'\d', string)) > 7:  # phone no.
            PH.append(string)
            PHID.append(i)
        # Address
        keywords = ['road', 'floor', ' st ', 'st,', 'street', ' dt ', 'district',
                    'near', 'beside', 'opposite', ' at ', ' in ', 'center', 'main road',
                    'state', 'country', 'post', 'zip', 'city', 'zone', 'mandal', 'town', 'rural',
                    'circle', 'next to', 'across from', 'area', 'building', 'towers', 'village',
                    ' ST ', ' VA ', ' VA,', ' EAST ', ' WEST ', ' NORTH ', ' SOUTH ']
        # Define the regular expression pattern to match six or seven continuous digits
        digit_pattern = r'\d{6,7}'
        # Check if the string contains any of the keywords or a sequence of six or seven digits
        if any(keyword in string.lower() for keyword in keywords) or re.search(digit_pattern, string):
            ADD.add(string)
            AID.append(i)
        states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat',
                  'Haryana', 'Hyderabad', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
                  'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
                  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
                  "India"]
        if any(state in string.lower() for state in states):  # States
            ADD.add(string)
            AID.append(i)
        if re.match(r"(?!.*@)(www|.*com$)", string):  # Website
            WEB = string.lower()
            WID = i
    with col3:
        # DISPLAY ALL THE ELEMENTS OF BUSINESS CARD
        st.write("##### EXTRACTED TEXT")
        st.write('###### :red[WEBSITE URL: ] ' + str(WEB))
        st.write('###### :red[EMAIL: ] ' + str(EMAIL))
        st.write('###### :red[PIN CODE: ] ' + str(PIN))
        ph_str = ', '.join(PH)
        st.write('###### :red[PHONE NUMBER(S): ] '+ph_str)
        add_str = ' '.join([str(elem) for elem in ADD])
        st.write('###### :red[ADDRESS: ] ', add_str)

        IDS = [EID, PID, WID]
        IDS.extend(AID)
        IDS.extend(PHID)
        # st.write(result_text)
        oth = ''
        fin = []
        for i, string in enumerate(result_text):
            if i not in IDS:
                if len(string) >= 4 and ',' not in string and '.' not in string and 'www.' not in string:
                    if not re.match("^[0-9]{0,3}$", string) and not re.match("^[^a-zA-Z0-9]+$", string):
                        numbers = re.findall('\d+', string)
                        if len(numbers) == 0 or all(len(num) < 3 for num in numbers) and not any(num in string for num in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']*3):
                            fin.append(string)
        st.write('###### :red[CARD HOLDER & COMPANY DETAILS: ] ')
        for i in fin:
            st.write('###### '+i)

        UP = st.button('UPLOAD TO DATABASE', key=90)
# DATABASE CODE
    website = str(WEB)
    email = str(EMAIL)
    pincode = str(PIN)
    phoneno = ph_str
    address = add_str
    det_str = ' '.join([str(elem) for elem in fin])
    details = det_str
    card_id = ', '.join(map(str, IDS))
    image.seek(0)
    image_data = image.read()
    

    if UP:
        if image is not None:
            inp_data = (website, email, pincode, phoneno,
                        address, details, card_id, image_data)
            cursor.execute(f"INSERT INTO business_cards (website_url, email, pin_code, phone_numbers, address, card_holder_details, card_id, image_data) VALUES (?,?,?,?,?,?,?,?)",inp_data)
            conn.commit()
        else:
            st.write('Please upload business card')
            st.write(' ')
            st.write(' ')
            st.write(' ')

col1.markdown(
    "<style>div[data-testid='stHorizontalBlock'] { background-color: rgb(230, 0, 172, 0.1); }</style>", unsafe_allow_html=True)
# DATABASE PART
st.write('### EXPLORE BUSINESS CARDS DATABASE ')
cd, c1, c2, c3 = st.columns([0.5, 4, 1, 4])
with c1:
    st.write(' ')
    st.write("#### BUSINESS CARDS AVAILABLE IN DATABASE")
    cursor.execute(f"SELECT id FROM business_cards")
    rows = cursor.fetchall()
    l = []
    # DISPLAY ALL THE CARDS AS BUTTONS
    for row in rows:
        l.append(row[0])
        button_label = f"SHOW BUSINESS CARD: {row[0]}"
        if st.button(button_label):
            cursor.execute(
                f"SELECT * FROM business_cards WHERE id ="+str(row[0]))
            row1 = cursor.fetchone()
            website_url = row1[1]
            email = row1[2]
            pin_code = row1[3]
            phone_numbers = row1[4]
            address = row1[5]
            card_holder_details = row1[6]
            card_id = row1[7]

            # DISPLAY SELECTED CARD DETAILS
            with c3:
                st.write(f"#### BUSINESS CARD {row[0]} DETAILS ")
                st.write(f"Website: {website_url}")
                st.write(f"Email: {email}")
                st.write(f"PIN Code: {pin_code}")
                st.write(f"Phone Numbers: {phone_numbers}")
                st.write(f"Address: {address}")
                st.write(
                    f"Card Holder & Company Details: {card_holder_details}")

                # If the button is clicked, display the corresponding row
                cursor.execute(
                    "SELECT image_data FROM business_cards WHERE id ="+str(row[0]))
                r = cursor.fetchone()
                if r is not None:
                    image_data = r[0]
                    image = Image.open(io.BytesIO(image_data))
                    st.image(image)
                st.write(' ')


# DELETE MULTIPLE ENTRIES
with c1:
    st.write(' ')
    st.write(f"#### SELECT ENTRIES TO DELETE")
    selected_options = st.multiselect('', l)

    if st.button('DELETE SELECTED ENTRIES'):
        for option in selected_options:
            cursor.execute(
                "DELETE FROM business_cards WHERE card_id = ?", (option,))
        conn.commit()
        st.write("DELETED SELECTED BUSINESS CARD ENTRIES SUCCESSFULLY")
    st.write(' ')
    st.write(' ')

st.balloons()
