#!/bin/bash
# Script to run the EV financing propensity model pipeline
echo 'Starting pipeline...'
python src/data_processing.py
python src/feature_engineering.py
python src/label_simulation.py
python src/modeling.py
echo 'Pipeline finished.'
echo 'To run the Streamlit app (if developed): streamlit run streamlit_app/app.py'
