
import os
import argparse
from pathlib import Path
from PIL import Image

def slice_spritesheet(sheet_path: str, sprite_width: int = None, sprite_height: int = None, output_dir: str = None, num_cols: int = None, num_rows: int = None, padding: int = 0):
    """
    Slices a sprite sheet into individual images.
    
    Args:
        sheet_path: Path to the sprite sheet image.
        sprite_width: Width of a single sprite (optional if rows/cols provided).
        sprite_height: Height of a single sprite (optional if rows/cols provided).
        output_dir: Directory to save extracted sprites.
        num_cols: Number of columns in the grid.
        num_rows: Number of rows in the grid.
        padding: Pixels to shrink each cell by (to remove grid lines).
    """
    path = Path(sheet_path)
    if not path.exists():
        print(f"Error: File {sheet_path} not found.")
        return

    try:
        sheet = Image.open(path)
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    sheet_w, sheet_h = sheet.size
    

    if output_dir is None:
        output_dir = path.parent / path.stem
    else:
        output_dir = Path(output_dir)
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cols = 0
    rows = 0
    
    if sprite_width and sprite_height:
        cols = sheet_w // sprite_width
        rows = sheet_h // sprite_height
    elif num_cols and num_rows:
        cols = num_cols
        rows = num_rows
        sprite_width = sheet_w // cols
        sprite_height = sheet_h // rows
    else:
        print("Error: Must specify either --width/--height OR --cols/--rows")
        return

    
    # Validate dimensions
    if sprite_width and sprite_height and (sheet_w % sprite_width != 0 or sheet_h % sprite_height != 0):
        print(f"Warning: Sheet dimensions ({sheet_w}x{sheet_h}) are not perfectly divisible by sprite size ({sprite_width}x{sprite_height}).")

    count = 0
    print(f"Slicing {path.name} ({sheet_w}x{sheet_h}) into {cols}x{rows} grid...")
    print(f"Cell size: {sprite_width}x{sprite_height}, Padding: {padding}")
    
    for row in range(rows):
        for col in range(cols):
            # Calculate cell bounds
            left = col * sprite_width
            upper = row * sprite_height
            right = left + sprite_width
            lower = upper + sprite_height
            
            # Apply padding (shrink inwards)
            left += padding
            upper += padding
            right -= padding
            lower -= padding
            
            if right <= left or lower <= upper:
                print(f"Warning: Padding too large for cell size at {col},{row}")
                continue
            
            box = (left, upper, right, lower)
            sprite = sheet.crop(box)
            
            # Skip empty sprites (optional, simple check for transparency)
            if sprite.getbbox() is None:
                continue

            out_name = output_dir / f"{path.stem}_{count:03d}.png"
            sprite.save(out_name)
            count += 1
            
    print(f"Done! Saved {count} sprites to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Slice a sprite sheet into individual images.")
    parser.add_argument("file", help="Path to the sprite sheet image")
    parser.add_argument("--width", "-w", type=int, help="Width of a single sprite")
    parser.add_argument("--height", "-H", type=int, help="Height of a single sprite")
    parser.add_argument("--rows", "-r", type=int, help="Number of rows")
    parser.add_argument("--cols", "-c", type=int, help="Number of columns")
    parser.add_argument("--padding", "-p", type=int, default=0, help="Padding to crop from edges of each cell")
    parser.add_argument("--out", "-o", help="Output directory (optional)")
    
    args = parser.parse_args()
    
    slice_spritesheet(args.file, args.width, args.height, args.out, args.cols, args.rows, args.padding)
