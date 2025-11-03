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
      setValidationMessage(`Please expand your idea to at least ${MIN_IDEA_LENGTH} characters so the AI has enough context.`);
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
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="brutal-card p-6 md:p-8 rotate-slightly bg-card">
        <h2 className="mb-6 font-bold">STEP 1: SHARE YOUR IDEA</h2>
        
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
          className="brutal-border min-h-[200px] text-lg resize-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:border-primary font-mono"
        />
        
        <div className={`mt-2 text-right text-sm font-bold ${charColor}`}>
          {charCount} characters
        </div>

        <p className="mt-2 text-sm font-bold text-muted-foreground">
          Minimum {MIN_IDEA_LENGTH} characters required. Share a sentence or two so we can craft quality posts.
        </p>

        {validationMessage && (
          <div className="mt-3 brutal-card p-3 bg-warning text-warning-foreground font-bold animate-in fade-in duration-300">
            {validationMessage}
          </div>
        )}
      </div>

      {idea.length >= MIN_IDEA_LENGTH && (
        <div className="brutal-card p-6 rotate-slightly-reverse bg-secondary animate-in slide-in-from-top duration-300">
          <h3 className="mb-4 font-bold text-secondary-foreground">
            PICK A MOOD (OPTIONAL)
          </h3>
          <div className="flex flex-wrap gap-3">
            {suggestedEmojis.map((emoji) => (
              <button
                key={emoji}
                onClick={() => setSelectedEmoji(selectedEmoji === emoji ? null : emoji)}
                className={`text-4xl transition-transform hover:scale-125 ${
                  selectedEmoji === emoji ? "scale-150 rotate-12" : ""
                }`}
              >
                {emoji}
              </button>
            ))}
          </div>
          {selectedEmoji && (
            <p className="mt-4 text-sm font-bold text-secondary-foreground">
              Selected: {selectedEmoji} (Click again to deselect)
            </p>
          )}
        </div>
      )}

      <Button
        onClick={handleSubmit}
        disabled={idea.trim().length < MIN_IDEA_LENGTH}
        size="lg"
        className="w-full brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 text-xl font-bold tracking-wider disabled:opacity-50 disabled:cursor-not-allowed uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none"
      >
        NEXT <ArrowRight className="ml-2" />
      </Button>
    </div>
  );
};

export default IdeaInput;
