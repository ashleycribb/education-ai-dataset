# AITA Canvas MCP Integration

## Overview

The AITA Canvas MCP (Model Context Protocol) Server provides seamless integration between the AITA AI Teaching Assistant platform and Canvas Learning Management System. This integration enables AITA to access Canvas assignments, analyze learning objectives, and provide personalized educational support aligned with North Carolina standards.

## 🚀 Features

### Core Canvas Integration
- **Course Management**: List and filter courses by enrollment status
- **Assignment Search**: Advanced search across all courses with date filtering
- **Assignment Details**: Comprehensive assignment information with HTML/Markdown conversion
- **Submission Tracking**: Monitor student submission status and progress

### AITA Educational Enhancements
- **Learning Analysis**: AI-powered difficulty assessment and time estimation
- **NC Standards Alignment**: Automatic detection of North Carolina educational standards
- **Prerequisite Identification**: Analysis of required skills and knowledge
- **Personalized Recommendations**: Tailored tutoring strategies based on assignment complexity
- **Support Resource Suggestions**: Context-aware learning material recommendations

### Advanced Capabilities
- **Multi-format Content**: Support for HTML, plain text, and Markdown formatting
- **Link Extraction**: Automatic identification of required materials and resources
- **Rubric Analysis**: Detailed grading criteria interpretation
- **Security Compliance**: FERPA-compliant data handling and privacy protection

## 📋 Prerequisites

### Required Dependencies
```bash
npm install @modelcontextprotocol/sdk zod node-fetch jsdom
npm install --save-dev @types/node typescript
```

### Environment Variables
```bash
# Canvas API Configuration
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_DOMAIN=your_institution.instructure.com

# Optional: AITA Configuration
AITA_API_ENDPOINT=https://api.aita.education
AITA_API_KEY=your_aita_api_key
```

### Canvas API Token Setup
1. Log into your Canvas instance
2. Go to Account → Settings → Approved Integrations
3. Click "+ New Access Token"
4. Set purpose: "AITA Educational Integration"
5. Set expiration date (recommended: 1 year)
6. Copy the generated token to `CANVAS_API_TOKEN`

## 🔧 Installation and Setup

### 1. TypeScript Compilation
```bash
# Compile TypeScript to JavaScript
npx tsc canvas_mcp_server.ts --target es2020 --module commonjs --outDir dist
```

### 2. MCP Server Configuration
Create `mcp_config.json`:
```json
{
  "mcpServers": {
    "aita-canvas": {
      "command": "node",
      "args": ["dist/canvas_mcp_server.js"],
      "env": {
        "CANVAS_API_TOKEN": "your_token_here",
        "CANVAS_DOMAIN": "your_domain.instructure.com"
      }
    }
  }
}
```

### 3. Integration with AITA Platform
```python
# Example Python integration
from aita_mcp_client import AITAMCPClient

# Initialize Canvas MCP client
canvas_client = AITAMCPClient("aita-canvas")

# Get student assignments
assignments = await canvas_client.call_tool(
    "search_assignments",
    {
        "dueBefore": "2024-12-31",
        "includeCompleted": False
    }
)

# Analyze assignment for learning support
analysis = await canvas_client.call_tool(
    "analyze_assignment_learning",
    {
        "courseId": "12345",
        "assignmentId": "67890"
    }
)
```

## 🛠️ Available Tools

### 1. `list_courses`
Lists all enrolled courses with filtering options.

**Parameters:**
- `state` (optional): Filter by 'active', 'completed', or 'all' (default: 'active')

**Example:**
```javascript
{
  "tool": "list_courses",
  "arguments": {
    "state": "active"
  }
}
```

### 2. `search_assignments`
Searches for assignments across courses with advanced filtering.

**Parameters:**
- `query` (optional): Search term for titles/descriptions
- `dueBefore` (optional): Date filter (YYYY-MM-DD)
- `dueAfter` (optional): Date filter (YYYY-MM-DD)
- `includeCompleted` (optional): Include completed courses (default: false)
- `courseId` (optional): Limit to specific course

**Example:**
```javascript
{
  "tool": "search_assignments",
  "arguments": {
    "query": "essay",
    "dueBefore": "2024-12-31",
    "includeCompleted": false
  }
}
```

### 3. `get_assignment`
Retrieves detailed assignment information with AITA analysis.

**Parameters:**
- `courseId`: Canvas course ID
- `assignmentId`: Canvas assignment ID
- `formatType` (optional): 'full', 'plain', or 'markdown' (default: 'markdown')
- `includeAITAAnalysis` (optional): Include learning analysis (default: true)

**Example:**
```javascript
{
  "tool": "get_assignment",
  "arguments": {
    "courseId": "12345",
    "assignmentId": "67890",
    "formatType": "markdown",
    "includeAITAAnalysis": true
  }
}
```

### 4. `get_student_submission`
Retrieves submission status and details for assignments.

**Parameters:**
- `courseId`: Canvas course ID
- `assignmentId`: Canvas assignment ID
- `studentId` (optional): Student ID (defaults to current user)

**Example:**
```javascript
{
  "tool": "get_student_submission",
  "arguments": {
    "courseId": "12345",
    "assignmentId": "67890"
  }
}
```

### 5. `analyze_assignment_learning` (AITA Enhanced)
Provides comprehensive learning analysis for assignments.

**Parameters:**
- `courseId`: Canvas course ID
- `assignmentId`: Canvas assignment ID

**Returns:**
- Difficulty assessment (easy/medium/hard)
- Estimated completion time
- NC standards alignment
- Prerequisite skills identification
- AITA tutoring recommendations
- Support resource suggestions

**Example:**
```javascript
{
  "tool": "analyze_assignment_learning",
  "arguments": {
    "courseId": "12345",
    "assignmentId": "67890"
  }
}
```

## 📊 AITA Learning Analysis Features

### Difficulty Assessment Algorithm
The system analyzes multiple factors to determine assignment difficulty:

```typescript
function analyzeAssignmentDifficulty(assignment: CanvasAssignment): 'easy' | 'medium' | 'hard' {
  let difficultyScore = 0;
  
  // Points possible factor (0-2 points)
  if (assignment.points_possible > 100) difficultyScore += 2;
  else if (assignment.points_possible > 50) difficultyScore += 1;
  
  // Word count factor (0-2 points)
  if (assignment.word_count && assignment.word_count > 1000) difficultyScore += 2;
  else if (assignment.word_count && assignment.word_count > 500) difficultyScore += 1;
  
  // Submission complexity (0-2 points)
  if (assignment.submission_types?.includes('external_tool')) difficultyScore += 2;
  else if (assignment.submission_types?.includes('online_upload')) difficultyScore += 1;
  
  // Additional complexity factors
  if (assignment.rubric && assignment.rubric.length > 5) difficultyScore += 2;
  if (assignment.peer_reviews) difficultyScore += 1;
  if (assignment.has_group_assignment) difficultyScore += 1;
  
  // Return difficulty level
  if (difficultyScore >= 5) return 'hard';
  if (difficultyScore >= 3) return 'medium';
  return 'easy';
}
```

### NC Standards Detection
Automatic alignment with North Carolina educational standards:

```typescript
function extractNCStandardsAlignment(assignment: CanvasAssignment): string[] {
  const content = `${assignment.name} ${htmlToPlainText(assignment.description)}`.toLowerCase();
  const standards: string[] = [];
  
  // Mathematics Standards
  if (content.includes('algebra') || content.includes('equation')) {
    standards.push('NC.M1.A-REI'); // Reasoning with Equations and Inequalities
  }
  if (content.includes('function') || content.includes('graph')) {
    standards.push('NC.M1.F-IF'); // Interpreting Functions
  }
  
  // ELA Standards
  if (content.includes('argument') || content.includes('persuasive')) {
    standards.push('NC.ELA.W.K-12.1'); // Argumentative Writing
  }
  if (content.includes('evidence') || content.includes('support')) {
    standards.push('NC.ELA.RL.K-12.1'); // Key Ideas and Details
  }
  
  // Science Standards
  if (content.includes('cell') || content.includes('organism')) {
    standards.push('NC.Bio.1.1'); // Structure and Function of Living Systems
  }
  
  return standards;
}
```

### Time Estimation Model
Intelligent estimation of assignment completion time:

```typescript
function estimateTimeRequired(assignment: CanvasAssignment): number {
  let baseTime = 30; // Base 30 minutes
  
  // Adjust based on points (proxy for complexity)
  baseTime += (assignment.points_possible / 10) * 5;
  
  // Adjust based on word count (50 words per minute writing speed)
  if (assignment.word_count) {
    baseTime += assignment.word_count / 50;
  }
  
  // Adjust based on submission complexity
  if (assignment.submission_types?.includes('online_upload')) baseTime += 15;
  if (assignment.submission_types?.includes('external_tool')) baseTime += 20;
  
  // Adjust for additional requirements
  if (assignment.rubric && assignment.rubric.length > 3) baseTime += 20;
  if (assignment.peer_reviews) baseTime += 30;
  if (assignment.has_group_assignment) baseTime += 45;
  
  return Math.round(baseTime);
}
```

## 🔒 Security and Privacy

### Data Protection Measures
- **Environment Variable Security**: Sensitive credentials stored in environment variables
- **API Token Encryption**: Canvas API tokens transmitted securely via HTTPS
- **Data Minimization**: Only necessary assignment data is accessed and processed
- **Session Management**: No persistent storage of student data
- **FERPA Compliance**: Adherence to educational privacy regulations

### Access Control
```typescript
// Example access control implementation
async function validateAccess(courseId: string, userId: string): Promise<boolean> {
  try {
    // Verify user enrollment in course
    const enrollment = await canvasApiRequest(
      `/courses/${courseId}/enrollments?user_id=${userId}`
    );
    return enrollment.length > 0;
  } catch (error) {
    console.error('Access validation failed:', error);
    return false;
  }
}
```

### Error Handling
```typescript
// Secure error handling that doesn't expose sensitive information
function handleSecureError(error: Error): string {
  // Log full error details for debugging (server-side only)
  console.error('Canvas API Error:', error);
  
  // Return sanitized error message to client
  if (error.message.includes('401')) {
    return 'Authentication failed. Please check your Canvas API token.';
  } else if (error.message.includes('403')) {
    return 'Access denied. You may not have permission to view this content.';
  } else if (error.message.includes('404')) {
    return 'The requested resource was not found.';
  } else {
    return 'An error occurred while processing your request.';
  }
}
```

## 🎯 Integration with AITA Platform

### Real-time Assignment Support
```python
# Example AITA integration for real-time help
class AITACanvasAssistant:
    def __init__(self, canvas_mcp_client):
        self.canvas = canvas_mcp_client
        
    async def provide_assignment_help(self, course_id: str, assignment_id: str, student_question: str):
        # Get assignment details and analysis
        assignment_data = await self.canvas.call_tool("get_assignment", {
            "courseId": course_id,
            "assignmentId": assignment_id,
            "includeAITAAnalysis": True
        })
        
        analysis = await self.canvas.call_tool("analyze_assignment_learning", {
            "courseId": course_id,
            "assignmentId": assignment_id
        })
        
        # Generate personalized response based on assignment context
        response = await self.generate_contextual_help(
            assignment_data, 
            analysis, 
            student_question
        )
        
        return response
```

### Progress Tracking Integration
```python
# Track student progress across Canvas assignments
class AITAProgressTracker:
    async def track_assignment_progress(self, student_id: str):
        # Get all current assignments
        assignments = await self.canvas.call_tool("search_assignments", {
            "dueAfter": datetime.now().strftime("%Y-%m-%d"),
            "includeCompleted": False
        })
        
        progress_data = []
        for assignment in assignments:
            # Get submission status
            submission = await self.canvas.call_tool("get_student_submission", {
                "courseId": assignment["courseId"],
                "assignmentId": assignment["id"],
                "studentId": student_id
            })
            
            # Analyze learning requirements
            learning_analysis = await self.canvas.call_tool("analyze_assignment_learning", {
                "courseId": assignment["courseId"],
                "assignmentId": assignment["id"]
            })
            
            progress_data.append({
                "assignment": assignment,
                "submission": submission,
                "analysis": learning_analysis,
                "aita_recommendations": self.generate_recommendations(learning_analysis)
            })
        
        return progress_data
```

## 📈 Performance Optimization

### Caching Strategy
```typescript
// Simple in-memory cache for frequently accessed data
class AssignmentCache {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private readonly TTL = 5 * 60 * 1000; // 5 minutes
  
  get(key: string): any | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.TTL) {
      return cached.data;
    }
    this.cache.delete(key);
    return null;
  }
  
  set(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }
}
```

### Batch Processing
```typescript
// Efficient batch processing for multiple assignments
async function batchAnalyzeAssignments(assignments: CanvasAssignment[]): Promise<AITAAssignmentAnalysis[]> {
  const analyses = await Promise.all(
    assignments.map(async (assignment) => {
      const difficulty = analyzeAssignmentDifficulty(assignment);
      const estimatedTime = estimateTimeRequired(assignment);
      const ncStandards = extractNCStandardsAlignment(assignment);
      
      return {
        assignment,
        difficulty_level: difficulty,
        estimated_time_minutes: estimatedTime,
        nc_standards_alignment: ncStandards,
        // ... other analysis data
      };
    })
  );
  
  return analyses;
}
```

## 🧪 Testing and Validation

### Unit Tests
```typescript
// Example test for difficulty analysis
describe('Assignment Difficulty Analysis', () => {
  test('should classify high-point assignment as hard', () => {
    const assignment: CanvasAssignment = {
      points_possible: 150,
      word_count: 1500,
      submission_types: ['external_tool'],
      rubric: [/* 6 criteria */],
      peer_reviews: true,
      // ... other properties
    };
    
    const difficulty = analyzeAssignmentDifficulty(assignment);
    expect(difficulty).toBe('hard');
  });
  
  test('should identify NC math standards', () => {
    const assignment: CanvasAssignment = {
      name: 'Solving Linear Equations',
      description: '<p>Solve algebraic equations using various methods</p>',
      // ... other properties
    };
    
    const standards = extractNCStandardsAlignment(assignment);
    expect(standards).toContain('NC.M1.A-REI');
  });
});
```

### Integration Tests
```typescript
// Test Canvas API integration
describe('Canvas API Integration', () => {
  test('should fetch course assignments', async () => {
    const assignments = await canvasApiRequest<CanvasAssignment[]>(
      '/courses/12345/assignments'
    );
    
    expect(assignments).toBeDefined();
    expect(Array.isArray(assignments)).toBe(true);
  });
  
  test('should handle API errors gracefully', async () => {
    try {
      await canvasApiRequest('/invalid/endpoint');
    } catch (error) {
      expect(error.message).toContain('Canvas API error');
    }
  });
});
```

## 📚 Troubleshooting

### Common Issues

#### 1. Authentication Errors
```
Error: Canvas API error: 401 - Invalid access token
```
**Solution:** Verify your Canvas API token is correct and hasn't expired.

#### 2. Permission Errors
```
Error: Canvas API error: 403 - Insufficient permissions
```
**Solution:** Ensure your Canvas account has appropriate permissions to access course data.

#### 3. Network Connectivity
```
Error: fetch failed
```
**Solution:** Check network connectivity and Canvas domain configuration.

#### 4. TypeScript Compilation Errors
```
Error: Cannot find module '@modelcontextprotocol/sdk'
```
**Solution:** Install required dependencies with `npm install`.

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=aita-canvas:*
```

### Health Check
```typescript
// Health check endpoint for monitoring
async function healthCheck(): Promise<{ status: string; details: any }> {
  try {
    const user = await canvasApiRequest<CanvasUser>('/users/self');
    return {
      status: 'healthy',
      details: {
        authenticated: true,
        user: user.name,
        domain: canvasDomain,
        timestamp: new Date().toISOString()
      }
    };
  } catch (error) {
    return {
      status: 'unhealthy',
      details: {
        error: error.message,
        timestamp: new Date().toISOString()
      }
    };
  }
}
```

## 🚀 Deployment

### Production Configuration
```bash
# Production environment variables
CANVAS_API_TOKEN=prod_token_here
CANVAS_DOMAIN=university.instructure.com
NODE_ENV=production
LOG_LEVEL=info

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379

# Optional: Database for analytics
DATABASE_URL=postgresql://user:pass@localhost/aita_canvas
```

### Docker Deployment
```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY dist/ ./dist/

EXPOSE 3000

CMD ["node", "dist/canvas_mcp_server.js"]
```

### Kubernetes Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aita-canvas-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: aita-canvas-mcp
  template:
    metadata:
      labels:
        app: aita-canvas-mcp
    spec:
      containers:
      - name: aita-canvas-mcp
        image: aita/canvas-mcp:latest
        env:
        - name: CANVAS_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: canvas-credentials
              key: api-token
        - name: CANVAS_DOMAIN
          value: "university.instructure.com"
        ports:
        - containerPort: 3000
```

## 📞 Support and Contributing

### Getting Help
- **Documentation**: [AITA Canvas Integration Docs](https://docs.aita.education/canvas)
- **Issues**: [GitHub Issues](https://github.com/aita-education/canvas-mcp/issues)
- **Community**: [AITA Discord](https://discord.gg/aita-education)
- **Email**: support@aita.education

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run tests: `npm test`
5. Commit changes: `git commit -m "Add new feature"`
6. Push to branch: `git push origin feature/new-feature`
7. Create a Pull Request

### Development Setup
```bash
# Clone repository
git clone https://github.com/aita-education/canvas-mcp.git
cd canvas-mcp

# Install dependencies
npm install

# Set up environment
cp .env.example .env
# Edit .env with your Canvas credentials

# Run in development mode
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

---

*This integration is part of the AITA Educational Platform and is designed to enhance learning outcomes through AI-powered personalized education while maintaining strict privacy and security standards.*