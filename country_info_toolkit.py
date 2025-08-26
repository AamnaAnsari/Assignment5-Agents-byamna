import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, List, Optional, Any
import time
import json

load_dotenv()

class CountryCapitalTool:
    """Tool Agent 1: Provides capital city information for countries."""
    
    def __init__(self):
        self.tool_name = "get_capital"
        self.description = "Returns the capital city of a given country"
        
        # Country capital database 
        self.country_capitals = {
            "united states": "Washington D.C.",
            "usa": "Washington D.C.",
            "united kingdom": "London",
            "uk": "London",
            "canada": "Ottawa",
            "australia": "Canberra",
            "india": "New Delhi",
            "germany": "Berlin",
            "france": "Paris",
            "japan": "Tokyo",
            "china": "Beijing",
            "brazil": "Brasília",
            "russia": "Moscow",
            "mexico": "Mexico City",
            "spain": "Madrid",
            "italy": "Rome",
            "south africa": "Pretoria",
            "egypt": "Cairo",
            "argentina": "Buenos Aires",
            "south korea": "Seoul"
        }
    
    def execute(self, country_name: str) -> Dict[str, str]:
        """
        Get the capital city of a country.
        
        Args:
            country_name (str): Name of the country
            
        Returns:
            Dict: Contains capital information or error message
        """
        country_lower = country_name.strip().lower()
        
        if country_lower in self.country_capitals:
            return {
                "status": "success",
                "capital": self.country_capitals[country_lower],
                "country": country_name.title()
            }
        else:
            return {
                "status": "error",
                "message": f"Capital information not available for {country_name}"
            }

class CountryLanguageTool:
    """Tool Agent 2: Provides language information for countries."""
    
    def __init__(self):
        self.tool_name = "get_language"
        self.description = "Returns the official language(s) of a given country"
        
        # Country language database 
        self.country_languages = {
            "united states": "English",
            "usa": "English",
            "united kingdom": "English",
            "uk": "English",
            "canada": "English, French",
            "australia": "English",
            "india": "Hindi, English (and 21 other official languages)",
            "germany": "German",
            "france": "French",
            "japan": "Japanese",
            "china": "Mandarin Chinese",
            "brazil": "Portuguese",
            "russia": "Russian",
            "mexico": "Spanish",
            "spain": "Spanish",
            "italy": "Italian",
            "south africa": "11 official languages including Zulu, Xhosa, Afrikaans, English",
            "egypt": "Arabic",
            "argentina": "Spanish",
            "south korea": "Korean"
        }
    
    def execute(self, country_name: str) -> Dict[str, str]:
        """
        Get the official language(s) of a country.
        
        Args:
            country_name (str): Name of the country
            
        Returns:
            Dict: Contains language information or error message
        """
        country_lower = country_name.strip().lower()
        
        if country_lower in self.country_languages:
            return {
                "status": "success",
                "language": self.country_languages[country_lower],
                "country": country_name.title()
            }
        else:
            return {
                "status": "error",
                "message": f"Language information not available for {country_name}"
            }

class CountryPopulationTool:
    """Tool Agent 3: Provides population information for countries."""
    
    def __init__(self):
        self.tool_name = "get_population"
        self.description = "Returns the approximate population of a given country"
        
        # Country population database 
        self.country_populations = {
            "united states": "341 million",
            "usa": "341 million",
            "united kingdom": "67 million",
            "uk": "67 million",
            "canada": "39 million",
            "australia": "26 million",
            "india": "1.43 billion",
            "germany": "83 million",
            "france": "68 million",
            "japan": "125 million",
            "china": "1.42 billion",
            "brazil": "216 million",
            "russia": "144 million",
            "mexico": "128 million",
            "spain": "48 million",
            "italy": "59 million",
            "south africa": "60 million",
            "egypt": "110 million",
            "argentina": "46 million",
            "south korea": "52 million"
        }
    
    def execute(self, country_name: str) -> Dict[str, str]:
        """
        Get the population of a country.
        
        Args:
            country_name (str): Name of the country
            
        Returns:
            Dict: Contains population information or error message
        """
        country_lower = country_name.strip().lower()
        
        if country_lower in self.country_populations:
            return {
                "status": "success",
                "population": self.country_populations[country_lower],
                "country": country_name.title()
            }
        else:
            return {
                "status": "error",
                "message": f"Population information not available for {country_name}"
            }

class CountryInfoOrchestrator:
    """Orchestrator Agent: Coordinates all three tools and provides complete country information."""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize all tool agents
        self.capital_tool = CountryCapitalTool()
        self.language_tool = CountryLanguageTool()
        self.population_tool = CountryPopulationTool()
        
        self.available_tools = {
            "capital": self.capital_tool,
            "language": self.language_tool,
            "population": self.population_tool
        }
    
    def validate_country(self, country_name: str) -> Dict[str, Any]:
        """
        Validate if the country exists in our databases.
        
        Args:
            country_name (str): Name of the country to validate
            
        Returns:
            Dict: Validation results
        """
        country_lower = country_name.strip().lower()
        
        # Check if country exists in any database
        exists_in_capitals = country_lower in self.capital_tool.country_capitals
        exists_in_languages = country_lower in self.language_tool.country_languages
        exists_in_populations = country_lower in self.population_tool.country_populations
        
        return {
            "is_valid": exists_in_capitals or exists_in_languages or exists_in_populations,
            "exists_in_capitals": exists_in_capitals,
            "exists_in_languages": exists_in_languages,
            "exists_in_populations": exists_in_populations
        }
    
    def execute_all_tools(self, country_name: str) -> Dict[str, Any]:
        """
        Execute all three tools for the given country.
        
        Args:
            country_name (str): Name of the country
            
        Returns:
            Dict: Results from all tools
        """
        results = {
            "country": country_name.title(),
            "capital": self.capital_tool.execute(country_name),
            "language": self.language_tool.execute(country_name),
            "population": self.population_tool.execute(country_name),
            "all_successful": True
        }
        
        # Check if all tools were successful
        for tool_result in [results["capital"], results["language"], results["population"]]:
            if tool_result["status"] == "error":
                results["all_successful"] = False
        
        return results
    
    def generate_complete_report(self, tool_results: Dict[str, Any]) -> str:
        """
        Generate a complete, formatted report using Gemini AI.
        
        Args:
            tool_results (Dict): Results from all tools
            
        Returns:
            str: Formatted country information report
        """
        country = tool_results["country"]
        
        # Prepare prompt for Gemini
        prompt = f"""
        Create a comprehensive and engaging country information report for {country}.
        
        Available information:
        - Capital: {tool_results['capital']['capital'] if tool_results['capital']['status'] == 'success' else 'Not available'}
        - Language: {tool_results['language']['language'] if tool_results['language']['status'] == 'success' else 'Not available'}
        - Population: {tool_results['population']['population'] if tool_results['population']['status'] == 'success' else 'Not available'}
        
        Format the response as a beautiful, informative report with emojis.
        Include:
        1. A welcoming introduction
        2. The available information in a structured way
        3. Any missing information with a polite note
        4. A friendly conclusion
        
        Keep it professional yet engaging.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback formatting if Gemini fails
            return self._create_fallback_report(tool_results)
    
    def _create_fallback_report(self, tool_results: Dict[str, Any]) -> str:
        """Create a fallback report if Gemini API fails."""
        country = tool_results["country"]
        
        report = f"""
        🌍 COUNTRY INFORMATION: {country}
        {'=' * 50}
        
        """
        
        # Add capital information
        if tool_results["capital"]["status"] == "success":
            report += f"🏛️  Capital: {tool_results['capital']['capital']}\n"
        else:
            report += f"❌ Capital: Information not available\n"
        
        # Add language information
        if tool_results["language"]["status"] == "success":
            report += f"🗣️  Language: {tool_results['language']['language']}\n"
        else:
            report += f"❌ Language: Information not available\n"
        
        # Add population information
        if tool_results["population"]["status"] == "success":
            report += f"👥 Population: {tool_results['population']['population']}\n"
        else:
            report += f"❌ Population: Information not available\n"
        
        report += f"""
        {'=' * 50}
        ℹ️  Note: This information is from our database. 
        For the most current data, please refer to official sources.
        """
        
        return report
    
    def process_country_query(self, country_name: str) -> Dict[str, Any]:
        """
        Process a complete country query using all tools.
        
        Args:
            country_name (str): Name of the country
            
        Returns:
            Dict: Complete processing results
        """
        print(f"🔍 Validating country: {country_name}...")
        time.sleep(1)
        
        # Validate country
        validation = self.validate_country(country_name)
        
        if not validation["is_valid"]:
            return {
                "status": "error",
                "message": f"Sorry, I don't have information about '{country_name}' in my database.",
                "suggestions": "Try countries like USA, India, Germany, Japan, Brazil, etc."
            }
        
        print("🔄 Executing all information tools...")
        time.sleep(1)
        
        # Execute all tools
        tool_results = self.execute_all_tools(country_name)
        
        print("📊 Generating comprehensive report...")
        time.sleep(1)
        
        # Generate complete report
        report = self.generate_complete_report(tool_results)
        
        return {
            "status": "success",
            "country": country_name.title(),
            "tool_results": tool_results,
            "report": report,
            "validation": validation
        }

class CountryInfoBot:
    """Main bot class to handle user interactions."""
    
    def __init__(self):
        self.orchestrator = CountryInfoOrchestrator()
    
    def format_output(self, results: Dict[str, Any]) -> str:
        """Format the output in a user-friendly way."""
        if results["status"] == "error":
            return f"""
            ❌ SORRY, INFORMATION NOT AVAILABLE
            {'=' * 50}
            {results['message']}
            💡 {results['suggestions']}
            """
        
        return f"""
        {results['report']}
        """
    
    def run_interactive(self):
        """Run the bot in interactive mode."""
        print("=" * 60)
        print("🌍 COUNTRY INFORMATION BOT")
        print("=" * 60)
        print("I can tell you about capitals, languages, and populations!")
        print("Available countries: USA, UK, Canada, India, Germany, France, Japan, China, Brazil, etc.")
        print("Type 'quit' to exit at any time.\n")
        
        while True:
            try:
                user_input = input("🇺🇳 Which country would you like to know about? ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'stop']:
                    print("\nThank you for using Country Info Bot! Goodbye! 👋")
                    break
                
                if not user_input:
                    print("Please enter a country name...")
                    continue
                
                # Process the country query
                results = self.orchestrator.process_country_query(user_input)
                
                # Display results
                print("\n" + self.format_output(results))
                print("\n" + "=" * 60)
                print("Would you like to know about another country?")
                
            except KeyboardInterrupt:
                print("\n\nSession ended. Thank you for using Country Info Bot! 🌏")
                break
            except Exception as e:
                print(f"\nI apologize, I encountered an error: {str(e)}")
                print("Please try again with a different country name.\n")

# Example usage for quick testing
def quick_test():
    """Quick test function to demonstrate the bot."""
    bot = CountryInfoBot()
    
    test_countries = ["USA", "Japan", "Germany", "InvalidCountry"]
    
    for country in test_countries:
        print(f"\nTesting: {country}")
        print("=" * 30)
        results = bot.orchestrator.process_country_query(country)
        print(bot.format_output(results))
        print("=" * 30)

# Main execution
if __name__ == "__main__":
    try:
        # Initialize the bot
        bot = CountryInfoBot()
        
        # Run in interactive mode
        bot.run_interactive()
        
        # Uncomment the line below for quick testing
        # quick_test()
        
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please make sure you have a .env file with GEMINI_API_KEY=your_api_key")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")