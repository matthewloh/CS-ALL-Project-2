import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image

def browse_image():
    filename = filedialog.askopenfilename(initialdir="/", title="Select Image File",
                                          filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")))
    if filename:
        image = Image.open(filename)
        image = image.resize((300, 300), Image.ANTIALIAS)
        image = ImageTk.PhotoImage(image)
        image_label.configure(image=image)
        image_label.image = image

def submit_form():
    name = name_entry.get()
    email = email_entry.get()
    problem = problem_text.get("1.0", tk.END)

    # Process the form data (e.g., send an email, store data in a database, etc.)

    # Show a confirmation message
    message = f"Thank you, {name}! Your form has been submitted successfully."
    confirmation_label.config(text=message)

# Create the main window
window = tk.Tk()
window.title("User Feedback Form")

# Create form elements
name_label = tk.Label(window, text="Name:")
name_label.pack()
name_entry = tk.Entry(window)
name_entry.pack()

email_label = tk.Label(window, text="Email:")
email_label.pack()
email_entry = tk.Entry(window)
email_entry.pack()

problem_label = tk.Label(window, text="Problem Description:")
problem_label.pack()
problem_text = tk.Text(window, height=5, width=30)
problem_text.pack()

image_label = tk.Label(window)
image_label.pack()

upload_button = tk.Button(window, text="Upload Image", command=browse_image)
upload_button.pack()

submit_button = tk.Button(window, text="Submit", command=submit_form)
submit_button.pack()

confirmation_label = tk.Label(window, text="")
confirmation_label.pack()



# Start the Tkinter event loop
window.mainloop()