import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab, Image, ImageEnhance
import pytesseract
import ctypes
import logging

# Enable DPI awareness for accurate screen scaling
ctypes.windll.shcore.SetProcessDpiAwareness(2)
# Set the Tesseract executable path if needed
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Get logger for this module
logger = logging.getLogger('pss_companion.screenReader')


class OCRProcessor:
    """Handles OCR processing for screen regions"""
    def __init__(self, engine=None):
        """
        Initialize the OCR processor
        :param engine: Optional OCR engine to use (if None, will try to initialize one)
        """
        self.engine = engine
        try:
            if not self.engine:
                # Try to import and initialize pytesseract
                try:
                    import pytesseract
                    from PIL import ImageGrab
                    self.engine = pytesseract
                    self._grab_image = ImageGrab.grab
                    logger.info("Initialized OCR processor with pytesseract")
                except ImportError:
                    logger.error("Failed to import pytesseract or PIL. OCR functionality will be limited.")
                    self.engine = None
        except Exception as e:
            logger.error(f"Error initializing OCR processor: {e}")
            self.engine = None

    def preprocess_image(self, image):
        try:
            image = image.convert('L')  # Grayscale
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)  # Increase contrast
            image = image.point(lambda p: 255 if p > 128 else 0)  # Thresholding
            # Upscale the image to improve OCR accuracy
            image = image.resize((image.width * 2, image.height * 2), Image.LANCZOS)
            return image
        except Exception as e:
            logging.error(f'Error in preprocess_image(self,: {e}')
            raise

    def perform_ocr(self, region):
        """
        Perform OCR on a screen region
        :param region: Tuple (x1, y1, x2, y2) defining the screen region
        :return: Extracted text
        """
        if not self.engine:
            logger.warning("No OCR engine available")
            return "OCR not available"
            
        try:
            # Capture the screen region
            image = self._grab_image(bbox=region)
            # Perform OCR
            text = self.engine.image_to_string(image)
            logger.debug(f"OCR result from region {region}: {text.strip()}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return f"OCR error: {str(e)}"


class MatchDetector:
    """Periodically checks a region (e.g. the match-making area) for updates via OCR."""
    def __init__(self, root, ocr_processor, region, callback, polling_interval=5000):
        """
        :param root: The Tkinter root (used for scheduling)
        :param ocr_processor: Instance of OCRProcessor to handle OCR
        :param region: The screen region (x1, y1, x2, y2) to monitor for match detection
        :param callback: Function to call when a new match is detected
        :param polling_interval: Milliseconds between checks
        """
        try:
            self.root = root
            self.ocr_processor = ocr_processor
            self.region = region
            self.callback = callback
            self.polling_interval = polling_interval
            self.active = False
            logger.debug(f"Match detector initialized with polling interval {polling_interval}ms")
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def start(self):
        """Start monitoring the region"""
        try:
            self.active = True
            logger.info("Match detector started")
            self._poll()
        except Exception as e:
            logging.error(f'Error in start(self):: {e}')
            raise

    def stop(self):
        """Stop monitoring the region"""
        try:
            self.active = False
            logger.info("Match detector stopped")
        except Exception as e:
            logging.error(f'Error in stop(self):: {e}')
            raise

    def _poll(self):
        """Poll the region for changes and call the callback if needed"""
        try:
            if not self.active:
                return
                
            try:
                result = self.ocr_processor.perform_ocr(self.region)
                logger.debug(f"Auto-match OCR Result: {result}")
                
                # Optionally, call the callback with the OCR result if it meets certain conditions
                if callable(self.callback):
                    self.callback(result)
                    
            except Exception as e:
                logger.error(f"Error in match detector polling: {e}")
                
            # Schedule the next poll
            self.root.after(self.polling_interval, self._poll)
        except Exception as e:
            logging.error(f'Error in _poll(self):: {e}')
            raise


class OverlayGUI:
    """Handles the overlay GUI including region selection and manual match capture."""
    def __init__(self, root, ocr_processor, num_regions=3):
        try:
            self.root = root
            self.ocr_processor = ocr_processor
            self.num_regions = num_regions
            self.regions = []
            self.overlay_shapes = []
            self.text_labels = []
            self.region_count = 0
            self.drawing = False
            self.current_box = None

            # Create a full-screen transparent window
            self.root.title("PSS Overlay")
            self.root.attributes("-transparentcolor", "#00FF00")
            self.root.attributes("-topmost", True)
            self.root.overrideredirect(True)
            self.root.attributes("-alpha", 1)
            self.root.configure(bg="#00FF00")
            self.screen_width = self.root.winfo_screenwidth()
            self.screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{self.screen_width}x{self.screen_height}+0+0")
            
            self.canvas = tk.Canvas(self.root, bg='#00FF00', highlightthickness=0)
            self.canvas.pack(fill='both', expand=True)
            
            # Setup basic button frame
            self.button_frame = tk.Frame(self.root, bg='gray')
            self.button_frame.place(x=10, y=10)
            button_font = ("Arial", 14, "bold")
            self.capture_button = tk.Button(self.button_frame, text="Capture Match", command=self.capture_match, bg='red', fg='white', font=button_font)
            self.capture_button.pack(padx=5, pady=5)
            # For auto-match toggling
            self.matchmaking_var = tk.BooleanVar(value=False)
            self.match_checkbutton = tk.Checkbutton(self.button_frame, text="Enable Match Making", command=self.toggle_matchmaking, bg='green', fg='white', font=button_font, variable=self.matchmaking_var, indicatoron=False)
            self.match_checkbutton.pack(padx=5, pady=5)

            # Bind escape key to exit
            self.root.bind('<Escape>', lambda e: self.root.destroy())
        except Exception as e:
            logging.error(f'Error in __init__(self,: {e}')
            raise

    def start_drawing(self):
        """Resets previous selections and starts region drawing."""
        try:
            self.drawing = True
            self.region_count = 0
            self.regions.clear()
            for shape in self.overlay_shapes:
                self.canvas.delete(shape)
            for label in self.text_labels:
                self.canvas.delete(label)
            self.overlay_shapes.clear()
            self.text_labels.clear()
            self.canvas.config(cursor='cross')
            self.canvas.bind('<Button-1>', self.start_draw)
            self.canvas.bind('<B1-Motion>', self.draw)
            self.canvas.bind('<ButtonRelease-1>', self.end_draw)
            # Make background semi-transparent for clarity
            self.root.attributes("-alpha", 0.5)
            self.canvas.config(bg='gray')
        except Exception as e:
            logging.error(f'Error in start_drawing(self):: {e}')
            raise

    def start_draw(self, event):
        """Start drawing a rectangle for a region."""
        try:
            if self.region_count >= self.num_regions:
                return
            self.start_x, self.start_y = event.x, event.y
            colors = ['green', 'orange', 'red']
            labels = ["User 1", "User 2", "Match Making"]
            self.current_box = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                            outline=colors[self.region_count], fill=colors[self.region_count],
                                                            stipple='gray50')
            self.overlay_shapes.append(self.current_box)
            text_label = self.canvas.create_text(self.start_x + 5, self.start_y + 5, text=labels[self.region_count],
                                                anchor="nw", fill="white", font=("Arial", 12, "bold"))
            self.text_labels.append(text_label)
        except Exception as e:
            logging.error(f'Error in start_draw(self,: {e}')
            raise

    def draw(self, event):
        """Update rectangle as the user drags the mouse."""
        try:
            self.canvas.coords(self.current_box, self.start_x, self.start_y, event.x, event.y)
            self.canvas.coords(self.text_labels[self.region_count], min(self.start_x, event.x) + 5, min(self.start_y, event.y) + 5)
        except Exception as e:
            logging.error(f'Error in draw(self,: {e}')
            raise

    def end_draw(self, event):
        """Finalize the drawn region."""
        try:
            self.region_count += 1
            self.regions.append(self.canvas.coords(self.current_box))
            if self.region_count >= self.num_regions:
                self.finish_drawing()
        except Exception as e:
            logging.error(f'Error in end_draw(self,: {e}')
            raise

    def finish_drawing(self):
        """Restore UI state after region selection."""
        try:
            self.drawing = False
            self.canvas.config(cursor='', bg='#00FF00')
            self.canvas.unbind('<Button-1>')
            self.canvas.unbind('<B1-Motion>')
            self.canvas.unbind('<ButtonRelease-1>')
            self.root.attributes("-alpha", 1)
            self.root.attributes("-transparentcolor", "#00FF00")
            print(f"Regions selected: {self.regions}")
        except Exception as e:
            logging.error(f'Error in finish_drawing(self):: {e}')
            raise

    def perform_ocr_on_regions(self, regions):
        """Perform OCR on the provided regions."""
        try:
            results = []
            for i, region in enumerate(regions):
                print(f"Performing OCR on region {i+1}: {region}")
                text = self.ocr_processor.perform_ocr(region)
                print(f"OCR result for region {i+1}: {text}")
                results.append(text)
            return results
        except Exception as e:
            logging.error(f'Error in perform_ocr_on_regions(self,: {e}')
            raise

    def capture_match(self):
        """Manually capture a match by OCR on the first two regions."""
        try:
            if len(self.regions) < 2:
                print("Not enough regions selected for match capture.")
                return
            # Use the first two regions for user names
            ocr_results = self.perform_ocr_on_regions(self.regions[:2])
            self.show_capture_popup(ocr_results)
        except Exception as e:
            logging.error(f'Error in capture_match(self):: {e}')
            raise

    def show_capture_popup(self, ocr_results):
        """Display a popup to confirm match details."""
        try:
            popup = tk.Toplevel(self.root)
            popup.title("Capture Match")
            popup.geometry("400x300")
            popup.transient(self.root)
            popup.grab_set()

            tk.Label(popup, text="User 1 Name:").pack(pady=5)
            user1_entry = tk.Entry(popup)
            user1_entry.pack(pady=5)
            user1_entry.insert(0, ocr_results[0] if len(ocr_results) > 0 else "")

            tk.Label(popup, text="User 2 Name:").pack(pady=5)
            user2_entry = tk.Entry(popup)
            user2_entry.pack(pady=5)
            user2_entry.insert(0, ocr_results[1] if len(ocr_results) > 1 else "")

            tk.Label(popup, text="Match Outcome:").pack(pady=5)
            outcome_var = tk.StringVar(popup)
            outcome_dropdown = ttk.Combobox(popup, textvariable=outcome_var)
            outcome_dropdown['values'] = ("User 1 Wins", "User 2 Wins", "Draw")
            outcome_dropdown.pack(pady=5)
            outcome_dropdown.current(0)

            def submit_match():
                try:
                    user1_name = user1_entry.get()
                    user2_name = user2_entry.get()
                    outcome = outcome_dropdown.get()
                    print(f"Match Captured: {user1_name} vs {user2_name} - Outcome: {outcome}")
                    popup.destroy()
                except Exception as e:
                    logging.error(f'Error in submit_match():: {e}')
                    raise

            tk.Button(popup, text="Submit", command=submit_match).pack(pady=10)
        except Exception as e:
            logging.error(f'Error in show_capture_popup(self,: {e}')
            raise

    def toggle_matchmaking(self):
        """Toggle auto-match detection and update button state."""
        try:
            if not self.matchmaking_var.get():
                # When enabling, set the button text to indicate waiting for a match
                self.match_checkbutton.config(bg='red', text="Match Making (Waiting)")
                self.matchmaking_var.set(True)
                if len(self.regions) < 3:
                    print("Match Making region not selected. Please select all regions first.")
                    return
                # Initialize and start the auto-match detector using the third region.
                self.match_detector = MatchDetector(self.root, self.ocr_processor, self.regions[2],
                                                    callback=self.handle_auto_match)
                self.match_detector.start()
            else:
                # When disabling, revert the button text
                self.match_checkbutton.config(bg='green', text="Enable Match Making")
                self.matchmaking_var.set(False)
                if hasattr(self, 'match_detector') and self.match_detector:
                    self.match_detector.stop()
        except Exception as e:
            logging.error(f'Error in toggle_matchmaking(self):: {e}')
            raise

    def handle_auto_match(self, ocr_result):
        """Callback for when auto-match detection gets an OCR result.
           Update the button text based on the OCR result."""
        try:
            if ocr_result == "N/A":
                # No match detected, update button to show waiting state
                self.match_checkbutton.config(text="Match Making (Waiting)")
            else:
                # Match detected: update button to show match found
                self.match_checkbutton.config(text=f"Match Found: {ocr_result}")
                # Optionally, you might stop auto detection once a match is found:
                self.match_detector.stop()
        except Exception as e:
            logging.error(f'Error in handle_auto_match(self,: {e}')
            raise


    def set_ocr_processor(self, ocr_processor):
        try:
            self.ocr_processor = ocr_processor
        except Exception as e:
            logging.error(f'Error in set_ocr_processor(self,: {e}')
            raise


class OverlayApp:
    """Main application that ties together the GUI and OCR functionality."""
    def __init__(self):
        try:
            self.root = tk.Tk()
            self.ocr_processor = OCRProcessor()
            # Create GUI and pass the OCR processor; auto-match will be set up later after regions are drawn
            self.gui = OverlayGUI(self.root, self.ocr_processor)
            # Optionally add a menu or button to trigger region selection:
            self.add_control_panel()
        except Exception as e:
            logging.error(f'Error in __init__(self):: {e}')
            raise

    def add_control_panel(self):
        try:
            control_panel = tk.Frame(self.root, bg='darkgray')
            control_panel.place(x=10, y=100)
            btn_font = ("Arial", 12, "bold")
            tk.Button(control_panel, text="Select Regions", command=self.gui.start_drawing, bg='blue', fg='white', font=btn_font).pack(padx=5, pady=5)
        except Exception as e:
            logging.error(f'Error in add_control_panel(self):: {e}')
            raise

    def run(self):
        try:
            self.root.mainloop()
        except Exception as e:
            logging.error(f'Error in run(self):: {e}')
            raise


if __name__ == '__main__':
    app = OverlayApp()
    app.run()
