import streamlit as st
import os
import docx
import pdfplumber
import re
import zipfile
import tempfile
from io import BytesIO

def kru2uni(akr_text):
    akruti_to_unicode = {
        'Dç': 'अ',
        'Kç': 'ख',
        'ç': '',
        'Æ': 'क',
        'k': 'ि',
        'À': 'त्',
        'l': 'ा',
        'y': 'ब्',
    }

    a2u = [
        (u'\xb1', u'Z\u0902'),  # ± -> Zं
        (u'\xc6', u'\u0930\u094df'),  # Æ -> र्f
        (u'\xc7', u'fa'),  # Ç -> fa
        (u'\xaf', u'fa'),  # ¯ -> fa
        (u'\xc9', u'\u0930\u094dfa'),  # É -> र्fa
        (u'\xca', u'\u0940Z')  # Ê -> ीZ
    ]

    unicode_vowel_signs = [u'ा', u'ि', u'ी', u'ु', u'ू', u'ृ', u'ॄ', u'ॅ', u'ॆ', u'े', u'ै', u'ॉ', u'ॊ', u'ो', u'ौ']
    unicode_unattached_vowel_signs = [u'ा', u'ि', u'ी', u'ु', u'ू', u'ृ', u'ॄ', u'ॅ', u'ॆ', u'े', u'ै', u'ॉ', u'ॊ', u'ो', u'ौ', u'्']

    for akr_char, unicode_char in akruti_to_unicode.items():
        akr_text = akr_text.replace(akr_char, unicode_char)

    for mapping in a2u:
        akr_text = akr_text.replace(mapping[0], mapping[1])

    akr_text = re.sub('f(.)', r'\1ि', akr_text)
    akr_text = re.sub('fa(.)', r'\1िं', akr_text)
    akr_text = re.sub(u'ि्(.)', u'्\1ि', akr_text)
    
    akr_text = akr_text.replace(u'्Z', u'Z')  # ्  + Z -> Z

    misplaced = re.search('(.?)Z', akr_text)
    if misplaced:
        misplaced = misplaced.group(1)
        index_r_halant = akr_text.index(misplaced + 'Z')
        while index_r_halant >= 0 and akr_text[index_r_halant] in unicode_vowel_signs:
            index_r_halant -= 1
            misplaced = akr_text[index_r_halant] + misplaced
        akr_text = akr_text.replace(misplaced + 'Z', u'र्' + misplaced)

    for matra in unicode_unattached_vowel_signs:
        akr_text = akr_text.replace(' ' + matra, matra)
        akr_text = akr_text.replace(',' + matra, matra + ',')
        akr_text = akr_text.replace(u'्' + matra, matra)

    akr_text = akr_text.replace(u'््र', u'्र')  # ्  + ्  + र -> ्  + र
    akr_text = akr_text.replace(u'्र्', u'र्')  # ्  + र + ्  -> र + ्
    akr_text = akr_text.replace(u'््', u'्')  # ्  + ्  -> ्
    akr_text = akr_text.replace(u'् ', ' ')

    return akr_text.encode('utf-8')

def process_input_file(input):
    if isinstance(input, str):  # Check if input is a string (manual input)
        input_text = input
    else:  # Otherwise, input is a file object
        _, file_extension = os.path.splitext(input.name)

        if file_extension == '.txt':
            input_text = input.getvalue().decode('utf-8')
        elif file_extension == '.docx':
            doc = docx.Document(input)
            input_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        elif file_extension == '.pdf':
            input_text = ''
            with pdfplumber.open(input) as pdf:
                for page in pdf.pages:
                    input_text += page.extract_text()

    output_text = kru2uni(input_text)
    return input_text, output_text

def process_manual_input(input_text):
    output_text = kru2uni(input_text)
    return output_text

def process_folder(input_folder_path):
    # Iterate through all files in the folder
    for filename in os.listdir(input_folder_path):
        if filename.endswith(('.txt', '.docx', '.pdf')):
            input_file_path = os.path.join(input_folder_path, filename)
            input_text, output_text = process_input_file(input_file_path)
            # Display the processed input and output text
            st.write(f"### File: {filename}")
            st.write("#### Input Text:")
            st.text_area("Input", value=input_text, height=300, max_chars=None)
            st.write("#### Converted Text:")
            st.text_area("Output", value=output_text, height=300, max_chars=None)
            st.markdown("---")  # Add a horizontal line between files

def main():
    
    st.title("Akruti to Unicode Converter")
    #st.title("Select input method")
    input_method = st.sidebar.radio("Select input method:", ('Upload a file', 'Select a folder','Enter text manually'))

    if input_method == 'Upload a file':
        uploaded_file = st.file_uploader("Upload a file", type=['txt', 'docx', 'pdf'])

        if uploaded_file is not None:
            input_text, output_text = process_input_file(uploaded_file)

            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Input Text")
                st.write(
                '<style>textarea{width:900px !important;height:300px;}</style>',
                unsafe_allow_html=True
                )
                st.text_area("Input", value=input_text )

            with col2:
                st.subheader("Converted Text")
                st.write(
                '<style>textarea{width:900px !important;height:300px;}</style>',
                unsafe_allow_html=True
                )
                st.text_area("Output", value=output_text.decode('utf-8'))

            download_button = st.button("Download Converted Text")
            if download_button:
                st.download_button(
                    label="Click to Download",
                    data=output_text,
                    file_name="converted_text.txt",
                    mime="text/plain"
                )

    elif input_method == 'Select a folder':
        st.write("Please upload a folder containing files.")
        uploaded_zip = st.file_uploader("Upload zip file", type=["zip"], accept_multiple_files=False)
        if uploaded_zip is not None:
            # Create a temporary directory to extract the uploaded zip file
            temp_dir = tempfile.TemporaryDirectory()
            zip_file_path = os.path.join(temp_dir.name, uploaded_zip.name)
            with open(zip_file_path, "wb") as f:
                f.write(uploaded_zip.read())

            # Extract the zip file
            with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir.name)

            # Process files in the extracted folder
            process_folder(temp_dir.name)

    elif input_method == 'Enter text manually':
        input_text_manual = st.text_area("Enter Text Manually:", height=300)

        if st.button("Convert"):
            if input_text_manual.strip() != "":
                output_text_manual = process_manual_input(input_text_manual)
                st.write("### Output Text")
                st.text_area("Output", value=output_text_manual.decode('utf-8'), height=300)

                st.download_button(
                    label="Download Converted Text",
                    data=output_text_manual,
                    file_name="converted_text_manual.txt",
                    mime="text/plain",
                    key="download_button_manual"
                )


if __name__ == '__main__':
    main()
