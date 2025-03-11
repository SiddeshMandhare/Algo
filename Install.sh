#!/bin/bash

# Upgrade pip
python3 -m pip install --upgrade pip

# Install required packages
pip3 install \
    dhanhq \
    typing \
    typing-extensions \
    logging \
    pdbpp \
    Twisted \
    pyOpenSSL \
    autobahn \
    pandas \
    smartapi-python \
    websocket-client \
    xlwings \
    mibian \
    numpy \
    xlrd \
    plyer \
    dateparser \
    halo \
    ta \
    pandas-ta \
    nsepy \
    scipy \
    selenium \
    tapy \
    dataclasses \
    openpyxl \
    urllib3 \
    requests \
    auto-py-to-exe \
    chromedriver-autoinstaller

# Note: The last two .whl file installations are specific to Windows. Remove them or find Linux-compatible versions if needed.

echo "Installation complete."
