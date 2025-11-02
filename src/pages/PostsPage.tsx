import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Plus, Copy, Eye, Trash2, Calendar, Linkedin } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { NavLink } from "react-router-dom";

// X (Twitter) SVG Icon Component  
const XIcon = ({ className = "w-4 h-4" }: { className?: string }) => (
  <svg viewBox="0 0 24 24" className={className} fill="currentColor">
    <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
  </svg>
);

interface Post {
  id: number;
  emoji: string | null;
  original_idea: string;
  platform: string;
  mode?: string;
  created_at: string;
  content?: string;
}

const PostsPage = () => {
  const { toast } = useToast();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      // TODO: Replace with actual backend call
      // const response = await fetch('/api/v1/drafts/');
      // const data = await response.json();
      // setPosts(data);
      
      // Mock data for now
      const mockPosts: Post[] = [
        {
          id: 1,
          emoji: "😎",
          original_idea: "travel to abj and i am building softwares",
          platform: "both",
          created_at: "2025-11-02T19:14:00Z",
          content: "Just landed in Abuja! 🛩️ Building software remotely while exploring new cities..."
        },
        {
          id: 2,
          emoji: "🔥",
          original_idea: "10/10/2004",
          platform: "twitter",
          mode: "single",
          created_at: "2025-11-02T16:48:00Z",
          content: "October 10th, 2004 - A date that changed everything 🔥"
        }
      ];
      
      setPosts(mockPosts);
      setLoading(false);
      
    } catch (error) {
      console.error("Failed to fetch posts:", error);
      setLoading(false);
    }
  };

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

  const handleView = (post: Post) => {
    // TODO: Open modal or navigate to detailed view
    toast({
      title: "👀 VIEW POST",
      description: "Detailed view coming soon!",
    });
  };

  const handleDelete = async (postId: number) => {
    try {
      // TODO: Replace with actual backend call
      // await fetch(`/api/v1/drafts/${postId}`, { method: 'DELETE' });
      
      setPosts(prev => prev.filter(p => p.id !== postId));
      toast({
        title: "🗑️ DELETED!",
        description: "Post deleted successfully",
      });
    } catch (error) {
      toast({
        title: "❌ DELETE FAILED",
        description: "Failed to delete post",
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
      <div className="max-w-4xl mx-auto p-6 space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="brutal-card p-6 bg-accent text-accent-foreground">
            <h1 className="text-4xl md:text-6xl font-bold">YOUR POSTS</h1>
          </div>
          <NavLink to="/">
            <Button
              size="lg"
              className="brutal-border brutal-shadow-lg bg-success text-success-foreground hover:bg-success/90 font-bold uppercase px-8 py-4"
            >
              <Plus className="mr-2 w-6 h-6" />
              NEW POST
            </Button>
          </NavLink>
        </div>

        <p className="text-xl font-bold text-center">
          COPY & PASTE TO YOUR PLATFORMS!
        </p>

        {/* Posts List */}
        {posts.length === 0 ? (
          <div className="brutal-card p-12 bg-card text-center">
            <h3 className="text-2xl font-bold mb-4">NO POSTS YET</h3>
            <p className="text-muted-foreground font-bold mb-6">
              Create your first post to get started!
            </p>
            <NavLink to="/">
              <Button
                size="lg"
                className="brutal-border brutal-shadow-lg bg-primary text-primary-foreground hover:bg-primary/90 font-bold uppercase"
              >
                <Plus className="mr-2 w-5 h-5" />
                CREATE YOUR FIRST POST
              </Button>
            </NavLink>
          </div>
        ) : (
          <div className="space-y-6">
            {posts.map((post) => (
              <div key={post.id} className="brutal-card p-6 bg-card">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="text-2xl">{post.emoji || "📝"}</span>
                      <h3 className="text-xl font-bold">
                        {post.original_idea}
                      </h3>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-muted-foreground font-bold mb-4">
                      <div className="flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Created {formatDate(post.created_at)}
                      </div>
                      <div className="flex items-center gap-2">
                        {getPlatformIcon(post.platform)}
                        <span className="uppercase">
                          {post.platform === "both" ? "LinkedIn + X" : post.platform}
                          {post.mode && ` (${post.mode})`}
                        </span>
                      </div>
                    </div>

                    {post.content && (
                      <div className="brutal-border bg-background p-4 font-mono text-sm">
                        {post.content.length > 150 
                          ? `${post.content.substring(0, 150)}...`
                          : post.content
                        }
                      </div>
                    )}
                  </div>

                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleCopy(post.content || post.original_idea)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold"
                    >
                      <Copy className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      onClick={() => handleView(post)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold"
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                    
                    <Button
                      onClick={() => handleDelete(post.id)}
                      variant="outline"
                      size="sm"
                      className="brutal-border brutal-shadow-sm hover:translate-x-1 hover:translate-y-1 hover:shadow-none transition-all font-bold text-destructive border-destructive hover:bg-destructive hover:text-destructive-foreground"
                    >
                      <Trash2 className="w-4 h-4" />
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