import { Button } from "@/components/ui/button";
import { ArrowLeft, RefreshCw, Save, Send } from "lucide-react";
import type { Platform, TwitterMode } from "@/pages/Index";
import { useEffect, useMemo, useState } from "react";
import { useToast } from "@/hooks/use-toast";
import type { GeneratedContentResponse } from "@/types/api";
import {
  generateLinkedInContent,
  generateTwitterContent,
  saveDraft,
  publishLinkedIn,
  publishTwitter,
} from "@/services/api";
import { ApiError } from "@/types/api";

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
    linkedin?: GeneratedContentResponse;
    twitter?: GeneratedContentResponse;
  }>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [refreshNonce, setRefreshNonce] = useState<number>(0);
  const [isPosting, setIsPosting] = useState<boolean>(false);
  const twitterEntries = useMemo(() => {
    if (!generatedContent.twitter) {
      return [] as { sequence: number; content: string; characterCount: number; }[];
    }

    if (generatedContent.twitter.is_thread && generatedContent.twitter.thread_tweets?.length) {
      return generatedContent.twitter.thread_tweets.map(tweet => ({
        sequence: tweet.sequence,
        content: tweet.content,
        characterCount: tweet.character_count,
      }));
    }

    if (generatedContent.twitter.generated_content) {
      return [{
        sequence: 1,
        content: generatedContent.twitter.generated_content,
        characterCount: generatedContent.twitter.character_count,
      }];
    }

    return [];
  }, [generatedContent.twitter]);

  useEffect(() => {
    let isActive = true;

    const loadGeneratedContent = async () => {
      if (!idea) {
        setGeneratedContent({});
        return;
      }

      setIsLoading(true);
      setError(null);

      const nextState: {
        linkedin?: GeneratedContentResponse;
        twitter?: GeneratedContentResponse;
      } = {};

      try {
        const promises: Promise<void>[] = [];

        if (platform === "linkedin" || platform === "both") {
          promises.push(
            generateLinkedInContent(idea, emoji ?? undefined, "standard").then(response => {
              if (isActive) {
                nextState.linkedin = response;
              }
            })
          );
        }

        if (platform === "twitter" || platform === "both") {
          const mode = twitterMode ?? "single";
          promises.push(
            generateTwitterContent(idea, emoji ?? undefined, mode).then(response => {
              if (isActive) {
                nextState.twitter = response;
              }
            })
          );
        }

        await Promise.all(promises);

        if (isActive) {
          setGeneratedContent(nextState);
        }
      } catch (err) {
        if (!isActive) {
          return;
        }

        console.error("Failed to generate content:", err);
        const message = err instanceof ApiError
          ? `Generation failed (status ${err.status}).`
          : "Failed to generate content. Please try again.";

        setError(message);
        setGeneratedContent({});
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadGeneratedContent();

    return () => {
      isActive = false;
    };
  }, [idea, emoji, platform, twitterMode, refreshNonce]);

  const handleRegenerate = () => {
    setRefreshNonce(prev => prev + 1);
  };

  const resolveApiError = (error: unknown, fallback: string): string => {
    if (error instanceof ApiError) {
      const payload = error.data;

      if (payload && typeof payload === "object" && "detail" in payload) {
        const detailValue = (payload as { detail?: unknown }).detail;

        if (typeof detailValue === "string") {
          return detailValue;
        }

        if (Array.isArray(detailValue) && detailValue.length) {
          const firstEntry = detailValue[0] as { msg?: unknown } | string;

          if (typeof firstEntry === "string") {
            return firstEntry;
          }

          if (firstEntry && typeof firstEntry === "object" && "msg" in firstEntry) {
            const msg = (firstEntry as { msg?: unknown }).msg;
            if (typeof msg === "string") {
              return msg;
            }
          }
        }
      }

      return fallback || `Request failed (status ${error.status}).`;
    }

    return fallback;
  };

  const handlePost = async () => {
    if (isPosting) {
      return;
    }

    if (!generatedContent.linkedin && !generatedContent.twitter) {
      toast({
        title: "⚠️ NO CONTENT",
        description: "Generate content before attempting to publish.",
      });
      return;
    }

    setIsPosting(true);

    const successes: string[] = [];
    const errors: string[] = [];

    if (generatedContent.linkedin) {
      try {
        await publishLinkedIn({
          content: generatedContent.linkedin.generated_content,
          image_url: imagePreview ?? undefined,
        });
        successes.push("LinkedIn");
      } catch (err) {
        console.error("Failed to publish to LinkedIn:", err);
        const detail = resolveApiError(err, "Unexpected error posting to LinkedIn.");
        errors.push(`LinkedIn: ${detail}`);
      }
    }

    if (generatedContent.twitter) {
      const isThread = Boolean(generatedContent.twitter.is_thread && generatedContent.twitter.thread_tweets?.length);
      const tweets = isThread
        ? generatedContent.twitter.thread_tweets?.map(tweet => tweet.content) ?? []
        : undefined;

      const baseContent = isThread
        ? (tweets && tweets.length ? tweets[0] : generatedContent.twitter.generated_content)
        : generatedContent.twitter.generated_content;

      try {
        await publishTwitter({
          content: baseContent,
          image_url: imagePreview ?? undefined,
          mode: isThread ? "thread" : "single",
          thread_tweets: isThread ? tweets : undefined,
        });
        successes.push("Twitter");
      } catch (err) {
        console.error("Failed to publish to Twitter:", err);
        const detail = resolveApiError(err, "Unexpected error posting to Twitter.");
        errors.push(`Twitter: ${detail}`);
      }
    }

    if (successes.length) {
      toast({
        title: "✅ PUBLISHED!",
        description: `Successfully posted to ${successes.join(" & ")}.`,
      });
    }

    if (errors.length) {
      toast({
        title: "❌ PUBLISH FAILED",
        description: errors.join(" \n"),
      });
    }

    setIsPosting(false);
  };

  const handleSaveDraft = async () => {
    const payloads = [];

    if (generatedContent.linkedin) {
      payloads.push(
        saveDraft({
          original_idea: generatedContent.linkedin.original_idea,
          emoji,
          generated_content: generatedContent.linkedin.generated_content,
          platform: "linkedin",
          mode: generatedContent.linkedin.mode,
          image_url: imagePreview ?? null,
        })
      );
    }

    if (generatedContent.twitter) {
      const twitterContent = generatedContent.twitter.is_thread && generatedContent.twitter.thread_tweets?.length
        ? generatedContent.twitter.thread_tweets.map(tweet => tweet.content).join("\n\n")
        : generatedContent.twitter.generated_content;

      payloads.push(
        saveDraft({
          original_idea: generatedContent.twitter.original_idea,
          emoji,
          generated_content: twitterContent,
          platform: "twitter",
          mode: generatedContent.twitter.mode,
          image_url: imagePreview ?? null,
        })
      );
    }

    if (!payloads.length) {
      toast({
        title: "⚠️ NOTHING TO SAVE",
        description: "Generate content before saving.",
      });
      return;
    }

    try {
      await Promise.all(payloads);
      toast({
        title: "💾 DRAFT SAVED!",
        description: "Draft saved to the backend successfully.",
      });
    } catch (err) {
      console.error("Failed to save draft:", err);
      toast({
        title: "❌ SAVE FAILED",
        description: "Unable to save draft. Please try again.",
      });
    }
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
          onClick={handleRegenerate}
          variant="outline"
          className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all"
        >
          <RefreshCw className="mr-2" /> REGENERATE
        </Button>
      </div>

      {isLoading && (
        <div className="brutal-card p-4 bg-card text-center font-bold">
          Generating optimized content...
        </div>
      )}

      {error && (
        <div className="brutal-card p-4 bg-destructive text-destructive-foreground font-bold text-center">
          {error}
        </div>
      )}

      <div className="brutal-card p-4 bg-warning text-warning-foreground">
        <p className="font-bold text-center">
          ⚠️ NOTE: Content is generated via the backend. Publishing still requires valid platform tokens.
        </p>
      </div>

      <div className="space-y-6">
        {generatedContent.linkedin && (
          <div className="brutal-card p-6 bg-linkedin/10">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">💼</div>
              <div>
                <h3 className="text-xl font-bold">LINKEDIN POST</h3>
                {generatedContent.linkedin.tone && (
                  <p className="text-xs text-muted-foreground font-bold">
                    Tone: {generatedContent.linkedin.tone} · Score: {generatedContent.linkedin.professional_score ?? "-"}
                  </p>
                )}
              </div>
            </div>
            <div className="brutal-border bg-card p-4 space-y-4">
              {imagePreview && (
                <img 
                  src={imagePreview} 
                  alt="Post" 
                  className="w-full h-48 object-cover brutal-border"
                />
              )}
              <p className="whitespace-pre-wrap font-mono text-sm">
                {generatedContent.linkedin.generated_content}
              </p>
              {generatedContent.linkedin.hashtags.length > 0 && (
                <div className="text-xs font-bold text-linkedin">
                  {generatedContent.linkedin.hashtags.map(tag => `#${tag.replace(/^#/, "")}`).join(" ")}
                </div>
              )}
              <div className="text-xs text-muted-foreground font-bold flex items-center justify-between">
                <span>{generatedContent.linkedin.character_count} characters</span>
                <span>Engagement: {generatedContent.linkedin.estimated_engagement}</span>
              </div>
            </div>
          </div>
        )}

        {generatedContent.twitter && twitterEntries.length > 0 && (
          <div className="brutal-card p-6 bg-twitter/10">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">𝕏</div>
              <h3 className="text-xl font-bold">
                X {generatedContent.twitter.is_thread ? "THREAD" : "POST"}
              </h3>
            </div>
            <div className="space-y-3">
              {twitterEntries.map((tweet, index) => (
                <div key={tweet.sequence ?? index} className="brutal-border bg-card p-4 space-y-3">
                  {index === 0 && imagePreview && (
                    <img 
                      src={imagePreview} 
                      alt="Tweet" 
                      className="w-full h-48 object-cover brutal-border mb-4"
                    />
                  )}
                  <p className="whitespace-pre-wrap font-mono text-sm">
                    {tweet.content}
                  </p>
                  <div className="text-xs text-muted-foreground font-bold flex items-center justify-between">
                    <span>Tweet {tweet.sequence}</span>
                    <span>{tweet.characterCount} characters</span>
                  </div>
                </div>
              ))}
            </div>
            {generatedContent.twitter.hashtags.length > 0 && (
              <div className="mt-3 text-xs font-bold text-twitter">
                {generatedContent.twitter.hashtags.map(tag => `#${tag.replace(/^#/, "")}`).join(" ")}
              </div>
            )}
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
          disabled={isPosting}
          className="brutal-border brutal-shadow-lg bg-success text-success-foreground hover:bg-success/90 font-bold uppercase disabled:opacity-70"
        >
          <Send className="mr-2" /> {isPosting ? "POSTING..." : "POST NOW"}
        </Button>
      </div>
    </div>
  );
};

export default ContentPreview;
