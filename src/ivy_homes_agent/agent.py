"""Ivy Homes property inquiry voice agent."""

import logging
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

load_dotenv()

logger = logging.getLogger("ivy-homes-agent")
logger.setLevel(logging.INFO)


# Property inquiry context for Ivy Homes
AGENT_INSTRUCTIONS = """You are a friendly and professional voice assistant for Ivy Homes, a real estate company.

Your role is to help potential buyers and renters with property inquiries. You should:

1. Greet callers warmly and identify yourself as the Ivy Homes assistant
2. Ask what type of property they're looking for (house, apartment, commercial, etc.)
3. Gather key requirements:
   - Location preferences
   - Budget range
   - Number of bedrooms/bathrooms
   - Special features or requirements
   - Preferred move-in date

4. Provide general information about:
   - Ivy Homes services (buying, renting, property management)
   - Current market conditions (when asked)
   - The property inquiry process

5. For specific property questions you cannot answer:
   - Politely explain that you'll connect them with a specialist
   - Offer to schedule a callback or viewing appointment
   - Collect their contact information (name, phone, email)

Keep responses concise and natural for voice conversation. Avoid complex formatting, bullet points, or long paragraphs.
Be empathetic and patient, especially with first-time buyers or renters.

Remember: You're providing initial assistance and gathering information. For specific property details, prices, or legal questions, offer to connect them with a property specialist."""


class IvyHomesAssistant(Agent):
    """Voice agent for Ivy Homes property inquiries."""

    @classmethod
    def create_pipeline(cls, job_context: JobContext) -> "IvyHomesAssistant":
        """Create the voice pipeline for the agent."""
        logger.info("Creating Ivy Homes assistant pipeline")

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

        # Create the assistant pipeline
        assistant = cls(
            instructions=AGENT_INSTRUCTIONS,
            llm=language_model,
            stt=speech_to_text,
            tts=text_to_speech,
            turn_detector=turn_detection,
            will_synthesize_assistant_reply=turn_detector.PredictionHint.LIKELY,
            preemptive_synthesis=True,  # Start generating response while user speaks
            min_endpointing_delay=0.5,  # Wait 0.5s after user stops speaking
        )

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
