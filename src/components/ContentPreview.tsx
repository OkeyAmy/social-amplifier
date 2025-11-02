import { Button } from "@/components/ui/button";
import { ArrowLeft, RefreshCw, Save, Send } from "lucide-react";
import type { Platform, TwitterMode } from "@/pages/Index";
import { useState } from "react";
import { useToast } from "@/hooks/use-toast";

interface ContentPreviewProps {
  idea: string;
  emoji: string | null;
  platform: Platform;
  twitterMode: TwitterMode | null;
  imagePreview: string | null;
  onBack: () => void;
  onStartOver: () => void;
}

const ContentPreview = ({
  idea,
  emoji,
  platform,
  twitterMode,
  imagePreview,
  onBack,
  onStartOver,
}: ContentPreviewProps) => {
  const { toast } = useToast();
  const [generatedContent, setGeneratedContent] = useState<{
    linkedin?: string;
    twitter?: string[];
  }>({});

  // Mock AI generation (in production, this would call backend)
  const generateContent = () => {
    const linkedinContent = `${emoji ? emoji + " " : ""}${idea}\n\nKey insights:\n• Professional perspective\n• Industry relevance\n• Call to action\n\n#Leadership #Innovation #Growth`;
    
    const twitterSingle = `${emoji ? emoji + " " : ""}${idea.substring(0, 240)}... 🚀`;
    
    const twitterThread = [
      `1/ ${emoji ? emoji + " " : ""}${idea.substring(0, 200)}...`,
      `2/ Here's why this matters: [AI would expand on the idea]`,
      `3/ Final thoughts: [AI would provide conclusion] 🎯`
    ];

    setGeneratedContent({
      linkedin: platform === "linkedin" || platform === "both" ? linkedinContent : undefined,
      twitter: platform === "twitter" || platform === "both" 
        ? (twitterMode === "thread" ? twitterThread : [twitterSingle])
        : undefined,
    });
  };

  // Generate on mount
  useState(() => {
    generateContent();
  });

  const handlePost = () => {
    toast({
      title: "🎉 READY TO POST!",
      description: "Backend integration needed for actual posting. Connect platforms to go live!",
    });
  };

  const handleSaveDraft = () => {
    toast({
      title: "💾 DRAFT SAVED!",
      description: "Your content has been saved (frontend demo only)",
    });
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex gap-4">
        <Button
          onClick={onBack}
          variant="outline"
          className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <ArrowLeft className="mr-2" /> BACK
        </Button>
        <Button
          onClick={generateContent}
          variant="outline"
          className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <RefreshCw className="mr-2" /> REGENERATE
        </Button>
      </div>

      <div className="brutal-card p-4 bg-warning text-warning-foreground">
        <p className="font-bold text-center">
          ⚠️ DEMO MODE: Backend integration needed for AI generation & posting
        </p>
      </div>

      <div className="space-y-6">
        {generatedContent.linkedin && (
          <div className="brutal-card p-6 bg-linkedin/10">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">💼</div>
              <h3 className="text-xl font-bold">LINKEDIN POST</h3>
            </div>
            <div className="brutal-border bg-card p-4">
              {imagePreview && (
                <img 
                  src={imagePreview} 
                  alt="Post" 
                  className="w-full h-48 object-cover brutal-border mb-4"
                />
              )}
              <p className="whitespace-pre-wrap font-mono text-sm">
                {generatedContent.linkedin}
              </p>
              <div className="mt-4 text-xs text-muted-foreground font-bold">
                {generatedContent.linkedin.length} characters
              </div>
            </div>
          </div>
        )}

        {generatedContent.twitter && (
          <div className="brutal-card p-6 bg-twitter/10">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">𝕏</div>
              <h3 className="text-xl font-bold">
                X {twitterMode === "thread" ? "THREAD" : "POST"}
              </h3>
            </div>
            <div className="space-y-3">
              {generatedContent.twitter.map((tweet, index) => (
                <div key={index} className="brutal-border bg-card p-4">
                  {index === 0 && imagePreview && (
                    <img 
                      src={imagePreview} 
                      alt="Tweet" 
                      className="w-full h-48 object-cover brutal-border mb-4"
                    />
                  )}
                  <p className="whitespace-pre-wrap font-mono text-sm">
                    {tweet}
                  </p>
                  <div className="mt-2 text-xs text-muted-foreground font-bold">
                    {tweet.length} characters
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <Button
          onClick={onStartOver}
          variant="outline"
          size="lg"
          className="brutal-border brutal-shadow hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold uppercase"
        >
          START OVER
        </Button>
        <Button
          onClick={handleSaveDraft}
          size="lg"
          className="brutal-border brutal-shadow bg-accent text-accent-foreground hover:bg-accent/90 font-bold uppercase"
        >
          <Save className="mr-2" /> SAVE DRAFT
        </Button>
        <Button
          onClick={handlePost}
          size="lg"
          className="brutal-border brutal-shadow-lg bg-success text-success-foreground hover:bg-success/90 font-bold uppercase"
        >
          <Send className="mr-2" /> POST NOW
        </Button>
      </div>
    </div>
  );
};

export default ContentPreview;
