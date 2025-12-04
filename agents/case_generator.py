import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from crewai import Agent, Task, Crew
from crewai_tools import PDFSearchTool
from django.conf import settings


class CaseGenerator:
    """
    Generates interview cases using CrewAI agents with RAG.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Case Generator with RAG capabilities.
        
        Sets up API keys and initializes the PDF search tool for casebook retrieval.
        """
        # Ensure API keys are set
        api_key = os.environ.get("OPENAI_API_KEY") or (settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None)
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in:\n"
                "1. Environment variable: OPENAI_API_KEY=your-key\n"
                "2. .env file: OPENAI_API_KEY=your-key\n"
                "3. Django settings: OPENAI_API_KEY = 'your-key'"
            )
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Set model
        os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
        
        # Initialize PDF search tool for casebook
        # Try multiple possible locations for the casebook
        possible_paths = [
            Path(settings.BASE_DIR) / "Darden-Case-Book-2018-2019.pdf",
            Path(settings.BASE_DIR) / "casebook.pdf",
            Path(settings.BASE_DIR) / "docs" / "Darden-Case-Book-2018-2019.pdf",
            Path(settings.BASE_DIR) / "static" / "Darden-Case-Book-2018-2019.pdf",
        ]
        
        self.pdf_tool: Optional[PDFSearchTool] = None
        for casebook_path in possible_paths:
            if casebook_path.exists():
                try:
                    self.pdf_tool = PDFSearchTool(str(casebook_path))
                    print(f"Casebook loaded from: {casebook_path}")
                    break
                except Exception as e:
                    print(f"Warning: Could not load PDF tool from {casebook_path}: {e}")
                    continue
        
        if not self.pdf_tool:
            print("Warning: No casebook PDF found. Case generation will proceed without RAG.")

    def generate_case(self, topic: str, case_type: str = "consulting") -> Dict[str, Any]:
        """
        Generates a full case interview scenario using RAG.
        
        Args:
            topic: The industry or topic (e.g., "Airline Profitability", "New Market Entry")
            case_type: "consulting" or "product_management"
            
        Returns:
            dict: A dictionary matching the Case model fields.
        """
        try:
            # --- Agents ---
            
            # Research Agent (RAG) - only if PDF tool is available
            if self.pdf_tool:
                researcher = Agent(
                    role="Case Research Specialist",
                    goal=f"Search the casebook for relevant examples related to {topic}.",
                    backstory="You are an expert at finding and analyzing case study examples. "
                              "You search through case libraries to find relevant patterns, "
                              "frameworks, and data structures that can inspire new cases.",
                    allow_delegation=False,
                    verbose=False,
                    tools=[self.pdf_tool]
                )
            
            designer = Agent(
                role="Case Designer",
                goal=f"Design a realistic and challenging {case_type} interview case about {topic}.",
                backstory=(
                    "You are a senior partner at a top consulting firm (McKinsey/BCG/Bain). "
                    "You are an expert at creating case studies that test a candidate's "
                    "problem-solving, analytical, and communication skills. "
                    "You focus on creating a clear narrative with distinct phases. "
                    "Your cases are realistic, challenging, and follow industry best practices."
                ),
                allow_delegation=False,
                verbose=False
            )
            
            writer = Agent(
                role="Case Writer",
                goal="Write the final case content in structured JSON format.",
                backstory=(
                    "You are a technical writer who specializes in structuring data for applications. "
                    "You take the case design and convert it into a precise JSON format "
                    "that can be parsed by the system. You are meticulous about JSON syntax."
                ),
                allow_delegation=False,
                verbose=False
            )
            
            # --- Tasks ---
            
            # Research Task (RAG) - only if PDF tool is available
            if self.pdf_tool:
                research_task = Task(
                    description=(
                        f"Search the casebook for cases related to '{topic}'. "
                        "Find examples of:\n"
                        "1. Similar industry contexts\n"
                        "2. Relevant frameworks (profitability, market entry, pricing, etc.)\n"
                        "3. Types of exhibits used (financial data, market data, etc.)\n"
                        "4. Question structures and flow\n"
                        "5. Typical case structure and narrative flow\n"
                        "Summarize your findings to help the Case Designer create a realistic case."
                    ),
                    expected_output="A summary of relevant case examples and patterns found in the casebook.",
                    agent=researcher,
                    tools=[self.pdf_tool]
                )
            
            # Enhanced design task with better instructions
            design_instructions = (
                f"Design a {case_type} case interview about '{topic}'. "
                "The case should be realistic, challenging, and solvable. "
                "Include the following elements:\n\n"
                "1. **Title**: A catchy, professional title (e.g., 'Airline Profitability Challenge')\n"
                "2. **Prompt**: A clear initial problem statement (2-3 sentences) that sets up the case\n"
                "3. **Context**: A JSON object with:\n"
                "   - 'client': Company/client name and brief description\n"
                "   - 'situation': Current business situation and background\n"
                "   - 'objective': What the client wants to achieve\n"
                "4. **Exhibits**: Create 2-3 exhibits with:\n"
                "   - Financial data (revenue, costs, margins)\n"
                "   - Market data (size, growth, competition)\n"
                "   - Operational data (capacity, utilization, etc.)\n"
                "   Each exhibit should be a JSON object with 'title', 'type' ('table' or 'chart'), and 'data'\n\n"
                "Make the case challenging but fair. Ensure there's a clear solution path."
            )
            
            if self.pdf_tool:
                design_instructions += (
                    "\n\nUse insights from the research findings to make the case realistic and "
                    "aligned with industry standards."
                )
            
            design_task = Task(
                description=design_instructions,
                expected_output="A detailed outline of the case including title, prompt, context, and exhibits.",
                agent=designer
            )
            
            # Enhanced write task with better JSON structure
            write_task = Task(
                description=(
                    "Convert the case design into a valid JSON object. "
                    "CRITICAL: Return ONLY valid JSON, no markdown, no code blocks, no explanations.\n\n"
                    "The JSON MUST have this exact structure:\n"
                    "{\n"
                    '  "title": "Case Title Here",\n'
                    f'  "case_type": "{case_type}",\n'
                    '  "prompt": "The initial problem statement given to the candidate (2-3 sentences)",\n'
                    '  "context": {\n'
                    '    "client": "Company name and description",\n'
                    '    "situation": "Current business situation",\n'
                    '    "objective": "What the client wants to achieve"\n'
                    '  },\n'
                    '  "exhibits": [\n'
                    '    {\n'
                    '      "title": "Exhibit 1: Financial Overview",\n'
                    '      "type": "table",\n'
                    '      "data": {\n'
                    '        "columns": ["Year", "Revenue", "Costs"],\n'
                    '        "rows": [\n'
                    '          ["2023", "100M", "80M"],\n'
                    '          ["2024", "110M", "85M"]\n'
                    '        ]\n'
                    '      }\n'
                    '    },\n'
                    '    {\n'
                    '      "title": "Exhibit 2: Market Data",\n'
                    '      "type": "table",\n'
                    '      "data": {\n'
                    '        "columns": ["Segment", "Size", "Growth"],\n'
                    '        "rows": [\n'
                    '          ["Segment A", "50M", "10%"],\n'
                    '          ["Segment B", "30M", "5%"]\n'
                    '        ]\n'
                    '      }\n'
                    '    }\n'
                    '  ]\n'
                    "}\n\n"
                    "Return ONLY the JSON object, nothing else. No markdown formatting, no code blocks."
                ),
                expected_output="A valid JSON string representing the case (no markdown, no code blocks).",
                agent=writer
            )
            
            # --- Crew ---
            if self.pdf_tool:
                tasks = [research_task, design_task, write_task]
                agents = [researcher, designer, writer]
            else:
                tasks = [design_task, write_task]
                agents = [designer, writer]
            
            crew = Crew(
                agents=agents,
                tasks=tasks,
                verbose=False
            )
            
            print(f"Generating case about '{topic}' ({case_type})...")
            result = crew.kickoff()
            
            # Parse result with improved error handling
            raw_output = str(result.raw).strip()
            
            # Remove markdown code blocks if present
            if raw_output.startswith("```json"):
                raw_output = raw_output[7:].strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output[3:].strip()
            
            if raw_output.endswith("```"):
                raw_output = raw_output[:-3].strip()
            
            # Try to extract JSON if it's embedded in text
            import re
            json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
            if json_match:
                raw_output = json_match.group(0)
            
            # Parse JSON
            case_data = json.loads(raw_output)
            
            # Validate required fields
            if not case_data.get('title'):
                case_data['title'] = f"{topic} Case"
            if not case_data.get('prompt'):
                case_data['prompt'] = f"Analyze the {topic} situation and provide recommendations."
            if not case_data.get('context'):
                case_data['context'] = {
                    'client': 'Client Company',
                    'situation': 'Business challenge',
                    'objective': 'Improve performance'
                }
            if not case_data.get('exhibits'):
                case_data['exhibits'] = []
            
            case_data['case_type'] = case_type
            print(f"Case generated successfully: {case_data.get('title')}")
            return case_data
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Raw output: {raw_output[:500]}...")
            # Return a fallback case
            return self._create_fallback_case(topic, case_type)
        except Exception as e:
            print(f"Error generating case: {e}")
            import traceback
            traceback.print_exc()
            return self._create_fallback_case(topic, case_type)
    
    def _create_fallback_case(self, topic: str, case_type: str) -> Dict[str, Any]:
        """Create a basic fallback case when generation fails."""
        return {
            "title": f"{topic} Case Study",
            "case_type": case_type,
            "prompt": (
                f"You are a consultant helping a client with a {topic} challenge. "
                "Analyze the situation and provide strategic recommendations."
            ),
            "context": {
                "client": "Client Company",
                "situation": f"The client is facing challenges related to {topic}.",
                "objective": "Develop a strategic plan to address the challenge."
            },
            "exhibits": [
                {
                    "title": "Exhibit 1: Key Metrics",
                    "type": "table",
                    "data": {
                        "columns": ["Metric", "Value"],
                        "rows": [
                            ["Revenue", "To be provided"],
                            ["Costs", "To be provided"]
                        ]
                    }
                }
            ]
        }
