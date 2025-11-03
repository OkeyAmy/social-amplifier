export interface ConnectionStatus {
  platform: "linkedin" | "twitter";
  connected: boolean;
  expires_at: string | null;
  username: string | null;
}

export interface PlatformConnectionsStatus {
  linkedin: ConnectionStatus;
  twitter: ConnectionStatus;
}

export interface TwitterTweet {
  sequence: number;
  content: string;
  character_count: number;
}

export interface GeneratedContentResponse {
  original_idea: string;
  emoji: string | null;
  platform: "linkedin" | "twitter";
  mode: string | null;
  generated_content: string;
  character_count: number;
  estimated_engagement: string;
  hashtags: string[];
  mentions: string[];
  is_thread: boolean;
  thread_tweets?: TwitterTweet[];
  tone?: string | null;
  professional_score?: number | null;
}

export interface Draft {
  id: number;
  original_idea: string;
  emoji: string | null;
  generated_content: string;
  edited_content: string | null;
  platform: string;
  mode: string | null;
  image_url: string | null;
  created_at: string;
  updated_at: string;
}

export interface DraftCreatePayload {
  original_idea: string;
  emoji?: string | null;
  generated_content: string;
  platform: string;
  mode?: string | null;
  image_url?: string | null;
}

export interface DraftUpdatePayload {
  edited_content?: string | null;
  generated_content?: string | null;
  image_url?: string | null;
}

export interface PublishRequestPayload {
  content: string;
  image_base64?: string | null;
  image_mime_type?: string | null;
}

export interface PublishTwitterRequestPayload extends PublishRequestPayload {
  mode?: "single" | "thread";
  thread_tweets?: string[];
}

export class ApiError extends Error {
  public readonly status: number;
  public readonly data: unknown;

  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}
