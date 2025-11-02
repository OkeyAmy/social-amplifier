"""
Draft management routes
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# In-memory draft storage (use database in production)
drafts_store = {}
draft_counter = 0


class DraftCreate(BaseModel):
    """Create draft request"""
    original_idea: str
    emoji: Optional[str] = None
    generated_content: str
    platform: str
    mode: Optional[str] = None
    image_url: Optional[str] = None


class DraftUpdate(BaseModel):
    """Update draft request"""
    edited_content: Optional[str] = None
    generated_content: Optional[str] = None
    image_url: Optional[str] = None


class Draft(BaseModel):
    """Draft response"""
    id: int
    original_idea: str
    emoji: Optional[str]
    generated_content: str
    edited_content: Optional[str]
    platform: str
    mode: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime


@router.get("/", response_model=List[Draft])
async def get_drafts(user_id: int = 1):
    """
    Get all drafts for a user
    TODO: Implement proper user authentication
    """
    user_drafts = [
        draft for draft_id, draft in drafts_store.items()
        if draft.get("user_id") == user_id
    ]
    
    return [
        Draft(
            id=draft["id"],
            original_idea=draft["original_idea"],
            emoji=draft.get("emoji"),
            generated_content=draft["generated_content"],
            edited_content=draft.get("edited_content"),
            platform=draft["platform"],
            mode=draft.get("mode"),
            image_url=draft.get("image_url"),
            created_at=draft["created_at"],
            updated_at=draft["updated_at"]
        )
        for draft in user_drafts
    ]


@router.post("/", response_model=Draft)
async def create_draft(draft: DraftCreate, user_id: int = 1):
    """
    Save a new draft
    TODO: Implement proper user authentication
    """
    global draft_counter
    draft_counter += 1
    
    now = datetime.utcnow()
    
    new_draft = {
        "id": draft_counter,
        "user_id": user_id,
        "original_idea": draft.original_idea,
        "emoji": draft.emoji,
        "generated_content": draft.generated_content,
        "edited_content": None,
        "platform": draft.platform,
        "mode": draft.mode,
        "image_url": draft.image_url,
        "created_at": now,
        "updated_at": now
    }
    
    drafts_store[draft_counter] = new_draft
    
    return Draft(**{k: v for k, v in new_draft.items() if k != "user_id"})


@router.put("/{draft_id}", response_model=Draft)
async def update_draft(draft_id: int, update: DraftUpdate, user_id: int = 1):
    """
    Update an existing draft
    TODO: Implement proper user authentication
    """
    if draft_id not in drafts_store:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    draft = drafts_store[draft_id]
    
    if draft["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this draft")
    
    # Update fields
    if update.edited_content is not None:
        draft["edited_content"] = update.edited_content
    if update.generated_content is not None:
        draft["generated_content"] = update.generated_content
    if update.image_url is not None:
        draft["image_url"] = update.image_url
    
    draft["updated_at"] = datetime.utcnow()
    
    return Draft(**{k: v for k, v in draft.items() if k != "user_id"})


@router.delete("/{draft_id}")
async def delete_draft(draft_id: int, user_id: int = 1):
    """
    Delete a draft
    TODO: Implement proper user authentication
    """
    if draft_id not in drafts_store:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    draft = drafts_store[draft_id]
    
    if draft["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this draft")
    
    del drafts_store[draft_id]
    
    return {"success": True, "message": "Draft deleted successfully"}
