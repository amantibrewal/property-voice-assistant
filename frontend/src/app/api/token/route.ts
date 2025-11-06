import { AccessToken } from 'livekit-server-sdk';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const apiKey = process.env.LIVEKIT_API_KEY;
    const apiSecret = process.env.LIVEKIT_API_SECRET;
    const wsUrl = process.env.LIVEKIT_URL;

    if (!apiKey || !apiSecret || !wsUrl) {
      return NextResponse.json(
        { error: 'LiveKit credentials not configured' },
        { status: 500 }
      );
    }

    // Generate a random room name for this session
    const roomName = `property-inquiry-${Math.random().toString(36).substring(7)}`;
    const participantName = `user-${Math.random().toString(36).substring(7)}`;

    // Create access token
    const at = new AccessToken(apiKey, apiSecret, {
      identity: participantName,
      ttl: '10m', // Token valid for 10 minutes
    });

    at.addGrant({
      room: roomName,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
    });

    const token = await at.toJwt();

    return NextResponse.json({
      url: wsUrl,
      token: token,
      roomName: roomName,
    });
  } catch (error) {
    console.error('Error generating token:', error);
    return NextResponse.json(
      { error: 'Failed to generate token' },
      { status: 500 }
    );
  }
}
