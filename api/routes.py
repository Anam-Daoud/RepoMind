from fastapi import APIRouter
from api.schemas import RunRequest, RunResponse, RefineRequest, RefineResponse, JobStatusResponse, JobStatus
from core.job_manager import job_manager
from core.exceptions import InvalidRepoURLError, InvalidInstructionError, JobAlreadyRunningError

# ── Router ────────────────────────────────────────────────────────────────────
# Implementation: Anam Daud
# This file is scaffolded by Ali. Anam will wire in the agent + GitHub logic.

router = APIRouter(tags=["Agent"])


@router.post("/run", response_model=RunResponse)
async def run(request: RunRequest):
    """
    Kick off a new agent job.
    - Accepts a repo URL and a plain-English instruction
    - Returns a job_id immediately so the client can start polling /status
    """
    if not request.repo_url.startswith("https://github.com/"):
        raise InvalidRepoURLError(request.repo_url)
    if not request.instruction.strip():
        raise InvalidInstructionError(request.instruction)

    job_id = job_manager.create_job(
        repo_url=request.repo_url,
        instruction=request.instruction,
    )
    return RunResponse(job_id=job_id, status=JobStatus.queued)


@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def status(job_id: str):
    """
    Poll the status of a running job.
    - Returns current status, PR URL once done, or error message if failed
    """
    record = job_manager.get(job_id)
    return JobStatusResponse(
        job_id=record.job_id,
        status=record.status,
        pr_url=record.pr_url,
        diff_summary=record.diff_summary,
        message=record.error_message,
    )


@router.post("/refine", response_model=RefineResponse)
async def refine(request: RefineRequest):
    """
    Send a follow-up instruction on an existing job.
    - Lets the user iterate on the same PR without losing session memory
    """
    record = job_manager.get(request.job_id)
    if record.status == JobStatus.running:
        raise JobAlreadyRunningError(request.job_id)
    return RefineResponse(
        job_id=request.job_id,
        status=record.status,
        message="Refine endpoint ready — agent wiring coming soon.",
    )
