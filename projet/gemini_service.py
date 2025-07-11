import os
import logging
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "default_key"))

def get_chat_response(user_message, conversation_id=None):
    """
    Get a response from Gemini for the university assistance chatbot
    """
    try:
        # Context for university assistance
        system_context = """
        Vous êtes un assistant virtuel d'une université. Votre rôle est d'aider les étudiants et le personnel 
        universitaire avec leurs questions concernant:
        
        - Les admissions et inscriptions
        - Les programmes d'études et cours
        - Les horaires et calendriers académiques
        - Les services aux étudiants (bibliothèque, résidences, restauration)
        - Les procédures administratives
        - Les bourses et aide financière
        - Les activités étudiantes et clubs
        - L'orientation académique et professionnelle
        - Les services informatiques et techniques
        - Les questions générales sur la vie universitaire
        
        Répondez de manière claire, utile et professionnelle. Si vous n'avez pas d'information 
        spécifique, proposez à l'utilisateur de contacter le service approprié de l'université.
        Utilisez un ton amical mais professionnel, et répondez en français.
        """
        
        # Combine system context with user message
        full_prompt = f"{system_context}\n\nQuestion de l'utilisateur: {user_message}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        
        if response.text:
            return response.text
        else:
            return "Je suis désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer ou contacter le support technique de l'université."
            
    except Exception as e:
        logging.error(f"Error getting Gemini response: {e}")
        return "Je suis temporairement indisponible. Veuillez réessayer dans quelques instants ou contacter directement les services de l'université."

def get_conversation_summary(messages):
    """
    Generate a summary of a conversation for better context
    """
    try:
        if not messages:
            return ""
        
        # Create a conversation history string
        conversation_history = ""
        for msg in messages[-10:]:  # Last 10 messages for context
            role = "Utilisateur" if msg.is_user else "Assistant"
            conversation_history += f"{role}: {msg.content}\n"
        
        prompt = f"""
        Résumez brièvement cette conversation pour maintenir le contexte:
        
        {conversation_history}
        
        Résumé en 2-3 phrases maximum:
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return response.text if response.text else ""
        
    except Exception as e:
        logging.error(f"Error generating conversation summary: {e}")
        return ""
