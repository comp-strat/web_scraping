#!/bin/bash
git clone https://github.com/URAP-charter/web_scraping
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
brew services start redis
brew services start mongodb-community@5.0

cd web_scraping/scrapy/schools
python schools/app.py
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~                                                                               
~            
