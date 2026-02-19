import os
import requests
import abc
from enum import Enum
from typing import Optional, List, Dict, Any, Type
from dataclasses import dataclass


class AIProviderType(Enum):
    """Available AI providers."""
    GEMINI = "gemini"
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class AIResponse:
    """Standardized AI response across all providers."""
    success: bool
    content: str
    provider: AIProviderType
    error: Optional[str] = None


class BaseAIProvider(abc.ABC):
    """Abstract base class for AI providers."""
    
    @abc.abstractmethod
    def name(self) -> AIProviderType:
        pass
        
    @abc.abstractmethod
    def setup(self, api_key: str) -> None:
        """Dynamically configure the provider with an API key."""
        pass
        
    @abc.abstractmethod
    def is_available(self) -> bool:
        pass
        
    @abc.abstractmethod
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        pass


class GeminiProvider(BaseAIProvider):
    """Google Gemini provider."""
    
    def __init__(self, model: str = "gemini-2.0-flash"):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.model_name = model
        
    def name(self) -> AIProviderType:
        return AIProviderType.GEMINI
        
    def setup(self, api_key: str) -> None:
        if "|" in api_key:
            self.api_key, self.model_name = api_key.split("|", 1)
        else:
            self.api_key = api_key


    def is_available(self) -> bool:
        return self.api_key is not None
        
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        try:
            # Using v1beta for system_instruction support
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            
            # Format history
            contents = []
            system_instr = None
            
            if system_prompt:
                system_instr = {"parts": [{"text": system_prompt}]}
                
            if context:
                for msg in context[-5:]:
                    role = "user" if msg.get('role') == 'user' else "model"
                    contents.append({"role": role, "parts": [{"text": msg.get('content', '')}]})
            
            contents.append({"role": "user", "parts": [{"text": prompt}]})
            
            payload = {"contents": contents}
            if system_instr:
                payload["system_instruction"] = system_instr

            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                resp_json = response.json()
                try:
                    content = resp_json['candidates'][0]['content']['parts'][0]['text']
                    return AIResponse(success=True, content=content, provider=self.name())
                except (KeyError, IndexError):
                    return AIResponse(success=False, content="", provider=self.name(), error="Unexpected API response structure")
            
            error_msg = f"HTTP {response.status_code}"
            
            if response.status_code == 429:
                return AIResponse(
                    success=False, 
                    content="", 
                    provider=self.name(), 
                    error="Quota Exceeded. New keys take ~10m to activate.\n"
                          "💡 **PRO TIP**: Install Ollama (https://ollama.com) for unlimited OFFLINE mentoring!"
                )
                
            try:
                error_msg += f": {response.json().get('error', {}).get('message', response.text)}"
            except:
                error_msg += f": {response.text}"
                
            return AIResponse(success=False, content="", provider=self.name(), error=error_msg)
        except Exception as e:
            return AIResponse(success=False, content="", provider=self.name(), error=str(e))


class OllamaProvider(BaseAIProvider):
    """Ollama local provider."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        
    def name(self) -> AIProviderType:
        return AIProviderType.OLLAMA
        
    def setup(self, api_key: str) -> None:
        """Ollama doesn't use API keys, but we could use this for base_url."""
        self.base_url = api_key

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=1)
            return response.status_code == 200 and len(response.json().get('models', [])) > 0
        except:
            return False
            
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        try:
            model = self._get_best_model()
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if context:
                messages.extend(context[-5:])
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={"model": model, "messages": messages, "stream": False},
                timeout=30
            )
            if response.status_code == 200:
                return AIResponse(success=True, content=response.json().get('message', {}).get('content', ''), provider=self.name())
            return AIResponse(success=False, content="", provider=self.name(), error=f"HTTP {response.status_code}")
        except Exception as e:
            return AIResponse(success=False, content="", provider=self.name(), error=str(e))
            
    def _get_best_model(self) -> str:
        # Simplified model selection
        return "llama3"


class OpenAIProvider(BaseAIProvider):
    """OpenAI provider."""
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.api_key = os.environ.get('OPENAI_API_KEY')
        
    def name(self) -> AIProviderType:
        return AIProviderType.OPENAI
        
    def setup(self, api_key: str) -> None:
        self.api_key = api_key

    def is_available(self) -> bool:
        return self.api_key is not None
        
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            if context:
                messages.extend(context[-5:])
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages
                },
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                return AIResponse(success=True, content=content, provider=self.name())
            
            return AIResponse(success=False, content="", provider=self.name(), error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return AIResponse(success=False, content="", provider=self.name(), error=str(e))


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.api_key = os.environ.get('ANTHROPIC_API_KEY')
        
    def name(self) -> AIProviderType:
        return AIProviderType.ANTHROPIC
        
    def setup(self, api_key: str) -> None:
        self.api_key = api_key

    def is_available(self) -> bool:
        return self.api_key is not None
        
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        try:
            messages = []
            if context:
                messages.extend(context[-5:])
            messages.append({"role": "user", "content": prompt})
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            data = {
                "model": self.model,
                "max_tokens": 1024,
                "messages": messages
            }
            
            if system_prompt:
                data["system"] = system_prompt
                
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                content = response.json()['content'][0]['text']
                return AIResponse(success=True, content=content, provider=self.name())
            
            return AIResponse(success=False, content="", provider=self.name(), error=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            return AIResponse(success=False, content="", provider=self.name(), error=str(e))


class LocalFallbackProvider(BaseAIProvider):
    """Intelligent local knowledge base fallback."""
    
    def __init__(self):
        from clioraOps_cli.integrations.local_knowledge import create_knowledge_base
        self.knowledge_base = create_knowledge_base()
    
    def name(self) -> AIProviderType:
        return AIProviderType.LOCAL
        
    def setup(self, api_key: str) -> None:
        pass

    def is_available(self) -> bool:
        return True
        
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        """
        Generate intelligent response using local knowledge base.
        
        Args:
            prompt: User's input prompt
            context: Conversation history (optional)
            system_prompt: System context (beginner/architect mode)
        
        Returns:
            AIResponse with knowledge base content
        """
        try:
            # Extract actual user prompt from full prompt if needed
            user_prompt = prompt
            if "USER INPUT:" in prompt:
                # Fallback handles the full prompt structure from conversation.py
                parts = prompt.split("USER INPUT:")
                if len(parts) > 1:
                    user_prompt = parts[1].strip().split("\n")[0]
            
            # Get intelligent response from knowledge base
            response = self.knowledge_base.get_response(user_prompt, system_prompt or "")
            
            return AIResponse(success=True, content=response, provider=self.name())
        except Exception as e:
            # Graceful fallback if knowledge base fails
            return AIResponse(
                success=True,
                content=f"I'm here to help! You asked: {prompt[:100]}...\n\nConnect an AI brain for detailed responses: setup ai gemini YOUR_KEY",
                provider=self.name()
            )


class AIClient:
    """
    Manager for multiple AI providers with fallback logic.
    """
    
    def __init__(self, mode=None):
        self.mode = mode
        self.providers: List[BaseAIProvider] = [
            GeminiProvider(),
            OpenAIProvider(),
            AnthropicProvider(),
            OllamaProvider(),
            LocalFallbackProvider()
        ]
        self.active_override: Optional[AIProviderType] = None
        
    def chat(self, prompt: str, context: Optional[List[Dict]] = None, system_prompt: Optional[str] = None) -> AIResponse:
        if not system_prompt:
            system_prompt = self._build_system_prompt()
            
        # Try active override first
        if self.active_override:
            for provider in self.providers:
                if provider.name() == self.active_override:
                    if provider.is_available():
                        response = provider.chat(prompt, context, system_prompt)
                        # RETURN even if it fails, because this was an explicit override
                        return response
            
        # Fallback to normal priority
        failures = []
        for provider in self.providers:
            if provider.is_available() and provider.name() != AIProviderType.LOCAL:
                response = provider.chat(prompt, context, system_prompt)
                if response.success:
                    return response
                else:
                    failures.append(f"{provider.name().value}: {response.error}")
        
        # Last resort: Local
        local = self.providers[-1]
        response = local.chat(prompt, context, system_prompt)
        if failures:
            response.content = f"(Local Fallback) {response.content}\n\nNote: Cloud providers failed:\n- " + "\n- ".join(failures)
        return response

    def _build_system_prompt(self) -> str:
        from clioraOps_cli.core.modes import Mode
        if self.mode == Mode.BEGINNER:
            return "You are a DevOps mentor for beginners."
        return "You are a DevOps expert architect."

    def ask(self, question: str, context: Optional[List[Dict]] = None) -> AIResponse:
        return self.chat(question, context)

    def explain(self, topic: str) -> str:
        return self.ask(f"Explain: {topic}")

    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers if p.name() != AIProviderType.LOCAL)

    def get_provider_status(self) -> Dict[str, bool]:
        return {p.name().value: p.is_available() for p in self.providers}

    def switch_to_provider(self, name: str) -> bool:
        """Manually override the active provider."""
        try:
            target = AIProviderType(name.lower())
            for p in self.providers:
                if p.name() == target:
                    if p.is_available():
                        self.active_override = target
                        return True
            return False
        except ValueError:
            return False

    def configure_provider(self, name: str, key: str) -> bool:
        """Dynamically configure a provider with a key."""
        try:
            target = AIProviderType(name.lower())
            for p in self.providers:
                if p.name() == target:
                    p.setup(key)
                    # Automatically switch to it if it becomes available
                    if p.is_available():
                        self.active_override = target
                        return True
            return False
        except ValueError:
            return False


def create_ai_client(mode=None) -> AIClient:
    return AIClient(mode)

def format_ai_response(response: AIResponse) -> str:
    badges = {
        AIProviderType.GEMINI: "🌟",
        AIProviderType.OPENAI: "🤖",
        AIProviderType.ANTHROPIC: "🧪",
        AIProviderType.OLLAMA: "🦙",
        AIProviderType.LOCAL: "📚"
    }
    badge = badges.get(response.provider, "🤖")
    
    if not response.success:
        return f"❌ {badge} {response.provider.value.capitalize()} Error: {response.error or 'Unknown error'}"
        
    return f"{badge} {response.content}"