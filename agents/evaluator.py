"""
Evaluator Agent for assessing interview performance.
"""
import os
import json
from typing import Dict, List, Any
from django.conf import settings


class EvaluatorAgent:
    """
    Evaluates candidate performance in case interviews.
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    
    def evaluate_interview(
        self, 
        case_data: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Evaluate the interview performance.
        
        Args:
            case_data: The case that was used
            conversation_history: List of messages (role, content)
            
        Returns:
            dict: Evaluation scores and analysis
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Build evaluation prompt
            evaluation_prompt = self._build_evaluation_prompt(case_data, conversation_history)
            
            # Call OpenAI for evaluation
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._get_evaluator_system_prompt()},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the response
            evaluation_text = response.choices[0].message.content
            
            # Extract structured scores
            scores = self._parse_evaluation(evaluation_text)
            
            return {
                "structure_score": scores.get("structure", 0),
                "hypothesis_score": scores.get("hypothesis", 0),
                "math_score": scores.get("math", 0),
                "insights_score": scores.get("insights", 0),
                "overall_score": scores.get("overall", 0),
                "detailed_analysis": evaluation_text,
                "strengths": scores.get("strengths", []),
                "areas_for_improvement": scores.get("improvements", [])
            }
            
        except Exception as e:
            print(f"Evaluation error: {e}")
            return {
                "structure_score": 0,
                "hypothesis_score": 0,
                "math_score": 0,
                "insights_score": 0,
                "overall_score": 0,
                "detailed_analysis": "Evaluation failed. Please try again.",
                "strengths": [],
                "areas_for_improvement": []
            }
    
    def _get_evaluator_system_prompt(self) -> str:
        """Get the system prompt for the evaluator."""
        return """You are a senior case interview evaluator at a top consulting firm (McKinsey/BCG/Bain).

Your task is to evaluate the candidate's performance across four dimensions:

1. **Structure** (0-100): Did they use a clear framework? Was their approach organized?
2. **Hypothesis** (0-100): Did they form and test hypotheses? Were they data-driven?
3. **Math** (0-100): Were calculations accurate? Did they handle quantitative analysis well?
4. **Insights** (0-100): Did they provide actionable insights? Were recommendations clear?

Provide your evaluation in the following format:

SCORES:
Structure: [0-100]
Hypothesis: [0-100]
Math: [0-100]
Insights: [0-100]
Overall: [0-100]

STRENGTHS:
- [Strength 1]
- [Strength 2]
- [Strength 3]

AREAS FOR IMPROVEMENT:
- [Area 1]
- [Area 2]
- [Area 3]

DETAILED ANALYSIS:
[2-3 paragraphs of detailed feedback]
"""
    
    def _build_evaluation_prompt(self, case_data: Dict[str, Any], conversation_history: List[Dict[str, str]]) -> str:
        """Build the evaluation prompt."""
        # Extract candidate messages
        candidate_messages = [
            msg['content'] for msg in conversation_history 
            if msg.get('role') in ['user', 'candidate']
        ]
        
        conversation_text = "\n\n".join([
            f"Candidate: {msg}" for msg in candidate_messages
        ])
        
        return f"""Case Title: {case_data.get('title', 'Unknown')}
Case Type: {case_data.get('case_type', 'consulting')}

Case Prompt:
{case_data.get('prompt', '')}

Candidate's Responses:
{conversation_text}

Please evaluate this candidate's performance."""
    
    def _parse_evaluation(self, evaluation_text: str) -> Dict[str, Any]:
        """Parse the evaluation text to extract scores and feedback."""
        scores = {
            "structure": 0,
            "hypothesis": 0,
            "math": 0,
            "insights": 0,
            "overall": 0,
            "strengths": [],
            "improvements": []
        }
        
        lines = evaluation_text.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Parse scores
            if 'Structure:' in line:
                try:
                    scores['structure'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'Hypothesis:' in line:
                try:
                    scores['hypothesis'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'Math:' in line:
                try:
                    scores['math'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'Insights:' in line:
                try:
                    scores['insights'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            elif 'Overall:' in line:
                try:
                    scores['overall'] = int(''.join(filter(str.isdigit, line)))
                except:
                    pass
            
            # Parse sections
            elif 'STRENGTHS:' in line:
                current_section = 'strengths'
            elif 'AREAS FOR IMPROVEMENT:' in line or 'IMPROVEMENTS:' in line:
                current_section = 'improvements'
            elif 'DETAILED ANALYSIS:' in line:
                current_section = None
            elif line.startswith('-') and current_section:
                item = line[1:].strip()
                if item:
                    scores[current_section].append(item)
        
        return scores
