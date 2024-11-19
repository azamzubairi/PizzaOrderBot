import mesop as me
import mesop.labs as mel
from chatbot import PizzaOrderChatbot

chatbot = PizzaOrderChatbot()


def on_load(e: me.LoadEvent):
    me.set_theme_mode("system")


@me.page(
    security_policy=me.SecurityPolicy(
        allowed_iframe_parents=["https://google.github.io"]
    ),
    path="/chat",
    title="PizzaPal - Pizza Ordering Bot",
    on_load=on_load,
)
def page():
    mel.chat(transform, title="PizzaPal - Pizza Ordering Bot", bot_user="Pizza Bot")


def transform(input: str, history: list[mel.ChatMessage]):
    response = chatbot.process_message(input)
    # Check for exit conditions
    if input.lower() in ["exit", "quit", "bye", "goodbye"]:
        print(
            "🤖 Thank you for choosing Delicious Slices Pizzeria! Have a wonderful day! 👋"
        )
    yield response
