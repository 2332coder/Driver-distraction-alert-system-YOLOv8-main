import tkinter as tk
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
from Detection_alert_code import detection_alert  # Ensure this module is accessible
from ultralytics import YOLO
import pathlib
import textwrap
from gtts import gTTS
import google.generativeai as genai
import time
import multiprocessing
import pyttsx3

def sayFunc(phrase):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.say(phrase)
    engine.runAndWait()

class YOLOApp:
    def __init__(self, window, window_title, model_path):
        self.window = window
        self.window.title(window_title)
        self.model = YOLO(model_path)
        self.model.fuse()
        self.names = self.model.names

        # Counters for each condition
        self.drowsy_count = 0
        self.phone_use_count = 0

        # Create a canvas that can fit the video source size
        self.canvas_width = 640
        self.canvas_height = 480

        self.canvas = tk.Canvas(window, width=self.canvas_width, height=self.canvas_height)
        self.canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        # Adjusted Grid placement for canvas
        

        # Dropdown menu
        self.options = ["Detection Mode", "Gemini API"]
        self.selected_option = tk.StringVar(window)
        self.selected_option.set(self.options[0])  # Default selection
        self.dropdown = ttk.OptionMenu(window, self.selected_option, self.options[0],*self.options, command=self.on_dropdown_select)
        self.dropdown.grid(row=0, column=2, padx=10, pady=10, sticky=tk.NE)  # Grid placement for dropdown menu

        # Start with detection UI
        self.show_detection_ui()

    def on_dropdown_select(self, value):
        if value == "Gemini API":
            self.show_gemini_ui()
        elif value == "Detection Mode":
            self.show_detection_ui()

    def show_gemini_ui(self):
        # Remove the detection UI elements
        if hasattr(self, 'btn_start'):
            self.btn_start.grid_forget()
        if hasattr(self, 'btn_quit'):
            self.btn_quit.grid_forget()
        if hasattr(self, 'btn_stop'):
            self.btn_stop.grid_forget()
        self.canvas.grid_forget()
        # Define colors for Gemini UI
        bg_color = '#E8F4F8'
        text_color = '#003366'
        button_color = '#006699'
        button_text_color = '#FFFFFF'
        entry_bg_color = '#FFFFFF'
        entry_text_color = '#000000'
        response_bg_color = '#FFFFFF'
        response_text_color = '#000000'
        quit_button_color = '#FF6347'

        # Create a new canvas for the Gemini UI
        self.gemini_canvas = tk.Canvas(self.window, width=self.canvas_width, height=self.canvas_height, bg=bg_color)
        self.gemini_canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.prompt_label = tk.Label(self.gemini_canvas, text="Gemini AI", font=('Arial', 16, 'bold'), bg=bg_color, fg=text_color)
        self.gemini_canvas.create_window(320, 20, window=self.prompt_label)

        self.ask_button = tk.Button(self.gemini_canvas, text="Ask", width=15, command=self.ask_gemini, bg=button_color, fg=button_text_color, font=('Arial', 12, 'bold'))
        self.gemini_canvas.create_window(320, 60, window=self.ask_button)

        self.prompt_entry = tk.Entry(self.gemini_canvas, width=50, bg=entry_bg_color, fg=entry_text_color, font=('Arial', 12))
        self.gemini_canvas.create_window(320, 100, window=self.prompt_entry)

        self.play_button = tk.Button(self.gemini_canvas, text="Play Audio", width=15, command=lambda: self.play_audio(self.response_text.get(1.0, tk.END)), bg=button_color, fg=button_text_color, font=('Arial', 12, 'bold'))
        self.gemini_canvas.create_window(220, 140, window=self.play_button)

        self.stop_button = tk.Button(self.gemini_canvas, text="Stop Audio", width=15, command=self.stop_audio, bg=button_color, fg=button_text_color, font=('Arial', 12, 'bold'))
        self.gemini_canvas.create_window(420, 140, window=self.stop_button)

        self.response_text = tk.Text(self.gemini_canvas, wrap=tk.WORD, height=10, width=60, bg=response_bg_color, fg=response_text_color, font=('Arial', 12))
        self.gemini_canvas.create_window(320, 250, window=self.response_text)

        self.quit_button = tk.Button(self.gemini_canvas, text="Quit", width=15, command=self.quit, bg=quit_button_color, fg=button_text_color, font=('Arial', 12, 'bold'))
        self.gemini_canvas.create_window(320, 360, window=self.quit_button)

    def show_detection_ui(self):
        # Remove Gemini API UI elements if they exist
        if hasattr(self, 'gemini_canvas'):
            self.gemini_canvas.grid_forget()

        # Add detection UI elements
        self.canvas.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.btn_start = tk.Button(self.window, text="Start Detection", width=20, command=self.start_detection, bg='#49df62', fg='white', font=('Arial', 12, 'bold'))
        self.btn_start.grid(row=2, column=0, padx=10, pady=10)  # Grid placement for start button

        self.btn_quit = ttk.Button(self.window, text="Quit", width=20, command=self.quit)
        self.btn_quit.grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)  # Grid placement for quit button

    def start_detection(self):
        self.btn_start.grid_forget()  # Remove the start button
        self.cap = cv2.VideoCapture(0)
        self.is_running = True
        self.dropdown.config(state="disabled")
        # Add Stop Detection button
        self.btn_stop = tk.Button(self.window, text="Stop Detection", width=20, command=self.stop_detection, bg='#8b0101', fg='white', font=('Arial', 12, 'bold'))
        self.btn_stop.grid(row=2, column=0, padx=10, pady=10)  # Grid placement for stop button

        self.update()

    def stop_detection(self):
        self.is_running = False
        self.dropdown.config(state="normal")
        if hasattr(self, 'cap') and self.cap:
            self.cap.release()
            self.cap = None

        # Remove Stop Detection button
        if hasattr(self, 'btn_stop'):
            self.btn_stop.grid_forget()

        # Re-add Start Detection button
        self.btn_start.grid(row=2, column=0, padx=10, pady=10)  # Grid placement for start button

        # Clear the canvas
        self.canvas.delete("all")

    def quit(self):
        self.stop_detection()
        self.window.quit()

    def update(self):
        if self.is_running and hasattr(self, 'cap') and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                results = self.model.predict(frame, conf=0.3, verbose=False)
                img = results[0].plot()

                self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.drowsy_count, self.phone_use_count = detection_alert(
                    results, self.names, self.drowsy_count, self.phone_use_count
                )

            self.window.after(10, self.update)
        
    def ask_gemini(self):
        prompt = self.prompt_entry.get()
        if prompt:
            GOOGLE_API_KEY = "YOUR_API_KEY"
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            
            # Check if response contains valid text
            if hasattr(response, 'text'):
                self.response_text.delete(1.0, tk.END)  # Clear the text box before inserting new response
                self.response_text.insert(tk.END, response.text)
            else:
                # Handle the case where no valid text is returned
                self.response_text.delete(1.0, tk.END)
                self.response_text.insert(tk.END, "No valid response received. Please check the safety ratings or try again.")

    def play_audio(self, text):
        if hasattr(self, 'audio_process') and self.audio_process.is_alive():
            return
        self.audio_process = multiprocessing.Process(target=sayFunc, args=(text,))
        self.audio_process.start()

    def stop_audio(self):
        if hasattr(self, 'audio_process') and self.audio_process.is_alive():
            self.audio_process.terminate()
            self.audio_process.join()

    def __del__(self):
        self.stop_detection()
        cv2.destroyAllWindows()

# Create a window and pass it to the Application object
if __name__ == "__main__":
    root = tk.Tk()
    app = YOLOApp(root,"Driver distraction detection & Alert system","last.pt")
    root.mainloop()

