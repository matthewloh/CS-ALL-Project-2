import tkinter as tk
from openai import ChatCompletion

# Create the main Tkinter window
window = tk.Tk()
window.title("Chatbot")
window.geometry("400x500")

# Create a Text widget for displaying chat history
chat_history = tk.Text(window)
chat_history.pack(pady=10)

# Create an Entry widget for user input
user_input = tk.Entry(window, width=50)
user_input.pack(pady=10)

# Function to handle user input and generate bot response
def handle_user_input(event):
    # Get the user input
    user_message = user_input.get()
    # Append user message to the chat history
    chat_history.insert(tk.END, "User: " + user_message + "\n")
    chat_history.insert(tk.END, "-" * 40 + "\n")
    # Clear the user input
    user_input.delete(0, tk.END)

    # Call the OpenAI Chat Completion API to generate bot response
    # Replace 'YOUR_API_KEY' with your actual OpenAI API key
    completion = ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message},
        ],
    )
    # Get the bot response from the API response
    bot_response = completion.choices[0].message.content

    # Append bot response to the chat history
    chat_history.insert(tk.END, "Chatbot: " + bot_response + "\n")
    chat_history.insert(tk.END, "=" * 40 + "\n")
    # Scroll to the end of the chat history
    chat_history.see(tk.END)

# Bind the Enter key to the user input handler function
user_input.bind("<Return>", handle_user_input)

# Start the Tkinter event loop
window.mainloop()
