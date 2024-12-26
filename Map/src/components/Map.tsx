import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

// Mock data structure - replace with your actual database fetch
const mockPlaces = [
  { 
    id: 1, 
    name: "Bhaktapur Durbar Square", 
    city: "Bhaktapur", 
    country: "Nepal",
    latitude: 27.6720,
    longitude: 85.4277
  },
  {
    id: 2,
    name: "Changu Narayan",
    city: "Bhaktapur",
    country: "Nepal",
    latitude: 27.7127,
    longitude: 85.4294
  }
];

const MapRecommendations = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [places, setPlaces] = useState(mockPlaces);
  const [center, setCenter] = useState([27.6720, 85.4277]);
  const [zoom, setZoom] = useState(12);

  const handleSearch = async () => {
    // In real implementation, fetch from your database
    // For now, we'll filter mock data
    const filteredPlaces = mockPlaces.filter(place => 
      place.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      place.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
      place.country.toLowerCase().includes(searchTerm.toLowerCase())
    );

    setPlaces(filteredPlaces);

    if (filteredPlaces.length > 0) {
      setCenter([filteredPlaces[0].latitude, filteredPlaces[0].longitude]);
      setZoom(12);
    }
  };

  return (
    <Card className="w-full max-w-4xl">
      <CardHeader>
        <CardTitle>Discover Places</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <Input
            type="text"
            placeholder="Enter place or country name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="flex-1"
          />
          <Button onClick={handleSearch}>
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
        </div>

        <div className="h-[500px] rounded-lg overflow-hidden border">
          <MapContainer 
            center={center} 
            zoom={zoom} 
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {places.map(place => (
              <Marker 
                key={place.id} 
                position={[place.latitude, place.longitude]}
              >
                <Popup>
                  <div className="p-2">
                    <h3 className="font-bold">{place.name}</h3>
                    <p>{place.city}, {place.country}</p>
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        <div className="mt-4 space-y-2">
          {places.map(place => (
            <Card key={place.id} className="p-4">
              <h3 className="font-bold">{place.name}</h3>
              <p className="text-sm text-gray-600">{place.city}, {place.country}</p>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default MapRecommendations;
