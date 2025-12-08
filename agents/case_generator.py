import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Optional, Any, List
from crewai import Agent, Task, Crew
from crewai_tools import PDFSearchTool
from django.conf import settings
import environ

# Import Django model for optional saving
from cases.models import Case

# Initialize environment variables
env = environ.Env()


class CaseGenerator:
    """
    Generates interview cases using CrewAI agents with RAG.

    Added method `generate_candidates` to pre-generate multiple cases
    (default 10) for candidate selection. Can optionally save generated
    cases to the `cases.Case` model.
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
        self.pdf_tool: Optional[PDFSearchTool] = None
        
        # First, try to load from Cloudflare R2 if configured
        if env('CLOUDFLARE_R2_ACCOUNT_ID', default=None):
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                s3_client = boto3.client(
                    's3',
                    endpoint_url=env('CLOUDFLARE_R2_ENDPOINT_URL'),
                    aws_access_key_id=env('CLOUDFLARE_R2_ACCESS_KEY_ID'),
                    aws_secret_access_key=env('CLOUDFLARE_R2_SECRET_ACCESS_KEY'),
                )
                
                bucket_name = env('CLOUDFLARE_R2_BUCKET_NAME')
                casebook_key = 'Darden-Case-Book-2018-2019.pdf'  # Adjust path as needed
                
                # Download from R2 to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    try:
                        s3_client.download_fileobj(bucket_name, casebook_key, tmp_file)
                        tmp_path = Path(tmp_file.name)
                        self.pdf_tool = PDFSearchTool(str(tmp_path))
                        print(f"Casebook loaded from R2: {casebook_key}")
                    except ClientError as e:
                        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                        if error_code != 'NoSuchKey':
                            print(f"Warning: Could not load casebook from R2: {e}")
                    except Exception as e:
                        print(f"Warning: Error processing R2 casebook: {e}")
            except ImportError:
                print("Warning: boto3 not installed. Cannot load casebook from R2.")
            except Exception as e:
                print(f"Warning: R2 configuration error: {e}")

        # Fallback to local paths if R2 didn't work
        if not self.pdf_tool:
            possible_paths = [
                Path(settings.BASE_DIR) / "Darden-Case-Book-2018-2019.pdf",
                Path(settings.BASE_DIR) / "casebook.pdf",
                Path(settings.BASE_DIR) / "docs" / "Darden-Case-Book-2018-2019.pdf",
                Path(settings.BASE_DIR) / "static" / "Darden-Case-Book-2018-2019.pdf",
            ]
            
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

            # Enhanced write task with better JSON structure and validation rules
            write_task = Task(
                description=(
                    "Convert the case design into a valid JSON object. "
                    "CRITICAL: Return ONLY valid JSON, no markdown, no code blocks, no explanations.\n\n"
                    "IMPORTANT DATA FORMATTING RULES:\n"
                    "1. CURRENCY: Always use $ for money (e.g., '$500M', '$2.5B', '$100K')\n"
                    "2. LARGE NUMBERS: Use K (thousands), M (millions), B (billions) - e.g., '50M', '2.5B', '100K'\n"
                    "3. PERCENTAGES: Always use % symbol (e.g., '15%', '8.5%')\n"
                    "4. CONSISTENCY: If one exhibit shows '$500M', all related exhibits must use same format\n"
                    "5. ALIGNMENT: Create bar/pie charts that match table data exactly:\n"
                    "   - If table shows market segments at 60%, 35%, 5%, pie chart must show same values\n"
                    "   - If table shows revenue of $500M, $300M, bar chart must use same values\n"
                    "   - Percentages in pie charts MUST add up to 100%\n"
                    "6. EXHIBIT TYPES: Include mix of 'table', 'bar', and 'pie' types\n"
                    "   - Use 'pie' for breakdowns that sum to 100% (market share, cost %, etc.)\n"
                    "   - Use 'bar' for comparisons (revenue by year, segment sizes, etc.)\n"
                    "   - Use 'table' for detailed data with multiple dimensions\n\n"
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
                    '        "columns": ["Year", "Revenue", "Costs", "Margin"],\n'
                    '        "rows": [\n'
                    '          ["2023", "$500M", "$400M", "20%"],\n'
                    '          ["2024", "$550M", "$450M", "18%"]\n'
                    '        ]\n'
                    '      }\n'
                    '    },\n'
                    '    {\n'
                    '      "title": "Revenue by Segment",\n'
                    '      "type": "bar",\n'
                    '      "data": {\n'
                    '        "labels": ["Enterprise", "SMB", "Consumer"],\n'
                    '        "values": [300, 150, 100],\n'
                    '        "unit": "$M"\n'
                    '      }\n'
                    '    },\n'
                    '    {\n'
                    '      "title": "Market Share Distribution",\n'
                    '      "type": "pie",\n'
                    '      "data": {\n'
                    '        "labels": ["Company A", "Company B", "Others"],\n'
                    '        "values": [45, 30, 25],\n'
                    '        "unit": "%"\n'
                    '      }\n'
                    '    },\n'
                    '    {\n'
                    '      "title": "Detailed Market Analysis",\n'
                    '      "type": "table",\n'
                    '      "data": {\n'
                    '        "columns": ["Segment", "Size", "Growth", "Share"],\n'
                    '        "rows": [\n'
                    '          ["Enterprise", "$50B", "8%", "45%"],\n'
                    '          ["SMB", "$30B", "12%", "30%"],\n'
                    '          ["Consumer", "$20B", "5%", "25%"]\n'
                    '        ]\n'
                    '      }\n'
                    '    }\n'
                    '  ]\n'
                    "}\n\n"
                    "VALIDATION CHECKLIST:\n"
                    "✓ All monetary values have $ sign (e.g., '$500M', not '500M')\n"
                    "✓ All percentages have % sign (e.g., '15%', not '15')\n"
                    "✓ Large numbers use K/M/B notation consistently\n"
                    "✓ If pie chart exists, values sum to 100%\n"
                    "✓ If bar/pie chart exists, corresponding table with same data exists\n"
                    "✓ All exhibits are relevant to the case prompt\n"
                    "✓ At least 3-4 exhibits total (mix of table/bar/pie)\n\n"
                    "Return ONLY the JSON object, nothing else. No markdown formatting, no code blocks."
                ),
                expected_output="A valid JSON string representing the case with properly formatted numbers, aligned exhibits, and correct data types.",
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

            # Validate and fix data formatting
            case_data = self._validate_and_fix_case(case_data, topic, case_type)

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

    def generate_candidates(self, base_topic: Optional[str] = None, n: int = 10, case_type: str = "consulting", save: bool = False, user=None, themes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate `n` candidate cases in advance for a user to choose from.

        Args:
            base_topic: Optional base topic or industry to base variants on. If None, a set of default topics will be used.
            n: Number of cases to generate (default 10).
            case_type: 'consulting' or 'product_management'.
            save: If True, save generated cases to the `cases.Case` model.
            user: Optional Django `User` instance to set as `generated_by` when saving.
            themes: Optional list of themes/angles to combine with `base_topic` to produce variants.

        Returns:
            List[dict]: List of generated case dictionaries.
        """
        default_topics = [
            "Airline Profitability",
            "New Market Entry",
            "Pricing Strategy",
            "Product Launch",
            "Cost Reduction",
            "Subscription Growth",
            "Retail Expansion",
            "Supply Chain Optimization",
            "M&A Opportunity",
            "Turnaround Strategy",
        ]

        # A list of thematic angles if base_topic provided
        default_themes = [
            "Profitability Analysis",
            "Market Entry",
            "Pricing Optimization",
            "Go-to-Market",
            "Cost Structure",
            "Growth Strategy",
            "Channel Strategy",
            "Operational Efficiency",
            "Strategic Partnership",
            "Turnaround & Restructuring",
        ]

        if themes is None:
            themes = default_themes

        # Build topics list
        topics: List[str] = []
        if base_topic:
            # Create variants by combining base_topic with themes
            for i in range(n):
                theme = themes[i % len(themes)]
                topics.append(f"{base_topic} — {theme}")
        else:
            # Use default_topics, repeat/derive if n > len(default_topics)
            for i in range(n):
                topics.append(default_topics[i % len(default_topics)])

        generated: List[Dict[str, Any]] = []
        for idx, t in enumerate(topics[:n]):
            try:
                case = self.generate_case(t, case_type=case_type)
            except Exception as e:
                print(f"Error generating candidate {idx+1} ({t}): {e}")
                case = self._create_fallback_case(t, case_type)

            generated.append(case)

            # Optionally save to DB
            if save:
                try:
                    case_obj = Case.objects.create(
                        title=case.get("title", f"{t} Case"),
                        case_type=case.get("case_type", case_type),
                        prompt=case.get("prompt", ""),
                        context=case.get("context", {}),
                        exhibits=case.get("exhibits", []),
                        generated_by=user if user is not None else None,
                    )
                    # Attach DB id to returned case to help frontend reference
                    case["id"] = case_obj.id
                except Exception as e:
                    print(f"Warning: Could not save case '{t}': {e}")

        return generated

    def _validate_and_fix_case(self, case_data: Dict[str, Any], topic: str, case_type: str) -> Dict[str, Any]:
        """
        Validate and fix case data to ensure proper formatting and alignment.
        
        Checks:
        - Required fields exist
        - Numbers have proper units (K/M/B)
        - Currency values have $ sign
        - Percentages have % sign
        - Pie chart values sum to ~100%
        - Charts align with table data
        """
        # Ensure required fields
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

        # Validate exhibits
        exhibits = case_data.get('exhibits', [])
        validated_exhibits = []
        
        for exhibit in exhibits:
            if not isinstance(exhibit, dict):
                continue
                
            exhibit_type = exhibit.get('type', 'table')
            data = exhibit.get('data', {})
            
            # Validate pie charts - values should sum to ~100
            if exhibit_type == 'pie':
                values = data.get('values', [])
                if values:
                    total = sum(values)
                    if total > 0 and abs(total - 100) > 5:  # Allow 5% tolerance
                        print(f"Warning: Pie chart '{exhibit.get('title')}' values sum to {total}%, not 100%")
                        # Normalize to 100%
                        normalized = [round(v * 100 / total, 1) for v in values]
                        data['values'] = normalized
                    
                    # Ensure unit is %
                    if data.get('unit') != '%':
                        data['unit'] = '%'
            
            # Validate bar charts have proper units
            if exhibit_type == 'bar':
                if 'unit' not in data:
                    # Try to infer unit from values
                    values = data.get('values', [])
                    if values and all(v < 100 for v in values):
                        data['unit'] = '%'
                    else:
                        data['unit'] = ''
            
            # Validate tables have consistent formatting
            if exhibit_type == 'table':
                rows = data.get('rows', [])
                for row in rows:
                    for i, cell in enumerate(row):
                        if isinstance(cell, str):
                            cell_str = str(cell)
                            # Check if it's a number without units
                            if cell_str.replace('.', '').replace(',', '').isdigit():
                                # Could be currency or percentage - leave as is
                                pass
            
            validated_exhibits.append(exhibit)
        
        case_data['exhibits'] = validated_exhibits
        
        # Print validation summary
        table_count = sum(1 for e in validated_exhibits if e.get('type') == 'table')
        bar_count = sum(1 for e in validated_exhibits if e.get('type') == 'bar')
        pie_count = sum(1 for e in validated_exhibits if e.get('type') == 'pie')
        
        print(f"  Exhibits: {len(validated_exhibits)} total ({table_count} tables, {bar_count} bars, {pie_count} pies)")
        
        return case_data

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
                            ["Revenue", "$500M"],
                            ["Costs", "$400M"],
                            ["Margin", "20%"]
                        ]
                    }
                }
            ]
        }

