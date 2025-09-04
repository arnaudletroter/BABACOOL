import os
import argparse
from PIL import Image

def images_to_gif(input_folder, prefix, output_file="output.gif", duration=100, loop=0):
    """
    Create an animated GIF from a folder of images with a given prefix.
    
    :param input_folder: Path to the folder containing the images
    :param prefix: Prefix of the image files (e.g., 'WM' for WM_0000.png)
    :param output_file: Name of the output GIF file
    :param duration: Duration of each frame in milliseconds
    :param loop: Number of loops (0 = infinite)
    """
    # Collect image files that match the prefix and valid extensions
    files = [f for f in os.listdir(input_folder) 
             if f.lower().endswith((".png", ".jpg", ".jpeg")) and f.startswith(prefix)]
    
    if not files:
        print(f"No images found with prefix '{prefix}' in {input_folder}")
        return
    
    # Sort files alphabetically (so WM_0000.png -> WM_0001.png -> ...)
    files.sort()

    # Load all frames
    frames = [Image.open(os.path.join(input_folder, f)) for f in files]

    # Save as animated GIF
    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=loop
    )
    print(f"GIF created: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create an animated GIF from a sequence of images.")
    parser.add_argument("--folder", type=str, required=True, help="Folder containing the images")
    parser.add_argument("--prefix", type=str, required=True, help="Prefix of the image files (e.g., WM)")
    parser.add_argument("--duration", type=int, default=100, help="Frame duration in milliseconds (default: 100)")
    parser.add_argument("--output", type=str, default="output.gif", help="Output GIF filename (default: output.gif)")
    
    args = parser.parse_args()
    
    images_to_gif(args.folder, args.prefix, args.output, args.duration, loop=0)
