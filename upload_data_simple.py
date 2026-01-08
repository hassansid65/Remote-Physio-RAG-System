import json
import requests
import os

# API endpoint for data upload
BASE_URL = "http://localhost:8002"

def upload_text_data(content, data_type, category):
    """Upload text data directly using the text endpoint"""
    try:
        response = requests.post(
            f"{BASE_URL}/data/upload/text",
            data={
                "content": content,
                "data_type": data_type,
                "category": category
            }
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"{response.status_code} - {response.text}"
            
    except Exception as e:
        return False, str(e)

def process_json_file(file_path, data_type):
    """Process a JSON file and upload each item"""
    print(f"Processing {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        success_count = 0
        total_count = 0
        
        if isinstance(data, list):
            for i, item in enumerate(data):
                total_count += 1
                content = item.get("Processed Summary", str(item))
                source = item.get("Full Path", f"item_{i}")
                category = f"{data_type}_{os.path.basename(file_path)}"
                
                # Add source information to content
                full_content = f"Source: {source}\n\n{content}"
                
                success, result = upload_text_data(full_content, data_type, category)
                if success:
                    success_count += 1
                    print(f"  ✅ Uploaded item {i+1}/{len(data)}")
                else:
                    print(f"  ❌ Failed to upload item {i+1}: {result}")
        else:
            total_count = 1
            content = data.get("Processed Summary", str(data))
            source = data.get("Full Path", "single_item")
            category = f"{data_type}_{os.path.basename(file_path)}"
            
            full_content = f"Source: {source}\n\n{content}"
            
            success, result = upload_text_data(full_content, data_type, category)
            if success:
                success_count = 1
                print(f"  ✅ Uploaded single item")
            else:
                print(f"  ❌ Failed to upload: {result}")
        
        print(f"  📊 Results: {success_count}/{total_count} items uploaded successfully")
        return success_count, total_count
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return 0, 0

def main():
    """Main function to upload all data"""
    print("🚀 Starting data upload to Remote Physio API...")
    print("=" * 60)
    
    total_success = 0
    total_items = 0
    
    # Upload assessment data
    assessment_files = [
        "data/assessments/assessment__info (2).json",
        "data/assessments/back_pain_assessment.json"
    ]
    
    print("\n📋 Uploading Assessment Data:")
    for file_path in assessment_files:
        if os.path.exists(file_path):
            success, total = process_json_file(file_path, "assessment")
            total_success += success
            total_items += total
        else:
            print(f"⚠️  File not found: {file_path}")
    
    # Upload exercise data
    exercise_files = [
        "data/exercises/exercise_info (2).json"
    ]
    
    print("\n🏃 Uploading Exercise Data:")
    for file_path in exercise_files:
        if os.path.exists(file_path):
            success, total = process_json_file(file_path, "exercise")
            total_success += success
            total_items += total
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print("=" * 60)
    print(f"🎯 Upload Complete! {total_success}/{total_items} items uploaded successfully.")
    
    if total_success > 0:
        print("\n🎉 Your physiotherapy data is now available in the RAG system!")
        print("You can now test the chatbot with questions like:")
        print("  • 'What assessments are available for back pain?'")
        print("  • 'Show me exercises for shoulder strengthening'")
        print("  • 'How do I perform a gait analysis?'")
        print("  • 'What is the Berg Balance Test?'")

if __name__ == "__main__":
    main()
