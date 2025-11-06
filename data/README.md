# Property Data

This directory contains property inventory data that the voice agent uses to answer inquiries.

## Format

The `properties.json` file should follow this structure:

```json
{
  "properties": [
    {
      "id": "unique-property-id",
      "type": "house|apartment|condo|commercial",
      "address": "Street address",
      "neighborhood": "Neighborhood name",
      "city": "City name",
      "state": "State code",
      "zip": "Postal code",
      "price": 1000000,
      "bedrooms": 3,
      "bathrooms": 2,
      "square_feet": 2000,
      "year_built": 2020,
      "description": "Detailed property description",
      "features": ["feature1", "feature2"],
      "status": "available|pending|sold",
      "listing_date": "YYYY-MM-DD"
    }
  ]
}
```

## Required Fields

- `id`: Unique identifier for the property
- `type`: Property type (house, apartment, condo, commercial)
- `city`: City where property is located
- `price`: Listing price in dollars
- `bedrooms`: Number of bedrooms
- `bathrooms`: Number of bathrooms

## Optional Fields

All other fields are optional but recommended for better search results and descriptions.

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

The included `properties.json` contains 8 sample properties in San Francisco. Replace this with your actual inventory data.
