import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMapEvents,
} from 'react-leaflet';
import {
  Box,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import { LocationOn } from '@mui/icons-material';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Исправляем иконки маркеров для Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl:
    'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface LocationPickerProps {
  open: boolean;
  onClose: () => void;
  onLocationSelect: (location: {
    lat: number;
    lng: number;
    address: string;
    city?: string;
    region?: string;
  }) => void;
  initialLocation?: { lat: number; lng: number };
  embedded?: boolean; // Режим встраивания без диалога
}

interface MapClickHandlerProps {
  onLocationSelect: (location: {
    lat: number;
    lng: number;
    address: string;
    city?: string;
    region?: string;
  }) => void;
}

const MapClickHandler: React.FC<MapClickHandlerProps & { autoSelect?: boolean }> = ({
  onLocationSelect,
  autoSelect = false,
}) => {
  const [position, setPosition] = useState<{ lat: number; lng: number } | null>(
    null,
  );

  useMapEvents({
    click: async e => {
      const { lat, lng } = e.latlng;
      setPosition({ lat, lng });

      // Получаем адрес через обратное геокодирование (используем Nominatim API)
      try {
        const response = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`,
          {
            headers: {
              'User-Agent': 'AgregatorService/1.0',
            },
          }
        );
        const data = await response.json();
        const address = data.display_name || `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
        const addr = data.address || {};
        const city = addr.city || addr.town || addr.village || addr.hamlet || '';
        const region = addr.state || addr.region || addr.province || addr.county || '';

        const locationData = { lat, lng, address, city, region };
        
        // Если autoSelect = true, сразу вызываем onLocationSelect без подтверждения
        if (autoSelect) {
          onLocationSelect(locationData);
        } else {
          // Иначе сохраняем для подтверждения в диалоге
          onLocationSelect(locationData);
        }
      } catch (error) {
        console.error('Ошибка получения адреса:', error);
        const locationData = {
          lat,
          lng,
          address: `${lat.toFixed(6)}, ${lng.toFixed(6)}`,
        };
        if (autoSelect) {
          onLocationSelect(locationData);
        } else {
          onLocationSelect(locationData);
        }
      }
    },
  });

  return position ? (
    <Marker position={position}>
      <Popup>
        <Typography variant='body2'>Выбранное место</Typography>
      </Popup>
    </Marker>
  ) : null;
};

const LocationPicker: React.FC<LocationPickerProps> = ({
  open,
  onClose,
  onLocationSelect,
  initialLocation = { lat: 55.7558, lng: 37.6176 }, // Москва по умолчанию
  embedded = false,
}) => {
  const [selectedLocation, setSelectedLocation] = useState<{
    lat: number;
    lng: number;
    address: string;
    city?: string;
    region?: string;
  } | null>(null);

  const handleLocationSelect = (location: {
    lat: number;
    lng: number;
    address: string;
    city?: string;
    region?: string;
  }) => {
    setSelectedLocation(location);
    // В embedded режиме сразу передаём выбор
    if (embedded) {
      onLocationSelect(location);
    }
  };

  const handleConfirm = () => {
    if (selectedLocation) {
      onLocationSelect(selectedLocation);
      setSelectedLocation(null);
      onClose();
    }
  };

  const handleCancel = () => {
    setSelectedLocation(null);
    onClose();
  };

  // Embedded режим: карта без диалога
  if (embedded) {
    return (
      <MapContainer
        center={initialLocation}
        zoom={13}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
        />
        <MapClickHandler onLocationSelect={handleLocationSelect} autoSelect={true} />
      </MapContainer>
    );
  }

  // Режим диалога
  return (
    <Dialog open={open} onClose={handleCancel} maxWidth='md' fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocationOn color='primary' />
          <Typography variant='h6'>Выберите место на карте</Typography>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ height: 400, width: '100%', mt: 1 }}>
          <MapContainer
            center={initialLocation}
            zoom={13}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
            />
            <MapClickHandler onLocationSelect={handleLocationSelect} />
          </MapContainer>
        </Box>
        {selectedLocation && (
          <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.100', borderRadius: 1 }}>
            <Typography variant='body2' color='text.secondary'>
              Выбранное место:
            </Typography>
            <Typography variant='body1' fontWeight='medium'>
              {selectedLocation.address}
            </Typography>
            <Typography variant='caption' color='text.secondary'>
              Координаты: {selectedLocation.lat.toFixed(6)},{' '}
              {selectedLocation.lng.toFixed(6)}
            </Typography>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCancel}>Отмена</Button>
        <Button
          onClick={handleConfirm}
          variant='contained'
          disabled={!selectedLocation}
        >
          Выбрать место
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default LocationPicker;
