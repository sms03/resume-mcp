"""
Generate a logo file for the MCP agent
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import logging

logger = logging.getLogger(__name__)

def generate_logo():
    """Generate a simple logo for the MCP agent"""
    try:
        # Determine the path to the static folder
        current_dir = Path(__file__).parent.absolute()
        static_dir = current_dir / "static"
        static_dir.mkdir(exist_ok=True)
        logo_path = static_dir / "logo.png"
        
        # Check if logo already exists
        if logo_path.exists():
            logger.info("Logo already exists, skipping generation")
            return
        
        # Create a blank image with a white background
        img = Image.new('RGB', (512, 512), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw background rectangle
        draw.rectangle([(0, 0), (512, 512)], fill=(56, 97, 235))
        
        # Draw a stylized "R" for Resume
        draw.rectangle([(100, 100), (412, 412)], fill=(255, 255, 255))
        draw.rectangle([(180, 100), (230, 412)], fill=(56, 97, 235))
        draw.rectangle([(180, 100), (412, 150)], fill=(56, 97, 235))
        draw.rectangle([(180, 240), (360, 290)], fill=(56, 97, 235))
        draw.polygon([(340, 290), (412, 290), (412, 412), (360, 412)], fill=(56, 97, 235))
        
        # Save the image
        img.save(logo_path)
        logger.info(f"Logo generated and saved to {logo_path}")
    except Exception as e:
        logger.error(f"Error generating logo: {str(e)}")


if __name__ == "__main__":
    generate_logo()
