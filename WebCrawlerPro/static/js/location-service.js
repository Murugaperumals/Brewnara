// Location Service - Better location handling without external APIs
class LocationService {
    constructor() {
        this.locationData = {
            // Major cities and regions with coordinates
            cities: [
                { name: "Chennai, Tamil Nadu", lat: 13.0827, lng: 80.2707, radius: 50 },
                { name: "Coimbatore, Tamil Nadu", lat: 11.0168, lng: 76.9558, radius: 30 },
                { name: "Tirupur, Tamil Nadu", lat: 11.1085, lng: 77.3411, radius: 25 },
                { name: "Salem, Tamil Nadu", lat: 11.6643, lng: 78.1460, radius: 25 },
                { name: "Erode, Tamil Nadu", lat: 11.3410, lng: 77.7172, radius: 20 },
                { name: "Bangalore, Karnataka", lat: 12.9716, lng: 77.5946, radius: 40 },
                { name: "Mumbai, Maharashtra", lat: 19.0760, lng: 72.8777, radius: 50 },
                { name: "Delhi, India", lat: 28.6139, lng: 77.2090, radius: 50 },
                { name: "Kolkata, West Bengal", lat: 22.5726, lng: 88.3639, radius: 40 },
                { name: "Hyderabad, Telangana", lat: 17.3850, lng: 78.4867, radius: 40 },
                { name: "Pune, Maharashtra", lat: 18.5204, lng: 73.8567, radius: 30 },
                { name: "Kochi, Kerala", lat: 9.9312, lng: 76.2673, radius: 25 },
                { name: "Thiruvananthapuram, Kerala", lat: 8.5241, lng: 76.9366, radius: 20 }
            ]
        };
    }

    // Calculate distance between two points
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.toRadians(lat2 - lat1);
        const dLng = this.toRadians(lng2 - lng1);
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                  Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    // Get nearest city or general location
    getLocationName(lat, lng) {
        // Find nearest city
        let nearestCity = null;
        let minDistance = Infinity;

        for (const city of this.locationData.cities) {
            const distance = this.calculateDistance(lat, lng, city.lat, city.lng);
            if (distance <= city.radius && distance < minDistance) {
                minDistance = distance;
                nearestCity = city;
            }
        }

        if (nearestCity) {
            return nearestCity.name;
        }

        // Fallback to general region based on coordinates
        return this.getGeneralRegion(lat, lng);
    }

    // Get general region based on coordinates
    getGeneralRegion(lat, lng) {
        // India regions
        if (lat >= 8 && lat <= 37 && lng >= 68 && lng <= 97) {
            if (lat >= 8 && lat <= 12 && lng >= 76 && lng <= 80) {
                return "South India (Tamil Nadu/Kerala region)";
            } else if (lat >= 12 && lat <= 16 && lng >= 74 && lng <= 80) {
                return "South India (Karnataka/Andhra region)";
            } else if (lat >= 16 && lat <= 22 && lng >= 72 && lng <= 82) {
                return "Central India (Maharashtra/Telangana region)";
            } else if (lat >= 22 && lat <= 28 && lng >= 70 && lng <= 88) {
                return "North India (Gujarat/Rajasthan/MP region)";
            } else if (lat >= 28 && lat <= 37 && lng >= 75 && lng <= 88) {
                return "North India (Delhi/Punjab/UP region)";
            } else {
                return "India";
            }
        }

        // Other regions
        if (lat >= 35 && lat <= 45 && lng >= -125 && lng <= -65) {
            return "United States";
        } else if (lat >= 49 && lat <= 60 && lng >= -140 && lng <= -52) {
            return "Canada";
        } else if (lat >= 50 && lat <= 60 && lng >= -10 && lng <= 30) {
            return "Europe";
        } else if (lat >= -35 && lat <= -10 && lng >= 110 && lng <= 155) {
            return "Australia";
        } else {
            return `Location (${lat.toFixed(2)}, ${lng.toFixed(2)})`;
        }
    }

    // Use browser's reverse geocoding if available
    async reverseGeocode(lat, lng) {
        try {
            // Try using the browser's built-in reverse geocoding
            if ('geolocation' in navigator && 'reverseGeocode' in navigator.geolocation) {
                const result = await navigator.geolocation.reverseGeocode({ latitude: lat, longitude: lng });
                if (result && result.length > 0) {
                    return result[0].formatted_address || result[0].name;
                }
            }
        } catch (error) {
            console.log('Browser reverse geocoding not available');
        }

        // Fallback to our local location service
        return this.getLocationName(lat, lng);
    }
}

// Initialize location service
const locationService = new LocationService();

// Global functions for backward compatibility
function reverseGeocode(lat, lng) {
    return locationService.reverseGeocode(lat, lng);
}

function getGeneralLocation(lat, lng) {
    return locationService.getLocationName(lat, lng);
}

// Export for use in other scripts
window.LocationService = LocationService;
window.locationService = locationService;