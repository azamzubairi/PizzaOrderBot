from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import ChatOllama
from datetime import datetime
from prompt import system_prompt
import json
import re

class PizzaOrderChatbot:
    def __init__(self):
        # Initialize the chat model
        self.llm = ChatOllama(model="llama3.1", temperature=0.2)
        
        # Load the system prompt
        self.system_prompt = system_prompt
        
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