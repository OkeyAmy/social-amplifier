import { useState } from "react";
import IdeaInput from "@/components/IdeaInput";
import PlatformSelector from "@/components/PlatformSelector";
import ImageUpload from "@/components/ImageUpload";
import ContentPreview from "@/components/ContentPreview";

export type Platform = "linkedin" | "twitter" | "both";
export type TwitterMode = "single" | "thread";

const Index = () => {
  const [stage, setStage] = useState<"idea" | "platform" | "image" | "preview">("idea");
  const [idea, setIdea] = useState("");
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [platform, setPlatform] = useState<Platform | null>(null);
  const [twitterMode, setTwitterMode] = useState<TwitterMode | null>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleIdeaSubmit = (ideaText: string, emoji: string | null) => {
    setIdea(ideaText);
    setSelectedEmoji(emoji);
    setStage("platform");
  };

  const handlePlatformSelect = (selectedPlatform: Platform, mode?: TwitterMode) => {
    setPlatform(selectedPlatform);
    if (selectedPlatform === "twitter" || selectedPlatform === "both") {
      setTwitterMode(mode || "single");
    }
    setStage("image");
  };

  const handleImageUpload = (file: File | null, preview: string | null) => {
    setImageFile(file);
    setImagePreview(preview);
    setStage("preview");
  };

  const handleBack = () => {
    if (stage === "platform") setStage("idea");
    if (stage === "image") setStage("platform");
    if (stage === "preview") setStage("image");
  };

  const handleStartOver = () => {
    setStage("idea");
    setIdea("");
    setSelectedEmoji(null);
    setPlatform(null);
    setTwitterMode(null);
    setImageFile(null);
    setImagePreview(null);
  };

  return (
    <div className="bg-background p-3 sm:p-4 md:p-8">
      <header className="mb-6 sm:mb-8 md:mb-12 text-center">
        <div className="brutal-card p-4 sm:p-6 md:p-8 bg-secondary text-secondary-foreground mx-auto inline-block mb-3 sm:mb-4">
          <h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold break-words">POSTBLASTER</h1>
        </div>
        <p className="text-base sm:text-lg md:text-xl font-bold px-2 sm:px-4 leading-tight">
          DROP YOUR IDEA. WE'LL MAKE IT <span className="text-destructive">POP</span> & <span className="text-success">CONVERT</span>!
        </p>
      </header>

      <div className="max-w-4xl mx-auto">
        {stage === "idea" && (
          <IdeaInput onSubmit={handleIdeaSubmit} />
        )}

        {stage === "platform" && (
          <PlatformSelector 
            onSelect={handlePlatformSelect} 
            onBack={handleBack}
            idea={idea}
          />
        )}

        {stage === "image" && (
          <ImageUpload 
            onSubmit={handleImageUpload}
            onBack={handleBack}
          />
        )}

        {stage === "preview" && platform && (
          <ContentPreview
            idea={idea}
            emoji={selectedEmoji}
            platform={platform}
            twitterMode={twitterMode}
            imagePreview={imagePreview}
            onBack={handleBack}
            onStartOver={handleStartOver}
          />
        )}
      </div>
    </div>
  );
};

export default Index;
