"""Property data service for querying live inventory."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("ivy-homes-agent")


class PropertyService:
    """Service for querying property inventory data.

    This service supports multiple data sources:
    - JSON file (for simple setups)
    - REST API (for live data)
    - Database (for production)
    """

    def __init__(
        self,
        data_source: str = "file",
        data_path: Optional[str] = None,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """Initialize the property service.

        Args:
            data_source: Source type ('file', 'api', or 'database')
            data_path: Path to JSON file (if using file source)
            api_url: API endpoint URL (if using API source)
            api_key: API authentication key (if required)
        """
        self.data_source = data_source
        self.data_path = data_path
        self.api_url = api_url
        self.api_key = api_key
        self.properties = []

        if data_source == "file":
            self._load_from_file()

    def _load_from_file(self) -> None:
        """Load property data from JSON file."""
        if not self.data_path:
            logger.warning("No data path specified, using empty property list")
            return

        try:
            data_file = Path(self.data_path)
            if data_file.exists():
                with open(data_file) as f:
                    data = json.load(f)
                    self.properties = data.get("properties", [])
                logger.info(f"Loaded {len(self.properties)} properties from file")
            else:
                logger.warning(f"Property data file not found: {self.data_path}")
        except Exception as e:
            logger.error(f"Error loading property data: {e}")

    async def search_properties(
        self,
        location: Optional[str] = None,
        property_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        bedrooms: Optional[int] = None,
        bathrooms: Optional[int] = None,
        max_results: int = 5,
    ) -> list[dict[str, Any]]:
        """Search for properties matching the criteria.

        Args:
            location: City, neighborhood, or area
            property_type: Type like 'house', 'apartment', 'condo', 'commercial'
            min_price: Minimum price
            max_price: Maximum price
            bedrooms: Number of bedrooms
            bathrooms: Number of bathrooms
            max_results: Maximum number of results to return

        Returns:
            List of matching properties with details
        """
        logger.info(
            f"Searching properties: location={location}, type={property_type}, "
            f"price={min_price}-{max_price}, bed={bedrooms}, bath={bathrooms}"
        )

        if self.data_source == "file":
            return self._search_file(
                location, property_type, min_price, max_price,
                bedrooms, bathrooms, max_results
            )
        elif self.data_source == "api":
            return await self._search_api(
                location, property_type, min_price, max_price,
                bedrooms, bathrooms, max_results
            )
        else:
            logger.error(f"Unsupported data source: {self.data_source}")
            return []

    def _search_file(
        self,
        location: Optional[str],
        property_type: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        bedrooms: Optional[int],
        bathrooms: Optional[int],
        max_results: int,
    ) -> list[dict[str, Any]]:
        """Search properties from loaded file data."""
        results = []

        for prop in self.properties:
            # Filter by location
            if location:
                prop_location = (
                    prop.get("city", "").lower() + " " +
                    prop.get("neighborhood", "").lower() + " " +
                    prop.get("address", "").lower()
                )
                if location.lower() not in prop_location:
                    print('Here could be location issue')
                    continue

            # Filter by property type
            if property_type:
                if prop.get("type", "").lower() != property_type.lower():
                    print('Here could be property type issue')
                    continue

            # Filter by price range
            price = prop.get("price", 0)
            if min_price and price < min_price:
                print('Here could be min price issue')
                continue
            if max_price and price > max_price:
                print('Here could be max price issue')
                continue

            # Filter by bedrooms
            if bedrooms:
                if prop.get("bedrooms") != bedrooms:
                    print('Here could be bedrooms issue')
                    continue

            # Filter by bathrooms
            if bathrooms:
                if prop.get("bathrooms") != bathrooms:
                    print('Here could be bathrooms issue')
                    continue

            results.append(prop)

            if len(results) >= max_results:
                break

        logger.info(f"Found {len(results)} matching properties")
        return results

    async def _search_api(
        self,
        location: Optional[str],
        property_type: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        bedrooms: Optional[int],
        bathrooms: Optional[int],
        max_results: int,
    ) -> list[dict[str, Any]]:
        """Search properties via API."""
        # TODO: Implement API integration
        # Example structure:
        # import aiohttp
        # params = {
        #     "location": location,
        #     "type": property_type,
        #     "min_price": min_price,
        #     "max_price": max_price,
        #     "bedrooms": bedrooms,
        #     "bathrooms": bathrooms,
        #     "limit": max_results,
        # }
        # headers = {"Authorization": f"Bearer {self.api_key}"}
        # async with aiohttp.ClientSession() as session:
        #     async with session.get(self.api_url, params=params, headers=headers) as resp:
        #         data = await resp.json()
        #         return data.get("properties", [])

        logger.warning("API integration not yet implemented")
        return []

    async def get_property_details(self, property_id: str) -> Optional[dict[str, Any]]:
        """Get detailed information about a specific property.

        Args:
            property_id: Unique property identifier

        Returns:
            Property details or None if not found
        """
        logger.info(f"Fetching details for property: {property_id}")

        if self.data_source == "file":
            for prop in self.properties:
                if prop.get("id") == property_id:
                    return prop
            return None
        elif self.data_source == "api":
            # TODO: Implement API call
            logger.warning("API integration not yet implemented")
            return None
        else:
            return None

    def format_property_summary(self, properties: list[dict[str, Any]]) -> str:
        """Format property list for voice response.

        Args:
            properties: List of property dictionaries

        Returns:
            Formatted string suitable for voice output
        """
        if not properties:
            return "I couldn't find any properties matching your criteria."

        if len(properties) == 1:
            prop = properties[0]
            return (
                f"I found a {prop.get('type', 'property')} at {prop.get('address', 'an available location')}. "
                f"It has {prop.get('bedrooms', 0)} bedrooms, {prop.get('bathrooms', 0)} bathrooms, "
                f"and is priced at ${prop.get('price', 0):,.0f}. "
                f"{prop.get('description', '')}"
            )
        else:
            summary = f"I found {len(properties)} properties. Here are the top matches: "
            for i, prop in enumerate(properties[:3], 1):
                summary += (
                    f"Property {i}: A {prop.get('bedrooms', 0)}-bedroom "
                    f"{prop.get('type', 'property')} in {prop.get('neighborhood', prop.get('city', 'the area'))} "
                    f"for ${prop.get('price', 0):,.0f}. "
                )

            if len(properties) > 3:
                summary += f"And {len(properties) - 3} more options. "

            summary += "Would you like more details on any of these?"
            return summary
