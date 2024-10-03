# Akruti to Unicode Converter

## Project Description

The **Akruti to Unicode Converter** is a web application designed to convert text written in the Akruti font (a popular font for writing in several Indian languages) to Unicode format. This tool is particularly useful for users with documents in `.txt`, `.docx`, or `.pdf` formats that need to be converted to a universally accepted format, allowing for easier sharing and editing. The application supports file uploads, manual text input, and folder uploads (in zipped format).

## Overview

This tool provides:
- **File Upload Support**: Convert `.txt`, `.docx`, or `.pdf` files to Unicode.
- **Manual Text Entry**: Users can input Akruti text directly for conversion.
- **Folder Processing**: Upload multiple files at once in a `.zip` folder.
- **Download Converted Text**: After conversion, users can download the Unicode text.

## Tech Stack

- **[Streamlit](https://streamlit.io/)**: A fast and easy-to-use Python library for building web applications with interactive UIs.
- **Python**: The primary programming language used to implement the conversion logic and build the web application.
- **[Docx](https://python-docx.readthedocs.io/en/latest/)**: A library for reading and extracting text from `.docx` files.
- **[PdfPlumber](https://pypi.org/project/pdfplumber/)**: Used for extracting text from PDF files.
- **Regular Expressions (`re`)**: For pattern matching and string manipulation in the conversion process.
- **Tempfile & Zipfile**: Python libraries for handling temporary file storage and processing zipped folders of documents.

## Steps to Build the Project

### 1. Set Up Environment

Install the necessary libraries by running the following command:

```bash
pip install streamlit python-docx pdfplumber
