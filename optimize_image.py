from PIL import Image
import os

# Define paths
input_path = 'static/images/Resume-AI.png'
output_path = 'static/images/Resume-AI-optimized.png'

# Open the image
img = Image.open(input_path)

# Resize if needed (keeping aspect ratio)
max_size = (800, 800)
img.thumbnail(max_size, Image.LANCZOS)

# Save with compression
img.save(output_path, 'PNG', optimize=True, quality=85)

print(f"Original image size: {os.path.getsize(input_path) / 1024:.2f} KB")
print(f"Optimized image size: {os.path.getsize(output_path) / 1024:.2f} KB")