# src/data_processing.py
import pandas as pd
import numpy as np
import os

def load_raw_data(file_path):
    """Loads the AHIES dataset from the specified path, trying different encodings."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found at '{file_path}'.")
        return None

    try:
        df = pd.read_csv(file_path, encoding="ISO-8859-1", low_memory=False)
        print(f"✅ File loaded with ISO-8859-1 encoding from '{file_path}'.")
        return df
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding="windows-1252", low_memory=False)
            print(f"✅ File loaded with windows-1252 encoding from '{file_path}'.")
            return df
        except Exception as e:
            print(f"❌ Error loading file with windows-1252: {e}")
            return None
    except Exception as e:
        print(f"❌ An unexpected error occurred while loading: {e}")
        return None

def select_and_rename_cols(df, column_map):
    """Selects and renames columns based on a dictionary."""
    if df is None or df.empty:
        print("❌ Input dataframe is empty. Cannot select columns.")
        return None

    existing_cols = {
        orig: new for orig, new in column_map.items() if orig in df.columns
    }
    missing = set(column_map.keys()) - set(existing_cols.keys())
    if missing:
        print(f"⚠️ Warning: These columns were not found and skipped: {sorted(list(missing))}")

    if not existing_cols:
        print("❌ Error: None of the specified columns exist.")
        return None

    df_selected = df[list(existing_cols.keys())].copy()
    df_selected.rename(columns=existing_cols, inplace=True)
    print(f"✅ {len(existing_cols)} columns selected and renamed.")
    return df_selected

def filter_by_age(df, min_age, age_column='age'):
    """Filters the DataFrame to include only rows where age is >= min_age."""
    if df is None or df.empty:
        print("❌ Input dataframe is empty. Cannot filter by age.")
        return None
    if age_column not in df.columns:
        print(f"❌ Error: Age column '{age_column}' not found in DataFrame.")
        return df # Return original df or None, depending on desired behavior

    original_rows = len(df)
    # Ensure age column is numeric, coercing errors if necessary
    # This step might be better placed in a dedicated type conversion function earlier
    # but is included here for robustness if not already done.
    if not pd.api.types.is_numeric_dtype(df[age_column]):
        print(f"⚠️ Warning: Age column '{age_column}' is not numeric. Attempting conversion...")
        df[age_column] = pd.to_numeric(df[age_column], errors='coerce')
        if df[age_column].isnull().any():
            print(f"   ⚠️ Some age values could not be converted to numeric and are now NaN. These rows will be excluded by the age filter if not handled.")

    df_filtered = df[df[age_column] >= min_age].copy()
    filtered_rows = len(df_filtered)
    rows_removed = original_rows - filtered_rows

    print(f"✅ Filtered by age: {filtered_rows} rows remaining (>= {min_age} years). {rows_removed} rows removed.")
    return df_filtered


def impute_missing_values(df, strategies):
    """Imputes missing values based on a dictionary of strategies ('median', 'mode', or a specific value)."""
    if df is None or df.empty:
        print("❌ Input dataframe is empty. Cannot impute.")
        return None

    print("\n--- Starting Generic Missing Value Imputation ---")
    df_cleaned = df.copy()
    imputed_cols_count = 0

    for col, strategy in strategies.items():
        if col not in df_cleaned.columns:
            print(f"ℹ️ Column '{col}' not found for imputation, skipping.")
            continue

        if df_cleaned[col].isnull().any():
            value_to_impute = None # Initialize
            if strategy == 'median':
                if not pd.api.types.is_numeric_dtype(df_cleaned[col]):
                    print(f"⚠️ Warning: Column '{col}' is not numeric. Cannot calculate median. Skipping.")
                    continue
                value_to_impute = df_cleaned[col].median()
            elif strategy == 'mode':
                mode_series = df_cleaned[col].mode()
                if mode_series.empty:
                    print(f"⚠️ Warning: Column '{col}' is all NaN or mode could not be determined. Skipping.")
                    continue
                value_to_impute = mode_series[0]
            elif isinstance(strategy, (int, float, str)):
                 value_to_impute = strategy
            else:
                print(f"⚠️ Unknown strategy '{strategy}' for column '{col}'. Skipping.")
                continue

            df_cleaned[col].fillna(value_to_impute, inplace=True)
            
            # Corrected print statement:
            value_display = f"{value_to_impute:.2f}" if isinstance(value_to_impute, (int, float)) else str(value_to_impute)
            print(f"✅ Missing '{col}' values imputed with {strategy} ({value_display}).")
            imputed_cols_count += 1
        else:
            print(f"ℹ️ No missing values found in '{col}'.")

    print(f"--- Generic Imputation finished. {imputed_cols_count} columns processed. ---")
    return df_cleaned



def drop_columns(df, columns_to_drop):
    """Drops specified columns from the DataFrame."""
    if df is None or df.empty:
        print("❌ Input dataframe is empty. Cannot drop columns.")
        return None
        
    original_cols = df.columns.tolist()
    cols_found = [col for col in columns_to_drop if col in original_cols]
    cols_not_found = [col for col in columns_to_drop if col not in original_cols]

    if cols_not_found:
        print(f"ℹ️ These columns to drop were not found: {cols_not_found}")

    if not cols_found:
        print("ℹ️ No columns to drop were found in the DataFrame.")
        return df

    df_dropped = df.drop(columns=cols_found)
    print(f"✅ Dropped {len(cols_found)} columns: {cols_found}")
    return df_dropped

def handle_worked_last_7_days(df, worked_col='worked_last_7_days'):
    """
    Ensures 'worked_last_7_days' is clean by imputing its missing values with the mode.
    Assumes the column already contains 'Yes'/'No' or similar text.
    """
    if df is None or worked_col not in df.columns:
        print(f"❌ Column '{worked_col}' not found or dataframe empty.")
        return df

    df_handled = df.copy()

    print(f"ℹ️ Values in '{worked_col}' before handling:")
    print(df_handled[worked_col].value_counts(dropna=False))

    # Check if there are any missing values.
    if df_handled[worked_col].isnull().any():
        mode_series = df_handled[worked_col].mode()
        
        # Check if mode calculation was successful (it might fail if all values were NaN)
        if not mode_series.empty:
            mode_val = mode_series[0]
            df_handled[worked_col].fillna(mode_val, inplace=True)
            print(f"✅ Imputed {df_handled[worked_col].isnull().sum()} missing '{worked_col}' values with mode ('{mode_val}').")
        else:
            print(f"⚠️ Could not determine mode for '{worked_col}'. Missing values remain.")
    else:
        print(f"ℹ️ No missing values found in '{worked_col}'.")

    # Double check if it contains 'Yes' and 'No' now
    current_values = set(df_handled[worked_col].dropna().unique())
    if not {'Yes', 'No'}.issubset(current_values) and current_values: # Check if it has something other than Yes/No
         print(f"⚠️ Warning: Column '{worked_col}' now contains: {current_values}. Ensure this is expected.")
         
    print(f"✅ Column '{worked_col}' processed.")
    return df_handled

def impute_primary_income_smart(df, worked_col='worked_last_7_days', income_col='primary_job_income_monthly', worked_value='Yes', not_worked_value='No'):
    """Imputes primary income based on work status, creating 'has_primary_income' flag."""
    if df is None or income_col not in df.columns or worked_col not in df.columns:
        print("❌ DataFrame or required columns missing for smart income imputation.")
        return df

    df_imputed = df.copy()

    # 1. Create the 'has_primary_income' flag
    df_imputed['has_primary_income'] = df_imputed[income_col].notna().astype(int)
    print("✅ Created 'has_primary_income' flag.")

    # 2. Impute 0 for those who didn't work and have missing income
    no_work_missing_income_mask = (df_imputed[worked_col] == not_worked_value) & (df_imputed[income_col].isna())
    df_imputed.loc[no_work_missing_income_mask, income_col] = 0
    print(f"✅ Imputed 0 for {no_work_missing_income_mask.sum()} individuals who didn't work and had missing income.")

    # 3. Impute median for those who worked but have missing income
    median_income_for_workers = df_imputed.loc[(df_imputed[worked_col] == worked_value) & (df_imputed[income_col].notna()), income_col].median()
    
    if pd.isna(median_income_for_workers):
        print("⚠️ Could not calculate median income for workers (maybe none reported?). Using overall median or 0.")
        median_income_for_workers = df_imputed[income_col].median() # Fallback
        if pd.isna(median_income_for_workers):
            median_income_for_workers = 0 # Final fallback

    print(f"ℹ️ Median income for workers used for imputation: {median_income_for_workers:.2f}")

    worked_missing_income_mask = (df_imputed[worked_col] == worked_value) & (df_imputed[income_col].isna())
    df_imputed.loc[worked_missing_income_mask, income_col] = median_income_for_workers
    print(f"✅ Imputed median ({median_income_for_workers:.2f}) for {worked_missing_income_mask.sum()} individuals who worked but had missing income.")

    # 4. Ensure no NaNs remain (handle edge cases if any)
    if df_imputed[income_col].isnull().any():
        remaining_nans = df_imputed[income_col].isnull().sum()
        print(f"⚠️ {remaining_nans} NaNs still remain in '{income_col}'. Filling with 0 as a final step.")
        df_imputed[income_col].fillna(0, inplace=True)

    print(f"✅ Smart imputation for '{income_col}' completed.")
    return df_imputed

def decode_categorical(df, column, mapping):
    """Decodes a categorical column using a mapping dictionary."""
    if df is None or column not in df.columns:
        print(f"❌ Column '{column}' not found or dataframe empty.")
        return df

    new_col_name = f"{column}_mapped"
    df[new_col_name] = df[column].map(mapping)
    print(f"✅ Column '{column}' mapped to '{new_col_name}'.")
    # Check for values not in the map
    unmapped = df[new_col_name].isnull() & df[column].notnull()
    if unmapped.any():
        print(f"   ⚠️ Found {unmapped.sum()} values in '{column}' not present in the provided map.")
    return df


def save_data(df, file_path):
    """Saves a DataFrame to a CSV file, creating directories if needed."""
    if df is None or df.empty:
        print(f"❌ DataFrame is empty. Cannot save to '{file_path}'.")
        return

    try:
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        df.to_csv(file_path, index=False)
        print(f"✅ Data saved successfully to '{file_path}'")
    except Exception as e:
        print(f"❌ Error saving data to '{file_path}': {e}")

print("✅ Data processing functions defined.")