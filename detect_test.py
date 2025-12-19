
from PIL import Image
import numpy as np

def detect_grid(image_path):
    img = Image.open(image_path).convert("RGBA")
    arr = np.array(img)
    
    # Analyze Alpha channel (or non-background color)
    # If the user sheet has a background color (gray), we need to detect changes.
    # The user's image `uploaded_image_...` had a gray background with grid lines.
    # Let's assume standard transparency or specific background color.
    
    # For the specific user image, it had a grid.
    # Let's try to detect the grid lines (which are uniform).
    
    # Simple algorithm: Look for empty/uniform rows and columns.
    width, height = img.size
    
    # Check simple alpha first
    alpha = arr[:, :, 3]
    
    # If alpha is fully opaque (no transparency), we might need color detection.
    # Let's check if there are transparent gaps.
    
    # Calculate row sums (if row is empty, sum is 0)
    # But the user's image likely has background.
    
    print(f"Image mode: {img.mode}")
    print(f"Corner pixel: {img.getpixel((0,0))}")
    
detect_grid("user_sheet.png")
