import cv2
import numpy as np
import time
import threading
import tkinter as tk
from tkinter import messagebox
import os
import glob
import time
from datetime import datetime
from PIL import Image, ImageTk
import shutil
import subprocess


# File to save the RTSP streams
STREAMS_FILE = "streams.txt"
MAX_RETRIES = 3  # Maximum number of retries for a stream
RETRY_DELAY = 2  # Delay (in seconds) between retries
RECORDINGS_DIR = "recordings"  # Directory to store motion detected videos
MAX_STORAGE_SIZE = 10 * 1024 * 1024 * 1024  # 10 GB limit for all recordings


# File to store the last used motion threshold value
SETTINGS_FILE = "settings.txt"

# Ensure the recordings directory exists
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)

# Load RTSP streams from file or use defaults
def load_streams():
    if os.path.exists(STREAMS_FILE):
        with open(STREAMS_FILE, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    return []

# Save RTSP streams to file
def save_streams(streams):
    with open(STREAMS_FILE, 'w') as file:
        for stream in streams:
            file.write(f"{stream}\n")

# Menu for adding and removing RTSP streams
# Inside the StreamInputMenu class


# Load the last motion threshold value from file or use a default if not set
def load_last_threshold():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as file:
            try:
                return int(file.read().strip())
            except ValueError:
                return 1000  # Default value if there's an error
    return 1000  # Default threshold value

# Save the last motion threshold value to file
def save_last_threshold(threshold):
    with open(SETTINGS_FILE, 'w') as file:
        file.write(str(threshold))

# Inside the StreamInputMenu class
class StreamInputMenu:
    def __init__(self, existing_streams):
        self.streams = existing_streams
        self.root = tk.Tk()
        self.root.title("RTSP Stream Configuration")
        self.root.geometry("400x700")  # Adjusted to accommodate new slider

        # Frame for stream management
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Label and Listbox for displaying current streams
        self.label = tk.Label(self.frame, text="Current RTSP Streams:", font=("Arial", 12))
        self.label.pack()

        # Scrollable listbox for the streams
        self.stream_listbox = tk.Listbox(self.frame, width=50, height=8)
        self.stream_listbox.pack(pady=10, side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add scrollbar to the listbox
        scrollbar = tk.Scrollbar(self.frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.stream_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.stream_listbox.yview)

        # Input for stream URLs
        self.stream_label = tk.Label(self.root, text="Enter RTSP Stream URL:", font=("Arial", 10))
        self.stream_label.pack(pady=5)
        
        self.stream_entry = tk.Entry(self.root, width=50)  # Input field for streams
        self.stream_entry.pack(pady=5)

        # Buttons for managing streams
        self.add_button = tk.Button(self.root, text="Add Stream", command=self.add_stream, font=("Arial", 10))
        self.add_button.pack(pady=5)

        self.edit_button = tk.Button(self.root, text="Edit Selected Stream", command=self.edit_stream, font=("Arial", 10))
        self.edit_button.pack(pady=5)

        self.remove_button = tk.Button(self.root, text="Remove Selected Stream", command=self.remove_stream, font=("Arial", 10))
        self.remove_button.pack(pady=5)

        # Button to clear all recordings
        self.clear_recordings_button = tk.Button(self.root, text="Clear All Recordings", command=self.clear_recordings, font=("Arial", 10), bg="red", fg="white")
        self.clear_recordings_button.pack(pady=5)

        # Button to open recordings folder
        self.open_folder_button = tk.Button(self.root, text="Open Recordings Folder", command=self.open_recordings_folder, font=("Arial", 10))
        self.open_folder_button.pack(pady=5)

        # Input field for rotation duration
        self.duration_label = tk.Label(self.root, text="Rotation Duration (seconds):", font=("Arial", 10))
        self.duration_label.pack(pady=10)

        self.duration_entry = tk.Entry(self.root, width=20)
        self.duration_entry.pack(pady=5)
        self.duration_entry.insert(0, "30")  # Default to 30 seconds

        # Slider for motion detection threshold with last saved value
        self.motion_threshold_label = tk.Label(self.root, text="Motion Detection Threshold:", font=("Arial", 10))
        self.motion_threshold_label.pack(pady=10)

        last_threshold = load_last_threshold()  # Load last saved threshold value
        self.motion_threshold_slider = tk.Scale(self.root, from_=100, to=10000, orient=tk.HORIZONTAL)
        self.motion_threshold_slider.set(last_threshold)  # Set slider to last saved value
        self.motion_threshold_slider.pack(pady=5)

        self.continue_button = tk.Button(self.root, text="Continue", command=self.launch_camera, font=("Arial", 12, "bold"), bg="green", fg="white")
        self.continue_button.pack(pady=10)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.update_stream_listbox()


    def update_stream_listbox(self):
        """Update the Listbox with current streams."""
        self.stream_listbox.delete(0, tk.END)  # Clear current list
        for stream in self.streams:
            self.stream_listbox.insert(tk.END, stream)  # Add each stream to the list

    def add_stream(self):
        stream = self.stream_entry.get()
        if stream:
            self.streams.append(stream)
            save_streams(self.streams)
            self.update_stream_listbox()  # Refresh the listbox
            messagebox.showinfo("Success", "Stream added successfully!")
            self.stream_entry.delete(0, tk.END)  # Clear the entry
        else:
            messagebox.showwarning("Warning", "Please enter a valid RTSP stream URL.")

    def edit_stream(self):
        selected_index = self.stream_listbox.curselection()
        if selected_index:
            stream = self.stream_entry.get()
            if stream:
                self.streams[selected_index[0]] = stream
                save_streams(self.streams)
                self.update_stream_listbox()  # Refresh the listbox
                messagebox.showinfo("Success", "Stream updated successfully!")
                self.stream_entry.delete(0, tk.END)  # Clear the entry
            else:
                messagebox.showwarning("Warning", "Please enter a valid RTSP stream URL.")
        else:
            messagebox.showwarning("Warning", "Please select a stream to edit.")

    def remove_stream(self):
        selected_index = self.stream_listbox.curselection()
        if selected_index:
            self.streams.pop(selected_index[0])
            save_streams(self.streams)
            self.update_stream_listbox()  # Refresh the listbox
            messagebox.showinfo("Success", "Stream removed successfully!")
            self.stream_entry.delete(0, tk.END)  # Clear the entry
        else:
            messagebox.showwarning("Warning", "Please select a stream to remove.")

    def clear_recordings(self):
        """Delete all recordings in the recordings directory."""
        if os.path.exists(RECORDINGS_DIR):
            confirm = messagebox.askyesno("Clear All Recordings", "Are you sure you want to delete all recordings?")
            if confirm:
                shutil.rmtree(RECORDINGS_DIR)  # Remove the entire directory
                os.makedirs(RECORDINGS_DIR)    # Recreate the empty directory
                messagebox.showinfo("Success", "All recordings have been deleted.")
        else:
            messagebox.showinfo("Info", "No recordings found to delete.")

    def open_recordings_folder(self):
        """Open the recordings directory in the system's default file explorer."""
        if os.path.exists(RECORDINGS_DIR):
            # Open the recordings folder in the default file explorer
            subprocess.Popen(f'explorer "{RECORDINGS_DIR}"' if os.name == 'nt' else f'xdg-open "{RECORDINGS_DIR}"')
        else:
            messagebox.showinfo("Info", "The recordings folder does not exist.")

    def launch_camera(self):
        try:
            # Get the rotation duration entered by the user
            rotation_duration = int(self.duration_entry.get())
            motion_threshold = self.motion_threshold_slider.get()  # Get the threshold from the slider
            save_last_threshold(motion_threshold)  # Save the threshold to retain for future
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for rotation duration.")
            return

        self.root.destroy()  # Close the menu
        main(self.streams, rotation_duration, motion_threshold)  # Pass the threshold to main

    def on_close(self):
        self.root.destroy()



# Frame Capture Thread with retry mechanism and rain filtering in motion detection
class FrameCapture(threading.Thread):
    def __init__(self, stream, motion_threshold):
        super().__init__()
        self.stream = stream
        self.motion_threshold = motion_threshold  # Set the threshold value for motion detection
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.last_frame_time = time.time()
        self.previous_frame = None
        self.motion_detected = False
        self.recording_start_time = None
        self.video_writer = None

    def run(self):
        retries = 0
        while retries < MAX_RETRIES and self.running:
            if self.initialize_capture():
                while self.running:
                    ret, frame = self.cap.read()
                    with self.lock:
                        if ret:
                            # Resize frame to improve performance
                            frame = cv2.resize(frame, (640, 360))  # Resize frame to lower resolution
                            self.frame = frame
                            self.last_frame_time = time.time()  # Update time when a new frame is received
                            self.check_and_record(frame)
                        else:
                            # If no frame, check if the stream is frozen for more than 3 seconds
                            if time.time() - self.last_frame_time > 3:
                                self.restart_stream()
                                break  # Break out to retry the stream initialization
            else:
                retries += 1
                time.sleep(RETRY_DELAY)  # Wait before retrying

    def initialize_capture(self):
        """Attempt to initialize the stream capture."""
        self.cap = cv2.VideoCapture(self.stream)
        if not self.cap.isOpened():
            print(f"Failed to open stream {self.stream}. Retrying...")
            return False
        return True

    def get_frame(self):
        with self.lock:
            return self.frame

    def check_and_record(self, frame):
        """Detect motion and record if needed."""
        motion = self.detect_motion()
        current_time = time.time()

        if motion and not self.motion_detected:
            self.motion_detected = True
            self.recording_start_time = current_time - 5  # Record 5 seconds before motion detected
            self.start_recording()

        # Write frame if currently recording and motion detected
        if self.motion_detected and self.video_writer is not None:
            try:
                self.video_writer.write(frame)
            except Exception as e:
                print(f"Error writing frame: {e}")
                self.stop_recording()  # Stop recording on error

        # Stop recording 5 seconds after motion stops
        if not motion and self.motion_detected and current_time - self.recording_start_time > 10:
            self.stop_recording()

    def detect_motion(self):
        """Detects significant motion by comparing frames."""
        if self.frame is None:
            return False

        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        self.previous_frame = gray

        for contour in contours:
            if cv2.contourArea(contour) > self.motion_threshold:  # Use the slider-defined threshold
                return True
        return False

    def start_recording(self):
        """Start recording the motion-detected video."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"{RECORDINGS_DIR}/motion_{timestamp}.avi"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(video_filename, fourcc, 10.0, (640, 360))
        if self.video_writer.isOpened():
            print(f"Started recording: {video_filename}")
        else:
            print("Failed to start recording")
            self.video_writer = None

    def stop_recording(self):
        """Stop the recording and release resources."""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            print("Stopped recording")
        self.motion_detected = False

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.stop_recording()

    def restart_stream(self):
        """Restart the stream capture if it freezes."""
        if self.cap:
            self.cap.release()
        print(f"Restarting stream {self.stream}...")
        self.run()

def check_storage_limit():
    """Ensure the total storage of recorded videos doesn't exceed 10GB by deleting the oldest files."""
    files = sorted(glob.glob(f"{RECORDINGS_DIR}/*.avi"), key=os.path.getmtime)
    total_size = sum(os.path.getsize(f) for f in files)

    while total_size > MAX_STORAGE_SIZE and files:
        oldest_file = files.pop(0)
        total_size -= os.path.getsize(oldest_file)
        os.remove(oldest_file)
        print(f"Deleted old video to free up space: {oldest_file}")

# Playback window to display recorded videos
class PlaybackWindow:
    def __init__(self, master, return_callback):
        self.master = master
        self.master.title("Playback Window")
        self.master.geometry("600x400")
        self.return_callback = return_callback

        # Create the listbox to display recorded videos
        self.video_listbox = tk.Listbox(self.master, width=80, height=15)
        self.video_listbox.pack(pady=10)

        # Load recorded videos and display them with time, date, and thumbnail
        self.load_recorded_videos()

        # Button to return to live stream
        self.return_button = tk.Button(self.master, text="Return to Live Stream", command=self.return_to_live)
        self.return_button.pack(pady=10)

    def load_recorded_videos(self):
        """Loads and displays recorded videos with their date, time, and thumbnails."""
        videos = sorted(glob.glob(f"{RECORDINGS_DIR}/*.avi"), key=os.path.getmtime)
        for video in videos:
            video_name = os.path.basename(video)
            video_time = time.ctime(os.path.getmtime(video))  # Get modification time
            thumbnail = self.get_video_thumbnail(video)

            # Create a Tkinter image from the thumbnail
            thumbnail_image = ImageTk.PhotoImage(Image.fromarray(thumbnail))
            thumbnail_label = tk.Label(self.master, image=thumbnail_image)
            thumbnail_label.image = thumbnail_image  # Keep reference to avoid garbage collection
            thumbnail_label.pack()

            self.video_listbox.insert(tk.END, f"{video_time} - {video_name}")

    def get_video_thumbnail(self, video_path):
        """Generates a thumbnail from the first frame of the video."""
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()

        if ret:
            frame = cv2.resize(frame, (100, 75))  # Resize to thumbnail size
            return frame
        else:
            return np.zeros((75, 100, 3), dtype=np.uint8)  # Return blank thumbnail if no frame

    def return_to_live(self):
        """Close the playback window and return to the live stream."""
        self.master.destroy()
        self.return_callback()

def open_playback_window():
    """Open the playback window."""
    root = tk.Tk()
    playback = PlaybackWindow(root, return_to_live_stream)
    root.mainloop()

def return_to_live_stream():
    """Return to the live stream."""
    streams = load_streams()
    main(streams)

def main(streams, rotation_duration=30, motion_threshold=1000):
    # Define the RTSP streams and other constants
    output_width = 1280
    output_height = 720
    padding = 5  # Minimal padding

    # Define the thumbnail width as 1/5th of the entire window
    thumbnail_width = output_width // 5
    full_screen_width = output_width - thumbnail_width

    # Determine grid size based on number of streams
    num_streams = len(streams)

    # Pass motion_threshold to FrameCapture objects
    capture_threads = [FrameCapture(stream, motion_threshold) for stream in streams]


    # Start all threads
    for thread in capture_threads:
        thread.start()

    # Create a window in normal mode
    cv2.namedWindow('RTSP Streams - Grid View', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('RTSP Streams - Grid View', output_width, output_height)  # Set the window size

    # To track the full-screen state and auto-switching
    full_screen = False
    full_screen_stream_idx = None
    auto_switch = False
    motion_detect_mode = False  # Motion detection mode tracking
    switch_time = time.time()
    current_stream_idx = 0

    try:
        while True:
            start_time = time.time()

            # List to hold the frames
            frames = []

            # Capture frames from each thread
            for thread in capture_threads:
                frame = thread.get_frame()
                if frame is not None:
                    frames.append(frame)
                else:
                    frames.append(np.zeros((360, 640, 3), np.uint8))  # Blank frame if no capture

            # Handle auto-switching based on the user-defined duration
            if auto_switch and (time.time() - switch_time > rotation_duration):
                current_stream_idx = (current_stream_idx + 1) % len(streams)
                full_screen = True
                full_screen_stream_idx = current_stream_idx
                switch_time = time.time()

            # Motion detection mode
            if motion_detect_mode:
                for idx, thread in enumerate(capture_threads):
                    if thread.motion_detected:
                        full_screen = True
                        full_screen_stream_idx = idx
                        break

            # Create the display layout
            if full_screen and full_screen_stream_idx is not None:
                # Display the selected stream in the left four-fifths
                full_screen_frame = cv2.resize(frames[full_screen_stream_idx], (full_screen_width, output_height))
                display_grid = full_screen_frame

                # Display the other streams as thumbnails in the right one-fifth
                other_frames = [frames[i] for i in range(len(frames)) if i != full_screen_stream_idx]
                if other_frames:
                    # Resize and stack the thumbnails vertically
                    thumbnail_frames = [
                        cv2.resize(f, (thumbnail_width, output_height // len(other_frames)))
                        for f in other_frames
                    ]
                    thumbnails = np.vstack(thumbnail_frames)
                    # Combine full-screen stream with the thumbnails
                    display_grid = np.hstack([full_screen_frame, thumbnails])

            else:
                # Add a blank frame if there are fewer than needed
                rows = (num_streams + 2) // 3  # Calculate rows based on stream count
                cols = min(num_streams, 3)      # Maximum 3 columns

                while len(frames) < rows * cols:
                    frames.append(np.zeros((360, 640, 3), np.uint8))

                # Create padded frames for grid display
                padded_frames = []
                for r in range(rows):
                    row_frames = [
                        cv2.copyMakeBorder(f, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(0, 0, 0))
                        for f in frames[r * cols:(r + 1) * cols]
                    ]
                    padded_frames.append(np.hstack(row_frames))

                # Create the final grid layout
                display_grid = np.vstack(padded_frames)

            # Resize grid for windowed mode
            grid_resized = cv2.resize(display_grid, (output_width, output_height))  # Resize for windowed mode

            # Display the grid in the window
            cv2.imshow('RTSP Streams - Grid View', grid_resized)

            # Frame rate limiting to 10 FPS
            elapsed_time = time.time() - start_time
            remaining_time = max(0, (1.0 / 10) - elapsed_time)  # 10 FPS

            # Detect key presses for toggling streams
            key = cv2.waitKey(int(remaining_time * 1000))
            if key & 0xFF == ord('q'):
                break
            elif key & 0xFF == ord('a'):
                # Toggle auto-switching mode
                auto_switch = not auto_switch
                if auto_switch:
                    # Start with the first stream
                    current_stream_idx = 0
                    full_screen = True
                    full_screen_stream_idx = current_stream_idx
                    switch_time = time.time()
                else:
                    full_screen = False
                    full_screen_stream_idx = None
            # elif key & 0xFF == ord('m'):
                # Open playback window
            #    open_playback_window()
            elif key & 0xFF == ord('s'):
                # Toggle motion detection mode
                motion_detect_mode = not motion_detect_mode
                if motion_detect_mode:
                    print("Motion detection mode enabled")
                else:
                    print("Motion detection mode disabled")

            elif ord('1') <= key <= ord(str(min(num_streams, 9))):
                stream_idx = key - ord('1')
                if stream_idx < len(streams):
                    if full_screen and full_screen_stream_idx == stream_idx:
                        # If already in full screen for this stream, go back to grid
                        full_screen = False
                        full_screen_stream_idx = None
                        auto_switch = False  # Stop auto-switching if manually changed
                    else:
                        # Go to full screen for the selected stream
                        full_screen = True
                        full_screen_stream_idx = stream_idx
                        auto_switch = False  # Stop auto-switching if manually changed

    finally:
        # Stop all threads
        for thread in capture_threads:
            thread.stop()

        # Release resources
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # Load existing streams at startup
    streams = load_streams()

    # Open stream input menu
    menu = StreamInputMenu(streams)
    menu.root.mainloop()
