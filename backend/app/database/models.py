"""
Database models for the Social Amplifier backend
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class PostStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    SCHEDULED = "scheduled"
    FAILED = "failed"


class PlatformType(str, enum.Enum):
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    BOTH = "both"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)  # Optional for OAuth-only users
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # OAuth tokens (encrypted)
    linkedin_access_token = Column(Text, nullable=True)
    linkedin_refresh_token = Column(Text, nullable=True)
    linkedin_token_expires = Column(DateTime, nullable=True)
    linkedin_connected = Column(Boolean, default=False)
    
    twitter_access_token = Column(Text, nullable=True)
    twitter_refresh_token = Column(Text, nullable=True)
    twitter_token_expires = Column(DateTime, nullable=True)
    twitter_connected = Column(Boolean, default=False)
    
    # User preferences
    default_tone = Column(String(50), default="professional")
    default_emoji_usage = Column(Boolean, default=True)
    
    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    drafts = relationship("Draft", back_populates="user", cascade="all, delete-orphan")


class Post(Base):
    """Published post model"""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    original_idea = Column(Text, nullable=False)
    selected_emoji = Column(String(10), nullable=True)
    generated_content = Column(Text, nullable=False)
    final_content = Column(Text, nullable=False)  # After user edits
    
    # Platform details
    platform = Column(Enum(PlatformType), nullable=False)
    twitter_mode = Column(String(20), nullable=True)  # 'single' or 'thread'
    
    # Image
    image_url = Column(String(500), nullable=True)
    
    # Status and metadata
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    published_at = Column(DateTime, nullable=True)
    scheduled_for = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Platform-specific IDs
    linkedin_post_id = Column(String(255), nullable=True)
    twitter_post_id = Column(String(255), nullable=True)
    
    # Engagement metrics (synced from platforms)
    linkedin_likes = Column(Integer, default=0)
    linkedin_comments = Column(Integer, default=0)
    linkedin_shares = Column(Integer, default=0)
    twitter_likes = Column(Integer, default=0)
    twitter_retweets = Column(Integer, default=0)
    twitter_replies = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="posts")


class Draft(Base):
    """Draft content model"""
    __tablename__ = "drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Content
    original_idea = Column(Text, nullable=False)
    selected_emoji = Column(String(10), nullable=True)
    generated_content = Column(Text, nullable=False)
    edited_content = Column(Text, nullable=True)
    
    # Platform details
    platform = Column(Enum(PlatformType), nullable=False)
    twitter_mode = Column(String(20), nullable=True)
    
    # Image
    image_url = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="drafts")


class AuditLog(Base):
    """Audit log for tracking all actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
