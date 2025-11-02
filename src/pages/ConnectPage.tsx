import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Linkedin, ExternalLink, CheckCircle, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

// X (Twitter) SVG Icon Component
const XIcon = ({ className = "w-16 h-16" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

interface ConnectionStatus {
  platform: string;
  connected: boolean;
  expires_at: string | null;
  username: string | null;
}

const ConnectPage = () => {
  const { toast } = useToast();
  const [connectionStatus, setConnectionStatus] = useState<{
    linkedin: ConnectionStatus;
    twitter: ConnectionStatus;
  }>({
    linkedin: { platform: "linkedin", connected: false, expires_at: null, username: null },
    twitter: { platform: "twitter", connected: false, expires_at: null, username: null }
  });
  const [loading, setLoading] = useState<{ linkedin: boolean; twitter: boolean }>({
    linkedin: false,
    twitter: false
  });

  useEffect(() => {
    fetchConnectionStatus();
  }, []);

  const fetchConnectionStatus = async () => {
    try {
      // TODO: Replace with actual backend call
      // const response = await fetch('/api/v1/auth/status');
      // const data = await response.json();
      // setConnectionStatus(data);
      
      // Mock data for now
      console.log("Fetching connection status...");
    } catch (error) {
      console.error("Failed to fetch connection status:", error);
    }
  };

  const handleConnect = async (platform: "linkedin" | "twitter") => {
    setLoading(prev => ({ ...prev, [platform]: true }));
    
    try {
      // TODO: Replace with actual backend call
      // const response = await fetch(`/api/v1/auth/${platform}/connect`);
      // const data = await response.json();
      // window.open(data.authorization_url, '_blank');
      
      toast({
        title: "🚀 CONNECTING...",
        description: `Opening ${platform} authorization window (backend integration needed)`,
      });
      
      // Mock connection after delay
      setTimeout(() => {
        setConnectionStatus(prev => ({
          ...prev,
          [platform]: {
            ...prev[platform],
            connected: true,
            username: `demo_user_${platform}`
          }
        }));
        
        toast({
          title: "✅ CONNECTED!",
          description: `Successfully connected to ${platform.toUpperCase()}`,
        });
      }, 2000);
      
    } catch (error) {
      console.error(`Failed to connect to ${platform}:`, error);
      toast({
        title: "❌ CONNECTION FAILED",
        description: `Failed to connect to ${platform}. Please try again.`,
      });
    } finally {
      setLoading(prev => ({ ...prev, [platform]: false }));
    }
  };

  const handleDisconnect = async (platform: "linkedin" | "twitter") => {
    try {
      // TODO: Replace with actual backend call
      // await fetch(`/api/v1/auth/disconnect`, {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ platform })
      // });
      
      setConnectionStatus(prev => ({
        ...prev,
        [platform]: {
          ...prev[platform],
          connected: false,
          username: null
        }
      }));
      
      toast({
        title: "🔌 DISCONNECTED",
        description: `Disconnected from ${platform.toUpperCase()}`,
      });
      
    } catch (error) {
      console.error(`Failed to disconnect from ${platform}:`, error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="brutal-card p-6 bg-secondary text-secondary-foreground">
            <h1 className="text-4xl md:text-6xl font-bold">CONNECT ACCOUNTS</h1>
          </div>
          <p className="text-xl font-bold">
            CONNECT YOUR SOCIAL MEDIA TO POST <span className="text-destructive">AUTOMATICALLY</span>!
          </p>
        </div>

        {/* Connection Cards */}
        <div className="space-y-6">
          {/* LinkedIn */}
          <div className="brutal-card p-8 bg-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="brutal-border brutal-shadow bg-linkedin text-linkedin-foreground p-4">
                  <Linkedin className="w-12 h-12" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">LINKEDIN</h3>
                  <p className="text-muted-foreground font-bold">
                    Professional Network • Business Content
                  </p>
                  {connectionStatus.linkedin.connected && (
                    <div className="flex items-center gap-2 mt-2">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span className="text-success font-bold">
                        Connected as @{connectionStatus.linkedin.username}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {connectionStatus.linkedin.connected ? (
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleDisconnect("linkedin")}
                      variant="outline"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                      DISCONNECT
                    </Button>
                    <div className="brutal-border brutal-shadow-sm bg-success text-success-foreground px-4 py-2 font-bold">
                      ✅ CONNECTED
                    </div>
                  </div>
                ) : (
                  <Button
                    onClick={() => handleConnect("linkedin")}
                    disabled={loading.linkedin}
                    className="brutal-border brutal-shadow-lg bg-linkedin text-linkedin-foreground hover:bg-linkedin/90 font-bold uppercase px-8 py-4 text-lg"
                  >
                    {loading.linkedin ? (
                      "CONNECTING..."
                    ) : (
                      <>
                        <ExternalLink className="mr-2 w-5 h-5" />
                        CONNECT
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Twitter/X */}
          <div className="brutal-card p-8 bg-card">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="brutal-border brutal-shadow bg-twitter text-twitter-foreground p-4">
                  <XIcon className="w-12 h-12" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">X (TWITTER)</h3>
                  <p className="text-muted-foreground font-bold">
                    Real-time Updates • Viral Content
                  </p>
                  {connectionStatus.twitter.connected && (
                    <div className="flex items-center gap-2 mt-2">
                      <CheckCircle className="w-5 h-5 text-success" />
                      <span className="text-success font-bold">
                        Connected as @{connectionStatus.twitter.username}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                {connectionStatus.twitter.connected ? (
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleDisconnect("twitter")}
                      variant="outline"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
                    >
                      DISCONNECT
                    </Button>
                    <div className="brutal-border brutal-shadow-sm bg-success text-success-foreground px-4 py-2 font-bold">
                      ✅ CONNECTED
                    </div>
                  </div>
                ) : (
                  <Button
                    onClick={() => handleConnect("twitter")}
                    disabled={loading.twitter}
                    className="brutal-border brutal-shadow-lg bg-twitter text-twitter-foreground hover:bg-twitter/90 font-bold uppercase px-8 py-4 text-lg"
                  >
                    {loading.twitter ? (
                      "CONNECTING..."
                    ) : (
                      <>
                        <ExternalLink className="mr-2 w-5 h-5" />
                        CONNECT
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Connection Status */}
        {!connectionStatus.linkedin.connected && !connectionStatus.twitter.connected && (
          <div className="brutal-card p-6 bg-warning text-warning-foreground">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6" />
              <div>
                <p className="font-bold">NO PLATFORMS CONNECTED</p>
                <p className="text-sm">Connect at least one platform to start posting automatically!</p>
              </div>
            </div>
          </div>
        )}

        {/* Features Info */}
        <div className="brutal-card p-6 bg-muted text-foreground">
          <h3 className="text-xl font-bold mb-4">🚀 WHAT HAPPENS AFTER CONNECTING?</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-bold">✨ AUTO-POSTING</h4>
              <p className="text-sm">Publish directly to your connected platforms</p>
            </div>
            <div>
              <h4 className="font-bold">🎯 OPTIMIZED CONTENT</h4>
              <p className="text-sm">Platform-specific content generation</p>
            </div>
            <div>
              <h4 className="font-bold">📊 ANALYTICS</h4>
              <p className="text-sm">Track performance across platforms</p>
            </div>
            <div>
              <h4 className="font-bold">🔒 SECURE</h4>
              <p className="text-sm">Your tokens are encrypted and secure</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectPage;