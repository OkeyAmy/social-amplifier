import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Linkedin } from "lucide-react";
import type { Platform, TwitterMode } from "@/pages/Index";

// X (Twitter) SVG Icon Component
const XIcon = () => (
  <svg viewBox="0 0 24 24" className="w-16 h-16" fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

interface PlatformSelectorProps {
  onSelect: (platform: Platform, twitterMode?: TwitterMode) => void;
  onBack: () => void;
  idea: string;
}

const PlatformSelector = ({ onSelect, onBack, idea }: PlatformSelectorProps) => {
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null);
  const [showTwitterMode, setShowTwitterMode] = useState(false);

  const handlePlatformClick = (platform: Platform) => {
    if (platform === "twitter") {
      setSelectedPlatform(platform);
      setShowTwitterMode(true);
    } else {
      onSelect(platform);
    }
  };

  const handleTwitterModeSelect = (mode: TwitterMode) => {
    if (selectedPlatform === "twitter") {
      onSelect("twitter", mode);
    }
  };

  const estimatedLength = Math.ceil(idea.length * 1.3);
  const recommendThread = estimatedLength > 280;

  return (
    <div className="space-y-4 sm:space-y-6 animate-in fade-in duration-500">
      <Button
        onClick={onBack}
        variant="outline"
        className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all w-full sm:w-auto min-h-[44px]"
      >
        <ArrowLeft className="mr-2 w-4 h-4 sm:w-5 sm:h-5" /> BACK
      </Button>

      {!showTwitterMode ? (
        <>
          <div className="brutal-card p-4 sm:p-6 md:p-8 bg-card">
            <h2 className="mb-4 sm:mb-6 font-bold text-lg sm:text-xl md:text-2xl">STEP 2: CHOOSE PLATFORM</h2>
            
            <div className="grid sm:grid-cols-2 gap-4 sm:gap-6">
              <button
                onClick={() => handlePlatformClick("linkedin")}
                className="brutal-card p-4 sm:p-6 md:p-8 bg-card hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all group min-h-[200px] sm:min-h-[240px] flex flex-col justify-center"
              >
                <div className="mb-3 sm:mb-4 flex justify-center">
                  <div className="brutal-border brutal-shadow bg-linkedin text-linkedin-foreground p-3 sm:p-4">
                    <Linkedin className="w-12 h-12 sm:w-16 sm:h-16" />
                  </div>
                </div>
                <h3 className="text-xl sm:text-2xl font-bold mb-2">LINKEDIN</h3>
                <p className="text-xs sm:text-sm text-muted-foreground font-bold leading-tight">EXPAND & PROFESSIONAL • HIGH CONVERSION</p>
              </button>

              <button
                onClick={() => handlePlatformClick("twitter")}
                className="brutal-card p-4 sm:p-6 md:p-8 bg-card hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all group min-h-[200px] sm:min-h-[240px] flex flex-col justify-center"
              >
                <div className="mb-3 sm:mb-4 flex justify-center">
                  <div className="brutal-border brutal-shadow bg-twitter text-twitter-foreground p-3 sm:p-4">
                    <XIcon />
                  </div>
                </div>
                <h3 className="text-xl sm:text-2xl font-bold mb-2">X (TWITTER)</h3>
                <p className="text-xs sm:text-sm text-muted-foreground font-bold leading-tight">THREAD OR SINGLE • MAX ENGAGEMENT</p>
              </button>
            </div>

            <button
              onClick={() => onSelect("both")}
              className="w-full mt-4 sm:mt-6 brutal-card p-4 sm:p-6 md:p-8 bg-gradient-to-r from-linkedin to-twitter text-white hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all min-h-[44px]"
            >
              <h3 className="text-lg sm:text-xl md:text-2xl font-bold mb-2">BOTH PLATFORMS</h3>
              <p className="text-xs sm:text-sm opacity-90">Maximum reach, impact & conversion</p>
            </button>
          </div>
        </>
      ) : (
        <div className="brutal-card p-4 sm:p-6 md:p-8 bg-card animate-in slide-in-from-right duration-300">
          <h2 className="mb-4 sm:mb-6 font-bold text-lg sm:text-xl md:text-2xl text-foreground">CHOOSE X MODE</h2>
          
          {recommendThread && (
            <div className="mb-4 sm:mb-6 brutal-card p-3 sm:p-4 bg-warning text-warning-foreground rotate-slightly-reverse">
              <p className="font-bold text-sm sm:text-base">⚡ AI RECOMMENDS: THREAD</p>
              <p className="text-xs sm:text-sm mt-1">Your idea has depth - a thread will do it justice</p>
            </div>
          )}

          <div className="space-y-3 sm:space-y-4">
            <button
              onClick={() => handleTwitterModeSelect("single")}
              className="w-full brutal-card p-4 sm:p-6 bg-card text-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all text-left min-h-[120px] sm:min-h-[140px]"
            >
              <h3 className="text-lg sm:text-xl font-bold mb-2">SINGLE POST</h3>
              <p className="text-xs sm:text-sm opacity-90">Concise, punchy, immediate impact</p>
              <p className="text-xs sm:text-sm opacity-90 mt-2">Max 280 characters</p>
            </button>

            <button
              onClick={() => handleTwitterModeSelect("thread")}
              className="w-full brutal-card p-4 sm:p-6 bg-card text-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all text-left min-h-[120px] sm:min-h-[140px]"
            >
              <h3 className="text-lg sm:text-xl font-bold mb-2">THREAD MODE</h3>
              <p className="text-xs sm:text-sm opacity-90">Multi-part narrative, deep dive</p>
              <p className="text-xs sm:text-sm opacity-90 mt-2">3-10 connected tweets</p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlatformSelector;
