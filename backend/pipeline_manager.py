import asyncio
import time
import traceback
import logging
from typing import Dict, List, Any
from fastapi import WebSocket
from steps import ALL_STEPS

logger = logging.getLogger("pipeline_manager")

class JobState:
    def __init__(self, job_id: str, apk_path: str):
        self.job_id = job_id
        self.apk_path = apk_path
        self.status = "queued"
        self.current_step = 0
        self.total_steps = len(ALL_STEPS)
        self.logs = []
        self.quality_score = 0.0
        self.repair_attempts = []
        self.build_status = "pending"
        self.testing_status = "pending"
        self.metadata = {}
        self.zip_filename = None
        self.steps = [
            {"index": i + 1, "name": step.name, "description": step.description, "status": "pending"}
            for i, step in enumerate(ALL_STEPS)
        ]

    def add_log(self, message: str) -> dict:
        log_entry = {
            "timestamp": time.time(),
            "message": message
        }
        self.logs.append(log_entry)
        return log_entry

    def to_dict(self) -> dict:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "logs": self.logs,
            "quality_score": self.quality_score,
            "repair_attempts": self.repair_attempts,
            "build_status": self.build_status,
            "testing_status": self.testing_status,
            "metadata": self.metadata,
            "zip_filename": self.zip_filename,
            "steps": self.steps
        }


class PipelineManager:
    def __init__(self):
        self.jobs: Dict[str, JobState] = {}
        self.connections: Dict[str, List[WebSocket]] = {}

    def get_job(self, job_id: str) -> JobState:
        return self.jobs.get(job_id)

    async def register_connection(self, job_id: str, websocket: WebSocket):
        if job_id not in self.connections:
            self.connections[job_id] = []
        self.connections[job_id].append(websocket)
        
        # Immediately send current state
        job = self.get_job(job_id)
        if job:
            await websocket.send_json({"type": "state", "data": job.to_dict()})

    def unregister_connection(self, job_id: str, websocket: WebSocket):
        if job_id in self.connections:
            if websocket in self.connections[job_id]:
                self.connections[job_id].remove(websocket)

    async def broadcast_state(self, job_id: str):
        job = self.get_job(job_id)
        if not job:
            return
        
        state_dict = job.to_dict()
        payload = {"type": "state", "data": state_dict}
        
        websockets = self.connections.get(job_id, [])
        if websockets:
            dead_sockets = []
            for ws in websockets:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ds in dead_sockets:
                websockets.remove(ds)

    async def broadcast_log(self, job_id: str, log_entry: dict):
        payload = {"type": "log", "data": log_entry}
        websockets = self.connections.get(job_id, [])
        if websockets:
            dead_sockets = []
            for ws in websockets:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead_sockets.append(ws)
            for ds in dead_sockets:
                websockets.remove(ds)

    def start_job(self, job_id: str, apk_path: str):
        job = JobState(job_id, apk_path)
        self.jobs[job_id] = job
        
        # Spawn background execution task
        asyncio.create_task(self._execute_pipeline(job_id))
        return job

    async def _execute_pipeline(self, job_id: str):
        job = self.get_job(job_id)
        if not job:
            return

        job.status = "running"
        job.add_log("Initializing APK-to-iOS migration background worker...")
        await self.broadcast_state(job_id)

        context = {
            "job_id": job_id,
            "apk_path": job.apk_path,
            "build_success": False,
            "global_quality_score": 0.0,
            "repair_attempts": [],
            "repair_loop_completed": False
        }

        try:
            for idx, step in enumerate(ALL_STEPS):
                step_idx = idx + 1
                job.current_step = step_idx
                job.steps[idx]["status"] = "running"
                await self.broadcast_state(job_id)

                def make_log_fn(index: int):
                    def log_fn(message: str):
                        logger.info(message)
                        entry = job.add_log(message)
                        # We use run_coroutine_threadsafe if called in thread, but since we are in async, 
                        # we can create task or run inline. We will run it async below.
                        asyncio.create_task(self.broadcast_log(job_id, entry))
                    return log_fn

                log_fn = make_log_fn(step_idx)
                log_fn(f"--- Starting Step {step_idx}: {step.name} ---")

                try:
                    # Run the step
                    result = await step.execute(context, log_fn)
                    
                    job.steps[idx]["status"] = "completed"
                    log_fn(f"--- Completed Step {step_idx}: {step.name} successfully. ---")
                    
                    # Update parameters from context dynamically
                    if "metadata" in context:
                        job.metadata = context["metadata"]
                    if "global_quality_score" in context:
                        job.quality_score = context["global_quality_score"]
                    if "repair_attempts" in context:
                        job.repair_attempts = context["repair_attempts"]
                    if "zip_filename" in context:
                        job.zip_filename = context["zip_filename"]
                        
                    # Build and testing status updates
                    if step_idx >= 8:
                        job.build_status = "success" if context.get("build_success") else "failed"
                    if step_idx >= 9:
                        test_results = context.get("test_results", {})
                        if test_results:
                            job.testing_status = "passed" if test_results.get("failed", 0) == 0 else "failed"
                    
                    await self.broadcast_state(job_id)
                except Exception as step_err:
                    job.steps[idx]["status"] = "failed"
                    log_fn(f"[ERROR] Step {step_idx} failed: {str(step_err)}")
                    log_fn(traceback.format_exc())
                    job.status = "failed"
                    job.build_status = "failed"
                    await self.broadcast_state(job_id)
                    return

            job.status = "completed"
            job.add_log("Migration Pipeline finished successfully! All deliverables packaged.")
            await self.broadcast_state(job_id)

        except Exception as e:
            job.status = "failed"
            job.add_log(f"Global pipeline failure: {str(e)}")
            job.add_log(traceback.format_exc())
            await self.broadcast_state(job_id)
