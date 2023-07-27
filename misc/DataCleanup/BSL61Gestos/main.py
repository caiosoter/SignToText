import cv2
import os
import numpy as np
from openni import openni2
from multiprocessing import Pool

#This script was used to convert .oni files to .avi. 
#The original dataset contained only files in this format
# Original DataSet:  https://web.inf.ufpr.br/vri/databases/brazilian-sign-language-libras-hand-configurations-database/ 

def process_file(args):
    file_path, new_dir_path, file_name = args  # Unpack the arguments
    try:
        # Load the ONI file
        print(file_path)
        dev = openni2.Device.open_file(file_path.encode('utf-8'))
        color_stream = dev.create_color_stream()

        # Start the stream
        color_stream.start()

        # Create an OpenCV video writer
        new_file_path = os.path.join(new_dir_path, file_name.replace(".oni", ".avi"))
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(new_file_path, fourcc, 20.0, (640,480))

        n_frames = color_stream.get_number_of_frames()

        n_processed_frames = 0
        while True:
            # Break the loop if all frames have been processed
            if n_processed_frames >= n_frames:
                break

            # Read a frame from the color stream
            frame = color_stream.read_frame()
            frame_data = np.array(frame.get_buffer_as_triplet()).reshape([480, 640, 3])

            # Convert the frame to a numpy array
            frame_data = cv2.cvtColor(frame_data, cv2.COLOR_RGB2BGR)
            # Write the frame to the video file
            out.write(frame_data)

            n_processed_frames += 1

        # Release everything when done
        out.release()
        color_stream.stop()
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# Main function
def main():
    # Initialize OpenNI
    openni2.initialize("/home/tokamak/Documents/OpenNI-Linux-x64-2.2/Redist")

    # Get a list of all directories in the "Gestures" folder
    root_dir = "/home/tokamak/Desktop/Libras/Gestos"  # Replace with the path to your "Gestures" folder
    target_dir = "/home/tokamak/Desktop/Libras/Videos" 
    dir_list = [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]

    print(dir_list)

    for dir_name in dir_list:
        # Create a new directory for the videos
        new_dir_path = os.path.join(target_dir, dir_name.replace("C", "V"))  # Replace with your desired path for "Videos"

        # Check if the directory already exists
        if os.path.exists(new_dir_path):
            print(f"Directory {new_dir_path} already exists. Skipping...")
            continue

        os.makedirs(new_dir_path, exist_ok=True)

        # Get a list of all ONI files in the directory
        dir_path = os.path.join(root_dir, dir_name)
        file_list = [(os.path.join(dir_path, f), new_dir_path, f) for f in os.listdir(dir_path) if f.endswith(".oni")]  # Add extra parameters

        # Create a pool of workers
        with Pool() as p:
            p.map(process_file, file_list)

    openni2.unload()

# Run the main function
if __name__ == "__main__":
    main()

