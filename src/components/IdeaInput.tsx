import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ArrowRight } from "lucide-react";

interface IdeaInputProps {
  onSubmit: (idea: string, emoji: string | null) => void;
}

const suggestedEmojis = ["💡", "🚀", "🔥", "✨", "💪", "🎯", "⚡", "🌟"];
const MIN_IDEA_LENGTH = 10;

const IdeaInput = ({ onSubmit }: IdeaInputProps) => {
  const [idea, setIdea] = useState("");
  const [selectedEmoji, setSelectedEmoji] = useState<string | null>(null);
  const [validationMessage, setValidationMessage] = useState<string | null>(null);

  const handleSubmit = () => {
    const trimmed = idea.trim();

    if (trimmed.length < MIN_IDEA_LENGTH) {
      setValidationMessage(`Please expand your idea to at least ${MIN_IDEA_LENGTH} characters so the AI can create conversion-focused content.`);
      return;
    }

    setValidationMessage(null);
    onSubmit(trimmed, selectedEmoji);
  };

  const charCount = idea.length;
  const charColor = 
    charCount < 50 ? "text-muted-foreground" : 
    charCount < 200 ? "text-success" : 
    "text-accent";

  return (
    <div className="space-y-4 sm:space-y-6 animate-in fade-in duration-500">
      <div className="brutal-card p-4 sm:p-6 md:p-8 rotate-slightly bg-card">
        <h2 className="mb-4 sm:mb-6 font-bold text-lg sm:text-xl md:text-2xl">STEP 1: SHARE YOUR IDEA</h2>
        
        <Textarea
          placeholder="What's on your mind? Type your raw idea here..."
          value={idea}
          onChange={(e) => {
            const value = e.target.value;
            setIdea(value);

            if (value.trim().length >= MIN_IDEA_LENGTH) {
              setValidationMessage(null);
            }
          }}
          className="brutal-border min-h-[180px] sm:min-h-[200px] text-base sm:text-lg resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-primary font-mono"
        />
        
        <div className={`mt-2 text-right text-xs sm:text-sm font-bold ${charColor}`}>
          {charCount} characters
        </div>

        <p className="mt-2 text-xs sm:text-sm font-bold text-muted-foreground leading-tight">
          Minimum {MIN_IDEA_LENGTH} characters required. Share a sentence or two so we can craft conversion-optimized posts.
        </p>

        {validationMessage && (
          <div className="mt-3 brutal-card p-3 bg-warning text-warning-foreground font-bold text-xs sm:text-sm animate-in fade-in duration-300">
            {validationMessage}
          </div>
        )}
      </div>

      {idea.length >= MIN_IDEA_LENGTH && (
        <div className="brutal-card p-4 sm:p-6 rotate-slightly-reverse bg-secondary animate-in slide-in-from-top duration-300">
          <h3 className="mb-3 sm:mb-4 font-bold text-sm sm:text-base text-secondary-foreground">
            PICK A MOOD (OPTIONAL)
          </h3>
          <div className="flex flex-wrap gap-3 sm:gap-4">
            {suggestedEmojis.map((emoji) => (
              <button
                key={emoji}
                onClick={() => setSelectedEmoji(selectedEmoji === emoji ? null : emoji)}
                className={`text-3xl sm:text-4xl transition-transform hover:scale-125 touch-manipulation min-h-[44px] min-w-[44px] flex items-center justify-center ${
                  selectedEmoji === emoji ? "scale-150 rotate-12" : ""
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>
          {selectedEmoji && (
            <p className="mt-3 sm:mt-4 text-xs sm:text-sm font-bold text-secondary-foreground">
              Selected: {selectedEmoji} (Click again to deselect)
            </p>
          )}
        </div>
      )}

      <Button
        onClick={handleSubmit}
        disabled={idea.trim().length < MIN_IDEA_LENGTH}
        size="lg"
        className="w-full brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 text-base sm:text-lg md:text-xl font-bold tracking-wider disabled:opacity-50 disabled:cursor-not-allowed uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none min-h-[44px]"
      >
        NEXT <ArrowRight className="ml-2 w-4 h-4 sm:w-5 sm:h-5" />
      </Button>
    </div>
  );
};

export default IdeaInput;
