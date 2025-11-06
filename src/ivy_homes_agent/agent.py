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
AGENT_INSTRUCTIONS = """You are a friendly and professional voice assistant for Ivy Homes, a real estate company.

Your role is to help potential buyers and renters with property inquiries. You have access to our live property inventory and can search for specific properties based on customer requirements.

You should:

1. Greet callers warmly and identify yourself as the Ivy Homes assistant
2. Ask what type of property they're looking for (house, apartment, condo, commercial, etc.)
3. Gather key requirements:
   - Location preferences (city, neighborhood)
   - Budget range (min and max price)
   - Number of bedrooms/bathrooms
   - Property type
   - Special features or requirements

4. **Use the search_properties function** to find matching properties when you have enough criteria
   - You MUST call this function when the user asks about available properties
   - Share the results naturally in conversation
   - If you find properties, describe them enthusiastically with details
   - If no properties match, suggest adjusting their criteria

5. **Use get_property_details function** when they ask about a specific property

6. After sharing properties:
   - Ask if they'd like more details
   - Offer to schedule a viewing
   - Ask if they want to see other options

7. For questions you cannot answer or to schedule viewings:
   - Offer to connect them with a property specialist
   - Collect their contact information (name, phone, email)

Keep responses concise and natural for voice conversation. Avoid complex formatting, bullet points, or long paragraphs.
Be empathetic and patient, especially with first-time buyers or renters.

When you find properties, be excited and descriptive! Make them sound appealing while being accurate."""


class IvyHomesAssistant(Agent):
    """Voice agent for Ivy Homes property inquiries."""

    @classmethod
    def create_pipeline(cls, job_context: JobContext) -> "IvyHomesAssistant":
        """Create the voice pipeline for the agent."""
        logger.info("Creating Ivy Homes assistant pipeline")

        # Define function for searching properties
        @llm.ai_callable(description="Search for properties in the inventory based on criteria")
        async def search_properties(
            location: Annotated[
                str | None,
                llm.TypeInfo(description="City, neighborhood, or area to search in")
            ] = None,
            property_type: Annotated[
                str | None,
                llm.TypeInfo(description="Type of property: house, apartment, condo, or commercial")
            ] = None,
            min_price: Annotated[
                float | None,
                llm.TypeInfo(description="Minimum price in dollars")
            ] = None,
            max_price: Annotated[
                float | None,
                llm.TypeInfo(description="Maximum price in dollars")
            ] = None,
            bedrooms: Annotated[
                int | None,
                llm.TypeInfo(description="Number of bedrooms required")
            ] = None,
            bathrooms: Annotated[
                int | None,
                llm.TypeInfo(description="Number of bathrooms required")
            ] = None,
        ) -> str:
            """Search for properties matching the criteria."""
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

        # Define function for getting property details
        @llm.ai_callable(description="Get detailed information about a specific property")
        async def get_property_details(
            property_id: Annotated[
                str,
                llm.TypeInfo(description="The unique ID of the property")
            ],
        ) -> str:
            """Get details about a specific property."""
            logger.info(f"Function called: get_property_details({property_id})")

            prop = await PROPERTY_SERVICE.get_property_details(property_id)

            if not prop:
                return f"I couldn't find a property with ID {property_id}."

            return (
                f"Here are the details for this property: "
                f"It's a {prop.get('bedrooms', 0)}-bedroom, {prop.get('bathrooms', 0)}-bathroom "
                f"{prop.get('type', 'property')} located at {prop.get('address', 'the address')} "
                f"in {prop.get('neighborhood', '')}, {prop.get('city', '')}. "
                f"The price is ${prop.get('price', 0):,.0f}. "
                f"It has {prop.get('square_feet', 0)} square feet. "
                f"{prop.get('description', '')} "
                f"Built in {prop.get('year_built', 'unknown')}. "
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
