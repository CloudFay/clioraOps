"""
Conversational interface for ClioraOps.

Makes ClioraOps feel like a mentor, not just a command executor.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.context import SessionContext
from clioraOps_cli.integrations.ai_provider import AIClient


@dataclass
class ConversationMessage:
    """A single message in the conversation."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: str


class ConversationManager:
    """
    Manages natural language conversations with the user.
    
    This is what makes ClioraOps feel like a real mentor.
    """
    
    def __init__(self, mode: Mode, context: SessionContext, ai: AIClient):
        self.mode = mode
        self.context = context
        self.ai = ai
        self.conversation_history: List[ConversationMessage] = []
        
    def is_conversational_input(self, user_input: str) -> bool:
        """
        Determine if input is conversational vs a command.
        
        Conversational patterns:
        - Questions: "what is", "how do", "why does", "can you"
        - Statements: "I want to", "show me", "tell me about"
        - Follow-ups: "yes", "no", "more", "explain"
        """
        conversational_indicators = [
            # Questions
            "what", "how", "why", "when", "where", "who",
            "can you", "could you", "would you",
            "do you", "does", "is", "are",
            
            # Requests
            "show me", "tell me", "explain", "help me",
            "i want", "i need", "i don't understand", "i am", "i'm",
            "tell", "show", "describe", "analyze",
            
            # Follow-ups
            "yes", "no", "sure", "okay", "ok",
            "more", "continue", "go on", "next",
            "example", "demo", "thanks", "thank you",
        ]
        
        # Check if input starts with any conversational indicator
        input_lower = user_input.lower().strip()
        
        # Single word responses (yes, no, more, etc.)
        if input_lower in ["yes", "no", "sure", "ok", "okay", "more", "next", "continue"]:
            return True
        
        # Starts with conversational word
        for indicator in conversational_indicators:
            if input_lower.startswith(indicator):
                return True
        
        # Contains question mark
        if "?" in user_input:
            return True
        
        return False
    
    def handle_conversation(self, user_input: str) -> str:
        """
        Handle conversational input and return AI response.
        
        This uses Gemini (or fallback providers) with rich context to generate natural responses.
        """
        
        # Build conversation context
        context_data = self.context.get_context_for_ai()
        
        # Build system prompt based on mode
        system_prompt = self._build_system_prompt()
        
        # Build conversation history for context
        conversation_context = self._format_conversation_history()
        
        # Build full prompt for AI
        full_prompt = f"""
{system_prompt}

CONVERSATION CONTEXT:
{conversation_context}

USER LEARNING STATE:
- Current topic: {context_data['learning']['current_topic'] or 'Getting started'}
- Concepts learned: {', '.join(context_data['learning']['concepts_learned']) or 'None yet'}
- Recent commands: {', '.join(context_data['recent_commands']) or 'None'}

USER INPUT:
{user_input}

RESPONSE GUIDELINES:
- Be conversational and friendly
- Reference their learning journey
- Offer to show examples or diagrams
- Ask follow-up questions to guide learning
- If they seem confused, break it down simpler
- Celebrate their progress!

YOUR RESPONSE:
"""
        
        # Get response from AI
        try:
            from clioraOps_cli.integrations.ai_provider import format_ai_response
            history_list = self._get_history_list()
            ai_response = self.ai.ask(full_prompt, history_list)
            
            if ai_response.success:
                # Add to conversation history
                self._add_to_history("user", user_input)
                self._add_to_history("assistant", ai_response.content)
                
                return format_ai_response(ai_response)
            else:
                # Still add the error to history for context
                return format_ai_response(ai_response)
                
        except Exception as e:
            return self._fallback_response(user_input)
    
    def _build_system_prompt(self) -> str:
        """Build system prompt based on mode."""
        
        if self.mode == Mode.BEGINNER:
            return """
You are a friendly DevOps mentor helping a beginner learn.

TONE: Encouraging, patient, uses simple analogies
STYLE: Conversational, breaks complex topics into simple steps
APPROACH:
- Use real-world analogies (shipping containers, assembly lines, etc.)
- Explain WHY before HOW
- Offer hands-on examples
- Check understanding frequently
- Celebrate small wins

EXAMPLE RESPONSE STYLE:
"Great question! Think of it like this... [analogy]. 
Let me show you how this works in practice. [example]
Making sense? Want to try it yourself?"
"""
        else:  # ARCHITECT
            return """
You are a technical DevOps architect mentoring an experienced engineer.

TONE: Professional, technical, reference-rich
STYLE: Concise, focused on trade-offs, scalability, and security
APPROACH:
- Reference industry standards (12-Factor, Google SRE Book, STRIDE)
- Discuss architectural trade-offs, blast targets, and failure modes
- Encourage threat modeling and system-level risk assessment
- Provide production-ready examples and cost-aware recommendations
- Link to complex architecture patterns and security controls

EXAMPLE RESPONSE STYLE:
"Scaling this component via [pattern] introduces [trade-off]. 
From a STRIDE perspective, consider [threat] at the [layer].
Mitigation follows the [standard]. In production, monitor [metric]."
"""
    
    def _format_conversation_history(self, last_n: int = 5) -> str:
        """Format recent conversation for context."""
        
        if not self.conversation_history:
            return "New conversation"
        
        recent = self.conversation_history[-last_n:]
        
        formatted = []
        for msg in recent:
            prefix = "User:" if msg.role == "user" else "Assistant:"
            formatted.append(f"{prefix} {msg.content}")
        
        return "\n".join(formatted)

    def _get_history_list(self, last_n: int = 5) -> List[Dict]:
        """Get recent conversation as a list of dicts for AI providers."""
        if not self.conversation_history:
            return []
        
        recent = self.conversation_history[-last_n:]
        return [{"role": msg.role, "content": msg.content} for msg in recent]

    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        from datetime import datetime
        
        self.conversation_history.append(ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        ))
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback response when AI providers are unavailable."""
        
        if self.mode == Mode.BEGINNER:
            return """
I'd love to chat about that! However, I need an AI brain to be connected first.

**Connecting a brain is easy:**
Run this command right here:
> setup ai gemini YOUR_API_KEY_HERE

(You can get a free key from: https://aistudio.google.com/app/apikey)

Once done, I'll be ready to answer all your questions!
"""
        else:
            return """
Conversational mode requires an AI provider. Gemini is recommended.

To activate, run:
  > setup ai gemini <key>
  > switch brain gemini

Alternatively, if you have Ollama running locally, I'll detect it automatically.
"""
    
    def suggest_next_action(self) -> Optional[str]:
        """
        Suggest what the user might want to do next.
        
        This makes the conversation feel guided and helpful.
        """
        
        # Based on context, suggest next steps
        concepts_learned = self.context.concepts_learned
        current_topic = self.context.current_topic
        
        suggestions = []
        
        if not concepts_learned:
            suggestions.append("💡 New here? Try asking: 'What should I learn first?'")
        
        if current_topic:
            suggestions.append(f"💡 Continue with: 'Show me an example of {current_topic}'")
        
        if self.context.safe_commands_run:
            suggestions.append("💡 Ask: 'What architecture would use these commands?'")
        
        if suggestions:
            return "\n\n" + "\n".join(suggestions)
        
        return None
    
    def update_mode(self, mode: Mode) -> None:
        """Update the current mode."""
        self.mode = mode