# Quick Setup Guide

## Prerequisites

- Python 3.9 or higher ✅ (You have Python 3.11)
- Node.js 18+ (for frontend)
- LiveKit account (sign up at cloud.livekit.io)
- OpenAI API key
- Cartesia API key

## Step 1: Install Python Dependencies

Already done! ✅ All packages are installed.

## Step 2: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# LiveKit Configuration
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key

# Cartesia Configuration
CARTESIA_API_KEY=your-cartesia-api-key

# Property Data (already configured)
PROPERTY_DATA_SOURCE=file
PROPERTY_DATA_PATH=data/properties.json
```

## Step 3: Run the Voice Agent

Use the startup script:

```bash
python start_agent.py dev
```

The agent will start in development mode and output:
```
2025-11-06 12:18:45,236 - DEV livekit.agents - Watching /home/user/property-voice-assistant
```

This means the agent is running and waiting for connections!

## Step 4: Setup and Run the Frontend

In a new terminal:

```bash
cd frontend
npm install
```

Create frontend environment file:
```bash
cp .env.local.example .env.local
```

Edit `frontend/.env.local` with your LiveKit credentials:
```env
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=your-api-key
LIVEKIT_API_SECRET=your-api-secret
```

Start the frontend:
```bash
npm run dev
```

## Step 5: Test It!

1. Open http://localhost:3000 in your browser
2. Click "Start Voice Chat"
3. Allow microphone access
4. Try saying:
   - "Show me 3 BHK flats in Whitefield"
   - "What do you have under 1 crore?"
   - "I need a 2 BHK in Electronic City"

## Troubleshooting

### Agent won't start
- Make sure all environment variables are set in `.env`
- Check that your API keys are valid
- Verify LiveKit URL starts with `wss://`

### Import errors
- All dependencies are installed, but if you see errors:
  ```bash
  pip install --upgrade livekit-agents livekit-plugins-openai livekit-plugins-cartesia
  ```

### Frontend won't connect
- Ensure the agent is running (`python start_agent.py dev`)
- Check LiveKit credentials in `frontend/.env.local`
- Verify no firewall is blocking WebSocket connections

## Next Steps

1. **Replace sample data**: Edit `data/properties.json` with your actual Ivy Homes inventory
2. **Test queries**: Try different search criteria to verify the agent works
3. **Customize**: Adjust the agent's greeting or behavior in `src/ivy_homes_agent/agent.py`
4. **Deploy**: See README.md for production deployment instructions

## Quick Commands Reference

```bash
# Start the agent (development mode with hot reload)
python start_agent.py dev

# Start the agent (production mode)
python start_agent.py start

# Install frontend dependencies
cd frontend && npm install

# Run frontend development server
cd frontend && npm run dev

# Build frontend for production
cd frontend && npm run build
```

## Getting Help

- Check the main README.md for detailed documentation
- LiveKit docs: https://docs.livekit.io/agents/
- Report issues: Check your environment variables and API keys first

---

✅ **Your agent is ready to run!** Just add your API keys to `.env` and you're good to go.
