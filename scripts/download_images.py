"""
Download breed images from GitHub dataset
Downloads 3 images per breed for the PawMatch application
"""

import os
import requests
import pandas as pd
from pathlib import Path
import time
import re

# GitHub raw content base URL
GITHUB_BASE = "https://raw.githubusercontent.com/maartenvandenbroeck/Dog-Breeds-Dataset/master"

# Create images directory
IMAGES_DIR = "static/images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Load breed data to get all breed names
df = pd.read_csv('data/breed_traits.csv')
breeds = df['Breed'].tolist()

def normalize_breed_for_github(breed_name):
    """
    Convert AKC breed name to GitHub folder format
    Examples:
      "Retrievers (Labrador)" -> "labrador retriever dog"
      "French Bulldogs" -> "french bulldog"
      "German Shepherd Dogs" -> "german shepherd dog"
    """
    # Manual mappings for breeds that don't follow the pattern
    # These are the EXACT folder names from GitHub
    manual_mappings = {
        "Retrievers (Labrador)": "labrador retriever dog",
        "Retrievers (Golden)": "golden retriever dog",
        "German Shepherd Dogs": "german shepherd dog",
        "French Bulldogs": "french bulldog",  # Note: GitHub has no "dog" suffix for this one!
        "Bulldogs": "bulldog",  # Note: GitHub has no "dog" suffix for this one!
        "Pembroke Welsh Corgis": "welsh corgi (pembroke) dog",
        "Cardigan Welsh Corgis": "welsh corgi (cardigan) dog",
        "Yorkshire Terriers": "yorkshire terrier dog",
        "Cavalier King Charles Spaniels": "cavalier king charles spaniel dog",
        "Doberman Pinschers": "dobermann dog",
        "Miniature Schnauzers": "miniature schnauzer dog",
        "Great Danes": "great dane dog",
        "Siberian Huskies": "siberian husky dog",
        "Pointers (German Shorthaired)": "german short- haired pointing dog",
        "Australian Shepherds": "australian shepherd dog",
        "Retrievers (Chesapeake Bay)": "chesapeake bay retriever dog",
        "Shih Tzu": "shih tzu dog",
        "Pugs": "pug dog",
        "Chihuahuas": "chihuahua dog",
        "Border Collies": "border collie dog",
        "Bernese Mountain Dogs": "bernese mountain dog",
        "Mastiffs": "mastiff dog",
        "Newfoundlands": "newfoundland dog",
        "Rhodesian Ridgebacks": "rhodesian ridgeback dog",
        "St. Bernards": "st. bernard dog",
        "Boston Terriers": "boston terrier dog",
        "Pomeranians": "pomeranian dog",
    }
    
    # Check manual mapping first
    if breed_name in manual_mappings:
        return manual_mappings[breed_name]
    
    # Remove parentheses content and swap if needed
    if '(' in breed_name:
        # "Setters (Irish)" -> "Irish Setter"
        match = re.match(r'(.+?)\s*\((.+?)\)', breed_name)
        if match:
            breed_name = f"{match.group(2)} {match.group(1)}"
    
    # Remove plural 's' from end
    # "Huskies" -> "Husky", "Terriers" -> "Terrier", but "Swiss" stays "Swiss"
    if breed_name.endswith('ies'):
        breed_name = breed_name[:-3] + 'y'  # "Huskies" -> "Husky"
    elif breed_name.endswith('s') and not breed_name.endswith('ss'):
        breed_name = breed_name[:-1]  # "Terriers" -> "Terrier", keep "Swiss"
    
    # Convert to lowercase
    breed_name = breed_name.lower().strip()
    
    # ONLY add " dog" suffix if not already ending with it
    # (manual mappings already have it, don't double-add!)
    if not breed_name.endswith(' dog'):
        breed_name = f"{breed_name} dog"
    
    return breed_name

def normalize_breed_for_folder(breed_name):
    """
    Convert breed name for local folder storage (same as app.py uses)
    """
    return breed_name.replace(' ', '_').replace("'", "").replace("-", "_")

print(f"📥 Downloading images for {len(breeds)} breeds...")
print(f"Will download up to 3 images per breed\n")

success_count = 0
failed_breeds = []

for i, breed in enumerate(breeds, 1):
    # Get GitHub folder name (with "dog" suffix, lowercase, spaces)
    github_folder = normalize_breed_for_github(breed)
    
    # Get local folder name (underscores, no special chars)
    local_folder = normalize_breed_for_folder(breed)
    
    # Create breed directory
    breed_dir = os.path.join(IMAGES_DIR, local_folder)
    os.makedirs(breed_dir, exist_ok=True)
    
    print(f"[{i}/{len(breeds)}] {breed}...", end=" ", flush=True)
    
    downloaded = 0
    # Try to download images numbered 1-35 (repo has 35 per breed)
    for img_num in range(1, 36):
        if downloaded >= 3:
            break
        
        # GitHub repo structure: "breed dog" folder with Image_N.jpg files
        img_filename = f"Image_{img_num}.jpg"
        github_url = f"{GITHUB_BASE}/{github_folder}/{img_filename}"
        
        try:
            response = requests.get(github_url, timeout=10, stream=True)
            if response.status_code == 200:
                # Save image
                img_path = os.path.join(breed_dir, f"photo_{downloaded + 1}.jpg")
                with open(img_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded += 1
        except Exception as e:
            continue
    
    if downloaded > 0:
        print(f"✅ {downloaded} images")
        success_count += 1
    else:
        print(f"❌ No images found (tried: {github_folder})")
        failed_breeds.append((breed, github_folder))
    
    # Small delay to be nice to GitHub
    time.sleep(0.2)

print(f"\n{'='*60}")
print(f"✨ Download Complete!")
print(f"{'='*60}")
print(f"Successfully downloaded images for {success_count}/{len(breeds)} breeds")

if failed_breeds:
    print(f"\n⚠️  Failed to download images for {len(failed_breeds)} breeds:")
    for breed, github_name in failed_breeds[:10]:  # Show first 10
        print(f"   - {breed} (tried: {github_name})")
    if len(failed_breeds) > 10:
        print(f"   ... and {len(failed_breeds) - 10} more")
    print("\nThese breeds will use placeholder images.")

print(f"\n📁 Images saved to: {os.path.abspath(IMAGES_DIR)}")
print(f"\n🎉 Your app will now show real breed images!")
