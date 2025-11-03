import { useState, useEffect, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Plus, Copy, Eye, Trash2, Calendar, Linkedin } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { NavLink } from "react-router-dom";
import { getDrafts, deleteDraft } from "@/services/api";
import type { Draft } from "@/types/api";
import { ApiError } from "@/types/api";

// X (Twitter) SVG Icon Component  
const XIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

const PostsPage = () => {
  const { toast } = useToast();
  const [posts, setPosts] = useState<Draft[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchPosts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getDrafts();
      setPosts(data);
    } catch (error) {
      console.error("Failed to fetch posts:", error);
      const message = error instanceof ApiError
        ? `Unable to load drafts (status ${error.status}).`
        : "Failed to load drafts. Please try again.";
      toast({
        title: "❌ LOAD FAILED",
        description: message,
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchPosts();
  }, [fetchPosts]);

  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      toast({
        title: "📋 COPIED!",
        description: "Content copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "❌ COPY FAILED",
        description: "Failed to copy content",
      });
    }
  };

  const handleView = (post: Draft) => {
    // TODO: Open modal or navigate to detailed view
    toast({
      title: "👀 VIEW POST",
      description: "Detailed view coming soon!",
    });
  };

  const handleDelete = async (postId: number) => {
    try {
      await deleteDraft(postId);
      setPosts(prev => prev.filter(p => p.id !== postId));
      toast({
        title: "🗑️ DELETED!",
        description: "Post deleted successfully",
      });
    } catch (error) {
      console.error("Failed to delete post:", error);
      const message = error instanceof ApiError
        ? `Delete failed (status ${error.status}).`
        : "Failed to delete post.";
      toast({
        title: "❌ DELETE FAILED",
        description: message,
      });
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case "linkedin":
        return <Linkedin className="w-4 h-4" />;
      case "twitter":
        return <XIcon className="w-4 h-4" />;
      case "both":
        return (
          <div className="flex gap-1">
            <Linkedin className="w-4 h-4" />
            <XIcon className="w-4 h-4" />
          </div>
        );
      default:
        return null;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-4xl mx-auto p-6">
          <div className="animate-pulse space-y-6">
            <div className="brutal-card p-6 bg-card h-32"></div>
            <div className="brutal-card p-6 bg-card h-24"></div>
            <div className="brutal-card p-6 bg-card h-24"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-3 sm:p-4 md:p-6 space-y-4 sm:space-y-6 md:space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4">
          <div className="brutal-card p-3 sm:p-4 md:p-6 bg-card text-foreground flex-1">
            <h1 className="text-2xl sm:text-3xl md:text-5xl lg:text-6xl font-bold break-words">YOUR POSTS</h1>
          </div>
          <NavLink to="/" className="w-full sm:w-auto">
            <Button
              size="lg"
              className="w-full sm:w-auto brutal-border brutal-shadow-lg bg-success text-success-foreground hover:bg-success/90 font-bold uppercase px-4 sm:px-6 md:px-8 py-3 sm:py-4 min-h-[44px] text-sm sm:text-base"
            >
              <Plus className="mr-2 w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6" />
              NEW POST
            </Button>
          </NavLink>
        </div>

        <p className="text-base sm:text-lg md:text-xl font-bold text-center px-2 sm:px-4 leading-tight">
          COPY & PASTE TO DRIVE <span className="text-success">CONVERSIONS</span>!
        </p>

        {/* Posts List */}
        {posts.length === 0 ? (
          <div className="brutal-card p-6 sm:p-8 md:p-12 bg-card text-center">
            <h3 className="text-lg sm:text-xl md:text-2xl font-bold mb-3 sm:mb-4">NO POSTS YET</h3>
            <p className="text-sm sm:text-base text-muted-foreground font-bold mb-4 sm:mb-6">
              Create your first post to get started!
            </p>
            <NavLink to="/">
              <Button
                size="lg"
                className="brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 font-bold uppercase text-sm sm:text-base min-h-[44px]"
              >
                <Plus className="mr-2 w-4 h-4 sm:w-5 sm:h-5" />
                CREATE YOUR FIRST POST
              </Button>
            </NavLink>
          </div>
        ) : (
          <div className="space-y-3 sm:space-y-4 md:space-y-6">
            {posts.map((post) => (
              <div key={post.id} className="brutal-card p-3 sm:p-4 md:p-6 bg-card">
                <div className="flex flex-col gap-3 sm:gap-4">
                  {/* Post Header */}
                  <div className="flex items-start gap-2 sm:gap-3">
                    <span className="text-xl sm:text-2xl md:text-3xl flex-shrink-0">{post.emoji || "📝"}</span>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-base sm:text-lg md:text-xl font-bold break-words">
                        {post.original_idea}
                      </h3>
                    </div>
                  </div>
                  
                  {/* Post Meta */}
                  <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-xs sm:text-sm text-muted-foreground font-bold">
                    <div className="flex items-center gap-2 min-w-0">
                      <Calendar className="w-3 h-3 sm:w-4 sm:h-4 flex-shrink-0" />
                      <span className="truncate">Created {formatDate(post.created_at)}</span>
                    </div>
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="flex items-center gap-1 flex-shrink-0">
                        {getPlatformIcon(post.platform)}
                      </div>
                      <span className="uppercase truncate">
                        {post.platform === "both" ? "LinkedIn + X" : post.platform}
                        {post.mode ? ` (${post.mode})` : ""}
                      </span>
                    </div>
                  </div>

                  {/* Post Content */}
                  {post.generated_content && (
                    <div className="brutal-border bg-background p-3 sm:p-4 font-mono text-xs sm:text-sm overflow-x-auto break-words">
                      {post.generated_content.length > 150 
                        ? `${post.generated_content.substring(0, 150)}...`
                        : post.generated_content
                      }
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2">
                    <Button
                      onClick={() => handleCopy(post.generated_content || post.original_idea)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold flex-1 sm:flex-initial min-h-[44px] text-xs sm:text-sm"
                    >
                      <Copy className="w-4 h-4 mr-1 sm:mr-2" />
                      <span className="hidden sm:inline">COPY</span>
                    </Button>
                    
                    <Button
                      onClick={() => handleView(post)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold flex-1 sm:flex-initial min-h-[44px] text-xs sm:text-sm"
                    >
                      <Eye className="w-4 h-4 mr-1 sm:mr-2" />
                      <span className="hidden sm:inline">VIEW</span>
                    </Button>
                    
                    <Button
                      onClick={() => handleDelete(post.id)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold text-destructive border-destructive hover:bg-destructive hover:text-destructive-foreground flex-1 sm:flex-initial min-h-[44px] text-xs sm:text-sm"
                    >
                      <Trash2 className="w-4 h-4 mr-1 sm:mr-2" />
                      <span className="hidden sm:inline">DELETE</span>
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PostsPage;