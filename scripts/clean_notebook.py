import json

# Load the notebook
with open('notebook.ipynb', 'r') as f:
    nb = json.load(f)

# Cell IDs to remove (non-essential cells)
cells_to_remove = [
    '#VSC-a1d6c79e',  # Old API key setup
    '#VSC-37db0545',  # Deployment test
    '#VSC-14107555',  # Deployment error instructions
    '#VSC-efd80644',  # Old Gemini test
    '#VSC-42523c01',  # Gemini notes
    '#VSC-2e90c304',  # Old chatbot test
    '#VSC-5513bc9b',  # Local LLM info
    '#VSC-595aba0a',  # Model test function
    '#VSC-cd05e0cb',  # Local LLM setup
    '#VSC-f8f54d1c',  # Local LLM test
]

print(f"Original cell count: {len(nb['cells'])}")

# Filter out cells
original_count = len(nb['cells'])
nb['cells'] = [cell for cell in nb['cells'] if cell.get('id') not in cells_to_remove]
removed_count = original_count - len(nb['cells'])

print(f"Removed {removed_count} cells")
print(f"New cell count: {len(nb['cells'])}")

# Save cleaned notebook
with open('notebook.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("\n✅ Notebook cleaned successfully!")
