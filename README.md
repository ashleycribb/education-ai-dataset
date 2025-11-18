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

### 🔌 Canvas LMS Integration (NEW!)
- **Model Context Protocol (MCP) Server** for seamless Canvas integration
- **Assignment Analysis** with AI-powered difficulty assessment and time estimation
- **NC Standards Alignment** automatic detection and mapping
- **Real-time Submission Tracking** and progress monitoring
- **FERPA-Compliant Data Handling** with secure API authentication
- **Multi-format Content Support** (HTML, Markdown, Plain Text)

📋 **Canvas Integration**: See [CANVAS_MCP_INTEGRATION.md](CANVAS_MCP_INTEGRATION.md) for setup and usage

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
├── 
├── # CANVAS LMS INTEGRATION
├── canvas_mcp_server.ts          # Canvas MCP server implementation
├── CANVAS_MCP_INTEGRATION.md     # Canvas integration documentation
├── package.json                  # Node.js dependencies for Canvas MCP
├── tsconfig.json                 # TypeScript configuration
├── .env.example                  # Environment configuration template
├── 
├── # NORTH CAROLINA INTEGRATION
├── NC_INTEGRATION_ANALYSIS.md    # NC standards integration analysis
├── NC_IMPLEMENTATION_GUIDE.md    # NC district implementation guide
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
