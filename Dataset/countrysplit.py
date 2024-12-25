import pandas as pd
import os

# Define the list of Asian countries
asian_countries = {
    'Nepal', 'India', 'China', 'Japan', 'South Korea', 'Thailand',
    'Vietnam', 'Cambodia', 'Laos', 'Myanmar', 'Malaysia', 'Indonesia',
    'Philippines', 'Singapore', 'Brunei', 'Bangladesh', 'Bhutan',
    'Sri Lanka', 'Maldives', 'Taiwan', 'Mongolia', 'Kazakhstan',
    'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan',
    'Afghanistan', 'Pakistan', 'Iran', 'Iraq', 'Saudi Arabia',
    'Yemen', 'Oman', 'UAE', 'Qatar', 'Bahrain', 'Kuwait', 'Jordan',
    'Lebanon', 'Syria', 'Israel', 'Palestine', 'Turkey', 'Cyprus'
}

def chunk_csv_by_country(input_file, output_dir, country_column='Country'):
    """
    Chunk a CSV file into separate files based on Asian countries.
    
    Args:
        input_file (str): Path to the input CSV file.
        output_dir (str): Directory where the chunked files will be saved.
        country_column (str): Column name in the CSV representing countries.
    """
    # Read the input file
    print(f"Reading input file: {input_file}")
    df = pd.read_csv(input_file)
    
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Process each country
    for country in asian_countries:
        if country in df[country_column].unique():
            # Filter data for the current country
            country_df = df[df[country_column] == country]
            
            # Define output file name
            output_file = os.path.join(output_dir, f"{country}_data.csv")
            
            # Save the filtered data
            print(f"Saving data for {country} with {len(country_df)} records to {output_file}")
            country_df.to_csv(output_file, index=False)
        else:
            print(f"No data found for {country}. Skipping...")
    
    print("Chunking completed.")

# Example usage
if __name__ == "__main__":
    input_file = "Attractions.csv"  # Path to your input file
    output_dir = "CountryChunks"  # Directory to save the chunked files
    chunk_csv_by_country(input_file, output_dir)
