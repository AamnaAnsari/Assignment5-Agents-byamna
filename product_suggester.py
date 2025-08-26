import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Optional
import textwrap
import time

# Load environment variables
load_dotenv()

class ProductSuggester:
    """
    A smart AI agent that suggests relevant products based on user needs and symptoms.
    Uses Google's Gemini API for intelligent product recommendations.
    """
    
    def __init__(self):
        """Initialize the Gemini API with the provided key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables. Please check your .env file.")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model with safety settings
        generation_config = {
            "temperature": 0.6,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 600,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Product database 
        self.product_database = {
            "pain_relief": [
                {
                    "name": "PainAway Extra Strength",
                    "description": "Fast-acting pain reliever for headaches and body aches",
                    "active_ingredient": "Acetaminophen 500mg",
                    "price": "$8.99",
                    "benefits": "Provides quick relief from headaches, muscle pain, and minor arthritis pain"
                },
                {
                    "name": "Migraine Relief Caplets",
                    "description": "Specifically formulated for migraine symptoms",
                    "active_ingredient": "Acetaminophen, Aspirin, Caffeine",
                    "price": "$12.99",
                    "benefits": "Targets migraine pain, sensitivity to light/sound, and nausea"
                }
            ],
            "cold_flu": [
                {
                    "name": "Cold & Flu Maximum Strength",
                    "description": "Multi-symptom relief for cold and flu",
                    "active_ingredient": "Acetaminophen, Dextromethorphan, Phenylephrine",
                    "price": "$10.99",
                    "benefits": "Relieves fever, cough, nasal congestion, and body aches"
                }
            ],
            "allergy": [
                {
                    "name": "Allergy Relief Non-Drowsy",
                    "description": "24-hour allergy relief without drowsiness",
                    "active_ingredient": "Loratadine 10mg",
                    "price": "$15.99",
                    "benefits": "Provides all-day relief from sneezing, runny nose, and itchy eyes"
                }
            ],
            "digestive_health": [
                {
                    "name": "Stomach Soother Antacid",
                    "description": "Fast relief from heartburn and acid indigestion",
                    "active_ingredient": "Calcium Carbonate",
                    "price": "$6.99",
                    "benefits": "Neutralizes stomach acid on contact"
                }
            ],
            "first_aid": [
                {
                    "name": "Advanced Healing Bandages",
                    "description": "Bandages with advanced healing technology",
                    "active_ingredient": "N/A",
                    "price": "$4.99",
                    "benefits": "Promotes faster healing and protects against infection"
                }
            ]
        }
        
        # prompt for the AI
        self.system_prompt = """You are a helpful and knowledgeable pharmacy assistant at Smart Health Store. 
        Your role is to recommend appropriate products based on customer symptoms and needs.
        
        IMPORTANT GUIDELINES:
        1. Always recommend specific products from our inventory when possible
        2. Explain why the product is suitable for their symptoms
        3. Mention key ingredients and benefits
        4. Include safety information and recommend consulting a doctor for serious conditions
        5. Be empathetic and professional
        6. If unsure, recommend speaking with our in-store pharmacist
        
        Available product categories: pain_relief, cold_flu, allergy, digestive_health, first_aid"""
    
    def analyze_user_query(self, user_input: str) -> Dict:
        """
        Analyze the user's query to understand their needs and symptoms.
        
        Args:
            user_input (str): The user's description of their need or symptom
            
        Returns:
            Dict: Analysis containing category, severity, and relevant products
        """
        prompt = f"""
        {self.system_prompt}
        
        Customer query: "{user_input}"
        
        Analyze this query and determine:
        1. What category does this fall into? (pain_relief, cold_flu, allergy, digestive_health, first_aid, or unknown)
        2. How severe does this sound? (mild, moderate, severe)
        3. What specific symptoms are mentioned?
        4. Which products from our inventory might be appropriate?
        
        Respond in this format:
        CATEGORY: [category]
        SEVERITY: [severity]
        SYMPTOMS: [comma separated symptoms]
        POTENTIAL_PRODUCTS: [comma separated product names]
        """
        
        try:
            response = self.model.generate_content(prompt)
            analysis = self._parse_analysis_response(response.text)
            return analysis
        except Exception as e:
            print(f"Error analyzing query: {e}")
            return {
                "category": "unknown",
                "severity": "unknown",
                "symptoms": [],
                "potential_products": []
            }
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the analysis response from Gemini."""
        lines = response_text.strip().split('\n')
        analysis = {
            "category": "unknown",
            "severity": "unknown",
            "symptoms": [],
            "potential_products": []
        }
        
        for line in lines:
            if line.startswith("CATEGORY:"):
                analysis["category"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("SEVERITY:"):
                analysis["severity"] = line.split(":", 1)[1].strip().lower()
            elif line.startswith("SYMPTOMS:"):
                symptoms = line.split(":", 1)[1].strip()
                analysis["symptoms"] = [s.strip() for s in symptoms.split(",")]
            elif line.startswith("POTENTIAL_PRODUCTS:"):
                products = line.split(":", 1)[1].strip()
                analysis["potential_products"] = [p.strip() for p in products.split(",")]
        
        return analysis
    
    def generate_recommendation(self, user_input: str, analysis: Dict) -> str:
        """
        Generate a product recommendation based on the analysis.
        
        Args:
            user_input (str): Original user query
            analysis (Dict): Analysis of the user's needs
            
        Returns:
            str: Formatted recommendation with explanation
        """
        category = analysis["category"]
        
        # Get relevant products from the category
        relevant_products = self.product_database.get(category, [])
        
        if not relevant_products:
            # Fallback to general recommendation
            prompt = f"""
            {self.system_prompt}
            
            Customer query: "{user_input}"
            
            Analysis:
            - Symptoms: {', '.join(analysis['symptoms'])}
            - Severity: {analysis['severity']}
            
            We don't have specific products for this category in our inventory.
            Provide general advice and recommend speaking with our pharmacist.
            """
        else:
            # Format product information for the prompt
            products_info = ""
            for i, product in enumerate(relevant_products, 1):
                products_info += f"""
                Product {i}:
                - Name: {product['name']}
                - Description: {product['description']}
                - Active Ingredient: {product['active_ingredient']}
                - Benefits: {product['benefits']}
                - Price: {product['price']}
                """
            
            prompt = f"""
            {self.system_prompt}
            
            Customer query: "{user_input}"
            
            Analysis:
            - Category: {category}
            - Symptoms: {', '.join(analysis['symptoms'])}
            - Severity: {analysis['severity']}
            
            Available products in this category:
            {products_info}
            
            Recommend the most appropriate product(s) and explain why it would help.
            Include:
            1. Product recommendation
            2. How it addresses their specific symptoms
            3. Key benefits
            4. Important usage information
            5. Safety disclaimer to consult a doctor for serious conditions
            """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"I apologize, I'm having trouble generating a recommendation right now. Error: {str(e)}"
    
    def format_recommendation(self, recommendation: str, analysis: Dict) -> str:
        """
        Format the recommendation with a professional structure.
        
        Args:
            recommendation (str): The raw recommendation from Gemini
            analysis (Dict): Analysis of the user's needs
            
        Returns:
            str: Beautifully formatted recommendation
        """
        # Create a header based on the category
        category_header = analysis["category"].replace("_", " ").title()
        
        formatted = f"""
        🏥 SMART HEALTH STORE RECOMMENDATION
        {'=' * 50}
        📋 Category: {category_header}
        ⚠️  Severity: {analysis['severity'].title()}
        🎯 Symptoms: {', '.join(analysis['symptoms']) if analysis['symptoms'] else 'Not specified'}
        {'=' * 50}

        💡 RECOMMENDATION:
        {textwrap.fill(recommendation, width=70)}

        {'=' * 50}
        ⚠️  IMPORTANT: This is an AI recommendation. Please consult with our 
        pharmacist for personalized advice, especially if symptoms persist 
        or worsen. Always read product labels and follow usage instructions.

        🏪 Visit us in-store for more options and professional consultation!
        """
        
        return formatted
    
    def process_query(self, user_input: str) -> str:
        """
        Complete processing of a user query from analysis to recommendation.
        
        Args:
            user_input (str): User's query about their needs/symptoms
            
        Returns:
            str: Formatted product recommendation
        """
        print("🔍 Analyzing your query...")
        time.sleep(1)  # Simulate processing time
        
        # Analyze the query
        analysis = self.analyze_user_query(user_input)
        
        print("💭 Generating recommendation...")
        time.sleep(1)  # Simulate processing time
        
        # Generate recommendation
        recommendation = self.generate_recommendation(user_input, analysis)
        
        # Format the response
        formatted_response = self.format_recommendation(recommendation, analysis)
        
        return formatted_response
    
    def run_interactive(self):
        """Run the product suggester in interactive mode."""
        print("=" * 60)
        print("🏪 WELCOME TO SMART HEALTH STORE - AI PRODUCT SUGGESTER")
        print("=" * 60)
        print("I can help you find the right products for your needs!")
        print("Examples: 'I have a headache', 'My allergies are acting up'")
        print("Type 'quit' or 'exit' to end the session\n")
        
        while True:
            try:
                user_input = input("👤 How can I help you today? ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                    print("\nThank you for visiting Smart Health Store! Get well soon! 👋")
                    break
                
                if not user_input:
                    print("Please tell me what you need help with.")
                    continue
                
                # Process the query and get recommendation
                recommendation = self.process_query(user_input)
                
                # Print the recommendation
                print("\n" + recommendation)
                print("\n" + "=" * 60)
                print("Is there anything else I can help you with today?")
                
            except KeyboardInterrupt:
                print("\n\nThank you for visiting Smart Health Store! 👋")
                break
            except Exception as e:
                print(f"\nI apologize, I encountered an error: {str(e)}")
                print("Please try again or visit our store for assistance.\n")

# Main execution
if __name__ == "__main__":
    try:
        # Initialize the product suggester
        suggester = ProductSuggester()
        
        # Run in interactive mode
        suggester.run_interactive()
        
    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please make sure you have a .env file with GEMINI_API_KEY=your_api_key")
    except Exception as e:
        print(f"Unexpected error: {e}")