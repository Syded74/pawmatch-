"""
Test Azure Blob Storage image URLs
Verifies that breed images are accessible from Azure Storage
"""
import os
import requests
from urllib.parse import quote
from breed_mapping import BREED_FOLDER_MAP

# Set Azure environment variables
AZURE_STORAGE_ACCOUNT = "pawmatchstorage2024"
AZURE_STORAGE_CONTAINER = "dog-breeds"

def test_azure_images(num_tests=10):
    """Test random breed images from Azure Blob Storage"""
    print(f"🧪 Testing Azure Blob Storage Images\n")
    print(f"Storage Account: {AZURE_STORAGE_ACCOUNT}")
    print(f"Container: {AZURE_STORAGE_CONTAINER}\n")
    print("=" * 70)
    
    # Test a few different breeds (using CSV format)
    test_breeds = [
        "Retrievers (Golden)",
        "German Shepherd Dogs",
        "Retrievers (Labrador)",
        "Beagles",
        "Bulldogs",
        "French Bulldogs",
        "Poodles",
        "Rottweilers",
        "Pointers (German Shorthaired)",
        "Yorkshire Terriers"
    ]
    
    success_count = 0
    fail_count = 0
    
    for breed in test_breeds[:num_tests]:
        folder_name = BREED_FOLDER_MAP.get(breed)
        
        if not folder_name:
            print(f"❌ {breed}: Not mapped")
            fail_count += 1
            continue
        
        # Test Image_1.jpg for each breed (URL-encode folder name)
        encoded_folder = quote(folder_name)
        image_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{encoded_folder}/Image_1.jpg"
        
        try:
            response = requests.head(image_url, timeout=5)
            if response.status_code == 200:
                print(f"✅ {breed}: Image accessible")
                print(f"   URL: {image_url}")
                success_count += 1
            else:
                print(f"❌ {breed}: HTTP {response.status_code}")
                print(f"   URL: {image_url}")
                fail_count += 1
        except Exception as e:
            print(f"❌ {breed}: Connection error - {str(e)}")
            fail_count += 1
        
        print()
    
    print("=" * 70)
    print(f"\n📊 Results:")
    print(f"   ✅ Success: {success_count}/{num_tests}")
    print(f"   ❌ Failed: {fail_count}/{num_tests}")
    print(f"   📈 Success Rate: {(success_count/num_tests)*100:.1f}%")
    
    if success_count == num_tests:
        print(f"\n🎉 All images are accessible from Azure Blob Storage!")
        print(f"✅ Your app is ready to deploy!")
    elif success_count > 0:
        print(f"\n⚠️  Some images are accessible, but check the failed ones.")
    else:
        print(f"\n❌ No images accessible. Check your Azure Storage configuration.")

if __name__ == "__main__":
    test_azure_images()
