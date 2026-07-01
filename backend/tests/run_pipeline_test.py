import time
import requests
import os

def run_test():
    url = "http://127.0.0.1:8000/api/upload"
    
    # 1. Create a dummy APK file
    apk_path = "fittrack_pro.apk"
    with open(apk_path, "wb") as f:
        f.write(b"PK\x03\x04\n\x00\x00\x00\x00\x00" + b"A" * 100) # dummy zip structure
        
    print(f"Created dummy APK file: {apk_path} ({os.path.getsize(apk_path)} bytes)")
    
    try:
        # 2. Upload the APK file
        print("Uploading APK to FastAPI server...")
        with open(apk_path, "rb") as f:
            files = {"file": (apk_path, f, "application/vnd.android.package-archive")}
            response = requests.post(url, files=files)
            
        if response.status_code != 200:
            print(f"Upload failed: {response.text}")
            return
            
        data = response.json()
        job_id = data["job_id"]
        print(f"Upload successful. Spawned job: {job_id}")
        
        # 3. Poll the job status until completion
        status = "queued"
        last_logged_len = 0
        
        while status in ["queued", "running"]:
            time.sleep(2)
            job_res = requests.get(f"http://127.0.0.1:8000/api/job/{job_id}")
            if job_res.status_code != 200:
                print(f"Failed to fetch job status: {job_res.text}")
                break
                
            job_data = job_res.json()
            status = job_data["status"]
            current_step = job_data["current_step"]
            total_steps = job_data["total_steps"]
            quality_score = job_data["quality_score"]
            build_status = job_data["build_status"]
            
            # Print new logs
            logs = job_data["logs"]
            if len(logs) > last_logged_len:
                for log in logs[last_logged_len:]:
                    print(f"[{status.upper()} - Step {current_step}/{total_steps}] {log['message']}")
                last_logged_len = len(logs)
                
        # 4. Final verification
        print("\n=== Pipeline Final Results ===")
        print(f"Status: {status}")
        print(f"Quality Score: {quality_score}%")
        print(f"Build Status: {build_status}")
        print(f"ZIP Deliverable name: {job_data.get('zip_filename')}")
        
        # Download files list
        files_res = requests.get(f"http://127.0.0.1:8000/api/job/{job_id}/files")
        if files_res.status_code == 200:
            files_data = files_res.json()
            print(f"Generated Android files: {[f['name'] for f in files_data['android']]}")
            print(f"Generated iOS files: {[f['name'] for f in files_data['ios']]}")
            
    finally:
        if os.path.exists(apk_path):
            os.remove(apk_path)

if __name__ == "__main__":
    run_test()
