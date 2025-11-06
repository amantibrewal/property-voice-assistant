# Ivy Homes Voice Assistant

A real-time AI voice assistant for property inquiries, built with LiveKit Agents framework. This assistant helps potential buyers and renters with property searches, scheduling viewings, and connecting with property specialists.

## Features

- **Real-time Voice Conversations**: Natural, conversational AI powered by OpenAI GPT-4
- **Property Inquiry Handling**: Specialized prompts for real estate inquiries
- **Multi-platform Support**: Web browser, mobile apps, or telephone integration
- **High-Quality Audio**: Professional text-to-speech with Cartesia
- **Noise Cancellation**: Built-in audio enhancement for clear conversations
- **Easy Deployment**: Docker support and cloud-ready architecture

## Architecture

### Backend (Python Agent)
- **Framework**: LiveKit Agents v1.2
- **LLM**: OpenAI GPT-4o-mini for natural language understanding
- **STT**: OpenAI Whisper for speech-to-text
- **TTS**: Cartesia Sonic-3 for high-quality voice synthesis
- **Audio Processing**: Silero VAD and BVC noise cancellation

### Frontend (Next.js)
- **Framework**: Next.js 14 with TypeScript
- **UI Library**: LiveKit React Components
- **Styling**: Tailwind CSS
- **Real-time Communication**: LiveKit Client SDK

## Prerequisites

Before you begin, ensure you have:

- Python 3.9 or higher
- Node.js 18 or higher
- A LiveKit account ([sign up at cloud.livekit.io](https://cloud.livekit.io))
- OpenAI API key ([get one here](https://platform.openai.com))
- Cartesia API key ([sign up at cartesia.ai](https://cartesia.ai))

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd property-voice-assistant
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
OPENAI_API_KEY=your-openai-api-key
CARTESIA_API_KEY=your-cartesia-api-key
```

### 3. Install Python Dependencies

Using pip:
```bash
pip install -r requirements.txt
```

Or using the project setup:
```bash
pip install -e .
```

### 4. Run the Voice Agent

```bash
python -m livekit.agents.cli start src.ivy_homes_agent.agent
```

The agent will start and wait for connections from the frontend.

### 5. Setup and Run Frontend

In a new terminal:

```bash
cd frontend
npm install
```

Create frontend environment file:
```bash
cp .env.local.example .env.local
```

Edit `frontend/.env.local` with your LiveKit credentials, then start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser and click "Start Voice Chat" to begin!

## Usage

### Testing the Agent

1. Open the web interface at `http://localhost:3000`
2. Click "Start Voice Chat" to connect
3. Allow microphone access when prompted
4. Start speaking! Try asking:
   - "I'm looking for a 3-bedroom house in downtown"
   - "What properties do you have available?"
   - "Can you schedule a viewing for me?"
   - "I need help finding an apartment"

### Customizing the Agent

Edit `src/ivy_homes_agent/agent.py` to customize:

**Agent Instructions**: Modify the `AGENT_INSTRUCTIONS` constant to change the assistant's behavior and knowledge.

**Voice Settings**: Change the TTS voice by updating the Cartesia voice ID:
```python
text_to_speech = cartesia.TTS(
    model="sonic-3-english",
    voice="your-preferred-voice-id",  # Change this
)
```

**LLM Settings**: Adjust temperature, model, or other parameters:
```python
language_model = openai.LLM(
    model="gpt-4o-mini",
    temperature=0.7,  # Adjust creativity (0.0-1.0)
)
```

## Project Structure

```
property-voice-assistant/
├── src/
│   └── ivy_homes_agent/
│       ├── __init__.py
│       └── agent.py           # Main voice agent logic
├── frontend/
│   ├── src/
│   │   └── app/
│   │       ├── api/
│   │       │   └── token/
│   │       │       └── route.ts  # Token generation API
│   │       ├── layout.tsx
│   │       ├── page.tsx          # Main UI
│   │       └── globals.css
│   ├── package.json
│   └── next.config.js
├── pyproject.toml             # Python dependencies
├── requirements.txt           # Pip requirements
├── Dockerfile                 # Container configuration
├── .env.example              # Environment template
└── README.md                 # This file
```

## Deployment

### Docker Deployment

Build the Docker image:
```bash
docker build -t ivy-homes-voice-agent .
```

Run the container:
```bash
docker run -d \
  --env-file .env \
  -p 8080:8080 \
  ivy-homes-voice-agent
```

### Cloud Deployment

#### Deploy Agent to LiveKit Cloud

1. Push your code to GitHub
2. Connect your repository to LiveKit Cloud
3. Configure environment variables in the cloud dashboard
4. Deploy!

#### Deploy Frontend to Vercel

```bash
cd frontend
vercel deploy
```

Or connect your GitHub repository to Vercel for automatic deployments.

## Advanced Features

### Adding Telephony Support

LiveKit supports SIP integration for phone calls. To enable:

1. Set up SIP trunking in LiveKit Cloud
2. Configure phone number routing
3. The agent will automatically handle phone calls!

See [LiveKit telephony docs](https://docs.livekit.io/agents/start/telephony/) for details.

### Custom Property Data Integration

To connect real property data:

1. Add a function in `agent.py` to query your property database
2. Register it as a tool the LLM can call
3. Update agent instructions to use the tool

Example:
```python
@agent.function()
async def search_properties(
    location: str,
    bedrooms: int,
    max_price: float
) -> list:
    # Query your property database
    return properties
```

## Troubleshooting

### Agent won't start
- Check that all environment variables are set correctly
- Verify your API keys are valid
- Ensure Python 3.9+ is installed

### Audio not working
- Check browser permissions for microphone access
- Verify LiveKit WebSocket connection (check browser console)
- Test with a different browser

### Connection issues
- Verify your LiveKit URL is correct (should start with `wss://`)
- Check that API key and secret match
- Ensure no firewall is blocking WebSocket connections

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
ruff format src/
```

### Linting

```bash
ruff check src/
```

## Resources

- [LiveKit Agents Documentation](https://docs.livekit.io/agents/)
- [LiveKit React Components](https://docs.livekit.io/reference/components/react/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Cartesia Voice API](https://docs.cartesia.ai)

## License

This project is built for Ivy Homes. Contact the development team for licensing information.

## Support

For questions or issues:
- Check the [LiveKit Community Forum](https://livekit.io/community)
- Review [LiveKit Examples](https://github.com/livekit-examples)
- Contact the Ivy Homes development team

---

Built with ❤️ using [LiveKit](https://livekit.io) for Ivy Homes
