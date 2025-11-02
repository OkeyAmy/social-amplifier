import type {
  Draft,
  DraftCreatePayload,
  PlatformConnectionsStatus,
  GeneratedContentResponse,
  PublishRequestPayload,
  PublishTwitterRequestPayload,
} from "@/types/api";
import { ApiError } from "@/types/api";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ?? "http://localhost:8000";

const defaultHeaders: HeadersInit = {
  "Content-Type": "application/json",
};

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      ...defaultHeaders,
      ...(init.headers ?? {}),
    },
  });

  if (!response.ok) {
    const data = await safeParseJson(response);
    throw new ApiError(response.statusText || "Request failed", response.status, data);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function safeParseJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch (error) {
    return null;
  }
}

export function getConnectionStatus(): Promise<PlatformConnectionsStatus> {
  return request<PlatformConnectionsStatus>("/api/v1/auth/status");
}

export function initiatePlatformConnect(platform: "linkedin" | "twitter"): Promise<{ authorization_url: string; state: string; }> {
  return request<{ authorization_url: string; state: string }>(`/api/v1/auth/${platform}/connect`);
}

export function disconnectPlatform(platform: "linkedin" | "twitter"): Promise<{ success: boolean; platform: string; message: string; }> {
  return request(`/api/v1/auth/disconnect`, {
    method: "POST",
    body: JSON.stringify({ platform }),
  });
}

export function generateLinkedInContent(idea: string, emoji?: string | null, mode: string = "standard"): Promise<GeneratedContentResponse> {
  return request<GeneratedContentResponse>(`/api/v1/generate/linkedin`, {
    method: "POST",
    body: JSON.stringify({ idea, emoji, mode }),
  });
}

export function generateTwitterContent(idea: string, emoji?: string | null, mode: "single" | "thread" = "single"): Promise<GeneratedContentResponse> {
  return request<GeneratedContentResponse>(`/api/v1/generate/twitter`, {
    method: "POST",
    body: JSON.stringify({ idea, emoji, mode }),
  });
}

export function saveDraft(payload: DraftCreatePayload): Promise<Draft> {
  return request<Draft>(`/api/v1/drafts/`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getDrafts(): Promise<Draft[]> {
  return request<Draft[]>(`/api/v1/drafts/`);
}

export function deleteDraft(draftId: number): Promise<{ success: boolean; message: string; }> {
  return request(`/api/v1/drafts/${draftId}`, {
    method: "DELETE",
  });
}

export function publishLinkedIn(payload: PublishRequestPayload): Promise<{ success: boolean; platform: string; post_id?: string; message: string; }> {
  return request(`/api/v1/publish/linkedin`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function publishTwitter(payload: PublishTwitterRequestPayload): Promise<{ success: boolean; platform: string; mode: string; tweet_id?: string; tweet_ids?: string[]; message: string; }> {
  return request(`/api/v1/publish/twitter`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export { API_BASE_URL };
