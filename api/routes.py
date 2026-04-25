from fastapi import APIRouter, BackgroundTasks
import traceback

from api.schemas import (
    RunRequest,
    RunResponse,
    JobStatusResponse,
    RefineRequest,
    RefineResponse,
    JobStatus,
)

from utils.job_manager import job_manager
from api.errors import (
    InvalidRepoURLError,
    InvalidInstructionError,
    JobAlreadyRunningError,
    JobNotFoundError,
)

from agent.executor import run_agent
from tools.pr_tool import create_pull_request


router = APIRouter(tags=["Agent"])


# -------------------------------
# Background worker
# -------------------------------
def process_job(job_id: str):
    import traceback

    try:
        print("\n🚀 JOB STARTED:", job_id)

        job = job_manager.get(job_id)
        print("📦 Job loaded successfully")

        job_manager.update(job_id, status=JobStatus.running)

        print("🧪 TEST 1: BEFORE AGENT")

        # ❌ COMMENT OUT EVERYTHING BELOW FOR NOW
        # result = run_agent(
        #     repo_url=job.repo_url,
        #     instruction=job.instruction,
        # )

        print("🧪 TEST 2: AFTER AGENT (skipped)")

        # fake result
        summary = "Test summary"

        print("🧪 TEST 3: BEFORE PR")

        # ❌ COMMENT OUT PR TOO
        # pr = create_pull_request(
        #     token="dummy_token",
        #     repo_full_name="owner/repo",
        #     title="Test PR",
        #     body=summary,
        #     head_branch="auto-update-branch",
        # )

        pr_url = "https://github.com/fake/repo/pull/1"

        print("🧪 TEST 4: BEFORE UPDATE")

        job_manager.update(
            job_id,
            status=JobStatus.completed,
            pr_url=pr_url,
            diff_summary=summary,
        )

        print("🎉 JOB COMPLETED (TEST MODE)")

    except Exception as e:
        print("\n❌ ERROR:")
        traceback.print_exc()

        job_manager.update(
            job_id,
            status=JobStatus.failed,
            error_message=str(e),
        )

# -------------------------------
# POST /run
# -------------------------------


@router.post("/run", response_model=RunResponse)
async def run(request: RunRequest, background_tasks: BackgroundTasks):

    if not request.repo_url.startswith("https://github.com/"):
        raise InvalidRepoURLError("Invalid GitHub URL")

    if not request.instruction.strip():
        raise InvalidInstructionError("Instruction cannot be empty")

    job_id = job_manager.create_job(
        repo_url=request.repo_url,
        instruction=request.instruction,
    )

    background_tasks.add_task(process_job, job_id)

    return RunResponse(
        job_id=job_id,
        status=JobStatus.queued,
    )


# -------------------------------
# GET /status/{job_id}
# -------------------------------
@router.get("/status/{job_id}", response_model=JobStatusResponse)
async def status(job_id: str):

    try:
        job = job_manager.get(job_id)
    except Exception:
        raise JobNotFoundError("Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        pr_url=job.pr_url,
        diff_summary=job.diff_summary,
        error_message=job.error_message,
    )


# -------------------------------
# POST /refine
# -------------------------------
@router.post("/refine", response_model=RefineResponse)
async def refine(request: RefineRequest, background_tasks: BackgroundTasks):

    try:
        job = job_manager.get(request.job_id)
    except Exception:
        raise JobNotFoundError("Job not found")

    if job.status == JobStatus.running:
        raise JobAlreadyRunningError("Job still running")

    if not request.instruction.strip():
        raise InvalidInstructionError("Instruction cannot be empty")

    job.instruction += f"\nRefinement: {request.instruction}"

    job_manager.update(request.job_id, status=JobStatus.queued)

    background_tasks.add_task(process_job, request.job_id)

    return RefineResponse(
        job_id=request.job_id,
        status=JobStatus.queued,
        message="Refinement started",
    )
