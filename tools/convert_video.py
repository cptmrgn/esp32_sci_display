import cv2
import numpy as np
import os
from pathlib import Path

def convert_video_to_frames(video_path, output_dir, target_size=(480, 480)):
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Resize frame
        frame = cv2.resize(frame, target_size)
        
        # Convert to RGB565
        # First convert from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to RGB565
        r = (frame[:,:,0] >> 3).astype(np.uint16) << 11
        g = (frame[:,:,1] >> 2).astype(np.uint16) << 5
        b = (frame[:,:,2] >> 3).astype(np.uint16)
        rgb565 = r | g | b
        
        # Save as raw binary file
        output_path = os.path.join(output_dir, f'frame{frame_count}.raw')
        rgb565.astype(np.uint16).tofile(output_path)
        
        frame_count += 1
        print(f'Processed frame {frame_count}')
    
    cap.release()
    print(f'Converted {frame_count} frames')

if __name__ == '__main__':
    # Replace with your video file path
    video_path = 'your_video.mp4'
    output_dir = '../data'
    
    convert_video_to_frames(video_path, output_dir)
