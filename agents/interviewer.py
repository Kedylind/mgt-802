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
    
    # Case phases
    PHASE_FRAMEWORK = "framework"
    PHASE_DATA_ANALYSIS = "data_analysis"
    PHASE_RECOMMENDATION = "recommendation"
    PHASE_PUSHBACK = "pushback"
    PHASE_CONCLUSION = "conclusion"
    PHASE_COMPLETED = "completed"
    
    # Maximum number of exhibits to provide during interview
    MAX_EXHIBITS = 3
    
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
        self.current_phase = self.PHASE_FRAMEWORK
        self.turn_count = 0
        self.phase_turns = {phase: 0 for phase in [self.PHASE_FRAMEWORK, self.PHASE_DATA_ANALYSIS, 
                                                     self.PHASE_RECOMMENDATION, self.PHASE_PUSHBACK, 
                                                     self.PHASE_CONCLUSION]}
        
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
        else:  # pm_product_case
            return (
                f"Welcome to your product management case interview.\n\n"
                f"{self.case_data.get('prompt', '')}\n\n"
                f"Please share your initial thoughts and approach to this product challenge."
            )
    
    def process_candidate_message(self, message: str) -> Dict[str, Any]:
        """
        Process a message from the candidate and generate an appropriate response.
        
        Args:
            message: The candidate's message
            
        Returns:
            dict: Response with message, phase, and completion status
        """
        # Check if already completed
        if self.current_phase == self.PHASE_COMPLETED:
            return {
                "message": "The interview has concluded. Please proceed to evaluation.",
                "phase": self.PHASE_COMPLETED,
                "completed": True
            }
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "candidate",
            "content": message
        })
        
        self.turn_count += 1
        self.phase_turns[self.current_phase] += 1
        
        # Check if candidate is requesting an exhibit
        if self._is_exhibit_request(message):
            exhibit_response, all_exhibits_provided = self._handle_exhibit_request(message)
            if exhibit_response:
                self.conversation_history.append({
                    "role": "interviewer",
                    "content": exhibit_response
                })
                
                # If all exhibits provided, automatically transition to next phase
                if all_exhibits_provided:
                    should_transition, next_phase = self._should_transition_phase(message)
                    if not should_transition and self.current_phase != self.PHASE_CONCLUSION:
                        # Auto-transition to next phase
                        self.current_phase = self._get_next_phase(self.current_phase)
                        self.phase_turns[self.current_phase] = 0
                
                return {
                    "message": exhibit_response,
                    "phase": self.current_phase,
                    "completed": False
                }
        
        # Check for phase transition
        should_transition, next_phase = self._should_transition_phase(message)
        
        # Generate contextual response using LLM
        response = self._generate_response(message, should_transition, next_phase)
        
        self.conversation_history.append({
            "role": "interviewer",
            "content": response
        })
        
        # Transition if needed
        if should_transition:
            self.current_phase = next_phase
            self.phase_turns[next_phase] = 0
        
        # Check if interview is complete
        completed = self.current_phase == self.PHASE_COMPLETED
        
        return {
            "message": response,
            "phase": self.current_phase,
            "completed": completed
        }
    
    def _is_exhibit_request(self, message: str) -> bool:
        """Check if the message is requesting an exhibit."""
        keywords = ['exhibit', 'data', 'numbers', 'show me', 'can i see', 'information']
        return any(keyword in message.lower() for keyword in keywords)
    
    def _handle_exhibit_request(self, message: str) -> tuple:
        """Handle exhibit requests. Returns (response_text, all_exhibits_provided)."""
        exhibits = self.case_data.get('exhibits', [])
        
        if not exhibits:
            return "I don't have any additional exhibits for this case.", False
        
        # Check if we've reached the maximum exhibit limit
        if len(self.exhibits_released) >= self.MAX_EXHIBITS:
            return "You've received all available exhibits for this interview. Please proceed with your analysis.", True
        
        # Find unreleased exhibits
        unreleased = [ex for i, ex in enumerate(exhibits) if i not in self.exhibits_released]
        
        if not unreleased:
            return "All exhibits have been provided.", True
        
        # Release the next exhibit
        next_exhibit = unreleased[0]
        exhibit_index = exhibits.index(next_exhibit)
        self.exhibits_released.append(exhibit_index)
        
        # Format exhibit for display - show data as generated (form/chart)
        exhibit_text = f"\n**{next_exhibit.get('title', 'Exhibit')}**\n\n"
        
        # Keep the data as-is (it's already in the proper form/chart format from generation)
        data = next_exhibit.get('data', {})
        if isinstance(data, dict):
            exhibit_text += json.dumps(data, indent=2)
        elif isinstance(data, list):
            exhibit_text += json.dumps(data, indent=2)
        else:
            exhibit_text += str(data)
        
        # Check if all exhibits are now released (or hit max limit)
        all_released = len(self.exhibits_released) >= self.MAX_EXHIBITS or len(self.exhibits_released) == len(exhibits)
        
        # Add note if this is the last exhibit
        suffix = ""
        if len(self.exhibits_released) >= self.MAX_EXHIBITS:
            suffix = "\n\n(This is the final exhibit. Please proceed with your analysis.)"
        
        return f"**{next_exhibit.get('title', 'Exhibit')}**\n{exhibit_text}{suffix}", all_released
    
    def _generate_response(self, candidate_message: str, transitioning: bool = False, next_phase: str = None) -> str:
        """
        Generate an interviewer response using OpenAI.
        
        This is a simplified version. In production, you'd use the OpenAI API.
        """
        try:
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            # Build system prompt
            system_prompt = self._build_system_prompt(transitioning, next_phase)
            
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
    
    def _build_system_prompt(self, transitioning: bool = False, next_phase: str = None) -> str:
        """Build the system prompt for the interviewer."""
        context = self.case_data.get('context', {})
        exhibits = self.case_data.get('exhibits', [])
        
        phase_descriptions = {
            self.PHASE_FRAMEWORK: "developing and presenting their framework/approach",
            self.PHASE_DATA_ANALYSIS: "analyzing data and deriving insights",
            self.PHASE_RECOMMENDATION: "formulating their final recommendation",
            self.PHASE_PUSHBACK: "defending their recommendation against challenges",
            self.PHASE_CONCLUSION: "providing final thoughts and summary"
        }
        
        # Build exhibits summary for reference
        exhibits_summary = "\n".join([
            f"  - {ex.get('title', 'Exhibit')}: {ex.get('type', 'data')}"
            for ex in exhibits[:self.MAX_EXHIBITS]  # Only reference exhibits that can be shown
        ]) if exhibits else "  - No exhibits available"
        
        base_prompt = (
            f"You are a case interviewer conducting a {self.interview_mode.replace('_', ' ')} interview. "
            f"The case is about: {self.case_data.get('title', 'a business problem')}.\n\n"
            f"**CRITICAL: You must ONLY use information from the case data below. Do NOT invent, assume, or add any new data, numbers, or facts.**\n\n"
            f"Case Context:\n{json.dumps(context, indent=2)}\n\n"
            f"Available Exhibits (already generated):\n{exhibits_summary}\n\n"
            f"Current Phase: {phase_descriptions.get(self.current_phase, self.current_phase)}\n\n"
            f"Exhibits Released So Far: {len(self.exhibits_released)}/{min(len(exhibits), self.MAX_EXHIBITS)}\n\n"
        )
        
        # Only add transition guidance for non-candidate-led modes
        if self.interview_mode != 'candidate_led':
            if transitioning and next_phase:
                base_prompt += f"TRANSITION: Guide the candidate to the next phase: {phase_descriptions.get(next_phase, next_phase)}.\n\n"
            
            # Add phase-specific guidance for interviewer-led and PM modes
            if self.current_phase == self.PHASE_FRAMEWORK:
                base_prompt += "Focus on: Structure, framework completeness, MECE principles.\n"
            elif self.current_phase == self.PHASE_DATA_ANALYSIS:
                base_prompt += "Focus on: Data interpretation, quantitative skills, insight generation.\n"
            elif self.current_phase == self.PHASE_RECOMMENDATION:
                base_prompt += "Focus on: Clear recommendation, supporting evidence, actionable steps.\n"
            elif self.current_phase == self.PHASE_PUSHBACK:
                base_prompt += "Challenge their recommendation with 1-2 tough questions about assumptions or risks.\n"
            elif self.current_phase == self.PHASE_CONCLUSION:
                base_prompt += "Ask them to summarize key takeaways. After they respond, thank them professionally and conclude: 'Thank you for your thoughtful analysis today. That concludes our interview. You'll receive feedback on your performance shortly.'\n"
        
        if self.interview_mode == 'interviewer_led':
            base_prompt += (
                "Your role:\n"
                "- You are the INTERVIEWER conducting this case interview\n"
                "- Guide the candidate through the case with structured questions\n"
                "- Ask probing questions to test their thinking\n"
                "- **ONLY reference facts, numbers, and context from the case data provided above**\n"
                "- If the candidate asks about data not in exhibits, redirect them: 'That information isn't available. Work with what you have.'\n"
                "- Maintain a professional, neutral tone\n"
                "- Keep responses concise (2-3 sentences)\n"
            )
        elif self.interview_mode == 'candidate_led':
            base_prompt += (
                "Your role:\n"
                "- You are the INTERVIEWER in this candidate-led interview\n"
                "- The candidate drives this interview; answer ONLY when asked\n"
                "- **CRITICAL: Provide ONLY information from the case data above. Do NOT invent any numbers, facts, or context.**\n"
                "- If asked about data not in the case or exhibits, respond: 'I don't have that information available.'\n"
                "- Respond with factual information only - no guidance, hints, or suggestions\n"
                "- If asked about data or exhibits, provide them directly and accurately from the case data\n"
                "- Do NOT ask questions, guide the candidate, or offer recommendations\n"
                "- Only provide minimal clarification if the candidate explicitly asks 'can you clarify?' or similar\n"
                "- Maintain a professional, neutral tone\n"
                "- Keep responses concise (1-2 sentences)\n"
            )
        else:  # pm_product_case
            base_prompt += (
                "Your role:\n"
                "- You are the INTERVIEWER conducting this PM case interview\n"
                "- Evaluate product thinking and user empathy\n"
                "- Ask about trade-offs and prioritization\n"
                "- Challenge assumptions\n"
                "- **ONLY use information from the case data above. Do NOT introduce new facts or market data.**\n"
                "- Keep all discussions grounded in the provided case context\n"
                "- Maintain a professional, neutral tone\n"
                "- Keep responses concise (2-3 sentences)\n"
            )
        
        return base_prompt
    
    def _should_transition_phase(self, candidate_message: str) -> tuple[bool, str]:
        """
        Determine if the interview should transition to the next phase.
        
        Returns:
            tuple: (should_transition, next_phase)
        """
        # Minimum turns per phase
        min_turns = 2
        
        if self.phase_turns[self.current_phase] < min_turns:
            return False, self.current_phase
        
        # Check for transition keywords and conditions
        msg_lower = candidate_message.lower()
        
        if self.current_phase == self.PHASE_FRAMEWORK:
            # Transition when candidate completes framework presentation
            framework_complete = any(keyword in msg_lower for keyword in [
                'those are my', 'that covers', 'framework complete', 'those are the',
                "now let's", 'shall we', 'can we look at', 'what data'
            ])
            # Or after 3-4 turns
            if framework_complete or self.phase_turns[self.current_phase] >= 3:
                return True, self.PHASE_DATA_ANALYSIS
        
        elif self.current_phase == self.PHASE_DATA_ANALYSIS:
            # Transition when candidate starts forming recommendation
            recommendation_signals = any(keyword in msg_lower for keyword in [
                'recommend', 'my recommendation', 'i think we should', 'i would suggest',
                'based on this', 'in conclusion', 'therefore'
            ])
            # Or after 4-5 turns
            if recommendation_signals or self.phase_turns[self.current_phase] >= 4:
                return True, self.PHASE_RECOMMENDATION
        
        elif self.current_phase == self.PHASE_RECOMMENDATION:
            # Transition to pushback after recommendation is given
            if self.phase_turns[self.current_phase] >= 2:
                return True, self.PHASE_PUSHBACK
        
        elif self.current_phase == self.PHASE_PUSHBACK:
            # Transition to conclusion after 1-2 pushback exchanges
            if self.phase_turns[self.current_phase] >= 2:
                return True, self.PHASE_CONCLUSION
        
        elif self.current_phase == self.PHASE_CONCLUSION:
            # Automatically conclude after candidate provides summary (1 turn)
            # The interviewer will give thank you message and close
            if self.phase_turns[self.current_phase] >= 1:
                return True, self.PHASE_COMPLETED
        
        return False, self.current_phase
    
    def _get_next_phase(self, current_phase: str) -> str:
        """Get the next phase in the interview sequence."""
        phase_sequence = [
            self.PHASE_FRAMEWORK,
            self.PHASE_DATA_ANALYSIS,
            self.PHASE_RECOMMENDATION,
            self.PHASE_PUSHBACK,
            self.PHASE_CONCLUSION,
            self.PHASE_COMPLETED
        ]
        try:
            current_index = phase_sequence.index(current_phase)
            return phase_sequence[current_index + 1] if current_index + 1 < len(phase_sequence) else current_phase
        except (ValueError, IndexError):
            return self.PHASE_FRAMEWORK
    
    def get_current_phase(self) -> str:
        """Get the current phase of the interview."""
        return self.current_phase
    
    def is_completed(self) -> bool:
        """Check if the interview is completed."""
        return self.current_phase == self.PHASE_COMPLETED

