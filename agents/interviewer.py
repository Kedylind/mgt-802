"""
Interviewer Agent for conducting case interviews.
"""
import os
import json
from typing import Dict, List, Any
from django.conf import settings


class InterviewerAgent:
    """
    Conducts case interviews with adaptive questioning.
    """
    
    def __init__(self, case_data: Dict[str, Any], interview_mode: str) -> None:
        """
        Initialize the interviewer with a case and mode.
        
        Args:
            case_data: The generated case (from Case model)
            interview_mode: 'interviewer_led', 'candidate_led', or 'product_management'
        """
        self.case_data = case_data
        self.interview_mode = interview_mode
        self.conversation_history = []
        self.exhibits_released = []
        
        # Ensure API key is set
        if not os.environ.get("OPENAI_API_KEY"):
            os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
    
    def get_opening_message(self) -> str:
        """
        Generate the opening message for the interview.
        """
        if self.interview_mode == 'interviewer_led':
            return (
                f"Welcome to your case interview. I'll be guiding you through this case.\n\n"
                f"{self.case_data.get('prompt', '')}\n\n"
                f"Let me know when you're ready to begin, and feel free to ask clarifying questions."
            )
        elif self.interview_mode == 'candidate_led':
            return (
                f"Welcome to your case interview. In this candidate-led format, "
                f"you'll drive the structure and analysis.\n\n"
                f"{self.case_data.get('prompt', '')}\n\n"
                f"Please take a moment to think about your approach, then walk me through your framework."
            )
        else:  # product_management
            return (
                f"Welcome to your product management case interview.\n\n"
                f"{self.case_data.get('prompt', '')}\n\n"
                f"Please share your initial thoughts and approach to this product challenge."
            )
    
    def process_candidate_message(self, message: str) -> str:
        """
        Process a message from the candidate and generate an appropriate response.
        
        Args:
            message: The candidate's message
            
        Returns:
            str: The interviewer's response
        """
        # Add to conversation history
        self.conversation_history.append({
            "role": "candidate",
            "content": message
        })
        
        # Check if candidate is requesting an exhibit
        if self._is_exhibit_request(message):
            exhibit_response = self._handle_exhibit_request(message)
            if exhibit_response:
                self.conversation_history.append({
                    "role": "interviewer",
                    "content": exhibit_response
                })
                return exhibit_response
        
        # Generate contextual response using LLM
        response = self._generate_response(message)
        
        self.conversation_history.append({
            "role": "interviewer",
            "content": response
        })
        
        return response
    
    def _is_exhibit_request(self, message: str) -> bool:
        """Check if the message is requesting an exhibit."""
        keywords = ['exhibit', 'data', 'numbers', 'show me', 'can i see', 'information']
        return any(keyword in message.lower() for keyword in keywords)
    
    def _handle_exhibit_request(self, message: str) -> str:
        """Handle exhibit requests."""
        exhibits = self.case_data.get('exhibits', [])
        
        if not exhibits:
            return "I don't have any additional exhibits for this case."
        
        # Find unreleased exhibits
        unreleased = [ex for i, ex in enumerate(exhibits) if i not in self.exhibits_released]
        
        if not unreleased:
            return "I've already provided all available exhibits."
        
        # Release the next exhibit
        next_exhibit = unreleased[0]
        exhibit_index = exhibits.index(next_exhibit)
        self.exhibits_released.append(exhibit_index)
        
        # Format exhibit for display
        exhibit_text = f"\n**{next_exhibit.get('title', 'Exhibit')}**\n\n"
        
        if next_exhibit.get('type') == 'table':
            exhibit_text += json.dumps(next_exhibit.get('data', {}), indent=2)
        else:
            exhibit_text += str(next_exhibit.get('data', ''))
        
        return f"Here's the exhibit you requested:\n{exhibit_text}\n\nWhat insights do you draw from this data?"
    
    def _generate_response(self, candidate_message: str) -> str:
        """
        Generate an interviewer response using OpenAI.
        
        This is a simplified version. In production, you'd use the OpenAI API.
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Build messages for API
            messages = [{"role": "system", "content": system_prompt}]
            
            for msg in self.conversation_history[-10:]:  # Last 10 messages for context
                role = "user" if msg["role"] == "candidate" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
            
            # Call OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback response
            return (
                "That's an interesting point. Can you elaborate on your reasoning? "
                "What factors are you considering in your analysis?"
            )
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt for the interviewer."""
        context = self.case_data.get('context', {})
        
        base_prompt = (
            f"You are a case interviewer conducting a {self.interview_mode.replace('_', ' ')} interview. "
            f"The case is about: {self.case_data.get('title', 'a business problem')}.\n\n"
            f"Case Context:\n{json.dumps(context, indent=2)}\n\n"
        )
        
        if self.interview_mode == 'interviewer_led':
            base_prompt += (
                "Your role:\n"
                "- Guide the candidate through the case with structured questions\n"
                "- Provide hints if they're stuck\n"
                "- Ask probing questions to test their thinking\n"
                "- Be supportive but challenging\n"
                "- Keep responses concise (2-3 sentences)\n"
            )
        elif self.interview_mode == 'candidate_led':
            base_prompt += (
                "Your role:\n"
                "- Let the candidate drive the structure\n"
                "- Answer their questions directly\n"
                "- Provide data when requested\n"
                "- Gently redirect if they're going off track\n"
                "- Keep responses concise (2-3 sentences)\n"
            )
        else:  # product_management
            base_prompt += (
                "Your role:\n"
                "- Evaluate product thinking and user empathy\n"
                "- Ask about trade-offs and prioritization\n"
                "- Challenge assumptions\n"
                "- Keep responses concise (2-3 sentences)\n"
            )
        
        return base_prompt
