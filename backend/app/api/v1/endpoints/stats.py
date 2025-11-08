from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.document_stats import DocumentStats
from app.schemas.stats import StatsOverviewResponse

router = APIRouter()


@router.get("/overview", response_model=StatsOverviewResponse)
async def get_stats_overview(
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.TEACHER)),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
):
    """
    Get statistics overview for admin/teacher dashboard.
    
    Returns:
    - Total documents
    - Total users
    - Average words per document
    - Documents by user (paginated)
    - Recent activity
    """
    # Total documents
    total_documents = db.query(Document).count()
    
    # Total users
    total_users = db.query(User).count()
    
    # Calculate average words per document
    # Get all documents with content
    documents_with_content = db.query(Document).filter(
        Document.content.isnot(None),
        Document.content != ""
    ).all()
    
    total_words = 0
    for doc in documents_with_content:
        word_count = len((doc.content or "").split())
        total_words += word_count
    
    average_words = total_words / len(documents_with_content) if documents_with_content else 0
    
    # Documents by user (paginated)
    # Get document counts per user
    user_doc_counts_query = db.query(
        User.id,
        User.email,
        func.count(Document.id).label('document_count')
    ).outerjoin(
        Document, User.id == Document.owner_id
    ).group_by(
        User.id, User.email
    ).order_by(desc('document_count'))
    
    # Get total count for pagination
    total_users_with_docs = user_doc_counts_query.count()
    
    # Apply pagination
    offset = (page - 1) * per_page
    paginated_users = user_doc_counts_query.offset(offset).limit(per_page).all()
    
    # Calculate total words per user
    documents_by_user = []
    for user_id, user_email, doc_count in paginated_users:
        # Get total words for this user's documents
        user_docs = db.query(Document).filter(Document.owner_id == user_id).all()
        user_total_words = sum(len((doc.content or "").split()) for doc in user_docs)
        
        documents_by_user.append({
            "user_id": str(user_id),
            "user_email": user_email,
            "document_count": doc_count or 0,
            "total_words": user_total_words,
        })
    
    # Recent activity
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    documents_last_7_days = db.query(Document).filter(
        Document.created_at >= seven_days_ago
    ).count()
    
    documents_last_30_days = db.query(Document).filter(
        Document.created_at >= thirty_days_ago
    ).count()
    
    return StatsOverviewResponse(
        total_documents=total_documents,
        total_users=total_users,
        average_words_per_document=round(average_words, 2),
        total_words=total_words,
        documents_by_user=documents_by_user,
        recent_activity={
            "documents_created_last_7_days": documents_last_7_days,
            "documents_created_last_30_days": documents_last_30_days,
        }
    )

