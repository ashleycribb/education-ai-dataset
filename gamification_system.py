#!/usr/bin/env python3
"""
Student Progress Gamification System for AITA
Achievement system with badges, progress tracking, and engagement metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
import random

# Configure Streamlit page
st.set_page_config(
    page_title="AITA Gamification Dashboard",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

class BadgeType(Enum):
    LEARNING = "learning"
    ENGAGEMENT = "engagement"
    COLLABORATION = "collaboration"
    ACHIEVEMENT = "achievement"
    SPECIAL = "special"

class BadgeRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class Badge:
    id: str
    name: str
    description: str
    icon: str
    type: BadgeType
    rarity: BadgeRarity
    points: int
    requirements: Dict[str, Any]
    unlocked_by: List[str] = None  # List of student IDs who unlocked this badge

@dataclass
class Achievement:
    id: str
    student_id: str
    badge_id: str
    unlocked_at: datetime
    progress_when_unlocked: Dict[str, Any]

@dataclass
class StudentProgress:
    student_id: str
    name: str
    level: int
    experience_points: int
    total_badges: int
    streak_days: int
    sessions_completed: int
    concepts_mastered: int
    help_given: int
    help_received: int
    quiz_average: float
    engagement_score: float
    last_activity: datetime

class GamificationEngine:
    def __init__(self):
        self.badges = self._initialize_badges()
        self.students = self._generate_sample_students()
        self.achievements = self._generate_sample_achievements()
        
    def _initialize_badges(self) -> List[Badge]:
        """Initialize the badge system with various achievements"""
        badges = [
            # Learning Badges
            Badge(
                id="first_session",
                name="First Steps",
                description="Complete your first learning session",
                icon="🚀",
                type=BadgeType.LEARNING,
                rarity=BadgeRarity.COMMON,
                points=10,
                requirements={"sessions_completed": 1}
            ),
            Badge(
                id="concept_master",
                name="Concept Master",
                description="Master 10 different concepts",
                icon="🧠",
                type=BadgeType.LEARNING,
                rarity=BadgeRarity.UNCOMMON,
                points=50,
                requirements={"concepts_mastered": 10}
            ),
            Badge(
                id="quiz_ace",
                name="Quiz Ace",
                description="Score 90% or higher on 5 quizzes",
                icon="🎯",
                type=BadgeType.ACHIEVEMENT,
                rarity=BadgeRarity.RARE,
                points=100,
                requirements={"quiz_high_scores": 5}
            ),
            
            # Engagement Badges
            Badge(
                id="daily_learner",
                name="Daily Learner",
                description="Learn for 7 consecutive days",
                icon="📅",
                type=BadgeType.ENGAGEMENT,
                rarity=BadgeRarity.UNCOMMON,
                points=75,
                requirements={"streak_days": 7}
            ),
            Badge(
                id="night_owl",
                name="Night Owl",
                description="Complete sessions after 8 PM",
                icon="🦉",
                type=BadgeType.ENGAGEMENT,
                rarity=BadgeRarity.COMMON,
                points=25,
                requirements={"late_sessions": 3}
            ),
            Badge(
                id="early_bird",
                name="Early Bird",
                description="Complete sessions before 7 AM",
                icon="🐦",
                type=BadgeType.ENGAGEMENT,
                rarity=BadgeRarity.COMMON,
                points=25,
                requirements={"early_sessions": 3}
            ),
            
            # Collaboration Badges
            Badge(
                id="helpful_peer",
                name="Helpful Peer",
                description="Help other students 10 times",
                icon="🤝",
                type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.UNCOMMON,
                points=60,
                requirements={"help_given": 10}
            ),
            Badge(
                id="team_player",
                name="Team Player",
                description="Participate in 5 group activities",
                icon="👥",
                type=BadgeType.COLLABORATION,
                rarity=BadgeRarity.COMMON,
                points=40,
                requirements={"group_activities": 5}
            ),
            
            # Special Badges
            Badge(
                id="perfectionist",
                name="Perfectionist",
                description="Complete 20 sessions without asking for help",
                icon="💎",
                type=BadgeType.SPECIAL,
                rarity=BadgeRarity.EPIC,
                points=200,
                requirements={"independent_sessions": 20}
            ),
            Badge(
                id="knowledge_seeker",
                name="Knowledge Seeker",
                description="Ask 50 thoughtful questions",
                icon="❓",
                type=BadgeType.LEARNING,
                rarity=BadgeRarity.RARE,
                points=120,
                requirements={"questions_asked": 50}
            ),
            Badge(
                id="legend",
                name="AITA Legend",
                description="Reach level 50 and maintain 95% engagement",
                icon="👑",
                type=BadgeType.SPECIAL,
                rarity=BadgeRarity.LEGENDARY,
                points=500,
                requirements={"level": 50, "engagement_score": 95}
            )
        ]
        
        return badges
    
    def _generate_sample_students(self) -> List[StudentProgress]:
        """Generate sample student progress data"""
        names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown", 
                "Frank Miller", "Grace Lee", "Henry Taylor", "Ivy Chen", "Jack Anderson"]
        
        students = []
        for i, name in enumerate(names):
            # Generate realistic progress data
            sessions = random.randint(5, 100)
            concepts = random.randint(3, 50)
            xp = sessions * random.randint(10, 50) + concepts * random.randint(5, 20)
            level = min(50, max(1, xp // 100))
            
            student = StudentProgress(
                student_id=f"student_{i+1:03d}",
                name=name,
                level=level,
                experience_points=xp,
                total_badges=random.randint(1, 8),
                streak_days=random.randint(0, 30),
                sessions_completed=sessions,
                concepts_mastered=concepts,
                help_given=random.randint(0, 20),
                help_received=random.randint(0, 15),
                quiz_average=random.uniform(70, 98),
                engagement_score=random.uniform(60, 95),
                last_activity=datetime.now() - timedelta(days=random.randint(0, 7))
            )
            students.append(student)
        
        return students
    
    def _generate_sample_achievements(self) -> List[Achievement]:
        """Generate sample achievement data"""
        achievements = []
        
        for student in self.students:
            # Each student gets some random achievements
            num_achievements = random.randint(1, min(5, student.total_badges))
            available_badges = random.sample(self.badges, num_achievements)
            
            for badge in available_badges:
                achievement = Achievement(
                    id=str(uuid.uuid4()),
                    student_id=student.student_id,
                    badge_id=badge.id,
                    unlocked_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    progress_when_unlocked={"level": student.level - random.randint(0, 5)}
                )
                achievements.append(achievement)
        
        return achievements
    
    def get_student_badges(self, student_id: str) -> List[Badge]:
        """Get all badges earned by a student"""
        student_achievements = [a for a in self.achievements if a.student_id == student_id]
        badge_ids = [a.badge_id for a in student_achievements]
        return [b for b in self.badges if b.id in badge_ids]
    
    def get_available_badges(self, student_id: str) -> List[Badge]:
        """Get badges that a student can still earn"""
        earned_badge_ids = [a.badge_id for a in self.achievements if a.student_id == student_id]
        return [b for b in self.badges if b.id not in earned_badge_ids]
    
    def calculate_next_level_progress(self, student: StudentProgress) -> Dict[str, Any]:
        """Calculate progress to next level"""
        current_level_xp = student.level * 100
        next_level_xp = (student.level + 1) * 100
        progress = (student.experience_points - current_level_xp) / (next_level_xp - current_level_xp)
        
        return {
            "current_xp": student.experience_points,
            "current_level_xp": current_level_xp,
            "next_level_xp": next_level_xp,
            "progress_percentage": min(100, max(0, progress * 100)),
            "xp_needed": max(0, next_level_xp - student.experience_points)
        }
    
    def get_leaderboard(self, metric: str = "experience_points", limit: int = 10) -> List[StudentProgress]:
        """Get leaderboard based on specified metric"""
        return sorted(self.students, key=lambda s: getattr(s, metric), reverse=True)[:limit]
    
    def get_badge_statistics(self) -> Dict[str, Any]:
        """Get statistics about badge distribution"""
        badge_counts = {}
        rarity_counts = {}
        type_counts = {}
        
        for achievement in self.achievements:
            badge = next(b for b in self.badges if b.id == achievement.badge_id)
            badge_counts[badge.name] = badge_counts.get(badge.name, 0) + 1
            rarity_counts[badge.rarity.value] = rarity_counts.get(badge.rarity.value, 0) + 1
            type_counts[badge.type.value] = type_counts.get(badge.type.value, 0) + 1
        
        return {
            "badge_distribution": badge_counts,
            "rarity_distribution": rarity_counts,
            "type_distribution": type_counts,
            "total_badges_earned": len(self.achievements),
            "unique_badges": len(set(a.badge_id for a in self.achievements))
        }

# Initialize gamification engine
@st.cache_data
def get_gamification_engine():
    return GamificationEngine()

gamification = get_gamification_engine()

# Custom CSS for badges and styling
st.markdown("""
<style>
.badge-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin: 10px 0;
}

.badge {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 8px 12px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    min-width: 100px;
}

.badge.common { background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%); }
.badge.uncommon { background: linear-gradient(135deg, #00b894 0%, #00a085 100%); }
.badge.rare { background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%); }
.badge.epic { background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%); }
.badge.legendary { background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%); }

.level-badge {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    color: #2d3436;
    padding: 5px 15px;
    border-radius: 25px;
    font-weight: bold;
    font-size: 18px;
}

.xp-bar {
    background-color: #ddd;
    border-radius: 10px;
    overflow: hidden;
    height: 20px;
    margin: 10px 0;
}

.xp-progress {
    background: linear-gradient(90deg, #00b894, #00a085);
    height: 100%;
    transition: width 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("🏆 Gamification Dashboard")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Select View",
    ["Student Progress", "Badge Gallery", "Leaderboards", "Achievement Analytics", "Progress Tracking"]
)

# Student selector for individual views
if page in ["Student Progress", "Progress Tracking"]:
    student_names = [s.name for s in gamification.students]
    selected_student_name = st.sidebar.selectbox("Select Student", student_names)
    selected_student = next(s for s in gamification.students if s.name == selected_student_name)

# Main content
if page == "Student Progress":
    st.title(f"🎮 {selected_student.name}'s Progress")
    
    # Level and XP display
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f'<div class="level-badge">Level {selected_student.level}</div>', unsafe_allow_html=True)
        
        # XP Progress bar
        level_progress = gamification.calculate_next_level_progress(selected_student)
        st.markdown(f"**Experience Points:** {selected_student.experience_points:,}")
        
        progress_html = f"""
        <div class="xp-bar">
            <div class="xp-progress" style="width: {level_progress['progress_percentage']}%"></div>
        </div>
        <small>{level_progress['xp_needed']} XP needed for Level {selected_student.level + 1}</small>
        """
        st.markdown(progress_html, unsafe_allow_html=True)
    
    with col2:
        st.metric("Total Badges", selected_student.total_badges)
        st.metric("Current Streak", f"{selected_student.streak_days} days")
    
    with col3:
        # Engagement score as a gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = selected_student.engagement_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Engagement"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Student stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Learning Statistics")
        stats_data = {
            "Sessions Completed": selected_student.sessions_completed,
            "Concepts Mastered": selected_student.concepts_mastered,
            "Quiz Average": f"{selected_student.quiz_average:.1f}%",
            "Help Given": selected_student.help_given,
            "Help Received": selected_student.help_received
        }
        
        for stat, value in stats_data.items():
            st.metric(stat, value)
    
    with col2:
        st.subheader("🏅 Earned Badges")
        student_badges = gamification.get_student_badges(selected_student.student_id)
        
        if student_badges:
            for badge in student_badges:
                badge_html = f"""
                <div class="badge {badge.rarity.value}">
                    {badge.icon} {badge.name}
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)
                st.caption(badge.description)
        else:
            st.info("No badges earned yet. Keep learning to unlock achievements!")
    
    # Available badges
    st.subheader("🎯 Available Badges")
    available_badges = gamification.get_available_badges(selected_student.student_id)
    
    for badge in available_badges[:5]:  # Show first 5 available badges
        with st.expander(f"{badge.icon} {badge.name} ({badge.rarity.value.title()})"):
            st.write(badge.description)
            st.write(f"**Points:** {badge.points}")
            st.write(f"**Type:** {badge.type.value.title()}")
            
            # Show progress towards badge (simplified)
            if "sessions_completed" in badge.requirements:
                required = badge.requirements["sessions_completed"]
                current = selected_student.sessions_completed
                progress = min(100, (current / required) * 100)
                st.progress(progress / 100)
                st.caption(f"Progress: {current}/{required} sessions")

elif page == "Badge Gallery":
    st.title("🏅 Badge Gallery")
    
    # Badge filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rarity_filter = st.selectbox("Filter by Rarity", 
                                   ["All"] + [r.value.title() for r in BadgeRarity])
    
    with col2:
        type_filter = st.selectbox("Filter by Type", 
                                 ["All"] + [t.value.title() for t in BadgeType])
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Name", "Points", "Rarity"])
    
    # Filter badges
    filtered_badges = gamification.badges
    
    if rarity_filter != "All":
        filtered_badges = [b for b in filtered_badges if b.rarity.value == rarity_filter.lower()]
    
    if type_filter != "All":
        filtered_badges = [b for b in filtered_badges if b.type.value == type_filter.lower()]
    
    # Sort badges
    if sort_by == "Points":
        filtered_badges = sorted(filtered_badges, key=lambda b: b.points, reverse=True)
    elif sort_by == "Rarity":
        rarity_order = {r: i for i, r in enumerate(BadgeRarity)}
        filtered_badges = sorted(filtered_badges, key=lambda b: rarity_order[b.rarity], reverse=True)
    else:
        filtered_badges = sorted(filtered_badges, key=lambda b: b.name)
    
    # Display badges in grid
    cols = st.columns(3)
    for i, badge in enumerate(filtered_badges):
        with cols[i % 3]:
            # Count how many students have this badge
            earned_count = len([a for a in gamification.achievements if a.badge_id == badge.id])
            
            st.markdown(f"""
            <div class="badge {badge.rarity.value}" style="width: 100%; margin-bottom: 10px;">
                {badge.icon} {badge.name}
            </div>
            """, unsafe_allow_html=True)
            
            st.write(f"**{badge.description}**")
            st.write(f"Points: {badge.points} | Type: {badge.type.value.title()}")
            st.write(f"Earned by: {earned_count} students")
            
            # Show requirements
            req_text = []
            for req, value in badge.requirements.items():
                req_text.append(f"{req.replace('_', ' ').title()}: {value}")
            st.caption("Requirements: " + ", ".join(req_text))

elif page == "Leaderboards":
    st.title("🏆 Leaderboards")
    
    # Leaderboard type selector
    leaderboard_type = st.selectbox(
        "Select Leaderboard",
        ["Experience Points", "Level", "Badges", "Streak", "Quiz Average", "Engagement Score"]
    )
    
    # Map display names to attribute names
    metric_mapping = {
        "Experience Points": "experience_points",
        "Level": "level",
        "Badges": "total_badges",
        "Streak": "streak_days",
        "Quiz Average": "quiz_average",
        "Engagement Score": "engagement_score"
    }
    
    metric = metric_mapping[leaderboard_type]
    leaderboard = gamification.get_leaderboard(metric, limit=10)
    
    # Display leaderboard
    st.subheader(f"🥇 Top 10 - {leaderboard_type}")
    
    for i, student in enumerate(leaderboard, 1):
        col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
        
        with col1:
            # Medal emojis for top 3
            if i == 1:
                st.markdown("🥇")
            elif i == 2:
                st.markdown("🥈")
            elif i == 3:
                st.markdown("🥉")
            else:
                st.markdown(f"**{i}**")
        
        with col2:
            st.write(f"**{student.name}**")
        
        with col3:
            value = getattr(student, metric)
            if metric in ["quiz_average", "engagement_score"]:
                st.write(f"{value:.1f}%")
            else:
                st.write(f"{value:,}")
        
        with col4:
            st.write(f"Level {student.level}")
    
    # Leaderboard visualization
    st.subheader("📊 Leaderboard Visualization")
    
    df = pd.DataFrame([asdict(s) for s in leaderboard])
    
    if metric in ["quiz_average", "engagement_score"]:
        fig = px.bar(df, x='name', y=metric, title=f"{leaderboard_type} Leaderboard",
                    color=metric, color_continuous_scale='viridis')
    else:
        fig = px.bar(df, x='name', y=metric, title=f"{leaderboard_type} Leaderboard",
                    color=metric, color_continuous_scale='blues')
    
    fig.update_layout(xaxis_title="Student", yaxis_title=leaderboard_type)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Achievement Analytics":
    st.title("📈 Achievement Analytics")
    
    # Get badge statistics
    stats = gamification.get_badge_statistics()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Badges Earned", stats["total_badges_earned"])
    
    with col2:
        st.metric("Unique Badges", stats["unique_badges"])
    
    with col3:
        st.metric("Total Available", len(gamification.badges))
    
    with col4:
        completion_rate = (stats["unique_badges"] / len(gamification.badges)) * 100
        st.metric("Completion Rate", f"{completion_rate:.1f}%")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 Badge Type Distribution")
        type_df = pd.DataFrame(list(stats["type_distribution"].items()), 
                              columns=['Type', 'Count'])
        fig = px.pie(type_df, values='Count', names='Type', 
                    title="Badges Earned by Type")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💎 Badge Rarity Distribution")
        rarity_df = pd.DataFrame(list(stats["rarity_distribution"].items()), 
                                columns=['Rarity', 'Count'])
        fig = px.pie(rarity_df, values='Count', names='Rarity', 
                    title="Badges Earned by Rarity")
        st.plotly_chart(fig, use_container_width=True)
    
    # Most popular badges
    st.subheader("🌟 Most Popular Badges")
    popular_badges = sorted(stats["badge_distribution"].items(), 
                           key=lambda x: x[1], reverse=True)[:10]
    
    popular_df = pd.DataFrame(popular_badges, columns=['Badge', 'Times Earned'])
    fig = px.bar(popular_df, x='Badge', y='Times Earned', 
                title="Top 10 Most Earned Badges")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Achievement timeline (simulated)
    st.subheader("📅 Achievement Timeline")
    
    # Create sample timeline data
    timeline_data = []
    for achievement in gamification.achievements[-20:]:  # Last 20 achievements
        badge = next(b for b in gamification.badges if b.id == achievement.badge_id)
        student = next(s for s in gamification.students if s.student_id == achievement.student_id)
        timeline_data.append({
            'date': achievement.unlocked_at,
            'student': student.name,
            'badge': badge.name,
            'points': badge.points
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    timeline_df = timeline_df.sort_values('date')
    
    fig = px.scatter(timeline_df, x='date', y='student', size='points', 
                    color='badge', title="Recent Badge Achievements",
                    hover_data=['badge', 'points'])
    st.plotly_chart(fig, use_container_width=True)

elif page == "Progress Tracking":
    st.title(f"📈 {selected_student.name}'s Progress Tracking")
    
    # Generate sample progress data over time
    dates = pd.date_range(start='2024-01-01', end='2024-06-20', freq='D')
    
    # Simulate cumulative progress
    np.random.seed(hash(selected_student.student_id) % 2**32)  # Consistent random data per student
    
    daily_xp = np.random.poisson(lam=20, size=len(dates))  # Daily XP gain
    cumulative_xp = np.cumsum(daily_xp)
    
    daily_concepts = np.random.poisson(lam=0.5, size=len(dates))  # Daily concepts learned
    cumulative_concepts = np.cumsum(daily_concepts)
    
    # Create progress dataframe
    progress_df = pd.DataFrame({
        'date': dates,
        'daily_xp': daily_xp,
        'cumulative_xp': cumulative_xp,
        'daily_concepts': daily_concepts,
        'cumulative_concepts': cumulative_concepts,
        'level': cumulative_xp // 100 + 1
    })
    
    # Progress visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Experience Points Over Time")
        fig = px.line(progress_df, x='date', y='cumulative_xp', 
                     title="Cumulative Experience Points")
        fig.add_scatter(x=progress_df['date'], y=progress_df['daily_xp'], 
                       mode='markers', name='Daily XP', opacity=0.6)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🧠 Concepts Mastered")
        fig = px.line(progress_df, x='date', y='cumulative_concepts', 
                     title="Cumulative Concepts Mastered")
        st.plotly_chart(fig, use_container_width=True)
    
    # Level progression
    st.subheader("🎯 Level Progression")
    fig = px.line(progress_df, x='date', y='level', title="Level Over Time")
    fig.update_traces(mode='lines+markers')
    st.plotly_chart(fig, use_container_width=True)
    
    # Weekly summary
    st.subheader("📅 Weekly Summary")
    
    # Group by week
    progress_df['week'] = progress_df['date'].dt.isocalendar().week
    weekly_summary = progress_df.groupby('week').agg({
        'daily_xp': 'sum',
        'daily_concepts': 'sum',
        'date': 'first'
    }).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(weekly_summary, x='week', y='daily_xp', 
                    title="Weekly XP Gained")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(weekly_summary, x='week', y='daily_concepts', 
                    title="Weekly Concepts Learned")
        st.plotly_chart(fig, use_container_width=True)
    
    # Progress insights
    st.subheader("💡 Progress Insights")
    
    recent_week_xp = weekly_summary['daily_xp'].iloc[-1] if len(weekly_summary) > 0 else 0
    avg_weekly_xp = weekly_summary['daily_xp'].mean() if len(weekly_summary) > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if recent_week_xp > avg_weekly_xp:
            st.success(f"🔥 Great week! {recent_week_xp:.0f} XP gained (above average)")
        else:
            st.info(f"📈 This week: {recent_week_xp:.0f} XP (average: {avg_weekly_xp:.0f})")
    
    with col2:
        best_week_xp = weekly_summary['daily_xp'].max() if len(weekly_summary) > 0 else 0
        st.metric("Best Week", f"{best_week_xp:.0f} XP")
    
    with col3:
        total_days_active = len([x for x in daily_xp if x > 0])
        st.metric("Active Days", f"{total_days_active}/{len(dates)}")

# Footer
st.markdown("---")
st.markdown("*AITA Gamification System - Making learning fun and engaging! 🎮*")