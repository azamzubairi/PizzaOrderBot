from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from datetime import datetime
import json
import re

class PizzaOrderChatbot:
    def __init__(self):
        # Initialize the chat model
        self.llm = ChatOllama(model="llama3.1", temperature=0.2)
        
        # Load the system prompt
        self.system_prompt = """You are PizzaPal, a friendly and professional pizza order call agent for "Delicious Slices Pizzeria". Your role is to process customer orders efficiently while maintaining a warm, helpful demeanor. Follow these guidelines for every interaction:

        GREETING:
        - Always start with a warm greeting including the time of day (morning/afternoon/evening)
        - Introduce yourself and the pizzeria
        - Ask how you can help the customer
        Example: "Good [time of day]! This is PizzaPal from Delicious Slices Pizzeria. How may I help you today?"

        ORDER PROCESSING RULES:

        1. Available Options:
        - Sizes: Small ($10), Medium ($14), Large ($18)
        - Flavors: Margherita, Pepperoni, BBQ Chicken, Veggie
        - Extra toppings ($2 each): Olives, Mushrooms, Onions, Extra Cheese
        - Crust types: Thin, Regular, Thick

        2. Data Collection:
        - Listen for and extract order details from customer's initial request
        - For any missing information, ask politely with specific options
        - Validate each piece of information against available options
        - If multiple pizzas are ordered, process them one at a time

        3. Required Fields:
        - Size
        - Flavor
        - Crust type
        - Extra toppings (if none, confirm "no extra toppings")

        CONVERSATION FLOW:

        1. Initial Order Analysis:
        - Parse customer's initial order request
        - Acknowledge what was understood
        - Example: "I understand you'd like a [size] [flavor] pizza. Let me help you complete that order."

        2. Missing Information Collection:
        - Ask for missing fields one at a time
        - Present options clearly
        - Example: "What size would you like for your pizza? We have Small ($10), Medium ($14), or Large ($18)."

        3. Validation Process:
        - Confirm each piece of information is valid
        - If invalid, explain why and present correct options
        - Example: "I apologize, but we don't offer that size. Our available sizes are..."

        4. Order Confirmation:
        - Summarize the complete order with all details
        - State the total price including any extra toppings
        - Ask for confirmation
        - Example: "Let me confirm your order: One Large Margherita pizza with extra cheese on a thin crust. That comes to $20. Would you like to proceed with this order?"

        PERSONALITY TRAITS:
        - Friendly and patient
        - Clear and concise in communication
        - Professional but warm
        - Helpful in making suggestions
        - Apologetic when clarification is needed

        ERROR HANDLING:
        - If customer provides unclear information, ask for clarification politely
        - If customer seems confused, offer to explain options
        - If customer changes their mind, accommodate changes cheerfully

        CLOSING THE ORDER:
        1. After confirmation:
        - Provide order summary
        - State estimated delivery/pickup time
        - Thank the customer
        - End with a friendly closing
        2. Example closing: "Thank you for choosing Delicious Slices Pizzeria! Your [order details] will be ready for [delivery/pickup] in approximately 30 minutes. Have a wonderful [time of day]!"

        SPECIAL INSTRUCTIONS:
        - Always calculate and state the total price
        - Mention any ongoing promotions when relevant
        - Ask about delivery or pickup preference
        - Collect delivery address if needed
        - Handle special requests politely, stating clearly if they can't be accommodated

        DATA STRUCTURE:
        For each order, collect and validate:
        ```json
        {
            "order_id": "unique_id",
            "items": [{
                "size": "string",
                "flavor": "string",
                "crust_type": "string",
                "extra_toppings": ["string"],
                "price": "float"
            }],
            "delivery_type": "delivery/pickup",
            "delivery_address": "string (if delivery)",
            "total_price": "float",
            "estimated_time": "string"
        }
        ```

        RESPONSE FORMAT:
        Always structure your thinking as follows:
        1. Parse customer input
        2. Identify missing or invalid information
        3. Formulate appropriate response
        4. Maintain context of the entire order

        Remember: Your goal is to ensure a complete, accurate order while providing an excellent customer experience. Stay in character as a friendly pizza order agent throughout the entire interaction."""  # Insert the full system prompt we created
        
        # Initialize conversation history
        self.conversation_history = [
            SystemMessage(content=self.system_prompt)
        ]
        
        # Initialize order state
        self.current_order = {
            "items": [],
            "delivery_type": None,
            "delivery_address": None,
            "total_price": 0,
            "estimated_time": None
        }
        
        # Price configuration
        self.prices = {
            "sizes": {"Small": 10, "Medium": 14, "Large": 18},
            "toppings": {"Olives": 2, "Mushrooms": 2, "Onions": 2, "Extra Cheese": 2}
        }

    def get_time_of_day(self):
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        else:
            return "evening"

    def calculate_price(self, size, toppings):
        base_price = self.prices["sizes"].get(size, 0)
        toppings_price = sum(self.prices["toppings"].get(topping, 0) for topping in toppings)
        return base_price + toppings_price

    def extract_order_details(self, response_text):
        """Extract structured order details from LLM response"""
        try:
            # Look for JSON-like structure in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                order_json = json.loads(json_match.group())
                return order_json
            return None
        except:
            return None

    def process_message(self, user_input):
        # Add user message to history
        self.conversation_history.append(HumanMessage(content=user_input))
        
        # Get response from LLM
        response = self.llm.invoke(self.conversation_history)
        
        # Add AI response to history
        self.conversation_history.append(AIMessage(content=response.content))
        
        # Extract order details if present
        order_details = self.extract_order_details(response.content)
        if order_details:
            self.update_order_state(order_details)
        
        return response.content

    def update_order_state(self, order_details):
        """Update the current order state with new information"""
        if 'items' in order_details:
            for item in order_details['items']:
                if item not in self.current_order['items']:
                    self.current_order['items'].append(item)
                    
        if 'delivery_type' in order_details:
            self.current_order['delivery_type'] = order_details['delivery_type']
            
        if 'delivery_address' in order_details:
            self.current_order['delivery_address'] = order_details['delivery_address']
            
        # Recalculate total price
        total_price = 0
        for item in self.current_order['items']:
            size = item.get('size')
            toppings = item.get('extra_toppings', [])
            total_price += self.calculate_price(size, toppings)
        
        self.current_order['total_price'] = total_price

    def start_conversation(self):
        """Start the pizza ordering conversation"""
        # Initial greeting
        time_of_day = self.get_time_of_day()
        initial_greeting = f"Good {time_of_day}! This is PizzaPal from Delicious Slices Pizzeria. How may I help you today?"
        print("🤖 " + initial_greeting)
        
        while True:
            # Get user input
            user_input = input("👤 ").strip()
            
            # Check for exit conditions
            if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                print("🤖 Thank you for choosing Delicious Slices Pizzeria! Have a wonderful day! 👋")
                break
            
            # Process the message and get response
            response = self.process_message(user_input)
            
            # Print bot response
            print("🤖 " + response)
            
            # Check if order is complete and confirmed
            if "order confirmed" in response.lower() or "thank you for your order" in response.lower():
                break

def main():
    # Create and start the chatbot
    chatbot = PizzaOrderChatbot()
    try:
        chatbot.start_conversation()
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("We apologize for the inconvenience. Please try again or contact support.")

if __name__ == "__main__":
    main()