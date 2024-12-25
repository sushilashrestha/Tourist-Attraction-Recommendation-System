import sqlite3
import csv
import requests
import time
import wikipediaapi

# OpenCage API Key
API_KEY = "e85a25e755224526ade70b3e9239ffbe"

# List of Asian countries
ASIAN_COUNTRIES = [
    "Afghanistan", "Armenia", "Azerbaijan", "Bahrain", "Bangladesh", "Bhutan", "Brunei", "Cambodia", "China",
    "Cyprus", "Georgia", "India", "Indonesia", "Iran", "Iraq", "Israel", "Japan", "Jordan", "Kazakhstan", "Kuwait",
    "Kyrgyzstan", "Laos", "Lebanon", "Malaysia", "Maldives", "Mongolia", "Myanmar (Burma)", "Nepal", "North Korea",
    "Oman", "Pakistan", "Palestine", "Philippines", "Qatar", "Saudi Arabia", "Singapore", "South Korea", "Sri Lanka",
    "Syria", "Tajikistan", "Thailand", "Timor-Leste", "Turkey", "Turkmenistan", "United Arab Emirates", "Uzbekistan",
    "Vietnam", "Yemen"
]

# Initialize Wikipedia API
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent="MyFinalYearProject/1.0 ()"
)


# Database connection
conn = sqlite3.connect("attractions.db")
cursor = conn.cursor()

# Create the Attractions table if it doesn't exist
cursor.execute(""" 
CREATE TABLE IF NOT EXISTS Attractions (
    ID INTEGER PRIMARY KEY,
    Name TEXT,
    City TEXT,
    Country TEXT,
    Latitude REAL,
    Longitude REAL,
    Description TEXT,
    UNIQUE(Name, City, Country)
)
""")
conn.commit()

# Function to get geocoding data from OpenCage API and filter for Asia
def get_geocode(name):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={name}&key={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            for result in data["results"]:
                country = result["components"].get("country", "Unknown")
                if country in ASIAN_COUNTRIES:  # Only consider places in Asia
                    city = result["components"].get("city", "Unknown")
                    lat = result["geometry"]["lat"]
                    lng = result["geometry"]["lng"]
                    return city, country, lat, lng
    else:
        print(f"API error for {name}: {response.status_code} {response.text}")
    return None, None, None, None

# Function to get description from Wikipedia if it's missing
def get_wikipedia_description(query):
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary
    else:
        return "Description not available"

# Output files
output_csv = "updated_attractions.csv"
skipped_csv = "skipped_attractions.csv"

# Open output CSV files
with open("attractions.csv", "r", encoding="utf-8") as csv_file, \
     open(output_csv, "w", newline="", encoding="utf-8") as updated_file, \
     open(skipped_csv, "w", newline="", encoding="utf-8") as skipped_file:

    csv_reader = csv.DictReader(csv_file)
    fieldnames = csv_reader.fieldnames + ["Latitude", "Longitude"]  # Add Lat/Lon columns

    updated_writer = csv.DictWriter(updated_file, fieldnames=fieldnames)
    skipped_writer = csv.DictWriter(skipped_file, fieldnames=csv_reader.fieldnames)

    updated_writer.writeheader()
    skipped_writer.writeheader()

    # Skip rows until ID 1330 is reached
    start_processing = False

    for row in csv_reader:
        try:
            attraction_id = int(row["ID"])

            # Start processing from ID 1330
            if attraction_id < 1330:
                print(f"Skipping ID {attraction_id}, Name: {row['Name']}")
                continue
            else:
                if not start_processing:
                    start_processing = True
                    print("Starting processing from ID 1330...")

            name = row["Name"]
            city = row["City"]
            country = row["Country"]
            description = row["Description"]

            # Skip rows with complete data in Asia
            if city != "Unknown" and country in ASIAN_COUNTRIES:
                print(f"Skipping ID {attraction_id}, Name: {name} (data already complete and in Asia)")
                updated_writer.writerow(row)
                continue

            print(f"Processing ID: {attraction_id}, Name: {name}...")

            # Get geocode data and ensure it's in Asia
            new_city, new_country, lat, lng = get_geocode(name)

            # Skip if no valid data was returned
            if not new_city or not new_country:
                print(f"Skipping ID {attraction_id}, Name: {name} (no valid geocode data)")
                skipped_writer.writerow(row)
                continue

            # Get description from Wikipedia if not available
            if not description:
                print(f"Fetching description for {name} from Wikipedia...")
                description = get_wikipedia_description(name)

            # Update row with new data
            row["City"] = new_city
            row["Country"] = new_country
            row["Latitude"] = lat
            row["Longitude"] = lng
            row["Description"] = description

            # Insert or update the row in the database
            try:
                cursor.execute(""" 
                INSERT OR REPLACE INTO Attractions (ID, Name, City, Country, Latitude, Longitude, Description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (attraction_id, name, new_city, new_country, lat, lng, description))
                conn.commit()
                print(f"Updated ID {attraction_id}, Name: {name} with City: {new_city}, Country: {new_country}, Lat: {lat}, Lon: {lng}")

                updated_writer.writerow(row)
            except sqlite3.IntegrityError as e:
                print(f"Database error for ID {attraction_id}, Name: {name}: {e}")
                skipped_writer.writerow(row)
                continue

        except Exception as e:
            print(f"Unexpected error for ID {row['ID']}, Name: {row['Name']}: {e}")
            skipped_writer.writerow(row)
            continue

# Close the database connection
conn.close()
print("Processing complete.")
