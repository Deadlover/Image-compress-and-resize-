from PIL import Image

def resize_image(input_path, output_path, target_mb, quality=85, resize_factor=0.9):
    with Image.open(input_path) as img:
        # Adjust resolution and quality iteratively
        while True:
            img.save(output_path, quality=quality)
            current_size_mb = os.path.getsize(output_path) / (1024 * 1024)
            if current_size_mb <= target_mb or quality <= 10:
                break
            quality -= 5
            if current_size_mb > target_mb:
                img = img.resize((int(img.width * resize_factor), int(img.height * resize_factor)), Image.Resampling.LANCZOS)
        
        print(f"Final file size: {current_size_mb} MB with quality: {quality} and size: {img.size}")

# Example usage
import os

input_image_path = 'input.jpg'
output_image_path = 'output_image.jpg'
target_file_size_mb = 2  # Target size in MB

resize_image(input_image_path, output_image_path, target_file_size_mb)
