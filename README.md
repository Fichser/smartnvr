This Python code is a motion-detection, multi-stream RTSP (Real-Time Streaming Protocol) viewer with recording functionality. It allows users to add RTSP streams, set motion-detection thresholds, and view live streams in a grid layout or full-screen mode, automatically switching based on user-defined settings.

Key Libraries and Their Roles
cv2 (OpenCV): A popular library for computer vision and image processing. It captures, processes, and displays video frames from RTSP streams. Here, it’s used to capture video streams, detect motion, and resize frames for layout display.
numpy: Used for handling arrays, such as the pixel data of frames captured from the streams.
time and datetime: These libraries provide functions to manage time for frame rates, recording duration, and timestamping recorded files.
threading: Allows concurrent operations using threads. Each RTSP stream runs in a separate thread to handle frame capturing independently, enhancing performance.
tkinter: A standard GUI library in Python, which is used to create the interactive menu for stream management and settings input.
PIL (Python Imaging Library): Used to process images (generate thumbnails of recorded videos) and display them in the playback window.
shutil: Provides functions for file operations like deleting directories. Here, it’s used to clear the recordings directory.
subprocess: Used to open the recordings directory in the system’s default file explorer.
Main Components and How They Work
Settings and Initialization

The program saves stream URLs, motion-detection threshold values, and other settings to files (streams.txt and settings.txt). It loads these settings on startup.
It ensures a directory named recordings exists to store videos where motion is detected.
StreamInputMenu Class: Handles the User Interface for stream management

This class allows users to add, edit, and remove RTSP streams through an interactive menu.
Users can also set motion detection sensitivity using a slider and specify the rotation duration for auto-switching between streams.
A threshold value slider allows for adjusting motion detection sensitivity, which is saved for future use.
FrameCapture Class: Handles capturing and processing frames from each RTSP stream

This class runs as a thread to handle a specific RTSP stream, with each instance capturing and processing frames independently.
Motion Detection: It converts frames to grayscale, blurs them, and compares consecutive frames to detect significant motion based on the user-defined threshold.
If motion is detected, it starts recording, and after motion ends, it records for an additional 5 seconds.
If no frames are captured for more than 3 seconds, the class attempts to restart the stream.
Storage Management

A function named check_storage_limit() limits storage usage by deleting the oldest videos if the recordings folder exceeds 10GB.
PlaybackWindow Class: Displays recorded videos for playback

This class displays a list of recorded videos, including their creation time and a thumbnail for each.
It generates thumbnails by capturing the first frame of each video, resized to fit within the GUI.
main Function: Controls the RTSP viewing and display layout

The main function captures frames from each stream and arranges them in a grid layout.
If motion detection mode is enabled, the interface automatically switches to the stream where motion is detected.
Full-screen mode can be toggled for any specific stream, and there’s an auto-switching feature for rotating through streams after a specified duration.
Keyboard commands allow toggling between grid view, full-screen mode, auto-switching, and motion detection mode.
Workflow
Stream Input and Configuration: Users interact with the menu to input stream URLs, set motion detection sensitivity, and select auto-switching duration.
Frame Capture and Motion Detection: Each stream runs on a separate thread to independently capture frames, detect motion, and record videos when motion is detected.
Display and Playback: Streams are displayed in either a grid or full-screen layout with optional auto-switching or motion-detection-based switching. Recorded videos can be viewed in the playback window.
This setup allows the system to monitor multiple streams, detect motion, record clips, manage storage, and provide a flexible display layout, all within an intuitive GUI.

The code includes a few keyboard shortcuts to control the RTSP viewer, allowing you to manage display modes and toggle features quickly. Here’s a breakdown of each shortcut:

q - Quit the Viewer:

Pressing q closes the RTSP viewer window and stops all threads, effectively ending the application.
a - Toggle Auto-Switch Mode:

This shortcut enables or disables auto-switching between streams based on the rotation duration set in the StreamInputMenu.
When auto-switching is enabled, the viewer cycles through streams in full-screen mode every few seconds (as set in the rotation duration).
Pressing a again stops the auto-switching, returning to the grid layout.
s - Toggle Motion Detection Mode:

When enabled, motion detection mode automatically switches the view to the stream where motion is detected.
If no motion is detected, the viewer remains in the grid layout or auto-switch mode.
Pressing s again disables this mode, and it returns to the previously active display mode.
1 to 9 - Select Specific Stream for Full-Screen Display:

Pressing a number key (1 through 9) displays the corresponding stream in full-screen mode.
For example, pressing 1 displays the first stream, 2 the second, and so on.
If the selected stream is already in full-screen mode, pressing its corresponding number again returns to the grid layout and disables auto-switching if it was active.
These shortcuts offer quick control over how the streams are displayed, allowing for flexible viewing with minimal interaction required in the GUI.
