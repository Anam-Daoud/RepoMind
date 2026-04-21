class RepoMindError(Exception):
    def __init__(self, message: str, detail: dict | None = None):
        super().__init__(message)
        self.message = message
        self.detail  = detail or {}

class ValidationError(RepoMindError):
    pass

class InvalidRepoURLError(RepoMindError):
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid or unreachable repository URL: {url}",
            detail={"url": url},
        )

class InvalidInstructionError(RepoMindError):
    def __init__(self, instruction: str):
        super().__init__(
            message="Instruction is empty or could not be parsed.",
            detail={"instruction": instruction[:200]},
        )

class JobNotFoundError(RepoMindError):
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job '{job_id}' not found.",
            detail={"job_id": job_id},
        )

class JobAlreadyRunningError(RepoMindError):
    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job '{job_id}' is already running — wait for it to complete before refining.",
            detail={"job_id": job_id},
        )

class GitHubError(RepoMindError):
    def __init__(self, operation: str, reason: str):
        super().__init__(
            message=f"GitHub operation '{operation}' failed: {reason}",
            detail={"operation": operation, "reason": reason},
        )

class LLMError(RepoMindError):
    def __init__(self, reason: str):
        super().__init__(
            message=f"LLM call failed: {reason}",
            detail={"reason": reason},
        )

class AgentExecutionError(RepoMindError):
    def __init__(self, step: str, reason: str):
        super().__init__(
            message=f"Agent crashed at step '{step}': {reason}",
            detail={"step": step, "reason": reason},
        )
