'use client';

import { useState } from 'react';
import { LiveKitRoom, RoomAudioRenderer, VoiceAssistantControlBar } from '@livekit/components-react';
import '@livekit/components-styles';

export default function Home() {
  const [connectionDetails, setConnectionDetails] = useState<{ url: string; token: string } | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      const response = await fetch('/api/token');
      const data = await response.json();
      setConnectionDetails(data);
    } catch (error) {
      console.error('Failed to get connection token:', error);
      alert('Failed to connect. Please check your configuration.');
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    setConnectionDetails(null);
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              Ivy Homes Voice Assistant
            </h1>
            <p className="text-lg text-gray-600">
              Talk to our AI assistant about your property needs
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            {!connectionDetails ? (
              <div className="text-center">
                <div className="mb-8">
                  <div className="w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg
                      className="w-12 h-12 text-indigo-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                      />
                    </svg>
                  </div>
                  <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                    Ready to help you find your dream property
                  </h2>
                  <p className="text-gray-600 mb-6">
                    Click the button below to start a voice conversation with our AI assistant.
                    We'll help you with property inquiries, viewings, and more.
                  </p>
                </div>

                <button
                  onClick={handleConnect}
                  disabled={isConnecting}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isConnecting ? 'Connecting...' : 'Start Voice Chat'}
                </button>

                <div className="mt-8 pt-6 border-t border-gray-200">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    What our assistant can help with:
                  </h3>
                  <ul className="text-sm text-gray-600 space-y-2">
                    <li>✓ Property search based on your requirements</li>
                    <li>✓ Schedule property viewings</li>
                    <li>✓ Answer questions about buying or renting</li>
                    <li>✓ Connect you with property specialists</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div>
                <LiveKitRoom
                  serverUrl={connectionDetails.url}
                  token={connectionDetails.token}
                  connect={true}
                  audio={true}
                  onDisconnected={handleDisconnect}
                  className="livekit-room"
                >
                  <div className="text-center mb-6">
                    <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
                      <span className="text-sm font-medium">Connected - Speak now</span>
                    </div>
                  </div>

                  <div className="mb-6">
                    <p className="text-center text-gray-600">
                      Start speaking to ask about properties, schedule viewings, or get help from our assistant.
                    </p>
                  </div>

                  <VoiceAssistantControlBar
                    controls={{
                      leave: true,
                    }}
                  />

                  <RoomAudioRenderer />
                </LiveKitRoom>

                <div className="mt-6 text-center">
                  <button
                    onClick={handleDisconnect}
                    className="text-sm text-gray-500 hover:text-gray-700 underline"
                  >
                    End conversation
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>Powered by LiveKit • Built for Ivy Homes</p>
          </div>
        </div>
      </div>

      <style jsx global>{`
        .livekit-room {
          --lk-bg: white;
          --lk-fg: #111827;
          --lk-accent: #4f46e5;
        }
      `}</style>
    </main>
  );
}
