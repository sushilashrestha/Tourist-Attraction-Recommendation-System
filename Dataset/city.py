import requests

# Define the URL for the Google API (e.g., Google Places API)
url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'

# Parameters for the API request
params = {
    'query': 'Garden of Dreams',  # Query for the place you're searching for
    'key': 'AIzaSyDFpKtt2iSsan9PPReh6tVGPRSIfhonnC4'
# Replace with your Google API key
}

# Send the GET request to the Google API
response = requests.get(url, params=params)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON
    data = response.json()
    # Print the JSON response
    print(data)
else:
    print(f"Error: {response.status_code}")
