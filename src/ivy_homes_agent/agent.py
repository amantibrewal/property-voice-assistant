"""Ivy Homes property inquiry voice agent."""

import logging
import os
from typing import Annotated

from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import (
    Agent,
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
    metrics,
    stt,
    tts,
    turn_detector,
)
from livekit.plugins import cartesia, openai, noise_cancellation

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
        @llm.ai_callable(description="Search for residential flats for sale in Bangalore based on buyer criteria")
        async def search_properties(
            location: Annotated[
                str | None,
                llm.TypeInfo(description="Neighborhood or area in Bangalore (e.g., Whitefield, Koramangala, HSR Layout, Indiranagar, Electronic City)")
            ] = None,
            property_type: Annotated[
                str | None,
                llm.TypeInfo(description="Always 'apartment' or 'flat' - we only sell residential flats")
            ] = None,
            min_price: Annotated[
                float | None,
                llm.TypeInfo(description="Minimum price in Indian Rupees")
            ] = None,
            max_price: Annotated[
                float | None,
                llm.TypeInfo(description="Maximum price in Indian Rupees")
            ] = None,
            bedrooms: Annotated[
                int | None,
                llm.TypeInfo(description="Number of bedrooms/BHK required (1, 2, 3, or 4)")
            ] = None,
            bathrooms: Annotated[
                int | None,
                llm.TypeInfo(description="Number of bathrooms required")
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
        @llm.ai_callable(description="Get detailed information about a specific flat for sale")
        async def get_property_details(
            property_id: Annotated[
                str,
                llm.TypeInfo(description="The unique ID of the flat")
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

        # Initialize the language model with property context
        language_model = openai.LLM(
            model="gpt-4o-mini",
            temperature=0.7,  # Slightly creative but focused
        )

        # Speech-to-text using OpenAI Whisper
        speech_to_text = openai.STT(
            model="whisper-1",
        )

        # Text-to-speech using Cartesia for natural voice
        text_to_speech = cartesia.TTS(
            model="sonic-3-english",
            voice="79a125e8-cd45-4c2e-bb9c-42b5d0a1804f",  # Friendly, professional voice
            encoding="pcm_s16le",
            sample_rate=24000,
        )

        # Configure turn detection for natural conversation flow
        turn_detection = turn_detector.EOUModel()

        # Create the assistant pipeline with function calling
        assistant = cls(
            instructions=AGENT_INSTRUCTIONS,
            llm=language_model,
            stt=speech_to_text,
            tts=text_to_speech,
            turn_detector=turn_detection,
            will_synthesize_assistant_reply=turn_detector.PredictionHint.LIKELY,
            preemptive_synthesis=True,  # Start generating response while user speaks
            min_endpointing_delay=0.5,  # Wait 0.5s after user stops speaking
            fnc_ctx=llm.FunctionContext(),  # Enable function calling
        )

        # Register the property search functions
        assistant.fnc_ctx.ai_callable(search_properties)
        assistant.fnc_ctx.ai_callable(get_property_details)

        # Add noise cancellation for better audio quality
        assistant.add_filter(
            noise_cancellation.BVC(
                aggressiveness=noise_cancellation.BVCAggressiveness.MEDIUM,
            )
        )

        # Track metrics
        assistant.add_filter(metrics.PipelineMetrics())

        return assistant


@agents.on_process_start
async def on_process_start() -> None:
    """Initialize the agent process."""
    logger.info("Ivy Homes voice agent process started")


@agents.on_job_request
async def entrypoint(job_request: agents.JobRequest) -> None:
    """Handle incoming job requests and manage agent lifecycle."""
    logger.info("Processing new job request for room: %s", job_request.room.name)

    await job_request.accept(
        entrypoint=_job_entrypoint,
        auto_subscribe=AutoSubscribe.AUDIO_ONLY,
    )


async def _job_entrypoint(job_context: JobContext) -> None:
    """Main entry point for agent jobs."""
    logger.info("Agent joining room: %s", job_context.room.name)

    # Create and start the assistant
    assistant = IvyHomesAssistant.create_pipeline(job_context)
    assistant.start(job_context.room)

    # Wait for the first participant to join
    await assistant.say("Hello! Welcome to Ivy Homes. How can I help you today?")

    logger.info("Ivy Homes assistant started successfully")


if __name__ == "__main__":
    # Run the agent using LiveKit CLI
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
