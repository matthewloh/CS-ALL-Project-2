import tkinter as tk

class QuizApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Quiz")
        
        # Create a label for displaying the rules
        self.rules_label = tk.Label(root, text="Welcome to the Math Quiz!\n\n"
                                                "Rules and Regulations:\n"
                                                "- This quiz contains multiple-choice questions.\n"
                                                "- Use the 'Next' button to move to the next question.\n"
                                                "- Use the 'Return' button to go back to the previous question.\n"
                                                "- You cannot exit the quiz once you start.\n"
                                                "- There is a time limit for the quiz.\n"
                                                "- Click 'Start Quiz' to begin.")
        self.rules_label.pack(pady=20)
        
        # Create a button to start the quiz
        self.start_button = tk.Button(root, text="Start Quiz", command=self.start_quiz)
        self.start_button.pack()
        
        # Quiz variables
        self.questions = ["Question 1", "Question 2", "Question 3", "Question 4", "Question 5"]
        self.answers = ["Answer 1", "Answer 2", "Answer 3", "Answer 4", "Answer 5"]
        self.current_question_index = 0
        self.current_question = None
        self.current_answer = None
        self.timer_seconds = 300
        self.timer_label = None
        self.timer_id = None
    
    def start_quiz(self):
        # Hide the rules label and start button
        self.rules_label.pack_forget()
        self.start_button.pack_forget()
        
        # Start the quiz timer
        self.start_timer()
        
        # Display the first question
        self.display_question()
    
    def display_question(self):
        # Get the current question and answer
        self.current_question = self.questions[self.current_question_index]
        self.current_answer = self.answers[self.current_question_index]
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.pack_forget()
        
        # Display the question number
        question_number_label = tk.Label(self.root, text=f"Question {self.current_question_index + 1}/{len(self.questions)}")
        question_number_label.pack(pady=10)
        
        # Display the question text
        question_label = tk.Label(self.root, text=self.current_question, font=("Arial", 14), wraplength=600)
        question_label.pack(pady=10)
        
        # Display an image (optional)
        # image = tk.PhotoImage(file="image.png")
        # image_label = tk.Label(self.root, image=image)
        # image_label.pack(pady=10)
        
        # Display the answer choices (radio buttons)
        answer_choices = ["Choice 1", "Choice 2", "Choice 3", "Choice 4"]
        selected_choice = tk.StringVar()
        for choice in answer_choices:
            choice_button = tk.Radiobutton(self.root, text=choice, variable=selected_choice, value=choice)
            choice_button.pack()
        
        # Create navigation buttons
        next_button = tk.Button(self.root, text="Next", command=self.next_question)
        next_button.pack(pady=10)
        
        return_button = tk.Button(self.root, text="Return", command=self.previous_question)
        return_button.pack(pady=5)
        
        submit_button = tk.Button(self.root, text="Submit", command=self.submit_quiz)
        submit_button.pack(pady=10)
    
    def next_question(self):
        # Increment the current question index
        self.current_question_index += 1
        
        # Check if it is the last question
        if self.current_question_index >= len(self.questions):
            self.submit_quiz()
        else:
            # Display the next question
            self.display_question()
    
    def previous_question(self):
        # Decrement the current question index
        self.current_question_index -= 1
        
        # Check if it is the first question
        if self.current_question_index < 0:
            self.current_question_index = 0
        
        # Display the previous question
        self.display_question()
    
    def start_timer(self):
        self.timer_label = tk.Label(self.root, text="")
        self.timer_label.pack()
        
        self.update_timer()
    
    def update_timer(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.config(text=f"Time left: {minutes:02d}:{seconds:02d}")
        
        if self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            self.submit_quiz()
    
    def submit_quiz(self):
        # Stop the timer
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
        
        # Clear the window
        for widget in self.root.winfo_children():
            widget.pack_forget()

        # Calculate and display the score
        score = self.calculate_score()
        score_label = tk.Label(self.root, text=f"Quiz Done!\n\nYour Score: {score}")
        score_label.pack(pady=20)

    def calculate_score(self):
        # Calculate the score based on the number of correct answers
        score = 0
        for i in range(len(self.questions)):
            if self.answers[i] == self.current_answer:
                score += 1
        return score


# Create the main window
root = tk.Tk()

# Create an instance of QuizApplication
quiz_app = QuizApplication(root)

# Run the Tkinter event loop
root.mainloop()