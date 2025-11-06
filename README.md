# Ivy Homes Voice Assistant

A real-time AI voice assistant for residential flat sales in Bangalore, built with LiveKit Agents framework. This assistant helps potential buyers find and purchase flats, schedule site visits, and connect with property specialists.

**Business Focus**: Ivy Homes exclusively sells residential flats (apartments) in Bangalore. We do not handle rentals, houses, villas, or commercial properties.

## Features

- **Real-time Voice Conversations**: Natural, conversational AI powered by OpenAI GPT-4
- **Bangalore-Specific**: Specialized for Bangalore neighborhoods, tech parks, and metro connectivity
- **Live Inventory Search**: Query real flat availability with pricing in Indian Rupees (lakhs/crores)
- **BHK-based Search**: Search by 1 BHK, 2 BHK, 3 BHK, or 4 BHK configurations
- **Multi-platform Support**: Web browser, mobile apps, or telephone integration
- **Indian English**: Uses local terminology (flat, BHK, lakhs, crores, site visit)
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

## Integrating Your Property Data

The voice agent can query your live property inventory to provide accurate information to callers. There are three ways to integrate your data:

### Option 1: File-Based (Quick Start)

Perfect for testing and small inventories. Simply edit `data/properties.json`:

```json
{
  "properties": [
    {
      "id": "prop-001",
      "type": "house",
      "address": "123 Oak Street",
      "neighborhood": "Downtown",
      "city": "San Francisco",
      "price": 1250000,
      "bedrooms": 3,
      "bathrooms": 2,
      "square_feet": 2100,
      "year_built": 2018,
      "description": "Beautiful modern home...",
      "features": ["hardwood floors", "updated kitchen"],
      "status": "available"
    }
  ]
}
```

**Setup**:
1. Edit `data/properties.json` with your properties
2. Restart the agent
3. The agent will automatically load the new data

See `data/README.md` for complete field documentation.

### Option 2: API Integration (Production)

Connect to your existing property management system API:

1. **Update environment variables** in `.env`:
   ```env
   PROPERTY_DATA_SOURCE=api
   PROPERTY_API_URL=https://your-api.com/properties
   PROPERTY_API_KEY=your-api-key
   ```

2. **Implement the API client** in `src/ivy_homes_agent/property_service.py`:
   ```python
   async def _search_api(self, location, property_type, ...):
       import aiohttp
       params = {
           "location": location,
           "type": property_type,
           "min_price": min_price,
           "max_price": max_price,
           # ... other parameters
       }
       headers = {"Authorization": f"Bearer {self.api_key}"}
       async with aiohttp.ClientSession() as session:
           async with session.get(self.api_url, params=params, headers=headers) as resp:
               data = await resp.json()
               return data.get("properties", [])
   ```

3. **Map your API response** to the expected format (id, type, address, price, etc.)

### Option 3: Database Integration (Enterprise)

For direct database access:

1. **Install database driver**:
   ```bash
   pip install asyncpg  # for PostgreSQL
   # or
   pip install aiomysql  # for MySQL
   ```

2. **Update `.env`**:
   ```env
   PROPERTY_DATA_SOURCE=database
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

3. **Implement database queries** in `property_service.py`

### How the Agent Uses Property Data

When a buyer asks about flats, the agent:

1. **Gathers requirements** through conversation:
   - Preferred area/neighborhood in Bangalore
   - Budget range in Indian Rupees
   - Number of BHK (bedrooms)
   - Special requirements (parking, amenities, floor, facing)

2. **Searches your inventory** using the `search_properties()` function

3. **Presents results** naturally in voice format:
   - "I found 3 flats that match. The first is a 3-BHK in Whitefield for ₹1.85 crores with excellent amenities..."

4. **Provides details** when asked about specific flats, including pricing in lakhs/crores

### Testing with Sample Data

The project includes 10 sample flats in `data/properties.json` covering popular Bangalore areas. Try these queries:

- "Show me 3 BHK flats in Whitefield"
- "What do you have under 1 crore?"
- "I need a 2 BHK apartment in Electronic City"
- "Show me flats near Bellandur with good amenities"
- "I'm looking for a flat with 80 lakhs budget"
- "What's available in HSR Layout?"

## Usage

### Testing the Agent

1. Open the web interface at `http://localhost:3000`
2. Click "Start Voice Chat" to connect
3. Allow microphone access when prompted
4. Start speaking! Try asking:
   - "I'm looking for a 3 BHK flat in Whitefield"
   - "What flats do you have under 1.5 crores?"
   - "Can you schedule a site visit for me?"
   - "I need a 2 BHK in Electronic City"
   - "Show me flats with good amenities in Bellandur"

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
│       ├── agent.py              # Main voice agent logic
│       └── property_service.py   # Property data service
├── data/
│   ├── properties.json           # Property inventory data
│   └── README.md                 # Data format documentation
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

### Extending with Custom Functions

You can add more capabilities to the agent by registering additional AI-callable functions:

```python
@llm.ai_callable(description="Schedule a property viewing")
async def schedule_viewing(
    property_id: str,
    date: str,
    time: str,
    contact_email: str,
) -> str:
    # Add to your calendar/CRM system
    return f"Viewing scheduled for {date} at {time}"
```

Then register it with the agent:
```python
assistant.fnc_ctx.ai_callable(schedule_viewing)
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
