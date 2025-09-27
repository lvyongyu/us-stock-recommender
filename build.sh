#!/bin/bash
pip install -r requirements.txt
streamlit run portfolio_app.py --server.port $PORT --server.headless true --server.enableCORS false