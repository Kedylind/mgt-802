"""
Coach Agent for generating personalized feedback and recommendations.
"""
import os
from typing import Dict, List, Any
from django.conf import settings


class CoachAgent:
    """
    Generates personalized coaching feedback and drill recommendations.
    """
    
    def __init__(self):
        """Initialize the coach."""
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    
    def generate_feedback(
        self, 
        evaluation_data: Dict[str, Any],
        case_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate personalized coaching feedback.
        
        Args:
            evaluation_data: Results from EvaluatorAgent
            case_data: The case that was used
            
        Returns:
            dict: Coaching feedback and recommendations
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Build coaching prompt
            coaching_prompt = self._build_coaching_prompt(evaluation_data, case_data)
            
            # Call OpenAI for coaching
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": self._get_coach_system_prompt()},
                    {"role": "user", "content": coaching_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse the response
            coaching_text = response.choices[0].message.content
            
            # Extract structured recommendations
            recommendations = self._parse_recommendations(coaching_text)
            
            return {
                "summary": recommendations.get("summary", ""),
                "strengths": evaluation_data.get("strengths", []),
                "areas_for_improvement": evaluation_data.get("areas_for_improvement", []),
                "recommendations": recommendations.get("drills", []),
                "next_steps": recommendations.get("next_steps", []),
                "full_feedback": coaching_text
            }
            
        except Exception as e:
            print(f"Coaching error: {e}")
            return {
                "summary": "Unable to generate coaching feedback at this time.",
                "strengths": evaluation_data.get("strengths", []),
                "areas_for_improvement": evaluation_data.get("areas_for_improvement", []),
                "recommendations": [],
                "next_steps": [],
                "full_feedback": ""
            }
    
    def _get_coach_system_prompt(self) -> str:
        """Get the system prompt for the coach."""
        return """You are an experienced case interview coach who has helped hundreds of candidates succeed at top consulting firms.

Your role is to:
1. Provide encouraging, actionable feedback
2. Recommend specific drills and practice exercises
3. Suggest concrete next steps for improvement
4. Be supportive while being honest about areas needing work

Format your response as follows:

SUMMARY:
[2-3 sentence overview of performance]

RECOMMENDED DRILLS:
- [Drill 1: Specific exercise with description]
- [Drill 2: Specific exercise with description]
- [Drill 3: Specific exercise with description]

NEXT STEPS:
- [Action item 1]
- [Action item 2]
- [Action item 3]

Keep your tone encouraging and specific. Focus on actionable advice."""
    
    def _build_coaching_prompt(self, evaluation_data: Dict[str, Any], case_data: Dict[str, Any]) -> str:
        """Build the coaching prompt."""
        scores_text = f"""Performance Scores:
- Structure: {evaluation_data.get('structure_score', 0)}/100
- Hypothesis: {evaluation_data.get('hypothesis_score', 0)}/100
- Math: {evaluation_data.get('math_score', 0)}/100
- Insights: {evaluation_data.get('insights_score', 0)}/100
- Overall: {evaluation_data.get('overall_score', 0)}/100

Strengths:
{chr(10).join(['- ' + s for s in evaluation_data.get('strengths', [])])}

Areas for Improvement:
{chr(10).join(['- ' + a for a in evaluation_data.get('areas_for_improvement', [])])}

Case Type: {case_data.get('case_type', 'consulting')}
"""
        
        return f"""{scores_text}

Based on this performance, please provide personalized coaching feedback with specific drill recommendations."""
    
    def _parse_recommendations(self, coaching_text: str) -> Dict[str, Any]:
        """Parse the coaching text to extract recommendations."""
        recommendations = {
            "summary": "",
            "drills": [],
            "next_steps": []
        }
        
        lines = coaching_text.split('\n')
        current_section = None
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            
            if 'SUMMARY:' in line:
                current_section = 'summary'
            elif 'RECOMMENDED DRILLS:' in line or 'DRILLS:' in line:
                current_section = 'drills'
            elif 'NEXT STEPS:' in line:
                current_section = 'next_steps'
            elif line.startswith('-') and current_section in ['drills', 'next_steps']:
                item = line[1:].strip()
                if item:
                    recommendations[current_section].append(item)
            elif current_section == 'summary' and line and not line.endswith(':'):
                summary_lines.append(line)
        
        recommendations['summary'] = ' '.join(summary_lines)
        
        return recommendations
