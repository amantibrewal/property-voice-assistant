# Ivy Homes Voice Assistant - Frontend

This is the web interface for the Ivy Homes Voice Assistant, built with Next.js and LiveKit React Components.

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.local.example .env.local
```

3. Add your LiveKit credentials to `.env.local`

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000)

## Features

- Clean, modern UI with Tailwind CSS
- Real-time voice communication
- LiveKit React components integration
- Responsive design for all devices

## Environment Variables

Required variables in `.env.local`:

- `LIVEKIT_URL` - Your LiveKit WebSocket URL
- `LIVEKIT_API_KEY` - Your LiveKit API key
- `LIVEKIT_API_SECRET` - Your LiveKit API secret

## Build for Production

```bash
npm run build
npm start
```

## Deploy

The easiest way to deploy is using [Vercel](https://vercel.com):

```bash
vercel deploy
```

Make sure to add your environment variables in the Vercel dashboard.
