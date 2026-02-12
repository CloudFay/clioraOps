"""
Conversational interface for ClioraOps.

Makes ClioraOps feel like a mentor, not just a command executor.
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.core.context import SessionContext
from clioraOps_cli.integrations.copilot import GitHubCopilotIntegration


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
    
    def __init__(self, mode: Mode, context: SessionContext, copilot: GitHubCopilotIntegration):
        self.mode = mode
        self.context = context
        self.copilot = copilot
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
            "i want", "i need", "i don't understand",
            
            # Follow-ups
            "yes", "no", "sure", "okay", "ok",
            "more", "continue", "go on", "next",
            "example", "demo",
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
        
        This uses Copilot with rich context to generate natural responses.
        """
        
        # Build conversation context
        context_data = self.context.get_context_for_ai()
        
        # Build system prompt based on mode
        system_prompt = self._build_system_prompt()
        
        # Build conversation history for context
        conversation_context = self._format_conversation_history()
        
        # Build full prompt for Copilot
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
        
        # Get response from Copilot
        try:
            response = self.copilot.ask(full_prompt, self.mode)
            
            if response.success:
                response_text = response.output
                
                # Add to conversation history
                self._add_to_history("user", user_input)
                self._add_to_history("assistant", response_text)
                
                return response_text
            else:
                return self._fallback_response(user_input)
                
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
STYLE: Concise, focused on trade-offs and best practices
APPROACH:
- Reference industry standards (12-Factor, Google SRE Book)
- Discuss trade-offs and failure modes
- Provide production-ready examples
- Link to architecture patterns

EXAMPLE RESPONSE STYLE:
"This follows the [pattern] from [source]. 
Key trade-off: [A vs B]. In production, consider [implications].
Relevant: [architecture pattern or standard]."
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
    
    def _add_to_history(self, role: str, content: str):
        """Add message to conversation history."""
        from datetime import datetime
        
        self.conversation_history.append(ConversationMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat()
        ))
    
    def _fallback_response(self, user_input: str) -> str:
        """Fallback response when Copilot unavailable."""
        
        if self.mode == Mode.BEGINNER:
            return """
I'd love to chat about that! However, I need GitHub Copilot CLI to have 
natural conversations with you.

To enable this:
1. Install GitHub CLI: https://cli.github.com/
2. Install Copilot extension: gh extension install github/gh-copilot
3. Restart ClioraOps

In the meantime, you can use commands like:
  - try <command>  (test commands safely)
  - design <architecture>  (see architecture diagrams)
  - learn <topic>  (guided learning)

Want to try one of those?
"""
        else:
            return """
Conversational mode requires GitHub Copilot CLI integration.

Setup:
  gh extension install github/gh-copilot

Available commands: try, design, learn, explain
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