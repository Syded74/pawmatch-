"""
Configure CORS for Azure Blob Storage
This allows the browser to load images into Canvas for social sharing
"""
from azure.storage.blob import BlobServiceClient
import os

# Azure Storage connection
connection_string = input("Paste your Azure Storage connection string: ")

try:
    # Create the BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get the service properties
    service_properties = blob_service_client.get_service_properties()
    
    # Configure CORS
    cors_rule = {
        'allowed_origins': ['*'],  # Allow all origins (or specify your domain)
        'allowed_methods': ['GET', 'HEAD'],
        'allowed_headers': ['*'],
        'exposed_headers': ['*'],
        'max_age_in_seconds': 3600
    }
    
    service_properties['cors'] = [cors_rule]
    
    # Set the service properties
    blob_service_client.set_service_properties(cors=service_properties['cors'])
    
    print("✅ CORS configured successfully!")
    print("   - Allowed origins: * (all)")
    print("   - Allowed methods: GET, HEAD")
    print("   - Images can now be loaded into Canvas for social sharing")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nAlternative: Configure CORS via Azure Portal:")
    print("1. Go to your storage account: pawmatchstorage2024")
    print("2. Click 'Resource sharing (CORS)' under Settings")
    print("3. In Blob service tab, add:")
    print("   - Allowed origins: *")
    print("   - Allowed methods: GET, HEAD")
    print("   - Allowed headers: *")
    print("   - Exposed headers: *")
    print("   - Max age: 3600")
    print("4. Click Save")
