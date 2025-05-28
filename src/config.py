# src/config.py
import os

# --- File Paths ---
# Use os.path.join for robust paths. Go up one level ('..') from src to the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "01_raw")
INTERMEDIATE_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "02_intermediate")
PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "03_processed")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

RAW_DATA_FILE = "AHIES2022Q1_2023Q3_SEC01234_202402.csv"
SELECTED_DATA_FILE = "ahies_selected_for_ev_propensity.csv"
CLEANED_DATA_FILE = "ahies_cleaned_for_eda.csv"

RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, RAW_DATA_FILE)
SELECTED_DATA_PATH = os.path.join(INTERMEDIATE_DATA_DIR, SELECTED_DATA_FILE)
CLEANED_DATA_PATH = os.path.join(INTERMEDIATE_DATA_DIR, CLEANED_DATA_FILE)

# --- Column Selection & Renaming Map ---
COLUMNS_TO_EXTRACT = {
    "hhid": "household_id",
    "personid": "person_id",
    "region": "region",
    "urbrur": "urban_rural",

    # Demographics
    "s1aq1": "sex",
    "s1aq4y": "age",
    "s1aq5": "marital_status",

    # Education
    "s2aq3": "highest_education_level",
    "s2aq4": "grade_completed",
    "s2aq6": "still_in_school",

    # Income
    "s4aq55a": "primary_job_income_monthly",
    "s4bq9": "secondary_job_income_monthly",

    # Expenditure
    "s2aq11a2": "tuition_fee_paid_last_12m",
    "s2aq11a15": "transportation_cost_to_school_last_12m",
    "s2aq11a16": "school_food_cost_last_12m",
    "s3aq21": "total_medical_expense_last_12m",

    # Employment
    "s4aq1": "worked_last_7_days",
}

# --- NEW: Columns to Drop ---
COLUMNS_TO_DROP_AFTER_AGE_FILTER = [
    'tuition_fee_paid_last_12m',
    'transportation_cost_to_school_last_12m',
    'school_food_cost_last_12m',
    'still_in_school', # Optional, but recommended based on 96.8% missing
]

# --- Data Cleaning Parameters (Updated) ---
IMPUTATION_STRATEGIES = {
    'highest_education_level': 'mode',
    'grade_completed': 'median',
    # 'primary_job_income_monthly': 'median', # REMOVED - Handled by impute_primary_income_smart
    'secondary_job_income_monthly': 0, # Explicitly setting to 0
    'total_medical_expense_last_12m': 0, # Setting to 0
    # 'worked_last_7_days': 'mode', # REMOVED - Handled by map_worked_last_7_days
    'marital_status': 'mode',
}

# --- Categorical Mappings (Examples - You will need to verify these from the Data Dictionary!) ---
REGION_MAP = {
    1: "Western",
    2: "Central",
    3: "Greater Accra",
    4: "Volta",
    5: "Eastern",
    6: "Ashanti",
    7: "Brong Ahafo",
    8: "Northern",
    9: "Upper East",
    10: "Upper West",
    11: "Oti",
    12: "Bono East",
    13: "Ahafo",
    14: "Western North",
    15: "Savannah",
    16: "North East",
}

URBAN_RURAL_MAP = {
    1: 'Urban',
    2: 'Rural'
}

SEX_MAP = {
    1: 'Male',
    2: 'Female'
}

# Add more maps as needed...

if __name__ == "__main__":
    print("✅ Configuration loaded.")

    # Example usage:
    print("Selected Data Path:", SELECTED_DATA_PATH)
    print("Cleaned Data Path:", CLEANED_DATA_PATH)