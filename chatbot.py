from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

# Initialize the language model with the Llama model
llm = ChatOllama(model="llama3.1", temperature=0)

# Define the pizza order model with Pydantic
class PizzaOrder(BaseModel):
    flavor: str = Field(default=None, description="This is the flavor of the pizza.")
    size: str = Field(default=None, description="This is the size of the pizza.")
    extra_toppings: str = Field(default=None, description="Is there any extra toppings")

# Function to extract fields safely from the response
def extract_order_details(response):
    # Initialize an empty PizzaOrder object
    pizza_order = PizzaOrder()

    # Extract fields from the response, if available
    if response.flavor:
        pizza_order.flavor = response.flavor
    if response.size:
        pizza_order.size = response.size
    if response.extra_toppings:
        pizza_order.extra_toppings = response.extra_toppings
    
    return pizza_order

# Function to greet the user, ask for the order, and handle missing information
def pizza_chatbot():
    # Greet the user
    print("Hello! Welcome to PizzaBot. How can I assist you today?")
    
    # Ask for the initial order input
    order_input = input("Please tell me your pizza order: ")

    # Process the input and ask for missing values
    order = llm.with_structured_output(PizzaOrder)
    response = order.invoke(order_input)

    # Extract the parsed order fields from the response
    pizza_order = extract_order_details(response)

    # Ask for missing values if needed
    if not pizza_order.flavor:
        pizza_order.flavor = input("What flavor would you like? ")

    if not pizza_order.size:
        pizza_order.size = input("What size would you like? (small, medium, large) ")

    if not pizza_order.extra_toppings:
        pizza_order.extra_toppings = input("Would you like any extra toppings? ")

    # Confirm the order
    print(f"Confirming your order: {pizza_order.size} {pizza_order.flavor} pizza with {pizza_order.extra_toppings}.")

    # Goodbye message
    print("Thank you for your order! Goodbye.")

    return pizza_order

# Example call to the chatbot
pizza_chatbot()
