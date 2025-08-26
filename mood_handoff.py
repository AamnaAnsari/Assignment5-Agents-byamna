import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Optional
import time

load_dotenv()

class MoodAnalyzerAgent:
    """Agent 1: Analyzes the user's mood from their message."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_mood(self, user_message: str) -> Dict[str, str]:
        """
        Analyze the user's mood and return the mood type and confidence.
        
        Args:
            user_message (str): User's input message
            
        Returns:
            Dict: Contains mood type and confidence level
        """
        prompt = f"""
        Analyze the mood of the following message and respond ONLY in this exact format:
        MOOD: [mood_type]
        CONFIDENCE: [high/medium/low]
        
        Available mood types: happy, sad, stressed, anxious, excited, angry, calm, neutral
        
        Message: "{user_message}"
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_mood_response(response.text)
        except Exception as e:
            print(f"Error analyzing mood: {e}")
            return {"mood": "neutral", "confidence": "medium"}
    
    def _parse_mood_response(self, response_text: str) -> Dict[str, str]:
        """Parse the mood analysis response."""
        lines = response_text.strip().split('\n')
        mood_data = {"mood": "neutral", "confidence": "medium"}
        
        for line in lines:
            if line.startswith("MOOD:"):
                mood_data["mood"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("CONFIDENCE:"):
                mood_data["confidence"] = line.split(":", 1)[1].strip().lower()
        
        return mood_data

class ActivitySuggesterAgent:
    """Agent 2: Suggests activities based on user's mood."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Activity database by mood
        self.activity_templates = {
            "sad": [
                "Take a walk in nature 🌳",
                "Listen to uplifting music 🎵",
                "Write in a journal 📝",
                "Call a friend or loved one 📞",
                "Watch a favorite movie 🎬"
            ],
            "stressed": [
                "Practice deep breathing exercises 🧘",
                "Try a short meditation session ☯️",
                "Do some light stretching or yoga 💪",
                "Take a warm bath 🛁",
                "Drink herbal tea 🍵"
            ],
            "anxious": [
                "Practice 4-7-8 breathing technique 🌬️",
                "Use the 5-4-3-2-1 grounding method 🌍",
                "Write down your thoughts 📝",
                "Listen to calming sounds 🌊",
                "Progressive muscle relaxation 💆"
            ],
            "angry": [
                "Physical exercise (running, boxing) 🏃",
                "Punch a pillow or scream into it 😤",
                "Write a letter (but don't send it) ✉️",
                "Count slowly to 10 🔢",
                "Listen to heavy metal music 🎸"
            ]
        }
    
    def suggest_activity(self, mood: str, user_message: str = "") -> str:
        """
        Suggest an appropriate activity based on the user's mood.
        
        Args:
            mood (str): Detected mood from Agent 1
            user_message (str): Original user message for context
            
        Returns:
            str: Suggested activity with explanation
        """
        # For neutral or positive moods
        if mood not in ["sad", "stressed", "anxious", "angry"]:
            return f"Your mood '{mood}' seems positive! 😊 Keep doing what makes you happy!"
        
        prompt = f"""
        The user is feeling {mood}. Their message was: "{user_message}"
        
        Suggest ONE appropriate activity that might help them feel better.
        Use this format:
        ACTIVITY: [Activity description with emoji]
        EXPLANATION: [Brief explanation of why this activity helps]
        
        Keep the suggestion practical, helpful, and empathetic.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return self._parse_activity_response(response.text)
        except Exception as e:
            # Fallback to predefined activities if API fails
            fallback_activity = self._get_fallback_activity(mood)
            return f"ACTIVITY: {fallback_activity}\nEXPLANATION: This activity can help improve your mood when feeling {mood}."
    
    def _parse_activity_response(self, response_text: str) -> str:
        """Parse the activity suggestion response."""
        return response_text.strip()
    
    def _get_fallback_activity(self, mood: str) -> str:
        """Get a random activity from predefined templates as fallback."""
        import random
        activities = self.activity_templates.get(mood, ["Take a break and breathe deeply 🌬️"])
        return random.choice(activities)

class MoodHandoffSystem:
    """Main system that coordinates between the two agents."""
    
    def __init__(self):
        self.mood_analyzer = MoodAnalyzerAgent()
        self.activity_suggester = ActivitySuggesterAgent()
    
    def run(self, user_message: str) -> Dict:
        """
        Run the complete analysis and suggestion pipeline.
        
        Args:
            user_message (str): User's input message
            
        Returns:
            Dict: Complete analysis with mood and suggestion
        """
        print("🔍 Agent 1: Analyzing your mood...")
        time.sleep(1)
        
        # Agent 1: Analyze mood
        mood_analysis = self.mood_analyzer.analyze_mood(user_message)
        mood = mood_analysis["mood"]
        confidence = mood_analysis["confidence"]
        
        print(f"✅ Mood detected: {mood} (confidence: {confidence})")
        
        result = {
            "user_message": user_message,
            "mood_analysis": mood_analysis,
            "activity_suggestion": None
        }
        
        # Handoff to Agent 2 if mood requires intervention
        if mood in ["sad", "stressed", "anxious", "angry"]:
            print("🔄 Handing off to Activity Suggester Agent...")
            time.sleep(1)
            
            # Agent 2: Suggest activity
            suggestion = self.activity_suggester.suggest_activity(mood, user_message)
            result["activity_suggestion"] = suggestion
            
            print("✅ Activity suggestion generated!")
        
        return result
    
    def format_results(self, results: Dict) -> str:
        """Format the results in a user-friendly way."""
        mood = results["mood_analysis"]["mood"]
        confidence = results["mood_analysis"]["confidence"]
        
        output = f"""
        🎭 MOOD ANALYSIS RESULTS
        {'=' * 40}
        📝 Your message: "{results['user_message']}"
        🎯 Detected mood: {mood.upper()}
        📊 Confidence: {confidence.upper()}
        {'=' * 40}
        """
        
        if results["activity_suggestion"]:
            output += f"""
        💡 SUGGESTED ACTIVITY
        {'=' * 40}
        {results['activity_suggestion']}
        {'=' * 40}
        
        🌟 Remember: It's okay to feel this way sometimes. 
        Take care of yourself! 💖
            """
        else:
            output += f"""
        🌟 Great! Your mood seems positive. 
        Keep spreading the good vibes! ✨
            """
        
        return output
    
    def run_interactive(self):
        """Run the system in interactive mode."""
        print("=" * 50)
        print("🤖 MOOD ANALYZER WITH HANDOFF SYSTEM")
        print("=" * 50)
        print("I can analyze your mood and suggest helpful activities!")
        print("Type 'quit' to exit at any time.\n")
        
        while True:
            try:
                user_input = input("💬 How are you feeling today? ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using Mood Analyzer! Take care! 👋")
                    break
                
                if not user_input:
                    print("Please share how you're feeling...")
                    continue
                
                # Run the complete analysis
                results = self.run(user_input)
                
                # Display formatted results
                print("\n" + self.format_results(results))
                print("\n" + "=" * 50)
                print("Would you like to share how you're feeling again?")
                
            except KeyboardInterrupt:
                print("\n\nSession ended. Take care of yourself! 💖")
                break
            except Exception as e:
                print(f"\nI apologize, I encountered an error: {str(e)}")
                print("Please try again or take a break and come back later.\n")

# Main execution
if __name__ == "__main__":
    try:
        # Initialize the system
        mood_system = MoodHandoffSystem()
        
     # run
        mood_system.run_interactive()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please make sure you have a .env file with GEMINI_API_KEY=your_api_key")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")