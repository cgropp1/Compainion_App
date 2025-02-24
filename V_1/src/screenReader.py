import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, Image, ImageEnhance
import pytesseract
import ctypes

# Enable DPI awareness for accurate screen scaling
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# Specify the Tesseract executable path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class ScreenReader:
    def __init__(self, match_callback=None, num_regions=3):
        self.root = tk.Tk()
        self.root.title("PSS overlay")

        # Set window attributes
        self.root.attributes("-transparentcolor", "#00FF00")  # Custom transparent color
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 1)
        self.root.configure(bg="#00FF00")  # Custom transparent color

        # Get actual screen resolution
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Create a full-screen canvas for overlays
        self.canvas = tk.Canvas(self.root, bg='#00FF00', highlightthickness=0)  # Custom transparent color
        self.canvas.pack(fill='both', expand=True)

        # Create a non-transparent frame for buttons
        self.button_frame = tk.Frame(self.root, bg='gray')
        self.button_frame.place(x=10, y=10)

        # Settings menu frame
        self.settings_frame = tk.Frame(self.root, bg='gray')
        self.settings_frame.place(x=10, y=50)

        # Define a common font for buttons
        button_font = ("Arial", 14, "bold")

        # Buttons in the settings menu
        self.select_button = tk.Button(self.settings_frame, text="Select Regions", command=self.start_drawing, bg='blue', fg='white', font=button_font)
        self.select_button.pack(padx=5, pady=5)

        self.toggle_button = tk.Button(self.settings_frame, text="Toggle Overlay", command=self.toggle_overlay, bg='purple', fg='white', font=button_font)
        self.toggle_button.pack(padx=5, pady=5)

        self.ocr_button = tk.Button(self.settings_frame, text="Perform OCR", command=self.perform_ocr, bg='green', fg='white', font=button_font)
        self.ocr_button.pack(padx=5, pady=5)

        # OCR result label
        self.ocr_label = tk.Label(self.settings_frame, text="", bg='gray', fg='white', font=button_font)
        self.ocr_label.pack(padx=5, pady=5)

        # Settings button
        self.settings_button = tk.Button(self.button_frame, text="Settings", command=self.toggle_settings, bg='gray', fg='white', font=button_font)
        self.settings_button.pack(padx=5, pady=5)

        # Capture Match button
        self.capture_button = tk.Button(self.button_frame, text="Capture Match", command=self.capture_match, bg='red', fg='white', font=button_font)
        self.capture_button.pack(padx=5, pady=5)

        self.root.bind('<Control-q>', self.close_window)

        # Overlay & region tracking
        self.overlays_visible = True  # Track overlay visibility
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.region_count = 0
        self.regions = []
        self.overlay_shapes = []  # Store drawn rectangles
        self.text_labels = []  # Store text labels

        # Attribute to store OCR results
        self.ocr_results = []
        self.match_callback = match_callback  # Store the callback function
        self.num_regions = num_regions  # Number of regions to select

        # Initially hide the settings menu
        self.settings_visible = False
        self.settings_frame.place_forget()

        # Store the positions of the frames
        self.button_frame_position = (10, 10)
        self.settings_frame_position = (10, 50)

        # Bind events for dragging the frames
        self.button_frame.bind('<Button-1>', self.start_drag)
        self.button_frame.bind('<B1-Motion>', self.do_drag)
        self.settings_frame.bind('<Button-1>', self.start_drag)
        self.settings_frame.bind('<B1-Motion>', self.do_drag)

    def start_drag(self, event):
        """Start dragging the frame."""
        self.drag_data = {"x": event.x, "y": event.y}

    def do_drag(self, event):
        """Handle dragging the frame."""
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        event.widget.place(x=event.widget.winfo_x() + dx, y=event.widget.winfo_y() + dy)

    def toggle_settings(self):
        """Toggle the visibility of the settings menu."""
        if self.settings_visible:
            self.settings_frame.place_forget()
        else:
            self.settings_frame.place(x=self.settings_frame_position[0], y=self.settings_frame_position[1])
        self.settings_visible = not self.settings_visible

    def toggle_overlay(self):
        """Toggle the visibility of the region overlays while keeping buttons visible."""
        new_state = 'hidden' if self.overlays_visible else 'normal'
        
        for shape in self.overlay_shapes:
            self.canvas.itemconfig(shape, state=new_state)
        for label in self.text_labels:
            self.canvas.itemconfig(label, state=new_state)

        self.overlays_visible = not self.overlays_visible  # Toggle state

    def start_drawing(self):
        """Reset and prepare for selecting regions."""
        self.drawing = False
        self.start_x = None
        self.start_y = None
        self.region_count = 0
        self.regions = []

        for shape in self.overlay_shapes:
            self.canvas.delete(shape)
        for label in self.text_labels:
            self.canvas.delete(label)
        self.overlay_shapes.clear()  # Clear previous overlays
        self.text_labels.clear()  # Clear text labels

        # Hide button frame during selection
        self.button_frame_position = (self.button_frame.winfo_x(), self.button_frame.winfo_y())
        self.settings_frame_position = (self.settings_frame.winfo_x(), self.settings_frame.winfo_y())
        self.button_frame.place_forget()
        self.settings_frame.place_forget()

        # Make the backround grey and semi-transparent
        self.root.attributes("-alpha", 0.5)
        self.canvas.config(bg='gray')
        
        self.enable_drawing_mode()

    def enable_drawing_mode(self):
        """Enable region selection."""
        self.drawing = True
        self.canvas.config(cursor='cross')

        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.end_draw)

    def start_draw(self, event):
        """Start drawing a selection rectangle."""
        if self.region_count >= self.num_regions:
            return  # Limit to the specified number of regions
        self.start_x, self.start_y = event.x, event.y
        colors = ['green', 'orange', 'red']
        labels = ["User 1", "User 2", "End Condition"]

        self.current_box = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline=colors[self.region_count], fill=colors[self.region_count], stipple='gray50')
        self.overlay_shapes.append(self.current_box)  # Store shape reference

        # Create text label inside the box
        text_label = self.canvas.create_text(self.start_x + 5, self.start_y + 5, text=labels[self.region_count], anchor="nw", fill="white", font=("Arial", 12, "bold"))
        self.text_labels.append(text_label)

    def draw(self, event):
        """Update rectangle dimensions as the user drags."""
        self.canvas.coords(self.current_box, self.start_x, self.start_y, event.x, event.y)
        self.canvas.coords(self.text_labels[self.region_count], min(self.start_x, event.x) + 5, min(self.start_y, event.y) + 5)

    def end_draw(self, event):
        """Finalize the drawn region."""
        if self.region_count >= self.num_regions:
            return  # Stop at the specified number of regions

        self.region_count += 1
        self.regions.append(self.canvas.coords(self.current_box))

        if self.region_count < self.num_regions:
            return  # Wait for all regions

        self.drawing = False
        self.canvas.config(cursor='', bg='#00FF00')  # Set canvas to opaque white
        self.canvas.unbind('<Button-1>')
        self.canvas.unbind('<B1-Motion>')
        self.canvas.unbind('<ButtonRelease-1>')

        self.root.attributes("-alpha", 1)
        self.root.attributes("-transparentcolor", "#00FF00")  # Custom transparent color

        # Restore button frame after selection
        self.button_frame.place(x=self.button_frame_position[0], y=self.button_frame_position[1])
        if self.settings_visible:
            self.settings_frame.place(x=self.settings_frame_position[0], y=self.settings_frame_position[1])

        print(f"Regions selected: {self.regions}")

    def perform_ocr(self):
        """Perform OCR on the selected regions and display the first word."""
        # Hide the frames during OCR
        self.button_frame.place_forget()
        self.settings_frame.place_forget()

        # Hide overlays temporarily for OCR accuracy
        for shape in self.overlay_shapes:
            self.canvas.itemconfig(shape, state='hidden')
        for label in self.text_labels:
            self.canvas.itemconfig(label, state='hidden')
        
        self.root.update_idletasks()

        self.ocr_results = []
        for i, region in enumerate(self.regions):
            x1, y1, x2, y2 = map(int, region)
            print(f"OCR Region {i+1}: ({x1}, {y1}, {x2}, {y2})")

            image = ImageGrab.grab().crop((x1, y1, x2, y2))
            image.save(f"region_{i+1}.png")  # Save for debugging
            processed_image = self.preprocess_image(image)
            text = pytesseract.image_to_string(processed_image)
            first_word = text.split()[0] if text else "N/A"
            print(f"OCR Result {i+1}: {first_word}")
            self.ocr_results.append(first_word)

        # Restore button frame after OCR
        self.button_frame.place(x=self.button_frame_position[0], y=self.button_frame_position[1])
        if self.settings_visible:
            self.settings_frame.place(x=self.settings_frame_position[0], y=self.settings_frame_position[1])
        
        # Restore overlay visibility based on toggle state
        if self.overlays_visible:
            for shape in self.overlay_shapes:
                self.canvas.itemconfig(shape, state='normal')
            for label in self.text_labels:
                self.canvas.itemconfig(label, state='normal')
        if self.ocr_results:
            self.ocr_label.config(text=f"R1: {self.ocr_results[0]}, R2: {self.ocr_results[1]}" + (f", R3: {self.ocr_results[2]}" if self.num_regions == 3 else ""))

    def preprocess_image(self, image):
        """Preprocess the image for better OCR accuracy."""
        image = image.convert('L')  # Convert to grayscale
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)  # Increase contrast
        image = image.point(lambda p: p > 128 and 255)  # Apply thresholding
        image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)  # Upscale
        return image

    def capture_match(self):
        """Capture the current match and show the pop-up window."""
        self.perform_ocr()
        self.show_capture_popup()

    def show_capture_popup(self):
        """Show the pop-up window for capturing match details."""
        popup = tk.Toplevel(self.root)
        popup.title("Capture Match")
        popup.geometry("400x300")
        popup.transient(self.root)
        popup.grab_set()

        tk.Label(popup, text="User 1 Name:").pack(pady=5)
        user1_entry = tk.Entry(popup)
        user1_entry.pack(pady=5)
        user1_entry.insert(0, self.ocr_results[0] if len(self.ocr_results) > 0 else "")

        tk.Label(popup, text="User 2 Name:").pack(pady=5)
        user2_entry = tk.Entry(popup)
        user2_entry.pack(pady=5)
        user2_entry.insert(0, self.ocr_results[1] if len(self.ocr_results) > 1 else "")

        tk.Label(popup, text="Match Outcome:").pack(pady=5)
        outcome_var = tk.StringVar(popup)
        outcome_dropdown = ttk.Combobox(popup, textvariable=outcome_var)
        outcome_dropdown['values'] = ("User 1 Wins", "User 2 Wins", "Draw")
        outcome_dropdown.pack(pady=5)
        outcome_dropdown.current(0)

        def submit_match():
            user1_name = user1_entry.get()
            user2_name = user2_entry.get()
            outcome = outcome_dropdown.current()
            self.match_callback([user1_name, user2_name, outcome])
            popup.destroy()

        submit_button = tk.Button(popup, text="Submit", command=submit_match)
        submit_button.pack(pady=10)

    def match_callback(self, results):
        """Handle the OCR results and create a match."""
        user1_name, user2_name, outcome = results
        match = (user1_name, user2_name, outcome)
        #print(f"Match Captured: {match}")
        # Here you can add code to create a match using the Match_Manager

    def close_window(self, event):
        """Close the application."""
        self.root.destroy()

    def run(self):
        """Run the Tkinter event loop."""
        self.root.mainloop()

    def get_ocr_results(self):
        """Retrieve the OCR results."""
        return self.ocr_results


if __name__ == "__main__":
    reader = ScreenReader()
    reader.run()
