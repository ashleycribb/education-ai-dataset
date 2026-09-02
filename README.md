# xAPI Profile for AI in Education

## Live Dashboard

**[Click here to see a live, interactive dashboard that demonstrates the power of this xAPI Profile.](./docs/index.md)**

This dashboard visualizes a sample dataset of AI-learner interactions, providing both quantitative and qualitative analysis of the data captured by our profile.

## The Vision: Extending xAPI for the Age of AI

This project defines a foundational **xAPI Profile** designed to capture the unique interactions that occur in AI-powered learning environments. Our goal is to extend the power and interoperability of the Experience API (xAPI) to create a common language for AI agents, small learning models (SLMs), and AI-powered teacher's assistants.

By building on the proven foundation of xAPI, we can ensure that data from these next-generation educational tools is interoperable, secure, and part of the wider learning ecosystem.

## The Problem: A Missing Vocabulary for AI Interactions

The existing xAPI standard is excellent for capturing a wide range of learning experiences. However, as AI tutors and agents become more common, we need a specialized vocabulary to describe the new types of interactions they enable, such as:

*   An AI agent personalizing a learning path for a student.
*   A small learning model generating a new assessment question.
*   A teacher's assistant AI summarizing a student's progress.

Without a common data model for these events, data from AI educational tools will become siloed, making it difficult to analyze the effectiveness of these new technologies and integrate them with existing systems like Learning Record Stores (LRS).

## The Solution: A Foundational xAPI Profile

This project provides a formal xAPI Profile that defines the specific `Verbs`, `Activity Types`, and statement templates needed to track AI-driven learning experiences. By providing this shared vocabulary, we can enable a future where:

*   Data from an AI tutor can be seamlessly stored in any conformant LRS.
*   Learning analytics platforms can compare the effectiveness of different AI agents.
*   Small learning models can be trained on standardized, high-quality datasets of AI-student interactions.

This profile will serve as a foundational layer, which can be further extended by the community to meet the needs of specific AI applications.

## Use Case: Analyzing AI Teacher's Assistants

To demonstrate the power of this profile, we have defined a specific vocabulary for the "AI Teacher's Assistant" use case. This extension allows for the detailed capture of interactions where an AI provides direct help to a learner.

By using the specialized `Verbs` (e.g., `provided-hint`, `gave-feedback`) and `Context Extensions` defined in this profile, researchers and educators can perform both quantitative and qualitative analysis on the effectiveness of AI assistants. For example, one could analyze not just *how often* an AI provides hints, but also the *exact content* of those hints and the learner prompts that triggered them.

### Teacher in the Loop: Improving AI with Human Expertise

A crucial aspect of responsible AI in education is ensuring that human educators can guide and improve AI agents. This profile includes a "Teacher in the Loop" vocabulary to facilitate this feedback cycle. When an AI's interaction with a student is recorded, a teacher can then review that specific interaction and record their own feedback as a new xAPI statement.

This allows the AI agent to learn from expert feedback, creating a powerful mechanism for continuous improvement and ensuring that the AI's behavior aligns with sound pedagogical practices.

## Implementation Guidance: The AI-Enhanced LRS

To fully leverage the analytical power of this xAPI Profile, we have designed a conceptual database model for an "AI-Enhanced" Learning Record Store (LRS). This model proposes a hybrid architecture that combines a traditional document database (for structured xAPI data) with a vector database (for semantic analysis of qualitative feedback).

**[Click here to view the Conceptual Database Model](./DATABASE_MODEL.md)**

This document serves as a guide for developers and organizations looking to build a next-generation LRS that is truly "AI-ready."

## Proof-of-Concept Tool

To help make the conceptual database model easier to understand, we have created a simple, runnable tool that simulates the data ingestion process. This tool is designed for a non-technical audience and provides a clear, step-by-step demonstration of how data flows into our proposed AI-Enhanced LRS.

**[Click here to learn about and run the Proof-of-Concept Tool](./poc-tool/README.md)**

### Communication Model

For advanced implementations, we also propose a conceptual communication model that includes a high-performance, model-centric interface for trusted communication between AI agents and the LRS, in addition to the standard xAPI REST interface.

**[Click here to view the Conceptual Communication Model](./COMMUNICATION_MODEL.md)**

## Guiding Principles

*   **xAPI Alignment:** We will adhere to the principles and data structures of the xAPI specification to ensure maximum interoperability.
*   **Focus on AI:** This profile is specifically focused on defining the data models for interactions that are unique to AI-powered educational tools.
*   **Privacy and Security First:** We will leverage the robust security and privacy features of the xAPI standard and the LRS specification.
*   **Open and Collaborative:** This is an open-source project, and we welcome contributions from educators, developers, and researchers.

## Get Involved

This project is in its early stages, and we are actively seeking collaborators. Whether you are an educator with deep domain expertise, a developer with experience in AI and xAPI, or a researcher with a passion for the future of education, we invite you to join us in extending xAPI for the age of AI.
# Education AI Dataset & AITA System

An AI-powered educational platform featuring the AITA (AI Teaching Assistant) system with comprehensive data processing, model fine-tuning, and interactive dashboards for K-12 education.

## 🚀 Features

- **AITA Interaction Service**: FastAPI-based service for AI teaching assistant interactions
- **Teacher Dashboard**: Streamlit-based dashboard for monitoring student progress and misconceptions
- **Student Frontend**: Interactive interface for students to engage with AITA
- **Data Processing Pipeline**: Tools for extracting and processing educational content from various sources
- **Model Fine-tuning**: Support for fine-tuning language models for educational contexts
- **MCP Integration**: Model Context Protocol client/server SDKs for educational tools
- **xAPI Logging**: Comprehensive learning analytics and experience tracking

## 📋 Prerequisites

- Python 3.9+
- CUDA-compatible GPU (optional, for model training/inference)
- Docker (optional, for containerized deployment)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ashleycribb/education-ai-dataset.git
   cd education-ai-dataset
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Model Context Protocol (if available):**
   ```bash
   # Note: MCP may need to be installed from a specific source
   # pip install modelcontextprotocol
   ```

## 🚀 Quick Start

### 🎉 NEW: Unified Feature Launcher

**Start all services with one command:**
```bash
# Command line mode - starts all services
python feature_launcher.py start

# GUI mode - interactive service management
streamlit run feature_launcher.py
```

### Running Individual Services

#### Core Services
```bash
# Main AITA Backend
python aita_interaction_service.py          # Port 8000

# API Integration Hub (NEW!)
python api_integration_hub.py               # Port 8001

# Real-time Notifications (NEW!)
python realtime_notifications.py            # Port 8002

# Quiz Generator (NEW!)
python quiz_generator.py                    # Port 8003
```

#### Dashboards and Interfaces
```bash
# Teacher Dashboard
streamlit run teacher_dashboard_main.py     # Port 12000

# Student Frontend
streamlit run student_frontend_streamlit.py # Port 12001

# Advanced Analytics (NEW!)
streamlit run advanced_analytics.py         # Port 12002

# Gamification Dashboard (NEW!)
streamlit run gamification_system.py        # Port 12003
```

### Using Docker

```bash
docker build -t education-ai .
docker run -p 8000:8000 education-ai
```

## 🎯 New Features (2024)

### 🔌 API Integration Hub
- **RESTful API endpoints** for LMS integration
- **LTI (Learning Tools Interoperability)** support
- **Webhook system** for real-time integrations
- **Student/session management** APIs
- **Analytics and reporting** endpoints

### 🔔 Real-time Notification System
- **WebSocket-based notifications** for teachers
- **Instant alerts** for help requests and misconceptions
- **Priority-based alert system** (low, medium, high, urgent)
- **Notification history** and analytics
- **Teacher subscription management**

### 📊 Advanced Learning Analytics
- **Enhanced analytics dashboard** with interactive visualizations
- **Learning pattern identification** (visual, auditory, kinesthetic, reading/writing)
- **Predictive insights** for student intervention
- **Risk assessment** and early warning system
- **Personalized recommendations** for students and teachers

### 🧪 Interactive Quiz/Assessment Generator
- **AI-powered quiz generation** based on conversation content
- **Multiple question types** (multiple choice, true/false, short answer, fill-in-blank)
- **Automatic grading system** with detailed feedback
- **Difficulty level adjustment** (easy, medium, hard)
- **Performance analytics** and progress tracking

### 🏆 Student Progress Gamification
- **Comprehensive badge system** with 5 rarity levels
- **Experience points and leveling** system
- **Leaderboards** and friendly competition
- **Achievement analytics** and progress tracking
- **Engagement motivation** tools

📖 **Detailed Guide**: See [NEW_FEATURES_GUIDE.md](NEW_FEATURES_GUIDE.md) for complete documentation

## 📁 Project Structure

```
education-ai-dataset/
├── aita_interaction_service.py    # Main FastAPI service
├── teacher_dashboard_main.py      # Teacher dashboard entry point
├── student_frontend_streamlit.py  # Student interface
├── model_loader_utils.py         # Model loading utilities
├── moderation_service.py          # Content moderation
├── dashboard_data_manager.py      # Data management for dashboards
├── k12_mcp_client_sdk/           # MCP client SDK
├── k12_mcp_server_sdk/           # MCP server SDK
├──
├── # NEW FEATURES (2024)
├── feature_launcher.py           # Unified service launcher
├── api_integration_hub.py        # API Integration Hub
├── realtime_notifications.py     # Real-time notification system
├── advanced_analytics.py         # Enhanced analytics dashboard
├── quiz_generator.py             # AI-powered quiz generator
├── gamification_system.py        # Student progress gamification
├── NEW_FEATURES_GUIDE.md         # Comprehensive feature documentation
├── pages/                        # Dashboard pages
├── source_data/                  # Raw data sources
├── data_processing_scripts.py    # Data processing utilities
├── fine_tune_aita.py            # Model fine-tuning
└── extract_*.py                 # Data extraction scripts
```

## 🔧 Configuration

### Model Configuration

The system supports various model configurations through adapter loading. Configure models in the `ADAPTER_CONFIG` section of `aita_interaction_service.py`.

### Data Sources

- **Project Gutenberg**: Classic literature extraction
- **OpenStax**: Educational content extraction
- **Custom datasets**: Support for custom educational datasets

## 📊 Dashboard Features

### Teacher Dashboard
- **Overview Dashboard**: Student engagement metrics and session summaries
- **Session Transcript View**: Detailed conversation analysis
- **Misconception Analysis**: Identification and tracking of student misconceptions
- **Learning Objective Progress**: Student progress tracking

### Analytics
- xAPI statement logging for comprehensive learning analytics
- Session-based interaction tracking
- Misconception pattern analysis

## 🤖 Model Fine-tuning

Fine-tune AITA models for specific educational contexts:

```bash
python fine_tune_aita.py
```

Supports:
- LoRA (Low-Rank Adaptation) fine-tuning
- Custom educational datasets
- Supervised fine-tuning with TRL

## 🔌 MCP Integration

The system includes SDKs for Model Context Protocol integration:

- **Client SDK**: For connecting to MCP servers
- **Server SDK**: For creating MCP-compatible educational tools
- **xAPI Integration**: Automatic learning analytics generation

## 🛡️ Content Moderation

Built-in content moderation using transformer-based models to ensure safe educational interactions.

## 📝 Data Processing

Extract and process educational content from various sources:

- **Gutenberg Stories**: `python extract_gutenberg_stories.py`
- **OpenStax Content**: `python extract_openstax_ecology.py`
- **Data Preprocessing**: `python preprocess_extracted_data.py`

## 🧪 Testing

Run syntax checks:
```bash
python -m py_compile *.py
```

## 🚨 Known Issues & Fixes Applied

- ✅ Fixed syntax errors in `aita_mcp_client.py` and `dashboard_data_manager.py`
- ⚠️ MCP dependencies may need manual installation
- ⚠️ Model adapters and weights need to be provided separately

## 📚 Documentation

Detailed documentation is available in the repository:
- `AITAClientGuide.md` - Client usage guide
- `AuthoringToolGuide.md` - Content authoring guide
- `DashboardGuide.md` - Dashboard usage guide
- `SDK_UsageGuide.md` - SDK documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and syntax checks
5. Submit a pull request

## 📄 License

See `LICENSE` file for details.

## 🆘 Support

For issues and questions, please check the documentation files or create an issue in the repository.
