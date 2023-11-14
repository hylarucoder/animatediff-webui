import cv2
import os


def extract_frames(video_path, output_path, frame_interval=3):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video file: {video_path}")
        return

    frame_count = 0
    write_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            # Output filename is zero-padded to eight digits
            output_filename = os.path.join(output_path, f"{write_count:08}.png")
            cv2.imwrite(output_filename, frame)
            write_count += 1

        frame_count += 1

    cap.release()
    print(f"Extracted {write_count} frames from {video_path}")


# Use the function
if __name__ == "__main__":
    extract_frames(video_path, output_path)
