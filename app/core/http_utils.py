from fastapi import HTTPException, status


def require_found(obj, detail: str = "Not found"):
    """Raise 404 if obj is None, otherwise return it."""
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
    return obj
