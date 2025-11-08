# How to Download Breed Images

## Option 1: Clone the Entire Repository (Recommended)
```bash
cd /Users/m2/Downloads/pawmatcher/static
git clone https://github.com/maartenvandenbroeck/Dog-Breeds-Dataset.git temp_images
mv temp_images/* images/
rm -rf temp_images
```

## Option 2: Download ZIP
1. Go to: https://github.com/maartenvandenbroeck/Dog-Breeds-Dataset
2. Click "Code" → "Download ZIP"
3. Extract all folders to: `/Users/m2/Downloads/pawmatcher/static/images/`

## Expected Structure
```
static/images/
├── labrador retriever dog/
│   ├── Image_1.jpg
│   ├── Image_2.jpg
│   └── Image_3.jpg
├── french bulldog/
│   ├── Image_1.jpg
│   └── ...
└── ...
```

## After Download
The app will automatically:
- Check local images first
- Use placeholder images if breed not found
- No API key needed!

Run: `python app.py` and images will appear automatically.
