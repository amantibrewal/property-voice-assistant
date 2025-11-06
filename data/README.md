# Property Data for Ivy Homes

This directory contains property inventory data for residential flats in Bangalore that the voice agent uses to answer buyer inquiries.

**Important**: Ivy Homes only sells residential flats/apartments in Bangalore. We do not deal with rentals, houses, villas, or commercial properties.

## Format

The `properties.json` file should follow this structure:

```json
{
  "properties": [
    {
      "id": "BLR-001",
      "type": "apartment",
      "address": "Complex name and street address",
      "neighborhood": "Area name (e.g., Whitefield, Koramangala, HSR Layout)",
      "city": "Bangalore",
      "state": "Karnataka",
      "zip": "560XXX",
      "price": 12500000,
      "bedrooms": 2,
      "bathrooms": 2,
      "square_feet": 1250,
      "year_built": 2021,
      "description": "Detailed flat description with amenities and location benefits",
      "features": ["clubhouse", "gym", "swimming pool", "parking"],
      "status": "available",
      "listing_date": "2024-02-01"
    }
  ]
}
```

## Required Fields

- `id`: Unique identifier for the flat (recommend format: BLR-XXX)
- `type`: Always "apartment" (we only sell flats)
- `neighborhood`: Area/locality in Bangalore
- `city`: Always "Bangalore"
- `price`: Price in Indian Rupees (e.g., 12500000 for ₹1.25 crores)
- `bedrooms`: Number of BHK (1, 2, 3, or 4)
- `bathrooms`: Number of bathrooms

## Optional but Recommended Fields

- `address`: Full address including complex/society name
- `square_feet`: Carpet/super built-up area
- `year_built`: Construction year
- `description`: Detailed description highlighting amenities and connectivity
- `features`: Array of amenities (clubhouse, gym, parking, security, etc.)
- `status`: "available", "pending", or "sold"

## Pricing Guidelines

Prices should be in Indian Rupees:
- 1 lakh = 100,000 (₹1,00,000)
- 1 crore = 10,000,000 (₹1,00,00,000)
- Example: A flat priced at ₹85 lakhs should be entered as 8500000

The agent will automatically convert these to lakhs/crores when speaking.

## Updating Data

### Option 1: File-Based (Current)

Simply edit `properties.json` with your current inventory. The agent will load this data on startup.

### Option 2: API Integration

To integrate with a live API:

1. Set environment variables:
   ```
   PROPERTY_DATA_SOURCE=api
   PROPERTY_API_URL=https://your-api.com/properties
   PROPERTY_API_KEY=your-api-key
   ```

2. Implement the API integration in `src/ivy_homes_agent/property_service.py`

### Option 3: Database Integration

For production use with a database:

1. Set `PROPERTY_DATA_SOURCE=database`
2. Add database connection code to `property_service.py`
3. Update the search methods to query your database

## Sample Data

The included `properties.json` contains 10 sample flats across popular Bangalore neighborhoods including:
- Whitefield (IT corridor)
- HSR Layout (prime residential)
- Electronic City (tech hub)
- Bellandur (IT corridor)
- Marathahalli (central location)
- Kanakapura Road (emerging area)

Price range: ₹75 lakhs to ₹2.5 crores
BHK range: 1 BHK to 4 BHK

Replace this with your actual Ivy Homes inventory data.
