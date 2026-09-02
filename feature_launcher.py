#!/usr/bin/env python3
"""
AITA Feature Launcher
Unified launcher for all new features and services
"""

import subprocess
import sys
import time
import threading
import signal
import os
from typing import List, Dict, Any
import streamlit as st

class ServiceManager:
    def __init__(self):
        self.services = {
            "api_hub": {
                "name": "API Integration Hub",
                "script": "api_integration_hub.py",
                "port": 8001,
                "description": "RESTful API endpoints for LMS integration and external tools",
                "process": None
            },
            "notifications": {
                "name": "Real-time Notifications",
                "script": "realtime_notifications.py",
                "port": 8002,
                "description": "WebSocket-based notifications for teachers",
                "process": None
            },
            "quiz_generator": {
                "name": "Quiz Generator",
                "script": "quiz_generator.py",
                "port": 8003,
                "description": "AI-powered quiz generation and assessment",
                "process": None
            },
            "main_service": {
                "name": "AITA Main Service",
                "script": "aita_interaction_service.py",
                "port": 8000,
                "description": "Core AITA teaching assistant service",
                "process": None
            }
        }

        self.streamlit_apps = {
            "teacher_dashboard": {
                "name": "Teacher Dashboard",
                "script": "teacher_dashboard_main.py",
                "port": 12000,
                "description": "Main teacher dashboard with student monitoring",
                "process": None
            },
            "student_frontend": {
                "name": "Student Frontend",
                "script": "student_frontend_streamlit.py",
                "port": 12001,
                "description": "Student interface for AITA interactions",
                "process": None
            },
            "advanced_analytics": {
                "name": "Advanced Analytics",
                "script": "advanced_analytics.py",
                "port": 12002,
                "description": "Enhanced learning analytics and insights",
                "process": None
            },
            "gamification": {
                "name": "Gamification Dashboard",
                "script": "gamification_system.py",
                "port": 12003,
                "description": "Student progress gamification and achievements",
                "process": None
            }
        }

        self.running_services = []

    def start_service(self, service_id: str, service_type: str = "api"):
        """Start a specific service"""
        if service_type == "api":
            service = self.services.get(service_id)
        else:
            service = self.streamlit_apps.get(service_id)

        if not service:
            print(f"❌ Service {service_id} not found")
            return False

        try:
            if service_type == "api":
                cmd = [sys.executable, service["script"]]
            else:
                cmd = [
                    sys.executable, "-m", "streamlit", "run",
                    service["script"],
                    "--server.port", str(service["port"]),
                    "--server.address", "0.0.0.0",
                    "--server.headless", "true"
                ]

            print(f"🚀 Starting {service['name']} on port {service['port']}...")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            service["process"] = process
            self.running_services.append((service_id, service_type))

            # Give service time to start
            time.sleep(2)

            if process.poll() is None:
                print(f"✅ {service['name']} started successfully")
                return True
            else:
                print(f"❌ {service['name']} failed to start")
                return False

        except Exception as e:
            print(f"❌ Error starting {service['name']}: {e}")
            return False

    def stop_service(self, service_id: str, service_type: str = "api"):
        """Stop a specific service"""
        if service_type == "api":
            service = self.services.get(service_id)
        else:
            service = self.streamlit_apps.get(service_id)

        if service and service["process"]:
            try:
                service["process"].terminate()
                service["process"].wait(timeout=5)
                print(f"🛑 {service['name']} stopped")
                if (service_id, service_type) in self.running_services:
                    self.running_services.remove((service_id, service_type))
            except subprocess.TimeoutExpired:
                service["process"].kill()
                print(f"🔪 {service['name']} force killed")
            except Exception as e:
                print(f"❌ Error stopping {service['name']}: {e}")

    def stop_all_services(self):
        """Stop all running services"""
        print("🛑 Stopping all services...")

        for service_id, service_type in self.running_services.copy():
            self.stop_service(service_id, service_type)

        print("✅ All services stopped")

    def get_service_status(self):
        """Get status of all services"""
        status = {"api_services": {}, "streamlit_apps": {}}

        for service_id, service in self.services.items():
            is_running = service["process"] and service["process"].poll() is None
            status["api_services"][service_id] = {
                "name": service["name"],
                "port": service["port"],
                "running": is_running,
                "url": f"http://localhost:{service['port']}" if is_running else None
            }

        for app_id, app in self.streamlit_apps.items():
            is_running = app["process"] and app["process"].poll() is None
            status["streamlit_apps"][app_id] = {
                "name": app["name"],
                "port": app["port"],
                "running": is_running,
                "url": f"http://localhost:{app['port']}" if is_running else None
            }

        return status

def create_launcher_interface():
    """Create Streamlit interface for service management"""
    st.set_page_config(
        page_title="AITA Feature Launcher",
        page_icon="🚀",
        layout="wide"
    )

    st.title("🚀 AITA Feature Launcher")
    st.markdown("Unified control panel for all AITA services and features")

    # Initialize service manager in session state
    if 'service_manager' not in st.session_state:
        st.session_state.service_manager = ServiceManager()

    manager = st.session_state.service_manager

    # Get current status
    status = manager.get_service_status()

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🚀 Start All Services"):
            with st.spinner("Starting all services..."):
                # Start API services
                for service_id in manager.services.keys():
                    manager.start_service(service_id, "api")
                    time.sleep(1)

                # Start Streamlit apps
                for app_id in manager.streamlit_apps.keys():
                    manager.start_service(app_id, "streamlit")
                    time.sleep(1)

                st.success("All services started!")
                st.experimental_rerun()

    with col2:
        if st.button("🛑 Stop All Services"):
            manager.stop_all_services()
            st.success("All services stopped!")
            st.experimental_rerun()

    with col3:
        if st.button("🔄 Refresh Status"):
            st.experimental_rerun()

    st.markdown("---")

    # API Services Section
    st.subheader("🔌 API Services")

    for service_id, service_info in status["api_services"].items():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            status_icon = "🟢" if service_info["running"] else "🔴"
            st.write(f"{status_icon} **{service_info['name']}**")
            st.caption(manager.services[service_id]["description"])

        with col2:
            st.write(f"Port: {service_info['port']}")

        with col3:
            if service_info["running"]:
                st.success("Running")
                if service_info["url"]:
                    st.markdown(f"[Open API]({service_info['url']}/docs)")
            else:
                st.error("Stopped")

        with col4:
            if service_info["running"]:
                if st.button(f"Stop", key=f"stop_api_{service_id}"):
                    manager.stop_service(service_id, "api")
                    st.experimental_rerun()
            else:
                if st.button(f"Start", key=f"start_api_{service_id}"):
                    manager.start_service(service_id, "api")
                    st.experimental_rerun()

    st.markdown("---")

    # Streamlit Apps Section
    st.subheader("📊 Streamlit Applications")

    for app_id, app_info in status["streamlit_apps"].items():
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            status_icon = "🟢" if app_info["running"] else "🔴"
            st.write(f"{status_icon} **{app_info['name']}**")
            st.caption(manager.streamlit_apps[app_id]["description"])

        with col2:
            st.write(f"Port: {app_info['port']}")

        with col3:
            if app_info["running"]:
                st.success("Running")
                if app_info["url"]:
                    st.markdown(f"[Open App]({app_info['url']})")
            else:
                st.error("Stopped")

        with col4:
            if app_info["running"]:
                if st.button(f"Stop", key=f"stop_app_{app_id}"):
                    manager.stop_service(app_id, "streamlit")
                    st.experimental_rerun()
            else:
                if st.button(f"Start", key=f"start_app_{app_id}"):
                    manager.start_service(app_id, "streamlit")
                    st.experimental_rerun()

    st.markdown("---")

    # Feature Overview
    st.subheader("🎯 Feature Overview")

    features = [
        {
            "name": "🔌 API Integration Hub",
            "description": "Standardized API endpoints for LMS integration and external tool connectivity",
            "benefits": ["LTI support", "Webhook system", "Student/session management", "Analytics APIs"]
        },
        {
            "name": "🔔 Real-time Notifications",
            "description": "WebSocket-based notifications for teachers when students need help",
            "benefits": ["Instant alerts", "Help requests", "Misconception detection", "System notifications"]
        },
        {
            "name": "📊 Advanced Analytics",
            "description": "Enhanced learning analytics with visualizations and predictive insights",
            "benefits": ["Learning patterns", "Performance predictions", "Risk assessment", "Intervention recommendations"]
        },
        {
            "name": "🧪 Quiz Generator",
            "description": "AI-powered quiz generation based on conversation content",
            "benefits": ["Multiple question types", "Automatic grading", "Difficulty levels", "Performance analytics"]
        },
        {
            "name": "🏆 Gamification System",
            "description": "Achievement system with badges, progress tracking, and engagement metrics",
            "benefits": ["Badge system", "Leaderboards", "Progress tracking", "Engagement analytics"]
        }
    ]

    for feature in features:
        with st.expander(feature["name"]):
            st.write(feature["description"])
            st.write("**Key Benefits:**")
            for benefit in feature["benefits"]:
                st.write(f"• {benefit}")

    # System Information
    st.markdown("---")
    st.subheader("ℹ️ System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Running Services:**")
        running_count = sum(1 for info in status["api_services"].values() if info["running"])
        running_count += sum(1 for info in status["streamlit_apps"].values() if info["running"])
        total_count = len(status["api_services"]) + len(status["streamlit_apps"])
        st.write(f"{running_count}/{total_count} services active")

    with col2:
        st.write("**Port Usage:**")
        ports = []
        for info in status["api_services"].values():
            if info["running"]:
                ports.append(str(info["port"]))
        for info in status["streamlit_apps"].values():
            if info["running"]:
                ports.append(str(info["port"]))
        st.write(f"Ports in use: {', '.join(ports) if ports else 'None'}")

def main():
    """Main function for command line usage"""
    if len(sys.argv) > 1:
        # Command line mode
        manager = ServiceManager()

        def signal_handler(sig, frame):
            print("\n🛑 Shutting down...")
            manager.stop_all_services()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        command = sys.argv[1].lower()

        if command == "start":
            print("🚀 Starting all AITA services...")

            # Start API services
            for service_id in manager.services.keys():
                manager.start_service(service_id, "api")
                time.sleep(1)

            print("\n📊 Starting Streamlit applications...")
            print("Note: Streamlit apps will run in headless mode")
            print("Access them via the URLs shown below:")

            # Start Streamlit apps
            for app_id in manager.streamlit_apps.keys():
                manager.start_service(app_id, "streamlit")
                time.sleep(1)

            # Show status
            print("\n" + "="*60)
            print("🎉 AITA Feature Suite Started Successfully!")
            print("="*60)

            status = manager.get_service_status()

            print("\n🔌 API Services:")
            for service_id, info in status["api_services"].items():
                if info["running"]:
                    print(f"  ✅ {info['name']}: {info['url']}")
                    print(f"     📖 API Docs: {info['url']}/docs")

            print("\n📊 Streamlit Applications:")
            for app_id, info in status["streamlit_apps"].items():
                if info["running"]:
                    print(f"  ✅ {info['name']}: {info['url']}")

            print("\n💡 Tips:")
            print("  • Use the Teacher Dashboard for monitoring students")
            print("  • Try the Advanced Analytics for deeper insights")
            print("  • Check out the Gamification Dashboard for engagement")
            print("  • Use API endpoints for external integrations")
            print("  • Press Ctrl+C to stop all services")

            # Keep running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        elif command == "stop":
            manager.stop_all_services()

        elif command == "status":
            status = manager.get_service_status()
            print("📊 Service Status:")

            for service_id, info in status["api_services"].items():
                status_icon = "🟢" if info["running"] else "🔴"
                print(f"  {status_icon} {info['name']} (Port {info['port']})")

            for app_id, info in status["streamlit_apps"].items():
                status_icon = "🟢" if info["running"] else "🔴"
                print(f"  {status_icon} {info['name']} (Port {info['port']})")

        else:
            print("Usage: python feature_launcher.py [start|stop|status]")
            print("   or: streamlit run feature_launcher.py (for GUI)")

    else:
        # Streamlit mode
        create_launcher_interface()

if __name__ == "__main__":
    main()