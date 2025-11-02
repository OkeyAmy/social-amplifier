import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import type { Platform, TwitterMode } from "@/pages/Index";

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
    <div className="space-y-6 animate-in fade-in duration-500">
      <Button
        onClick={onBack}
        variant="outline"
        className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
      >
        <ArrowLeft className="mr-2" /> BACK
      </Button>

      {!showTwitterMode ? (
        <>
          <div className="brutal-card p-6 md:p-8 bg-card">
            <h2 className="mb-6 font-bold">STEP 2: CHOOSE PLATFORM</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <button
                onClick={() => handlePlatformClick("linkedin")}
                className="brutal-card p-8 bg-linkedin text-linkedin-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all group"
              >
                <div className="text-6xl mb-4">💼</div>
                <h3 className="text-2xl font-bold mb-2">LINKEDIN</h3>
                <p className="text-sm opacity-90">Professional audience</p>
                <p className="text-sm opacity-90 mt-2">~1,500 characters</p>
              </button>

              <button
                onClick={() => handlePlatformClick("twitter")}
                className="brutal-card p-8 bg-twitter text-twitter-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all group"
              >
                <div className="text-6xl mb-4">𝕏</div>
                <h3 className="text-2xl font-bold mb-2">X (TWITTER)</h3>
                <p className="text-sm opacity-90">Fast-paced conversation</p>
                <p className="text-sm opacity-90 mt-2">280 chars or threads</p>
              </button>
            </div>

            <button
              onClick={() => onSelect("both")}
              className="w-full mt-6 brutal-card p-8 bg-gradient-to-r from-linkedin to-twitter text-white hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all"
            >
              <h3 className="text-2xl font-bold mb-2">BOTH PLATFORMS</h3>
              <p className="text-sm opacity-90">Maximum reach & impact</p>
            </button>
          </div>
        </>
      ) : (
        <div className="brutal-card p-6 md:p-8 bg-card animate-in slide-in-from-right duration-300">
          <h2 className="mb-6 font-bold">CHOOSE X MODE</h2>
          
          {recommendThread && (
            <div className="mb-6 brutal-card p-4 bg-warning text-warning-foreground rotate-slightly-reverse">
              <p className="font-bold">⚡ AI RECOMMENDS: THREAD</p>
              <p className="text-sm mt-1">Your idea has depth - a thread will do it justice</p>
            </div>
          )}

          <div className="space-y-4">
            <button
              onClick={() => handleTwitterModeSelect("single")}
              className="w-full brutal-card p-6 bg-twitter text-twitter-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all text-left"
            >
              <h3 className="text-xl font-bold mb-2">SINGLE POST</h3>
              <p className="text-sm opacity-90">Concise, punchy, immediate impact</p>
              <p className="text-sm opacity-90 mt-2">Max 280 characters</p>
            </button>

            <button
              onClick={() => handleTwitterModeSelect("thread")}
              className="w-full brutal-card p-6 bg-accent text-accent-foreground hover:translate-x-2 hover:translate-y-2 hover:shadow-none transition-all text-left"
            >
              <h3 className="text-xl font-bold mb-2">THREAD MODE</h3>
              <p className="text-sm opacity-90">Multi-part narrative, deep dive</p>
              <p className="text-sm opacity-90 mt-2">3-10 connected tweets</p>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default PlatformSelector;
