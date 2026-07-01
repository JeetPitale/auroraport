import os
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict

import config
from pipeline_manager import PipelineManager

app = FastAPI(title="AI APK-to-iOS Migration Platform API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = PipelineManager()

class ErrorResponse(BaseModel):
    detail: str

@app.post("/api/upload")
async def upload_apk(file: UploadFile = File(...)):
    # Validate it's an APK file
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only APK files are supported.")
    
    # Generate job ID and file path
    job_id = str(uuid.uuid4())
    apk_filename = f"{job_id}_{file.filename}"
    save_path = config.UPLOAD_DIR / apk_filename
    
    try:
        with open(save_path, "wb") as f:
            content = await file.read()
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save APK file: {str(e)}")
        
    # Start the migration pipeline job
    job = manager.start_job(job_id, str(save_path))
    
    return {
        "job_id": job.job_id,
        "app_name": job.metadata.get("app_name", "FitLife Tracker"),
        "file_size": len(content),
        "status": "queued"
    }

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_dict()

@app.get("/api/job/{job_id}/files")
async def get_job_files(job_id: str):
    job = manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
        
    # Check if decompile path exists to read files
    decompile_base = config.DECOMPILE_DIR / job_id
    ios_base = config.IOS_PROJECT_DIR / job_id
    
    files = {
        "android": [],
        "ios": []
    }
    
    # Read Android sources
    if decompile_base.exists():
        for root, dirs, filenames in os.walk(decompile_base):
            for name in filenames:
                if name.endswith((".kt", ".java", ".xml")):
                    full_p = os.path.join(root, name)
                    rel_p = os.path.relpath(full_p, decompile_base)
                    try:
                        with open(full_p, "r") as f:
                            content = f.read()
                    except Exception:
                        content = ""
                    files["android"].append({
                        "name": name,
                        "path": rel_p,
                        "content": content
                    })
                    
    # Read iOS sources
    if ios_base.exists():
        for root, dirs, filenames in os.walk(ios_base):
            for name in filenames:
                if name.endswith((".swift", "Package.swift")):
                    full_p = os.path.join(root, name)
                    rel_p = os.path.relpath(full_p, ios_base)
                    try:
                        with open(full_p, "r") as f:
                            content = f.read()
                    except Exception:
                        content = ""
                    files["ios"].append({
                        "name": name,
                        "path": rel_p,
                        "content": content
                    })
                    
    return files

@app.get("/api/download/{filename}")
async def download_deliverable(filename: str):
    file_path = config.DELIVERABLES_DIR / filename
    if not file_path.exists():
         raise HTTPException(status_code=404, detail="Deliverable not found.")
    return FileResponse(path=file_path, filename=filename, media_type="application/zip")

@app.websocket("/api/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.accept()
    job = manager.get_job(job_id)
    if not job:
        await websocket.send_json({"type": "error", "message": "Job not found"})
        await websocket.close()
        return
        
    await manager.register_connection(job_id, websocket)
    try:
        while True:
            # We just wait for incoming client pings or disconnects
            data = await websocket.receive_text()
            # client sends ping, we send state
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.unregister_connection(job_id, websocket)
    except Exception:
        manager.unregister_connection(job_id, websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True)
