"""
Download breed images from GitHub dataset
Downloads 3 images per breed - tries multiple folder name patterns
"""

import os
import requests
import pandas as pd
import time
import re
from urllib.parse import quote

# GitHub raw content base URL
GITHUB_BASE = "https://raw.githubusercontent.com/maartenvandenbroeck/Dog-Breeds-Dataset/master"

# Create images directory
IMAGES_DIR = "static/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Load breed data
df = pd.read_csv('data/breed_traits.csv')
breeds = df['Breed'].tolist()

def generate_github_patterns(breed_name):
    """Generate multiple possible GitHub folder names for a breed"""
    patterns = []
    
    # Pattern 1: Remove parentheses and swap: "Retrievers (Labrador)" -> "labrador retriever dog"
    if '(' in breed_name:
        match = re.match(r'(.+?)\s*\((.+?)\)', breed_name)
        if match:
            swapped = f"{match.group(2)} {match.group(1)}".lower().strip()
            # Remove plural s
            if swapped.endswith('ies'):
                swapped = swapped[:-3] + 'y'
            elif swapped.endswith('s') and not swapped.endswith('ss'):
                swapped = swapped[:-1]
            patterns.append(f"{swapped} dog")
    
    # Pattern 2: Direct conversion: "French Bulldogs" -> "french bulldog" (no dog suffix)
    simple = breed_name.lower().strip()
    if simple.endswith('ies'):
        simple = simple[:-3] + 'y'
    elif simple.endswith('s') and not simple.endswith('ss'):
        simple = simple[:-1]
    patterns.append(simple)  # Without "dog"
    patterns.append(f"{simple} dog")  # With "dog"
    
    # Pattern 3: Keep as-is with dog: "Shih Tzu" -> "shih tzu dog"
    patterns.append(f"{breed_name.lower()} dog")
    
    return list(dict.fromkeys(patterns))  # Remove duplicates while preserving order

def normalize_breed_for_folder(breed_name):
    """Convert breed name for local folder storage"""
    return breed_name.replace(' ', '_').replace("'", "").replace("-", "_").replace("(", "").replace(")", "")

print(f"📥 Downloading images for {len(breeds)} breeds...")
print(f"Will try multiple folder patterns for each breed\n")

success_count = 0
failed_breeds = []

for i, breed in enumerate(breeds, 1):
    # Generate possible GitHub folder names
    github_patterns = generate_github_patterns(breed)
    
    # Get local folder name
    local_folder = normalize_breed_for_folder(breed)
    
    # Create breed directory
    breed_dir = os.path.join(IMAGES_DIR, local_folder)
    os.makedirs(breed_dir, exist_ok=True)
    
    print(f"[{i}/{len(breeds)}] {breed}...", end=" ", flush=True)
    
    downloaded = 0
    found_pattern = None
    
    # Try each pattern
    for pattern in github_patterns:
        if downloaded >= 3:
            break
            
        # Try downloading images with this pattern
        for img_num in range(1, 11):  # Try first 10 images
            if downloaded >= 3:
                break
            
            img_filename = f"Image_{img_num}.jpg"
            github_url = f"{GITHUB_BASE}/{quote(pattern)}/{img_filename}"
            
            try:
                response = requests.get(github_url, timeout=10, stream=True)
                if response.status_code == 200:
                    if not found_pattern:
                        found_pattern = pattern
                    
                    # Save image
                    img_path = os.path.join(breed_dir, f"photo_{downloaded + 1}.jpg")
                    with open(img_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded += 1
            except Exception:
                continue
        
        if downloaded > 0:
            break  # Found working pattern, stop trying others
    
    if downloaded > 0:
        print(f"✅ {downloaded} images ({found_pattern})")
        success_count += 1
    else:
        print(f"❌ No images found")
        failed_breeds.append((breed, github_patterns[0]))
    
    # Small delay
    time.sleep(0.15)

print(f"\n{'='*60}")
print(f"✨ Download Complete!")
print(f"{'='*60}")
print(f"Successfully downloaded images for {success_count}/{len(breeds)} breeds")

if failed_breeds:
    print(f"\n⚠️  Failed to download images for {len(failed_breeds)} breeds:")
    for breed, tried in failed_breeds[:15]:
        print(f"   - {breed}")
    if len(failed_breeds) > 15:
        print(f"   ... and {len(failed_breeds) - 15} more")
    print("\nThese breeds will use placeholder images.")

print(f"\n📁 Images saved to: {os.path.abspath(IMAGES_DIR)}")
print(f"\n🎉 Your app will now show real breed images!")
