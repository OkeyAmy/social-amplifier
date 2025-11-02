import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Linkedin, ExternalLink, CheckCircle, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import type { PlatformConnectionsStatus } from "@/types/api";
import { getConnectionStatus, initiatePlatformConnect, disconnectPlatform } from "@/services/api";

const createInitialStatus = (): PlatformConnectionsStatus => ({
  linkedin: { platform: "linkedin", connected: false, expires_at: null, username: null },
  twitter: { platform: "twitter", connected: false, expires_at: null, username: null }
});

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
  const [connectionStatus, setConnectionStatus] = useState<PlatformConnectionsStatus>(createInitialStatus);
  const [statusLoading, setStatusLoading] = useState<boolean>(true);
  const [loading, setLoading] = useState<{ linkedin: boolean; twitter: boolean }>({
    linkedin: false,
    twitter: false
  });

  const fetchConnectionStatus = useCallback(async () => {
    try {
      setStatusLoading(true);
      const data = await getConnectionStatus();
      setConnectionStatus(data);
    } catch (error) {
      console.error("Failed to fetch connection status:", error);
      toast({
        title: "⚠️ STATUS ERROR",
        description: "Unable to retrieve platform status. Please refresh.",
      });
      setConnectionStatus(createInitialStatus());
    } finally {
      setStatusLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchConnectionStatus();
  }, [fetchConnectionStatus]);

  const handleConnect = async (platform: "linkedin" | "twitter") => {
    setLoading(prev => ({ ...prev, [platform]: true }));
    
    try {
      const data = await initiatePlatformConnect(platform);
      toast({
        title: "🚀 CONNECTING...",
        description: `Proceed with ${platform.toUpperCase()} authorization in the new window.`,
      });

      window.open(data.authorization_url, "_blank", "noopener,noreferrer");

    } catch (error) {
      console.error(`Failed to connect to ${platform}:`, error);
      toast({
        title: "❌ CONNECTION FAILED",
        description: `Failed to connect to ${platform}. Please try again.`,
      });
    } finally {
      setLoading(prev => ({ ...prev, [platform]: false }));
      fetchConnectionStatus();
    }
  };

  const handleDisconnect = async (platform: "linkedin" | "twitter") => {
    try {
      await disconnectPlatform(platform);
      await fetchConnectionStatus();

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
      <div className="max-w-4xl mx-auto p-4 md:p-6 space-y-6 md:space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="brutal-card p-4 md:p-6 bg-secondary text-secondary-foreground">
            <h1 className="text-3xl md:text-5xl lg:text-6xl font-bold">CONNECT ACCOUNTS</h1>
          </div>
          <p className="text-base md:text-xl font-bold px-4">
            CONNECT YOUR SOCIAL MEDIA TO POST <span className="text-destructive">AUTOMATICALLY</span>!
          </p>
        </div>

        {/* Connection Cards */}
        <div className="space-y-4 md:space-y-6">
          {/* LinkedIn */}
          <div className="brutal-card p-4 md:p-8 bg-card">
            <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-6">
              <div className="flex items-center gap-4 md:gap-6 flex-1">
                <div className="brutal-border brutal-shadow bg-linkedin text-linkedin-foreground p-3 md:p-4 flex-shrink-0">
                  <Linkedin className="w-8 h-8 md:w-12 md:h-12" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl md:text-2xl font-bold">LINKEDIN</h3>
                  <p className="text-xs md:text-sm text-muted-foreground font-bold">
                    Professional Network • Business Content
                  </p>
                  {connectionStatus.linkedin.connected && (
                    <div className="flex items-center gap-2 mt-2">
                      <CheckCircle className="w-4 h-4 md:w-5 md:h-5 text-success flex-shrink-0" />
                      <span className="text-xs md:text-sm text-success font-bold truncate">
                        Connected as @{connectionStatus.linkedin.username}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 md:gap-4">
                {connectionStatus.linkedin.connected ? (
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      onClick={() => handleDisconnect("linkedin")}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all text-xs md:text-sm"
                    >
                      DISCONNECT
                    </Button>
                    <div className="brutal-border brutal-shadow-sm bg-success text-success-foreground px-3 py-2 font-bold text-xs md:text-sm whitespace-nowrap">
                      ✅ CONNECTED
                    </div>
                  </div>
                ) : (
                  <Button
                    onClick={() => handleConnect("linkedin")}
                    disabled={loading.linkedin}
                    className="w-full md:w-auto brutal-border brutal-shadow-lg bg-linkedin text-linkedin-foreground hover:bg-linkedin/90 font-bold uppercase px-4 md:px-8 py-3 md:py-4 text-sm md:text-lg"
                  >
                    {loading.linkedin ? (
                      "CONNECTING..."
                    ) : (
                      <>
                        <ExternalLink className="mr-2 w-4 h-4 md:w-5 md:h-5" />
                        CONNECT
                      </>
                    )}
                  </Button>
                )}
              </div>
            </div>
          </div>

          {/* Twitter/X */}
          <div className="brutal-card p-4 md:p-8 bg-card">
            <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-6">
              <div className="flex items-center gap-4 md:gap-6 flex-1">
                <div className="brutal-border brutal-shadow bg-twitter text-twitter-foreground p-3 md:p-4 flex-shrink-0">
                  <XIcon className="w-8 h-8 md:w-12 md:h-12" />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="text-xl md:text-2xl font-bold">X (TWITTER)</h3>
                  <p className="text-xs md:text-sm text-muted-foreground font-bold">
                    Real-time Updates • Viral Content
                  </p>
                  {connectionStatus.twitter.connected && (
                    <div className="flex items-center gap-2 mt-2">
                      <CheckCircle className="w-4 h-4 md:w-5 md:h-5 text-success flex-shrink-0" />
                      <span className="text-xs md:text-sm text-success font-bold truncate">
                        Connected as @{connectionStatus.twitter.username}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-2 md:gap-4">
                {connectionStatus.twitter.connected ? (
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      onClick={() => handleDisconnect("twitter")}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all text-xs md:text-sm"
                    >
                      DISCONNECT
                    </Button>
                    <div className="brutal-border brutal-shadow-sm bg-success text-success-foreground px-3 py-2 font-bold text-xs md:text-sm whitespace-nowrap">
                      ✅ CONNECTED
                    </div>
                  </div>
                ) : (
                  <Button
                    onClick={() => handleConnect("twitter")}
                    disabled={loading.twitter}
                    className="w-full md:w-auto brutal-border brutal-shadow-lg bg-twitter text-twitter-foreground hover:bg-twitter/90 font-bold uppercase px-4 md:px-8 py-3 md:py-4 text-sm md:text-lg"
                  >
                    {loading.twitter ? (
                      "CONNECTING..."
                    ) : (
                      <>
                        <ExternalLink className="mr-2 w-4 h-4 md:w-5 md:h-5" />
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
        {!statusLoading && !connectionStatus.linkedin.connected && !connectionStatus.twitter.connected && (
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
        <div className="brutal-card p-4 md:p-6 bg-muted text-foreground">
          <h3 className="text-lg md:text-xl font-bold mb-4">🚀 WHAT HAPPENS AFTER CONNECTING?</h3>
          <div className="grid sm:grid-cols-2 gap-3 md:gap-4">
            <div>
              <h4 className="font-bold text-sm md:text-base">✨ AUTO-POSTING</h4>
              <p className="text-xs md:text-sm">Publish directly to your connected platforms</p>
            </div>
            <div>
              <h4 className="font-bold text-sm md:text-base">🎯 OPTIMIZED CONTENT</h4>
              <p className="text-xs md:text-sm">Platform-specific content generation</p>
            </div>
            <div>
              <h4 className="font-bold text-sm md:text-base">📊 ANALYTICS</h4>
              <p className="text-xs md:text-sm">Track performance across platforms</p>
            </div>
            <div>
              <h4 className="font-bold text-sm md:text-base">🔒 SECURE</h4>
              <p className="text-xs md:text-sm">Your tokens are encrypted and secure</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectPage;