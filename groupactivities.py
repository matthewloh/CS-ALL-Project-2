import tkinter as tk
import random
import time

class RabbitVsTurtleGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Rabbit vs Turtle Game")
        
        # Create canvas for animations
        self.canvas = tk.Canvas(root, width=800, height=200)
        self.canvas.pack()
        
        # Create label for displaying questions
        self.question_label = tk.Label(root, text="", font=("Arial", 14))
        self.question_label.pack()
        
        # Create entry for user's answer
        self.answer_entry = tk.Entry(root, width=30)
        self.answer_entry.pack()
        
        # Create submit button
        self.submit_button = tk.Button(root, text="Submit", command=self.check_answer)
        self.submit_button.pack()
        
        # Game variables
        self.questions = ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        self.correct_answers = ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5"]
        self.current_question = None
        self.current_correct_answer = None
        self.rabbit_position = 0
        self.turtle_position = 0
        self.start_time = None
        
        # Start the game
        self.start_game()
    
    def start_game(self):
        self.next_question()
    
    def next_question(self):
        # Select a random question
        question_index = random.randint(0, len(self.questions) - 1)
        self.current_question = self.questions[question_index]
        self.current_correct_answer = self.correct_answers[question_index]
        
        # Display the question
        self.question_label.config(text=self.current_question)
        
        # Clear the answer entry
        self.answer_entry.delete(0, tk.END)
        
        # Start the timer
        self.start_time = time.time()
    
    def check_answer(self):
        # Get the user's answer
        user_answer = self.answer_entry.get()
        
        # Compare the user's answer with the correct answer
        if user_answer == self.current_correct_answer:
            # Move the rabbit and turtle forward
            self.rabbit_position += 1
            self.turtle_position += 1
        else:
            # Only move the rabbit forward
            self.rabbit_position += 1
        
        # Check if the game is over
        if self.rabbit_position >= len(self.questions):
            self.end_game()
        else:
            self.next_question()
    
    def end_game(self):
        # Calculate the elapsed time
        elapsed_time = time.time() - self.start_time
        
        # Determine the winner
        if elapsed_time < 300:
            if self.rabbit_position > self.turtle_position:
                winner = "Rabbit"
            elif self.rabbit_position < self.turtle_position:
                winner = "Turtle"
            else:
                winner = "Tie"
        else:
            winner = "Time's up! No winner."
        
        # Display the winner
        self.question_label.config(text=f"Game Over! Winner: {winner}")

# Create the main window
root = tk.Tk()

# Create an instance of RabbitVsTurtleGame
game = RabbitVsTurtleGame(root)

# Run the Tkinter event loop
root.mainloop()