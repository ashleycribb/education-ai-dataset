#!/usr/bin/env python3
"""
Real-time Notification System for AITA
WebSocket-based notifications for teachers when students need help or encounter issues
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Set
import json
import uuid
import datetime
import asyncio
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    HELP_REQUEST = "help_request"
    MISCONCEPTION_DETECTED = "misconception_detected"
    STUDENT_STUCK = "student_stuck"
    INAPPROPRIATE_CONTENT = "inappropriate_content"
    SESSION_TIMEOUT = "session_timeout"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: NotificationType
    priority: NotificationPriority
    title: str
    message: str
    student_id: Optional[str] = None
    session_id: Optional[str] = None
    teacher_id: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    metadata: Optional[Dict[str, Any]] = {}
    read: bool = False
    action_required: bool = False
    action_url: Optional[str] = None

class HelpRequest(BaseModel):
    student_id: str
    session_id: str
    message: str
    urgency: NotificationPriority = NotificationPriority.MEDIUM
    context: Optional[Dict[str, Any]] = {}

class ConnectionManager:
    def __init__(self):
        # Store active WebSocket connections by teacher ID
        self.active_connections: Dict[str, WebSocket] = {}
        # Store teacher subscriptions (which students they monitor)
        self.teacher_subscriptions: Dict[str, Set[str]] = {}
        # Store notification history
        self.notification_history: List[Notification] = []
        # Store pending notifications for offline teachers
        self.pending_notifications: Dict[str, List[Notification]] = {}

    async def connect(self, websocket: WebSocket, teacher_id: str):
        """Connect a teacher to the notification system"""
        await websocket.accept()
        self.active_connections[teacher_id] = websocket
        logger.info(f"Teacher {teacher_id} connected to notification system")

        # Send pending notifications
        if teacher_id in self.pending_notifications:
            for notification in self.pending_notifications[teacher_id]:
                await self.send_notification_to_teacher(teacher_id, notification)
            del self.pending_notifications[teacher_id]

    def disconnect(self, teacher_id: str):
        """Disconnect a teacher from the notification system"""
        if teacher_id in self.active_connections:
            del self.active_connections[teacher_id]
        logger.info(f"Teacher {teacher_id} disconnected from notification system")

    async def send_notification_to_teacher(self, teacher_id: str, notification: Notification):
        """Send a notification to a specific teacher"""
        if teacher_id in self.active_connections:
            try:
                await self.active_connections[teacher_id].send_text(notification.json())
                logger.info(f"Sent notification {notification.id} to teacher {teacher_id}")
            except Exception as e:
                logger.error(f"Failed to send notification to teacher {teacher_id}: {e}")
                # Remove broken connection
                self.disconnect(teacher_id)
        else:
            # Store notification for when teacher comes online
            if teacher_id not in self.pending_notifications:
                self.pending_notifications[teacher_id] = []
            self.pending_notifications[teacher_id].append(notification)
            logger.info(f"Stored notification {notification.id} for offline teacher {teacher_id}")

    async def broadcast_notification(self, notification: Notification):
        """Broadcast a notification to all connected teachers"""
        self.notification_history.append(notification)

        for teacher_id in self.active_connections.copy():
            await self.send_notification_to_teacher(teacher_id, notification)

    async def send_to_student_teachers(self, student_id: str, notification: Notification):
        """Send notification to teachers monitoring a specific student"""
        for teacher_id, students in self.teacher_subscriptions.items():
            if student_id in students:
                await self.send_notification_to_teacher(teacher_id, notification)

    def subscribe_teacher_to_student(self, teacher_id: str, student_id: str):
        """Subscribe a teacher to notifications for a specific student"""
        if teacher_id not in self.teacher_subscriptions:
            self.teacher_subscriptions[teacher_id] = set()
        self.teacher_subscriptions[teacher_id].add(student_id)
        logger.info(f"Teacher {teacher_id} subscribed to student {student_id}")

    def unsubscribe_teacher_from_student(self, teacher_id: str, student_id: str):
        """Unsubscribe a teacher from notifications for a specific student"""
        if teacher_id in self.teacher_subscriptions:
            self.teacher_subscriptions[teacher_id].discard(student_id)
            logger.info(f"Teacher {teacher_id} unsubscribed from student {student_id}")

# Create FastAPI app for notifications
notification_app = FastAPI(
    title="AITA Real-time Notification System",
    description="WebSocket-based notifications for teachers",
    version="1.0.0"
)

# Add CORS middleware
notification_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize connection manager
manager = ConnectionManager()

# WebSocket endpoint for teachers
@notification_app.websocket("/ws/teacher/{teacher_id}")
async def websocket_endpoint(websocket: WebSocket, teacher_id: str):
    await manager.connect(websocket, teacher_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            if message.get("type") == "subscribe":
                student_id = message.get("student_id")
                if student_id:
                    manager.subscribe_teacher_to_student(teacher_id, student_id)
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "student_id": student_id
                    }))

            elif message.get("type") == "unsubscribe":
                student_id = message.get("student_id")
                if student_id:
                    manager.unsubscribe_teacher_from_student(teacher_id, student_id)
                    await websocket.send_text(json.dumps({
                        "type": "unsubscription_confirmed",
                        "student_id": student_id
                    }))

            elif message.get("type") == "mark_read":
                notification_id = message.get("notification_id")
                # Mark notification as read
                for notification in manager.notification_history:
                    if notification.id == notification_id:
                        notification.read = True
                        break

    except WebSocketDisconnect:
        manager.disconnect(teacher_id)

# REST API endpoints for creating notifications
@notification_app.post("/api/notifications/help-request")
async def create_help_request(help_request: HelpRequest):
    """Create a help request notification from a student"""
    notification = Notification(
        type=NotificationType.HELP_REQUEST,
        priority=help_request.urgency,
        title="Student Help Request",
        message=f"Student needs help: {help_request.message}",
        student_id=help_request.student_id,
        session_id=help_request.session_id,
        metadata=help_request.context,
        action_required=True,
        action_url=f"/teacher/session/{help_request.session_id}"
    )

    await manager.send_to_student_teachers(help_request.student_id, notification)

    return {"success": True, "notification_id": notification.id}

@notification_app.post("/api/notifications/misconception")
async def create_misconception_alert(
    student_id: str,
    session_id: str,
    misconception: str,
    confidence: float = 0.8
):
    """Create a misconception detection notification"""
    priority = NotificationPriority.HIGH if confidence > 0.9 else NotificationPriority.MEDIUM

    notification = Notification(
        type=NotificationType.MISCONCEPTION_DETECTED,
        priority=priority,
        title="Misconception Detected",
        message=f"Potential misconception identified: {misconception}",
        student_id=student_id,
        session_id=session_id,
        metadata={"misconception": misconception, "confidence": confidence},
        action_required=True,
        action_url=f"/teacher/session/{session_id}/misconceptions"
    )

    await manager.send_to_student_teachers(student_id, notification)

    return {"success": True, "notification_id": notification.id}

@notification_app.post("/api/notifications/student-stuck")
async def create_student_stuck_alert(
    student_id: str,
    session_id: str,
    duration_minutes: int,
    last_interaction: str
):
    """Create a notification when a student appears to be stuck"""
    notification = Notification(
        type=NotificationType.STUDENT_STUCK,
        priority=NotificationPriority.MEDIUM,
        title="Student May Be Stuck",
        message=f"Student has been inactive for {duration_minutes} minutes. Last interaction: {last_interaction}",
        student_id=student_id,
        session_id=session_id,
        metadata={"duration_minutes": duration_minutes, "last_interaction": last_interaction},
        action_required=True,
        action_url=f"/teacher/session/{session_id}"
    )

    await manager.send_to_student_teachers(student_id, notification)

    return {"success": True, "notification_id": notification.id}

@notification_app.post("/api/notifications/inappropriate-content")
async def create_inappropriate_content_alert(
    student_id: str,
    session_id: str,
    content: str,
    moderation_score: float
):
    """Create a notification for inappropriate content detection"""
    notification = Notification(
        type=NotificationType.INAPPROPRIATE_CONTENT,
        priority=NotificationPriority.URGENT,
        title="Inappropriate Content Detected",
        message=f"Potentially inappropriate content detected from student",
        student_id=student_id,
        session_id=session_id,
        metadata={"content": content, "moderation_score": moderation_score},
        action_required=True,
        action_url=f"/teacher/session/{session_id}/moderation"
    )

    await manager.send_to_student_teachers(student_id, notification)

    return {"success": True, "notification_id": notification.id}

@notification_app.post("/api/notifications/achievement")
async def create_achievement_notification(
    student_id: str,
    achievement_name: str,
    achievement_description: str
):
    """Create a positive achievement notification"""
    notification = Notification(
        type=NotificationType.ACHIEVEMENT_UNLOCKED,
        priority=NotificationPriority.LOW,
        title="Student Achievement",
        message=f"Student unlocked achievement: {achievement_name}",
        student_id=student_id,
        metadata={"achievement": achievement_name, "description": achievement_description},
        action_required=False
    )

    await manager.send_to_student_teachers(student_id, notification)

    return {"success": True, "notification_id": notification.id}

@notification_app.post("/api/notifications/system")
async def create_system_notification(
    title: str,
    message: str,
    priority: NotificationPriority = NotificationPriority.MEDIUM,
    action_url: Optional[str] = None
):
    """Create a system-wide notification"""
    notification = Notification(
        type=NotificationType.SYSTEM_ALERT,
        priority=priority,
        title=title,
        message=message,
        action_required=action_url is not None,
        action_url=action_url
    )

    await manager.broadcast_notification(notification)

    return {"success": True, "notification_id": notification.id}

# Get notification history
@notification_app.get("/api/notifications/history/{teacher_id}")
async def get_notification_history(teacher_id: str, limit: int = 50):
    """Get notification history for a teacher"""
    # Filter notifications relevant to the teacher
    relevant_notifications = []

    for notification in manager.notification_history[-limit:]:
        # Include system notifications and notifications for students the teacher monitors
        if (notification.type == NotificationType.SYSTEM_ALERT or
            notification.teacher_id == teacher_id or
            (notification.student_id and
             teacher_id in manager.teacher_subscriptions and
             notification.student_id in manager.teacher_subscriptions[teacher_id])):
            relevant_notifications.append(notification.dict())

    return {"notifications": relevant_notifications}

# Get notification statistics
@notification_app.get("/api/notifications/stats")
async def get_notification_stats():
    """Get notification system statistics"""
    total_notifications = len(manager.notification_history)
    unread_count = sum(1 for n in manager.notification_history if not n.read)

    type_counts = {}
    priority_counts = {}

    for notification in manager.notification_history:
        type_counts[notification.type] = type_counts.get(notification.type, 0) + 1
        priority_counts[notification.priority] = priority_counts.get(notification.priority, 0) + 1

    return {
        "total_notifications": total_notifications,
        "unread_count": unread_count,
        "active_teachers": len(manager.active_connections),
        "type_distribution": type_counts,
        "priority_distribution": priority_counts,
        "teacher_subscriptions": len(manager.teacher_subscriptions)
    }

# Health check
@notification_app.get("/health")
async def health_check():
    """Health check for notification system"""
    return {
        "status": "healthy",
        "active_connections": len(manager.active_connections),
        "total_notifications": len(manager.notification_history),
        "timestamp": datetime.datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🔔 Starting AITA Real-time Notification System...")
    uvicorn.run(notification_app, host="0.0.0.0", port=8002)