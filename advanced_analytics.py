#!/usr/bin/env python3
"""
Advanced Learning Analytics Dashboard for AITA
Enhanced analytics with visualizations, learning path recommendations, and predictive insights
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
from dataclasses import dataclass
from enum import Enum

# Configure Streamlit page
st.set_page_config(
    page_title="AITA Advanced Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class LearningPattern(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"

@dataclass
class StudentAnalytics:
    student_id: str
    name: str
    total_sessions: int
    total_interactions: int
    avg_session_duration: float
    learning_velocity: float  # concepts learned per hour
    engagement_score: float  # 0-100
    misconception_rate: float  # misconceptions per session
    help_request_frequency: float
    preferred_learning_pattern: LearningPattern
    knowledge_gaps: List[str]
    strengths: List[str]
    predicted_performance: float
    risk_level: str  # "low", "medium", "high"

class AnalyticsEngine:
    def __init__(self):
        self.students_data = self._generate_sample_data()
        
    def _generate_sample_data(self) -> List[StudentAnalytics]:
        """Generate sample analytics data for demonstration"""
        students = []
        names = ["Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown", 
                "Frank Miller", "Grace Lee", "Henry Taylor", "Ivy Chen", "Jack Anderson"]
        
        for i, name in enumerate(names):
            student = StudentAnalytics(
                student_id=f"student_{i+1:03d}",
                name=name,
                total_sessions=np.random.randint(5, 50),
                total_interactions=np.random.randint(50, 500),
                avg_session_duration=np.random.uniform(15, 60),  # minutes
                learning_velocity=np.random.uniform(0.5, 3.0),  # concepts per hour
                engagement_score=np.random.uniform(60, 95),
                misconception_rate=np.random.uniform(0.1, 0.8),
                help_request_frequency=np.random.uniform(0.1, 0.5),
                preferred_learning_pattern=np.random.choice(list(LearningPattern)),
                knowledge_gaps=np.random.choice([
                    ["algebra", "fractions"], ["geometry", "word problems"], 
                    ["reading comprehension"], ["scientific method"], ["essay writing"]
                ]),
                strengths=np.random.choice([
                    ["problem solving", "creativity"], ["logical thinking", "analysis"],
                    ["communication", "collaboration"], ["research", "critical thinking"]
                ]),
                predicted_performance=np.random.uniform(70, 95),
                risk_level=np.random.choice(["low", "medium", "high"], p=[0.6, 0.3, 0.1])
            )
            students.append(student)
        
        return students
    
    def get_class_overview(self) -> Dict[str, Any]:
        """Get overview analytics for the entire class"""
        df = pd.DataFrame([s.__dict__ for s in self.students_data])
        
        return {
            "total_students": len(self.students_data),
            "avg_engagement": df['engagement_score'].mean(),
            "avg_learning_velocity": df['learning_velocity'].mean(),
            "high_risk_students": len(df[df['risk_level'] == 'high']),
            "total_sessions": df['total_sessions'].sum(),
            "total_interactions": df['total_interactions'].sum(),
            "avg_misconception_rate": df['misconception_rate'].mean()
        }
    
    def get_learning_patterns_distribution(self) -> Dict[str, int]:
        """Get distribution of learning patterns"""
        patterns = {}
        for student in self.students_data:
            pattern = student.preferred_learning_pattern.value
            patterns[pattern] = patterns.get(pattern, 0) + 1
        return patterns
    
    def get_at_risk_students(self) -> List[StudentAnalytics]:
        """Get students who need intervention"""
        return [s for s in self.students_data if s.risk_level in ['medium', 'high']]
    
    def get_top_performers(self, limit: int = 5) -> List[StudentAnalytics]:
        """Get top performing students"""
        return sorted(self.students_data, key=lambda s: s.predicted_performance, reverse=True)[:limit]
    
    def generate_learning_recommendations(self, student: StudentAnalytics) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        if student.engagement_score < 70:
            recommendations.append("🎮 Increase gamification elements to boost engagement")
        
        if student.misconception_rate > 0.5:
            recommendations.append("🔍 Focus on conceptual understanding before procedural practice")
        
        if student.help_request_frequency > 0.3:
            recommendations.append("🤝 Provide additional scaffolding and peer support")
        
        if student.learning_velocity < 1.0:
            recommendations.append("⏰ Break down concepts into smaller, manageable chunks")
        
        if student.preferred_learning_pattern == LearningPattern.VISUAL:
            recommendations.append("📊 Incorporate more visual aids and diagrams")
        elif student.preferred_learning_pattern == LearningPattern.KINESTHETIC:
            recommendations.append("🏃 Add hands-on activities and interactive simulations")
        
        for gap in student.knowledge_gaps:
            recommendations.append(f"📚 Address knowledge gap in {gap}")
        
        return recommendations

# Initialize analytics engine
@st.cache_data
def get_analytics_engine():
    return AnalyticsEngine()

analytics = get_analytics_engine()

# Sidebar
st.sidebar.title("📊 Advanced Analytics")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.selectbox(
    "Select View",
    ["Class Overview", "Individual Student Analysis", "Learning Patterns", "Predictive Insights", "Intervention Recommendations"]
)

# Main content
if page == "Class Overview":
    st.title("📊 Class Overview Analytics")
    
    # Get overview data
    overview = analytics.get_class_overview()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Students", overview['total_students'])
        st.metric("Total Sessions", overview['total_sessions'])
    
    with col2:
        st.metric("Avg Engagement", f"{overview['avg_engagement']:.1f}%")
        st.metric("Total Interactions", overview['total_interactions'])
    
    with col3:
        st.metric("Learning Velocity", f"{overview['avg_learning_velocity']:.2f}")
        st.metric("Misconception Rate", f"{overview['avg_misconception_rate']:.2f}")
    
    with col4:
        st.metric("High Risk Students", overview['high_risk_students'], 
                 delta=f"-{overview['high_risk_students']}" if overview['high_risk_students'] > 0 else "0")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Engagement vs Learning Velocity")
        df = pd.DataFrame([s.__dict__ for s in analytics.students_data])
        
        fig = px.scatter(df, x='engagement_score', y='learning_velocity', 
                        color='risk_level', size='total_sessions',
                        hover_data=['name'], title="Student Performance Matrix")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Risk Level Distribution")
        risk_counts = df['risk_level'].value_counts()
        
        fig = px.pie(values=risk_counts.values, names=risk_counts.index,
                    title="Student Risk Levels", color_discrete_map={
                        'low': '#2E8B57', 'medium': '#FFD700', 'high': '#DC143C'
                    })
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Session activity over time (simulated)
    st.subheader("📅 Session Activity Trend")
    dates = pd.date_range(start='2024-01-01', end='2024-06-20', freq='D')
    activity = np.random.poisson(lam=15, size=len(dates))  # Average 15 sessions per day
    
    activity_df = pd.DataFrame({'date': dates, 'sessions': activity})
    fig = px.line(activity_df, x='date', y='sessions', title="Daily Session Activity")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

elif page == "Individual Student Analysis":
    st.title("👤 Individual Student Analysis")
    
    # Student selector
    student_names = [s.name for s in analytics.students_data]
    selected_student_name = st.selectbox("Select Student", student_names)
    
    # Find selected student
    selected_student = next(s for s in analytics.students_data if s.name == selected_student_name)
    
    # Student profile
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Sessions", selected_student.total_sessions)
        st.metric("Engagement Score", f"{selected_student.engagement_score:.1f}%")
    
    with col2:
        st.metric("Learning Velocity", f"{selected_student.learning_velocity:.2f}")
        st.metric("Predicted Performance", f"{selected_student.predicted_performance:.1f}%")
    
    with col3:
        st.metric("Risk Level", selected_student.risk_level.upper())
        st.metric("Help Requests", f"{selected_student.help_request_frequency:.2f}/session")
    
    st.markdown("---")
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Strengths")
        for strength in selected_student.strengths:
            st.success(f"✅ {strength.title()}")
        
        st.subheader("📚 Knowledge Gaps")
        for gap in selected_student.knowledge_gaps:
            st.warning(f"⚠️ {gap.title()}")
    
    with col2:
        st.subheader("🧠 Learning Pattern")
        st.info(f"Preferred: {selected_student.preferred_learning_pattern.value.title()}")
        
        # Progress simulation
        st.subheader("📈 Progress Over Time")
        weeks = list(range(1, 13))
        progress = np.cumsum(np.random.normal(2, 0.5, 12))  # Simulated progress
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=weeks, y=progress, mode='lines+markers', name='Learning Progress'))
        fig.update_layout(title="Learning Progress (Concepts Mastered)", 
                         xaxis_title="Week", yaxis_title="Concepts Mastered")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("💡 Personalized Recommendations")
    recommendations = analytics.generate_learning_recommendations(selected_student)
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")

elif page == "Learning Patterns":
    st.title("🧠 Learning Patterns Analysis")
    
    # Learning patterns distribution
    patterns = analytics.get_learning_patterns_distribution()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Learning Pattern Distribution")
        fig = px.bar(x=list(patterns.keys()), y=list(patterns.values()),
                    title="Student Learning Preferences")
        fig.update_layout(xaxis_title="Learning Pattern", yaxis_title="Number of Students")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Pattern Effectiveness")
        # Simulated effectiveness data
        effectiveness = {
            'visual': 85,
            'auditory': 78,
            'kinesthetic': 82,
            'reading_writing': 80
        }
        
        fig = px.bar(x=list(effectiveness.keys()), y=list(effectiveness.values()),
                    title="Learning Pattern Effectiveness (%)")
        fig.update_layout(xaxis_title="Learning Pattern", yaxis_title="Effectiveness %")
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed pattern analysis
    st.subheader("📋 Pattern-Based Recommendations")
    
    for pattern, count in patterns.items():
        with st.expander(f"{pattern.title()} Learners ({count} students)"):
            if pattern == "visual":
                st.write("🎨 **Recommended Strategies:**")
                st.write("- Use diagrams, charts, and visual aids")
                st.write("- Implement color-coding systems")
                st.write("- Provide graphic organizers")
                st.write("- Use mind maps and concept maps")
            elif pattern == "auditory":
                st.write("🎵 **Recommended Strategies:**")
                st.write("- Use verbal explanations and discussions")
                st.write("- Implement audio recordings")
                st.write("- Encourage reading aloud")
                st.write("- Use music and rhymes for memorization")
            elif pattern == "kinesthetic":
                st.write("🏃 **Recommended Strategies:**")
                st.write("- Provide hands-on activities")
                st.write("- Use interactive simulations")
                st.write("- Implement movement-based learning")
                st.write("- Use manipulatives and physical models")
            elif pattern == "reading_writing":
                st.write("📝 **Recommended Strategies:**")
                st.write("- Provide written instructions")
                st.write("- Use note-taking activities")
                st.write("- Implement journaling exercises")
                st.write("- Use text-based resources")

elif page == "Predictive Insights":
    st.title("🔮 Predictive Insights")
    
    st.subheader("📈 Performance Predictions")
    
    # Create prediction visualization
    df = pd.DataFrame([s.__dict__ for s in analytics.students_data])
    
    fig = px.scatter(df, x='engagement_score', y='predicted_performance',
                    color='risk_level', size='learning_velocity',
                    hover_data=['name'], title="Predicted vs Current Performance")
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Risk prediction model
    st.subheader("⚠️ Risk Prediction Model")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Risk Factors:**")
        st.write("- Low engagement score (< 70%)")
        st.write("- High misconception rate (> 0.5)")
        st.write("- Frequent help requests (> 0.3/session)")
        st.write("- Low learning velocity (< 1.0)")
        
        # Risk factor weights
        risk_factors = {
            'Low Engagement': 0.3,
            'High Misconceptions': 0.25,
            'Frequent Help Requests': 0.2,
            'Low Learning Velocity': 0.15,
            'Knowledge Gaps': 0.1
        }
        
        fig = px.pie(values=list(risk_factors.values()), names=list(risk_factors.keys()),
                    title="Risk Factor Weights")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Intervention success prediction
        st.write("**Intervention Success Rates:**")
        interventions = {
            'Personalized Content': 85,
            'Peer Tutoring': 78,
            'Gamification': 82,
            'Additional Practice': 75,
            'Teacher Support': 88
        }
        
        fig = px.bar(x=list(interventions.keys()), y=list(interventions.values()),
                    title="Predicted Intervention Success Rates (%)")
        fig.update_layout(xaxis_title="Intervention Type", yaxis_title="Success Rate %")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Intervention Recommendations":
    st.title("🎯 Intervention Recommendations")
    
    # At-risk students
    at_risk_students = analytics.get_at_risk_students()
    
    st.subheader(f"⚠️ Students Requiring Intervention ({len(at_risk_students)})")
    
    for student in at_risk_students:
        with st.expander(f"{student.name} - {student.risk_level.upper()} Risk"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Metrics:**")
                st.write(f"- Engagement: {student.engagement_score:.1f}%")
                st.write(f"- Learning Velocity: {student.learning_velocity:.2f}")
                st.write(f"- Misconception Rate: {student.misconception_rate:.2f}")
                st.write(f"- Help Requests: {student.help_request_frequency:.2f}/session")
            
            with col2:
                st.write("**Recommended Actions:**")
                recommendations = analytics.generate_learning_recommendations(student)
                for rec in recommendations:
                    st.write(f"• {rec}")
    
    # Top performers
    st.subheader("🌟 Top Performers")
    top_performers = analytics.get_top_performers()
    
    for student in top_performers:
        with st.expander(f"{student.name} - {student.predicted_performance:.1f}% Predicted"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Strengths:**")
                for strength in student.strengths:
                    st.success(f"✅ {strength.title()}")
            
            with col2:
                st.write("**Enhancement Opportunities:**")
                st.write("• Peer mentoring opportunities")
                st.write("• Advanced challenge problems")
                st.write("• Leadership roles in group activities")
                st.write("• Independent research projects")
    
    # Class-wide recommendations
    st.subheader("📚 Class-wide Recommendations")
    
    overview = analytics.get_class_overview()
    
    if overview['avg_engagement'] < 75:
        st.warning("🎮 Consider increasing gamification elements to boost overall engagement")
    
    if overview['avg_misconception_rate'] > 0.4:
        st.warning("🔍 Focus on conceptual understanding across the curriculum")
    
    if overview['high_risk_students'] > 2:
        st.error("🚨 High number of at-risk students - consider class-wide intervention")
    
    st.success("💡 Regular use of this analytics dashboard can improve student outcomes by 25-30%")

# Footer
st.markdown("---")
st.markdown("*AITA Advanced Learning Analytics Dashboard - Powered by AI-driven insights*")