"""Ivy Homes property inquiry voice agent."""

import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.plugins import openai, silero

from .property_service import PropertyService

load_dotenv()

logger = logging.getLogger("ivy-homes-agent")
logger.setLevel(logging.INFO)

# Initialize property service
PROPERTY_SERVICE = PropertyService(
    data_source=os.getenv("PROPERTY_DATA_SOURCE", "file"),
    data_path=os.getenv("PROPERTY_DATA_PATH", "data/properties.json"),
    api_url=os.getenv("PROPERTY_API_URL"),
    api_key=os.getenv("PROPERTY_API_KEY"),
)


# Property inquiry context for Ivy Homes
AGENT_INSTRUCTIONS = """You are a friendly and professional voice assistant for Ivy Homes, a real estate company specializing in residential flats in Bangalore.

IMPORTANT: Ivy Homes ONLY sells residential flats (apartments) in Bangalore. We do NOT have:
- Rental properties (we only sell)
- Houses, villas, or independent homes
- Commercial properties
- Properties outside Bangalore

Your role is to help potential buyers find and purchase flats in Bangalore. You have access to our live property inventory.

You should:

1. Greet callers warmly and identify yourself as the Ivy Homes assistant
2. Clarify that we specialize in selling residential flats in Bangalore
3. If they ask about rentals or other property types, politely explain we only sell flats
4. Gather key requirements for flat purchase:
   - Preferred area/neighborhood in Bangalore (e.g., Whitefield, Koramangala, HSR Layout, Indiranagar)
   - Budget range in Indian Rupees (lakhs or crores)
   - Number of BHK (1 BHK, 2 BHK, 3 BHK, 4 BHK)
   - Special features (parking, amenities, floor preference, facing)
   - Timeline for purchase

5. **Use the search_properties function** to find matching flats when you have enough criteria
   - You MUST call this function when the buyer asks about available flats
   - Share the results naturally in conversation
   - Describe flats enthusiastically with details about location, amenities, and features
   - If no flats match, suggest adjusting their budget or location preferences

6. **Use get_property_details function** when they ask about a specific flat

7. After sharing flats:
   - Ask if they'd like more details about any specific flat
   - Offer to schedule a site visit/viewing
   - Ask if they want to see other options in different areas or budget ranges
   - Mention amenities and nearby facilities (metro stations, schools, hospitals, tech parks)

8. For scheduling site visits or detailed discussions:
   - Offer to connect them with a property specialist
   - Collect their contact information (name, phone number, email)

Keep responses concise and natural for voice conversation. Use Indian English and terminology (flat, lakhs, crores, BHK).
Be empathetic and patient, especially with first-time home buyers.

When you find flats, be excited and descriptive! Highlight Bangalore-specific benefits like proximity to tech parks, metro connectivity, and amenities."""


class IvyHomesAssistant(Agent):
    """Voice agent for Ivy Homes property inquiries."""

    @classmethod
    def create_pipeline(cls, job_context: JobContext) -> "IvyHomesAssistant":
        """Create the voice pipeline for the agent."""
        logger.info("Creating Ivy Homes assistant pipeline")

        # Define function for searching flats
        @llm.function_tool(description="Search for residential flats for sale in Bangalore based on buyer criteria")
        async def search_properties(
            location: Annotated[
                str | None,
                "Neighborhood or area in Bangalore (e.g., Whitefield, Koramangala, HSR Layout, Indiranagar, Electronic City)"
            ] = None,
            property_type: Annotated[
                str | None,
                "Always 'apartment' or 'flat' - we only sell residential flats"
            ] = None,
            min_price: Annotated[
                float | None,
                "Minimum price in Indian Rupees"
            ] = None,
            max_price: Annotated[
                float | None,
                "Maximum price in Indian Rupees"
            ] = None,
            bedrooms: Annotated[
                int | None,
                "Number of bedrooms/BHK required (1, 2, 3, or 4)"
            ] = None,
            bathrooms: Annotated[
                int | None,
                "Number of bathrooms required"
            ] = None,
        ) -> str:
            """Search for flats matching the buyer's criteria."""
            logger.info("Function called: search_properties")

            properties = await PROPERTY_SERVICE.search_properties(
                location=location,
                property_type=property_type,
                min_price=min_price,
                max_price=max_price,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                max_results=5,
            )

            return PROPERTY_SERVICE.format_property_summary(properties)

        # Define function for getting flat details
        @llm.function_tool(description="Get detailed information about a specific flat for sale")
        async def get_property_details(
            property_id: Annotated[
                str,
                "The unique ID of the flat"
            ],
        ) -> str:
            """Get details about a specific flat."""
            logger.info(f"Function called: get_property_details({property_id})")

            prop = await PROPERTY_SERVICE.get_property_details(property_id)

            if not prop:
                return f"I couldn't find a flat with ID {property_id}."

            # Format price in Indian Rupees (lakhs/crores)
            price = prop.get('price', 0)
            if price >= 10000000:  # 1 crore or more
                price_str = f"₹{price / 10000000:.2f} crores"
            else:
                price_str = f"₹{price / 100000:.2f} lakhs"

            return (
                f"Here are the details for this flat: "
                f"It's a {prop.get('bedrooms', 0)}-BHK flat with {prop.get('bathrooms', 0)} bathrooms, "
                f"located in {prop.get('neighborhood', '')}, {prop.get('city', 'Bangalore')}. "
                f"The address is {prop.get('address', 'available on request')}. "
                f"The price is {price_str}. "
                f"It has {prop.get('square_feet', 0)} square feet of space. "
                f"{prop.get('description', '')} "
                f"Built in {prop.get('year_built', 'recent year')}. "
            )

        # Create the assistant with function calling
        assistant = cls(
            instructions=AGENT_INSTRUCTIONS,
            tools=[search_properties, get_property_details],
        )

        return assistant


async def entrypoint(job_context: JobContext) -> None:
    """Handle incoming job requests and manage agent lifecycle."""
    logger.info("Agent joining room: %s", job_context.room.name)

    # Connect to the room
    await job_context.connect()

    # Create the assistant
    assistant = IvyHomesAssistant.create_pipeline(job_context)

    # Create and start the agent session
    session = AgentSession(
        vad=silero.VAD.load(),
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o-mini", temperature=0.7),
        tts=openai.TTS(voice="alloy"),
    )

    await session.start(agent=assistant, room=job_context.room)

    # Generate initial greeting
    await session.generate_reply(
        instructions="Greet the caller warmly and introduce yourself as the Ivy Homes assistant."
    )

    logger.info("Ivy Homes assistant started successfully")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
