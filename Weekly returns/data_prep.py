import pandas as pd

def load_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    return df

# Check and handle missing data
def handle_missing_data(df):
    # Define the columns to check for missing values
    columns_to_check = ['ajexdi', 'prccd', 'trfd']
    
    # Check if columns exist in the DataFrame
    missing_columns = [col for col in columns_to_check if col not in df.columns]
    
    if missing_columns:
        print(f"Warning: The following columns are missing in the DataFrame: {missing_columns}")
        columns_to_check = [col for col in columns_to_check if col in df.columns]  # Adjust the list

    # Display missing data summary before filling
    missing_data_summary_before = df[columns_to_check].isnull().sum()
    print("Missing data summary before filling:\n", missing_data_summary_before)
    
    # Calculate and display missing data percentage before filling
    missing_data_percentage_before = df[columns_to_check].isnull().mean() * 100
    print("Missing data percentage before filling:\n", missing_data_percentage_before)

    # Group by 'tic' (ticker) and interpolate missing values
    for column in columns_to_check:
        if column in df.columns:
            df[column] = df.groupby('tic')[column].transform(lambda x: x.interpolate(method='linear'))
    df['trfd'] = df['trfd'].fillna(method='ffill')  # Forward fill
# Adjust trfd to 1 where it is missing
    df['trfd'].fillna(1, inplace=True)
    
    missing_data_summary_after = df[columns_to_check].isnull().sum()
    print("Missing data summary after filling:\n", missing_data_summary_after)
    
    # Calculate and display missing data percentage after filling
    missing_data_percentage_after = df[columns_to_check].isnull().mean() * 100
    print("Missing data percentage after filling:\n", missing_data_percentage_after)



    return df
