import os
from pathlib import Path
from src.utils.fhir import load_bundle_from_file

def load_fhir_bundles_from_directory():
    """
    Load all FHIR bundles from the data/fhir_bundles directory.
    """
    # Get the directory containing FHIR bundles
    current_dir = Path(__file__).parent
    bundles_dir = current_dir / "src" / "data" / "fhir_bundles"
    
    print(f"Looking for FHIR bundles in: {bundles_dir}")
    
    if not bundles_dir.exists():
        print(f"Error: Directory {bundles_dir} does not exist")
        return []
    
    loaded_bundles = []
    
    # Get all JSON files in the directory
    json_files = list(bundles_dir.glob("*.json"))
    
    if not json_files:
        print("No JSON files found in the bundles directory")
        return []
    
    print(f"Found {len(json_files)} JSON files")
    
    # Load each FHIR bundle
    for json_file in json_files:
        print(f"\n--- Loading {json_file.name} ---")
        bundle = load_bundle_from_file(str(json_file))
        
        if bundle:
            loaded_bundles.append({
                'filename': json_file.name,
                'bundle': bundle,
                'path': str(json_file)
            })
            print(f"Successfully loaded bundle: {json_file.name}")
            print(f"Bundle ID: {bundle.id if bundle.id else 'No ID'}")
            print(f"Resource Type: {getattr(bundle, '__resource_type__', 'Bundle')}")
            if bundle.entry:
                print(f"Number of entries: {len(bundle.entry)}")
                # Print resource types in the bundle
                resource_types = [getattr(entry.resource, '__resource_type__', entry.resource.__class__.__name__) for entry in bundle.entry if entry.resource]
                print(f"Resource types: {set(resource_types)}")
        else:
            print(f"Failed to load bundle: {json_file.name}")
    
    return loaded_bundles

def main():
    """
    Main function to test FHIR bundle loading.
    """
    print("=== FHIR Bundle Loading Test ===")
    
    bundles = load_fhir_bundles_from_directory()
    
    print(f"\n=== Summary ===")
    print(f"Successfully loaded {len(bundles)} FHIR bundles")
    
    for bundle_info in bundles:
        print(f"\nBundle: {bundle_info['filename']}")
        bundle = bundle_info['bundle']
        if bundle.entry:
            print(f"  Entries: {len(bundle.entry)}")
            for i, entry in enumerate(bundle.entry):
                if entry.resource:
                    resource_type = getattr(entry.resource, '__resource_type__', entry.resource.__class__.__name__)
                    print(f"    [{i}] {resource_type} - ID: {entry.resource.id if entry.resource.id else 'No ID'}")

if __name__ == "__main__":
    main()
