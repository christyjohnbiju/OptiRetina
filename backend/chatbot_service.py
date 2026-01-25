import os
import json
from openai import OpenAI

class ChatbotService:
    def __init__(self):
        # Support for OpenAI or Groq (Free Tier)
        self.api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("GROQ_API_KEY")
        self.base_url = os.environ.get("OPENAI_BASE_URL")
        self.model = os.environ.get("AI_MODEL", "gpt-3.5-turbo")
        
        # Auto-configure Groq if using Groq Key
        if os.environ.get("GROQ_API_KEY"):
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = "llama-3.3-70b-versatile" # High quality free model
            
        self.client = None
        if self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url # None by default (uses OpenAI)
            )
        else:
            print("Warning: No API_KEY found. Chatbot running in MOCK mode.")

    def _get_system_prompt(self, context: dict) -> str:
        """
        Constructs a safe, context-aware system prompt.
        """
        diagnosis = context.get('prediction', 'Unknown').replace('_', ' ')
        confidence = str(round(float(context.get('confidence', 0)) * 100, 1)) + "%"
        tips = "\n".join([f"- {tip}" for tip in context.get('tips', [])])

        return f"""
You are a helpful and empathetic Medical Assistant for a patient who has just been analyzed for Diabetic Retinopathy (DR).
Your goal is to explain their condition, answer questions, and provide lifestyle advice based on their report.

PATIENT CONTEXT:
- Diagnosis: {diagnosis}
- Recommended Tips:
{tips}

RULES:
1. **Safety First**: NEVER provide dosage information or prescribe specific medications. Always advise consulting their doctor for medical decisions.
2. **Context Awareness**: Your answers must be tailored to their specific diagnosis ({diagnosis}). Do not give advice for Stage 4 if they have Stage 0.
3. **Empathy**: Use a reassuring, professional, and simple tone. Avoid overly complex medical jargon without explanation.
4. **Disclaimer**: If asked about prognosis or severe symptoms, remind them you are an AI assistant and not a doctor.
5. **No Confidence Scores**: Do not mention AI confidence scores or probabilities in your responses.
6. **Scope**: Stick to eye health, diabetes management, diet, and lifestyle interactions.

If the user asks "What is my condition?", explain {diagnosis} in simple terms using the context provided.
"""

    def get_response(self, query: str, context: dict) -> str:
        """
        Generates a response using OpenAI or a Mock fallback.
        """
        if not self.client:
            return self._get_mock_response(query, context)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(context)},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return "I'm having trouble connecting to my knowledge base right now. Please try again later. (Error: API Connection Failed)"

    def _get_mock_response(self, query: str, context: dict) -> str:
        """
        Fallback responses for when OpenAI key is missing.
        """
        diagnosis = context.get('prediction', 'Unknown').replace('_', ' ')
        q_lower = query.lower()

        header = "[MOCK MODE - No API Key]\n"

        if "condition" in q_lower or "what do i have" in q_lower:
            return f"{header}Based on the analysis, you have **{diagnosis}**. Please refer to the 'Medical Recommendations' section for initial steps."
        elif "cure" in q_lower or "reversible" in q_lower:
            return f"{header}Diabetic Retinopathy management focuses on controlling blood sugar to prevent progression. Early stages can sometimes improve, but advanced stages require medical intervention."
        elif "precautions" in q_lower or "tips" in q_lower:
             return f"{header}General precautions include: Strict blood sugar control, regular exercise, and annual eye exams."
        else:
            return f"{header}I am a demo chatbot. I see you have {diagnosis}. Please add an OPENAI_API_KEY to get real AI responses."
