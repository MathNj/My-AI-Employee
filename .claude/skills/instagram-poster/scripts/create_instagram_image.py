import sys
sys.stdout.reconfigure(encoding='utf-8')

from PIL import Image, ImageDraw, ImageFont
import os

# Create image
width = 1080
height = 1080
img = Image.new('RGB', (width, height), color='#0a0e27')  # Dark cyberpunk blue

draw = ImageDraw.Draw(img)

# Try to load fonts
try:
    title_font = ImageFont.truetype('arial.ttf', 70)
    text_font = ImageFont.truetype('arial.ttf', 35)
    small_font = ImageFont.truetype('arial.ttf', 28)
except:
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Draw title
title = "I Built an AI Employee"
draw.text((540, 120), title, fill='#00d4ff', font=title_font, anchor='mm')

subtitle = "and It Changed Everything"
draw.text((540, 200), subtitle, fill='#ffffff', font=text_font, anchor='mm')

# Draw horizontal line
draw.line([(100, 270), (980, 270)], fill='#00ff88', width=3)

# Key features
y = 320
features = [
    "24 Specialized Skills",
    "6 Intelligent Watchers",
    "Zero-Cost ERP (Odoo)",
    "Live PM2 Dashboard",
    "Ralph Loop Autonomous",
    "Saved 20+ hrs/week"
]

for feature in features:
    # Draw bullet point
    draw.ellipse([(130, y-10), (150, y+10)], fill='#00ff88')
    draw.text((540, y), feature, fill='#ffffff', font=text_font, anchor='mm')
    y += 75

# Bottom tagline
draw.text((540, 920), "Not replacing humans", fill='#ff00ff', font=small_font, anchor='mm')
draw.text((540, 960), "Building AI teammates", fill='#ff00ff', font=small_font, anchor='mm')

# Save
output_path = 'instagram_ai_employee.png'
img.save(output_path)
print(f"Created: {output_path}")
print(f"Size: {width}x{height}")
