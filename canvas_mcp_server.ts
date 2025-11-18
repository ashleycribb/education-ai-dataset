import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fetch from "node-fetch";
import { JSDOM } from "jsdom";

// Create the MCP server
const server = new McpServer({
  name: "AITA-Canvas-Integration",
  version: "1.0.0",
  capabilities: {
    resources: {},
    tools: {},
  }
});

// Load credentials from environment variables
let canvasApiToken: string | null = process.env.CANVAS_API_TOKEN || null;
let canvasDomain: string | null = process.env.CANVAS_DOMAIN || null;

// Define interfaces for API responses
interface CanvasUser {
  id: number;
  name: string;
  email: string;
}

interface CanvasCourse {
  id: number;
  name: string;
  term?: {
    name: string;
  };
}

interface CanvasAssignment {
  id: number;
  name: string;
  description: string | null;
  due_at: string | null;
  points_possible: number;
  submission_types: string[];
  allowed_extensions: string[] | null;
  allowed_attempts: number | null;
  grading_type: string;
  lock_at: string | null;
  unlock_at: string | null;
  has_group_assignment: boolean;
  group_category_id: number | null;
  peer_reviews: boolean;
  word_count: number | null;
  external_tool_tag_attributes?: {
    url: string;
    new_tab: boolean;
  };
  rubric: Array<{
    id: string;
    points: number;
    description: string;
    long_description: string | null;
  }> | null;
  use_rubric_for_grading: boolean;
  published: boolean;
  only_visible_to_overrides: boolean;
  locked_for_user: boolean;
  lock_explanation: string | null;
  turnitin_enabled: boolean;
  vericite_enabled: boolean;
  submission_draft_status?: string;
  annotatable_attachment_id?: number;
  anonymize_students: boolean;
  require_lockdown_browser: boolean;
}

interface CanvasSubmission {
  id: number;
  user_id: number;
  assignment_id: number;
  submitted_at: string | null;
  score: number | null;
  grade: string | null;
  attempt: number;
  workflow_state: string;
  late: boolean;
  missing: boolean;
  excused: boolean;
  submission_type: string | null;
  body: string | null;
  url: string | null;
  attachments?: Array<{
    id: number;
    filename: string;
    url: string;
    content_type: string;
  }>;
}

// AITA-specific interfaces for enhanced functionality
interface AITALearningObjective {
  id: string;
  description: string;
  standard: string;
  grade_level: string;
  subject: string;
}

interface AITAAssignmentAnalysis {
  assignment: CanvasAssignment;
  difficulty_level: 'easy' | 'medium' | 'hard';
  estimated_time_minutes: number;
  learning_objectives: AITALearningObjective[];
  prerequisite_skills: string[];
  support_resources: string[];
  nc_standards_alignment: string[];
}

// Base URL for Canvas API
const getBaseUrl = () => {
  if (!canvasDomain) {
    throw new Error("Canvas domain not set. Please check CANVAS_DOMAIN environment variable.");
  }
  return `https://${canvasDomain}/api/v1`;
};

// Helper function for API requests with proper typing
async function canvasApiRequest<T>(path: string, method = 'GET', body?: any): Promise<T> {
  if (!canvasApiToken) {
    throw new Error("Canvas API token not set. Please check CANVAS_API_TOKEN environment variable.");
  }

  const url = `${getBaseUrl()}${path}`;
  const response = await fetch(url, {
    method,
    headers: {
      'Authorization': `Bearer ${canvasApiToken}`,
      'Content-Type': 'application/json',
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Canvas API error: ${response.status} - ${error}`);
  }

  return response.json() as Promise<T>;
}

// Parse HTML to plain text with better handling of special characters
function htmlToPlainText(html: string | null): string {
  if (!html) return '';
  const dom = new JSDOM(html);
  // Preserve line breaks and spacing in text content
  return dom.window.document.body.textContent?.replace(/\$(\d+)/g, '\\$$$1') || '';
}

// Helper function for safer HTML to Markdown conversion
function convertHtmlToMarkdown(html: string): string {
  const dom = new JSDOM(html);
  const document = dom.window.document;
  
  // Helper to get text content while preserving $ signs
  const getTextContent = (element: Element): string => {
    return element.textContent?.replace(/\$(\d+)/g, '\\$$$1') || '';
  };

  // Process the HTML in a more structured way
  function processNode(node: Node): string {
    if (node.nodeType === node.TEXT_NODE) {
      return node.textContent?.replace(/\$(\d+)/g, '\\$$$1') || '';
    }

    if (node.nodeType !== node.ELEMENT_NODE) {
      return '';
    }

    const element = node as Element;
    let result = '';

    switch (element.tagName.toLowerCase()) {
      case 'h1':
        return `# ${getTextContent(element)}\n\n`;
      case 'h2':
        return `## ${getTextContent(element)}\n\n`;
      case 'h3':
        return `### ${getTextContent(element)}\n\n`;
      case 'strong':
      case 'b':
        return `**${getTextContent(element)}**`;
      case 'em':
      case 'i':
        return `*${getTextContent(element)}*`;
      case 'ul':
        return Array.from(element.children)
          .map(li => `- ${processNode(li)}`)
          .join('\n') + '\n\n';
      case 'ol':
        return Array.from(element.children)
          .map((li, index) => `${index + 1}. ${processNode(li)}`)
          .join('\n') + '\n\n';
      case 'li':
        return Array.from(element.childNodes)
          .map(child => processNode(child))
          .join('').trim();
      case 'p':
        return Array.from(element.childNodes)
          .map(child => processNode(child))
          .join('') + '\n\n';
      case 'br':
        return '\n';
      case 'a':
        const href = element.getAttribute('href');
        const text = getTextContent(element);
        return href ? `[${text}](${href})` : text;
      default:
        return Array.from(element.childNodes)
          .map(child => processNode(child))
          .join('');
    }
  }

  // Process the body content
  const result = Array.from(document.body.childNodes)
    .map(node => processNode(node))
    .join('')
    .trim();

  // Clean up any extra newlines
  return result.replace(/\n\n\n+/g, '\n\n');
}

// Helper function to extract links from HTML
function extractLinks(html: string | null): { text: string; href: string }[] {
  if (!html) return [];
  const dom = new JSDOM(html);
  const links = dom.window.document.querySelectorAll('a');
  return Array.from(links).map(link => ({
    text: link.textContent || '',
    href: link.getAttribute('href') || ''
  }));
}

// Helper function for date formatting and validation
function formatDate(dateStr: string | null, format: 'full' | 'date-only' = 'full'): string {
  if (!dateStr) return 'No date set';
  try {
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return 'Invalid date';
    
    if (format === 'date-only') {
      return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      });
    }
    
    return date.toLocaleString(undefined, {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short'
    });
  } catch (error) {
    return 'Invalid date';
  }
}

// Helper function to parse and validate date strings
function parseDate(dateStr: string | null): Date | null {
  if (!dateStr) return null;
  try {
    // If the date string is just YYYY-MM-DD, treat it as local timezone
    if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
      const [year, month, day] = dateStr.split('-').map(Number);
      const date = new Date(year, month - 1, day);
      return isNaN(date.getTime()) ? null : date;
    }
    // Otherwise parse as ISO string
    const date = new Date(dateStr);
    return isNaN(date.getTime()) ? null : date;
  } catch {
    return null;
  }
}

// Helper function to check if a date is within a range
function isDateInRange(date: string | null, before?: string, after?: string): boolean {
  if (!date) return true; // Include assignments with no due date
  
  const dueDate = parseDate(date);
  if (!dueDate) return true; // Include if date parsing fails
  
  if (before) {
    const beforeDate = parseDate(before);
    if (beforeDate) {
      // Set to end of day (23:59:59.999) in local timezone
      beforeDate.setHours(23, 59, 59, 999);
      if (dueDate.getTime() > beforeDate.getTime()) return false;
    }
  }
  
  if (after) {
    const afterDate = parseDate(after);
    if (afterDate) {
      // Set to start of day (00:00:00.000) in local timezone
      afterDate.setHours(0, 0, 0, 0);
      if (dueDate.getTime() < afterDate.getTime()) return false;
    }
  }
  
  return true;
}

// AITA-specific helper functions
function analyzeAssignmentDifficulty(assignment: CanvasAssignment): 'easy' | 'medium' | 'hard' {
  let difficultyScore = 0;
  
  // Points possible factor
  if (assignment.points_possible > 100) difficultyScore += 2;
  else if (assignment.points_possible > 50) difficultyScore += 1;
  
  // Word count factor
  if (assignment.word_count && assignment.word_count > 1000) difficultyScore += 2;
  else if (assignment.word_count && assignment.word_count > 500) difficultyScore += 1;
  
  // Submission type complexity
  if (assignment.submission_types?.includes('online_upload')) difficultyScore += 1;
  if (assignment.submission_types?.includes('external_tool')) difficultyScore += 2;
  
  // Rubric complexity
  if (assignment.rubric && assignment.rubric.length > 5) difficultyScore += 2;
  else if (assignment.rubric && assignment.rubric.length > 3) difficultyScore += 1;
  
  // Peer reviews add complexity
  if (assignment.peer_reviews) difficultyScore += 1;
  
  // Group assignments can be more complex
  if (assignment.has_group_assignment) difficultyScore += 1;
  
  if (difficultyScore >= 5) return 'hard';
  if (difficultyScore >= 3) return 'medium';
  return 'easy';
}

function estimateTimeRequired(assignment: CanvasAssignment): number {
  let baseTime = 30; // Base 30 minutes
  
  // Adjust based on points
  baseTime += (assignment.points_possible / 10) * 5;
  
  // Adjust based on word count
  if (assignment.word_count) {
    baseTime += assignment.word_count / 50; // ~50 words per minute writing
  }
  
  // Adjust based on submission type
  if (assignment.submission_types?.includes('online_upload')) baseTime += 15;
  if (assignment.submission_types?.includes('external_tool')) baseTime += 20;
  
  // Adjust based on complexity factors
  if (assignment.rubric && assignment.rubric.length > 3) baseTime += 20;
  if (assignment.peer_reviews) baseTime += 30;
  if (assignment.has_group_assignment) baseTime += 45;
  
  return Math.round(baseTime);
}

function extractNCStandardsAlignment(assignment: CanvasAssignment): string[] {
  const description = htmlToPlainText(assignment.description) || '';
  const title = assignment.name || '';
  const fullText = `${title} ${description}`.toLowerCase();
  
  const standards: string[] = [];
  
  // NC Math Standards
  if (fullText.includes('math') || fullText.includes('algebra') || fullText.includes('geometry')) {
    if (fullText.includes('linear') || fullText.includes('equation')) standards.push('NC.M1.A-REI');
    if (fullText.includes('function') || fullText.includes('graph')) standards.push('NC.M1.F-IF');
    if (fullText.includes('geometry') || fullText.includes('triangle')) standards.push('NC.M1.G-CO');
    if (fullText.includes('statistics') || fullText.includes('data')) standards.push('NC.M1.S-ID');
  }
  
  // NC ELA Standards
  if (fullText.includes('reading') || fullText.includes('literature') || fullText.includes('text')) {
    if (fullText.includes('main idea') || fullText.includes('theme')) standards.push('NC.ELA.RL.K-12.2');
    if (fullText.includes('evidence') || fullText.includes('support')) standards.push('NC.ELA.RL.K-12.1');
    if (fullText.includes('character') || fullText.includes('setting')) standards.push('NC.ELA.RL.K-12.3');
  }
  
  if (fullText.includes('writing') || fullText.includes('essay') || fullText.includes('argument')) {
    if (fullText.includes('argument') || fullText.includes('persuasive')) standards.push('NC.ELA.W.K-12.1');
    if (fullText.includes('informative') || fullText.includes('explain')) standards.push('NC.ELA.W.K-12.2');
    if (fullText.includes('narrative') || fullText.includes('story')) standards.push('NC.ELA.W.K-12.3');
  }
  
  // NC Science Standards
  if (fullText.includes('science') || fullText.includes('biology') || fullText.includes('chemistry')) {
    if (fullText.includes('cell') || fullText.includes('organism')) standards.push('NC.Bio.1.1');
    if (fullText.includes('ecosystem') || fullText.includes('environment')) standards.push('NC.Bio.2.1');
    if (fullText.includes('genetics') || fullText.includes('dna')) standards.push('NC.Bio.3.1');
  }
  
  // NC Social Studies Standards
  if (fullText.includes('history') || fullText.includes('government') || fullText.includes('civics')) {
    if (fullText.includes('constitution') || fullText.includes('democracy')) standards.push('NC.SS.CE.1');
    if (fullText.includes('economics') || fullText.includes('market')) standards.push('NC.SS.CE.2');
    if (fullText.includes('american history') || fullText.includes('revolution')) standards.push('NC.SS.AH1.H.1');
  }
  
  return standards;
}

// Validate environment setup and print info
(async function validateSetup() {
  if (!canvasApiToken) {
    console.error("Warning: CANVAS_API_TOKEN not set. Server will not function correctly.");
  }
  
  if (!canvasDomain) {
    console.error("Warning: CANVAS_DOMAIN not set. Server will not function correctly.");
  }
  
  if (canvasApiToken && canvasDomain) {
    console.error(`AITA Canvas Integration configured for domain: ${canvasDomain}`);
    try {
      const user = await canvasApiRequest<CanvasUser>('/users/self');
      console.error(`Successfully authenticated as ${user.name} (${user.email})`);
    } catch (error) {
      console.error(`Authentication failed: ${(error as Error).message}`);
    }
  }
})();

// List courses tool
server.tool(
  "list_courses",
  "Lists all courses you are enrolled in, with options to filter by active, completed, or all courses.",
  {
    state: z.enum(['active', 'completed', 'all']).default('active')
      .describe("Filter courses by state: active, completed, or all"),
  },
  async ({ state }) => {
    try {
      const courses = await canvasApiRequest<CanvasCourse[]>(`/courses?enrollment_state=${state}&include[]=term`);
      
      if (courses.length === 0) {
        return {
          content: [{ 
            type: "text", 
            text: `No ${state} courses found.` 
          }]
        };
      }

      const courseList = courses.map((course) => {
        const termName = course.term ? `(${course.term.name})` : '';
        return `- ID: ${course.id} | ${course.name} ${termName}`;
      }).join('\n');

      return {
        content: [{ 
          type: "text", 
          text: `Your ${state} courses:\n\n${courseList}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Failed to fetch courses: ${(error as Error).message}` 
        }],
        isError: true
      };
    }
  }
);

// Extend course and assignment types for search results
interface CourseWithAssignments extends CanvasCourse {
  assignments: CanvasAssignment[];
}

interface AssignmentWithCourse extends CanvasAssignment {
  courseName: string;
  courseId: number;
}

// Search assignments tool (across courses)
server.tool(
  "search_assignments",
  "Searches for assignments across all courses based on title, description, due dates, and course filters.",
  {
    query: z.string().optional().default("").describe("Search term to find in assignment titles or descriptions"),
    dueBefore: z.string().optional().describe("Only include assignments due before this date (YYYY-MM-DD)"),
    dueAfter: z.string().optional().describe("Only include assignments due after this date (YYYY-MM-DD)"),
    includeCompleted: z.boolean().default(false).describe("Include assignments from completed courses"),
    courseId: z.string().or(z.number()).optional().describe("Optional: Limit search to specific course ID"),
  },
  async ({ query = "", dueBefore, dueAfter, includeCompleted, courseId }) => {
    try {
      let courses: CanvasCourse[];
      
      // If courseId is provided, only search that course
      if (courseId) {
        courses = [await canvasApiRequest<CanvasCourse>(`/courses/${courseId}`)];
      } else {
        // Otherwise, get all courses based on state
        const courseState = includeCompleted ? 'all' : 'active';
        courses = await canvasApiRequest<CanvasCourse[]>(`/courses?enrollment_state=${courseState}`);
      }
      
      if (courses.length === 0) {
        return {
          content: [{ 
            type: "text", 
            text: "No courses found." 
          }]
        };
      }

      // Search assignments in each course
      let allResults: AssignmentWithCourse[] = [];
      
      for (const course of courses) {
        try {
          // Build the assignments query
          let assignmentsUrl = `/courses/${course.id}/assignments?per_page=100&order_by=due_at&include[]=submission`;
          
          // Add date filtering parameters if provided
          const params = new URLSearchParams();
          
          // Canvas API uses bucket parameter for broad date filtering
          if (dueAfter && !dueBefore) {
            params.append('bucket', 'future');
          } else if (dueBefore && !dueAfter) {
            params.append('bucket', 'past');
          }
          
          // Add specific date range parameters
          if (dueAfter) {
            const afterDate = parseDate(dueAfter);
            if (afterDate) {
              afterDate.setHours(0, 0, 0, 0);
              params.append('due_after', afterDate.toISOString());
            }
          }
          if (dueBefore) {
            const beforeDate = parseDate(dueBefore);
            if (beforeDate) {
              beforeDate.setHours(23, 59, 59, 999);
              params.append('due_before', beforeDate.toISOString());
            }
          }
          
          if (params.toString()) {
            assignmentsUrl += `&${params.toString()}`;
          }

          console.error(`Fetching assignments from URL: ${assignmentsUrl}`); // Debug logging
          const assignments = await canvasApiRequest<CanvasAssignment[]>(assignmentsUrl);
          console.error(`Found ${assignments.length} assignments in course ${course.id}`); // Debug logging
          
          // Filter by search terms if query is provided
          const searchTerms = query.toLowerCase().split(/\s+/).filter(term => term.length > 0);
          const matchingAssignments = searchTerms.length > 0 ? 
            assignments.filter((assignment) => {
              // Search in title and description
              const titleMatch = searchTerms.some(term => 
                assignment.name.toLowerCase().includes(term)
              );
              
              const descriptionMatch = assignment.description ? 
                searchTerms.some(term => 
                  htmlToPlainText(assignment.description).toLowerCase().includes(term)
                ) : false;
              
              return titleMatch || descriptionMatch;
            }) : assignments;
          
          // Double-check date range (in case API filter wasn't exact)
          const dateFilteredAssignments = matchingAssignments.filter(assignment => {
            // Skip local date filtering if the API is already handling it
            if ((dueAfter && !dueBefore && params.has('bucket')) || 
                (dueBefore && !dueAfter && params.has('bucket'))) {
              return true;
            }
            return isDateInRange(assignment.due_at, dueBefore, dueAfter);
          });
          
          // Add course information to each matching assignment
          dateFilteredAssignments.forEach((assignment) => {
            allResults.push({
              ...assignment,
              courseName: course.name,
              courseId: course.id
            });
          });
        } catch (error) {
          console.error(`Error searching in course ${course.id}: ${(error as Error).message}`);
          // Continue with other courses even if one fails
        }
      }
      
      // Sort results by due date
      allResults.sort((a, b) => {
        // Put assignments with no due date at the end
        if (!a.due_at && !b.due_at) return 0;
        if (!a.due_at) return 1;
        if (!b.due_at) return -1;
        
        const dateA = parseDate(a.due_at);
        const dateB = parseDate(b.due_at);
        if (!dateA || !dateB) return 0;
        return dateA.getTime() - dateB.getTime();
      });
      
      if (allResults.length === 0) {
        const dateRange = [];
        if (dueAfter) dateRange.push(`after ${dueAfter}`);
        if (dueBefore) dateRange.push(`before ${dueBefore}`);
        const dateStr = dateRange.length > 0 ? ` due ${dateRange.join(' and ')}` : '';
        const queryStr = query ? ` matching "${query}"` : '';
        
        return {
          content: [{ 
            type: "text", 
            text: `No assignments found${queryStr}${dateStr}.` 
          }]
        };
      }

      const resultsList = allResults.map((assignment) => {
        const dueDate = formatDate(assignment.due_at);
        const status = assignment.published ? '' : ' (Unpublished)';
        return [
          `- Course: ${assignment.courseName} (ID: ${assignment.courseId})`,
          `  Assignment: ${assignment.name}${status} (ID: ${assignment.id})`,
          `  Due: ${dueDate}`
        ].join('\n');
      }).join('\n\n');

      const dateRange = [];
      if (dueAfter) dateRange.push(`after ${dueAfter}`);
      if (dueBefore) dateRange.push(`before ${dueBefore}`);
      const dateStr = dateRange.length > 0 ? ` due ${dateRange.join(' and ')}` : '';
      const queryStr = query ? ` matching "${query}"` : '';

      return {
        content: [{ 
          type: "text", 
          text: `Found ${allResults.length} assignments${queryStr}${dateStr}:\n\n${resultsList}` 
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Search failed: ${(error as Error).message}` 
        }],
        isError: true
      };
    }
  }
);

// Get assignment details tool with AITA enhancements
server.tool(
  "get_assignment",
  "Retrieves detailed information about a specific assignment, including its description, submission requirements, and AITA learning analysis.",
  {
    courseId: z.string().or(z.number()).describe("Course ID"),
    assignmentId: z.string().or(z.number()).describe("Assignment ID"),
    formatType: z.enum(['full', 'plain', 'markdown']).default('markdown')
      .describe("Format type: full (HTML), plain (text only), or markdown (formatted)"),
    includeAITAAnalysis: z.boolean().default(true)
      .describe("Include AITA learning analysis and NC standards alignment"),
  },
  async ({ courseId, assignmentId, formatType, includeAITAAnalysis }) => {
    try {
      const assignment = await canvasApiRequest<CanvasAssignment>(`/courses/${courseId}/assignments/${assignmentId}`);
      
      let description: string;
      let links: { text: string; href: string }[] = [];
      
      if (assignment.description) {
        links = extractLinks(assignment.description);
      }

      switch (formatType) {
        case 'full':
          description = assignment.description || 'No description available';
          break;
        case 'plain':
          description = htmlToPlainText(assignment.description) || 'No description available';
          break;
        case 'markdown':
        default:
          description = assignment.description ? 
            convertHtmlToMarkdown(assignment.description) : 
            'No description available';
          break;
      }
      
      const details = [
        `# ${assignment.name}`,
        ``,
        `**Course ID:** ${courseId}`,
        `**Assignment ID:** ${assignment.id}`,
        `**Due Date:** ${formatDate(assignment.due_at)}`,
        `**Points Possible:** ${assignment.points_possible}`,
        `**Status:** ${assignment.published ? 'Published' : 'Unpublished'}${assignment.only_visible_to_overrides ? ' (Only visible to specific students)' : ''}`,
        ``,
      ];

      // Add AITA learning analysis if requested
      if (includeAITAAnalysis) {
        const difficulty = analyzeAssignmentDifficulty(assignment);
        const estimatedTime = estimateTimeRequired(assignment);
        const ncStandards = extractNCStandardsAlignment(assignment);
        
        details.push(
          `## 🎯 AITA Learning Analysis`,
          ``,
          `**Difficulty Level:** ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`,
          `**Estimated Time:** ${estimatedTime} minutes`,
          ``
        );
        
        if (ncStandards.length > 0) {
          details.push(
            `**NC Standards Alignment:**`,
            ...ncStandards.map(standard => `- ${standard}`),
            ``
          );
        }
        
        // Add learning recommendations based on difficulty
        details.push(`**AITA Recommendations:**`);
        switch (difficulty) {
          case 'easy':
            details.push(
              `- This assignment is well-suited for independent work`,
              `- Consider using it as practice for core concepts`,
              `- Good opportunity to build confidence`
            );
            break;
          case 'medium':
            details.push(
              `- May benefit from some guidance or scaffolding`,
              `- Consider breaking into smaller steps`,
              `- Good for applying learned concepts`
            );
            break;
          case 'hard':
            details.push(
              `- Recommend additional support and resources`,
              `- Consider collaborative work or peer support`,
              `- May need prerequisite skill review`
            );
            break;
        }
        details.push(``);
      }

      details.push(
        `## Submission Requirements`,
        `- **Submission Type:** ${assignment.submission_types?.join(', ') || 'Not specified'}`,
      );

      // Add allowed file extensions if relevant
      if (assignment.submission_types?.includes('online_upload') && assignment.allowed_extensions?.length) {
        details.push(`- **Allowed File Types:** ${assignment.allowed_extensions.map(ext => `\`.${ext}\``).join(', ')}`);
      }

      // Add attempt limits if specified
      if (assignment.allowed_attempts !== null && assignment.allowed_attempts !== -1) {
        details.push(`- **Allowed Attempts:** ${assignment.allowed_attempts}`);
      }

      // Add grading type info
      details.push(`- **Grading Type:** ${assignment.grading_type.replace(/_/g, ' ').toLowerCase()}`);

      // Add time restrictions if any
      if (assignment.unlock_at || assignment.lock_at) {
        details.push(`- **Time Restrictions:**`);
        if (assignment.unlock_at) {
          details.push(`  - Available from: ${formatDate(assignment.unlock_at)}`);
        }
        if (assignment.lock_at) {
          details.push(`  - Locks at: ${formatDate(assignment.lock_at)}`);
        }
      }

      // Add group assignment info if relevant
      if (assignment.has_group_assignment) {
        details.push(`- **Group Assignment:** Yes`);
      }

      // Add peer review info if enabled
      if (assignment.peer_reviews) {
        details.push(`- **Peer Reviews Required:** Yes`);
      }

      // Add word count requirement if specified
      if (assignment.word_count) {
        details.push(`- **Required Word Count:** ${assignment.word_count}`);
      }

      // Add external tool info if present
      if (assignment.external_tool_tag_attributes?.url) {
        details.push(`- **External Tool Required:** Yes`);
        details.push(`  - Tool URL: ${assignment.external_tool_tag_attributes.url}`);
        if (assignment.external_tool_tag_attributes.new_tab) {
          details.push(`  - Opens in new tab: Yes`);
        }
      }

      // Add plagiarism detection info
      if (assignment.turnitin_enabled || assignment.vericite_enabled) {
        details.push(`- **Plagiarism Detection:**`);
        if (assignment.turnitin_enabled) details.push(`  - Turnitin enabled`);
        if (assignment.vericite_enabled) details.push(`  - VeriCite enabled`);
      }

      // Add rubric information if available
      if (assignment.rubric && assignment.rubric.length > 0) {
        details.push('', '## Rubric');
        if (assignment.use_rubric_for_grading) {
          details.push('*This rubric is used for grading*', '');
        }
        assignment.rubric.forEach(criterion => {
          details.push(`### ${criterion.description} (${criterion.points} points)`);
          if (criterion.long_description) {
            details.push(criterion.long_description);
          }
          details.push('');
        });
      }

      // Add special requirements
      const specialReqs = [];
      if (assignment.anonymize_students) specialReqs.push('Anonymous Grading Enabled');
      if (assignment.require_lockdown_browser) specialReqs.push('Lockdown Browser Required');
      if (assignment.annotatable_attachment_id) specialReqs.push('Annotation Required');
      if (specialReqs.length > 0) {
        details.push('', '## Special Requirements', '');
        specialReqs.forEach(req => details.push(`- ${req}`));
      }

      // Add lock status if relevant
      if (assignment.locked_for_user) {
        details.push('', '## Access Restrictions', '');
        details.push(assignment.lock_explanation || 'This assignment is currently locked.');
      }

      details.push(
        ``,
        `## Description`,
        ``,
        description
      );

      // Add links section if any links were found
      if (links.length > 0) {
        details.push('', '## Required Materials and Links', '');
        links.forEach(link => {
          details.push(`- [${link.text}](${link.href})`);
        });
      }

      return {
        content: [{ 
          type: "text", 
          text: details.join('\n')
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Failed to fetch assignment details: ${(error as Error).message}` 
        }],
        isError: true
      };
    }
  }
);

// New AITA-specific tool: Get student submission status
server.tool(
  "get_student_submission",
  "Retrieves submission status and details for a specific assignment and student (for teachers/instructors).",
  {
    courseId: z.string().or(z.number()).describe("Course ID"),
    assignmentId: z.string().or(z.number()).describe("Assignment ID"),
    studentId: z.string().or(z.number()).optional().describe("Student ID (optional, defaults to current user)"),
  },
  async ({ courseId, assignmentId, studentId }) => {
    try {
      const userId = studentId || 'self';
      const submission = await canvasApiRequest<CanvasSubmission>(
        `/courses/${courseId}/assignments/${assignmentId}/submissions/${userId}?include[]=submission_comments&include[]=rubric_assessment`
      );
      
      const details = [
        `# Submission Status`,
        ``,
        `**Assignment ID:** ${assignmentId}`,
        `**Student ID:** ${submission.user_id}`,
        `**Submission Status:** ${submission.workflow_state}`,
        `**Submitted:** ${submission.submitted_at ? formatDate(submission.submitted_at) : 'Not submitted'}`,
        `**Score:** ${submission.score !== null ? `${submission.score}/${submission.assignment_id}` : 'Not graded'}`,
        `**Grade:** ${submission.grade || 'Not graded'}`,
        `**Attempt:** ${submission.attempt}`,
        ``
      ];

      // Add status indicators
      const statusIndicators = [];
      if (submission.late) statusIndicators.push('Late');
      if (submission.missing) statusIndicators.push('Missing');
      if (submission.excused) statusIndicators.push('Excused');
      
      if (statusIndicators.length > 0) {
        details.push(`**Status Flags:** ${statusIndicators.join(', ')}`);
        details.push('');
      }

      // Add submission content if available
      if (submission.submission_type && submission.submission_type !== 'none') {
        details.push(`## Submission Content`);
        details.push(`**Type:** ${submission.submission_type}`);
        
        if (submission.body) {
          details.push('', '**Text Submission:**', '', submission.body);
        }
        
        if (submission.url) {
          details.push('', `**URL Submission:** ${submission.url}`);
        }
        
        if (submission.attachments && submission.attachments.length > 0) {
          details.push('', '**File Attachments:**');
          submission.attachments.forEach(attachment => {
            details.push(`- [${attachment.filename}](${attachment.url}) (${attachment.content_type})`);
          });
        }
      }

      return {
        content: [{ 
          type: "text", 
          text: details.join('\n')
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Failed to fetch submission: ${(error as Error).message}` 
        }],
        isError: true
      };
    }
  }
);

// New AITA-specific tool: Analyze assignment for learning objectives
server.tool(
  "analyze_assignment_learning",
  "Analyzes an assignment to extract learning objectives, prerequisite skills, and provide AITA tutoring recommendations.",
  {
    courseId: z.string().or(z.number()).describe("Course ID"),
    assignmentId: z.string().or(z.number()).describe("Assignment ID"),
  },
  async ({ courseId, assignmentId }) => {
    try {
      const assignment = await canvasApiRequest<CanvasAssignment>(`/courses/${courseId}/assignments/${assignmentId}`);
      
      const difficulty = analyzeAssignmentDifficulty(assignment);
      const estimatedTime = estimateTimeRequired(assignment);
      const ncStandards = extractNCStandardsAlignment(assignment);
      
      // Extract key concepts from description
      const description = htmlToPlainText(assignment.description) || '';
      const title = assignment.name || '';
      const fullText = `${title} ${description}`.toLowerCase();
      
      // Identify subject area
      let subjectArea = 'General';
      if (fullText.includes('math') || fullText.includes('algebra') || fullText.includes('geometry') || fullText.includes('calculus')) {
        subjectArea = 'Mathematics';
      } else if (fullText.includes('english') || fullText.includes('writing') || fullText.includes('literature') || fullText.includes('reading')) {
        subjectArea = 'English Language Arts';
      } else if (fullText.includes('science') || fullText.includes('biology') || fullText.includes('chemistry') || fullText.includes('physics')) {
        subjectArea = 'Science';
      } else if (fullText.includes('history') || fullText.includes('social') || fullText.includes('government') || fullText.includes('civics')) {
        subjectArea = 'Social Studies';
      }
      
      // Generate prerequisite skills based on content analysis
      const prerequisites: string[] = [];
      if (subjectArea === 'Mathematics') {
        if (fullText.includes('algebra')) prerequisites.push('Basic arithmetic operations', 'Understanding of variables');
        if (fullText.includes('geometry')) prerequisites.push('Basic shapes and measurements', 'Coordinate plane understanding');
        if (fullText.includes('function')) prerequisites.push('Understanding of input/output relationships', 'Graphing skills');
      } else if (subjectArea === 'English Language Arts') {
        if (fullText.includes('essay') || fullText.includes('writing')) prerequisites.push('Paragraph structure', 'Thesis development', 'Grammar fundamentals');
        if (fullText.includes('analysis')) prerequisites.push('Reading comprehension', 'Critical thinking skills', 'Evidence identification');
      }
      
      // Generate support resources
      const supportResources: string[] = [];
      supportResources.push('AITA AI Tutor for personalized help');
      supportResources.push('Canvas course materials and readings');
      
      if (subjectArea === 'Mathematics') {
        supportResources.push('Khan Academy math practice', 'Desmos graphing calculator', 'Math help videos');
      } else if (subjectArea === 'English Language Arts') {
        supportResources.push('Writing center resources', 'Grammar checking tools', 'Citation guides');
      } else if (subjectArea === 'Science') {
        supportResources.push('Virtual lab simulations', 'Scientific calculator', 'Research databases');
      }
      
      const analysis = [
        `# 🎯 AITA Learning Analysis: ${assignment.name}`,
        ``,
        `## Assignment Overview`,
        `- **Subject Area:** ${subjectArea}`,
        `- **Difficulty Level:** ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`,
        `- **Estimated Time:** ${estimatedTime} minutes`,
        `- **Points Possible:** ${assignment.points_possible}`,
        ``,
        `## NC Standards Alignment`,
      ];
      
      if (ncStandards.length > 0) {
        ncStandards.forEach(standard => {
          analysis.push(`- ${standard}`);
        });
      } else {
        analysis.push('- No specific NC standards identified (may require manual review)');
      }
      
      analysis.push(
        ``,
        `## Prerequisite Skills`,
      );
      
      if (prerequisites.length > 0) {
        prerequisites.forEach(skill => {
          analysis.push(`- ${skill}`);
        });
      } else {
        analysis.push('- Basic reading and comprehension skills');
        analysis.push('- Familiarity with assignment submission process');
      }
      
      analysis.push(
        ``,
        `## AITA Tutoring Recommendations`,
      );
      
      switch (difficulty) {
        case 'easy':
          analysis.push(
            `- **Approach:** Independent work with minimal guidance`,
            `- **AITA Support:** Available for clarification questions`,
            `- **Focus:** Building confidence and reinforcing concepts`,
            `- **Intervention:** Monitor for completion and basic understanding`
          );
          break;
        case 'medium':
          analysis.push(
            `- **Approach:** Guided practice with scaffolding`,
            `- **AITA Support:** Step-by-step guidance and concept explanation`,
            `- **Focus:** Breaking down complex tasks into manageable steps`,
            `- **Intervention:** Provide examples and check understanding frequently`
          );
          break;
        case 'hard':
          analysis.push(
            `- **Approach:** Intensive support with multiple resources`,
            `- **AITA Support:** Comprehensive tutoring and skill building`,
            `- **Focus:** Prerequisite review and concept development`,
            `- **Intervention:** Consider additional time, peer collaboration, or instructor consultation`
          );
          break;
      }
      
      analysis.push(
        ``,
        `## Recommended Support Resources`,
      );
      
      supportResources.forEach(resource => {
        analysis.push(`- ${resource}`);
      });
      
      analysis.push(
        ``,
        `## Learning Objectives (Inferred)`,
        `Based on assignment content analysis:`,
      );
      
      // Generate learning objectives based on content
      if (fullText.includes('solve') || fullText.includes('calculate')) {
        analysis.push('- Demonstrate problem-solving skills');
      }
      if (fullText.includes('analyze') || fullText.includes('evaluate')) {
        analysis.push('- Apply critical thinking and analysis skills');
      }
      if (fullText.includes('write') || fullText.includes('compose')) {
        analysis.push('- Communicate ideas effectively in writing');
      }
      if (fullText.includes('research') || fullText.includes('investigate')) {
        analysis.push('- Conduct research and gather relevant information');
      }
      if (fullText.includes('create') || fullText.includes('design')) {
        analysis.push('- Apply creative and design thinking');
      }
      
      // Add generic objectives if none were identified
      if (!analysis[analysis.length - 1].startsWith('-')) {
        analysis.push('- Demonstrate understanding of course concepts');
        analysis.push('- Apply learned skills to complete assignment requirements');
      }

      return {
        content: [{ 
          type: "text", 
          text: analysis.join('\n')
        }]
      };
    } catch (error) {
      return {
        content: [{ 
          type: "text", 
          text: `Failed to analyze assignment: ${(error as Error).message}` 
        }],
        isError: true
      };
    }
  }
);

// Assignment content resource
server.resource(
  "assignment_content",
  new ResourceTemplate("canvas://courses/{courseId}/assignments/{assignmentId}", { list: undefined }),
  async (uri, { courseId, assignmentId }) => {
    try {
      const assignment = await canvasApiRequest<CanvasAssignment>(`/courses/${courseId}/assignments/${assignmentId}`);
      
      // Format the content nicely with AITA enhancements
      const difficulty = analyzeAssignmentDifficulty(assignment);
      const estimatedTime = estimateTimeRequired(assignment);
      const ncStandards = extractNCStandardsAlignment(assignment);
      
      const content = [
        `# ${assignment.name}`,
        ``,
        `## Assignment Details`,
        `**Due Date:** ${assignment.due_at ? new Date(assignment.due_at).toLocaleString() : 'No due date'}`,
        `**Points Possible:** ${assignment.points_possible}`,
        `**Submission Type:** ${assignment.submission_types?.join(', ') || 'Not specified'}`,
        ``,
        `## AITA Learning Analysis`,
        `**Difficulty:** ${difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}`,
        `**Estimated Time:** ${estimatedTime} minutes`,
      ];
      
      if (ncStandards.length > 0) {
        content.push(`**NC Standards:** ${ncStandards.join(', ')}`);
      }
      
      content.push(
        ``,
        `## Description`,
        ``,
        assignment.description || 'No description available'
      );

      return {
        contents: [{
          uri: uri.href,
          text: content.join('\n'),
          mimeType: "text/markdown"
        }]
      };
    } catch (error) {
      throw new Error(`Failed to fetch assignment content: ${(error as Error).message}`);
    }
  }
);

// Start the server
(async () => {
  try {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("AITA Canvas MCP Server started on stdio");
  } catch (error) {
    console.error("Server failed to start:", error);
    process.exit(1);
  }
})();