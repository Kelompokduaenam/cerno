from fastapi import HTTPException


def problem(status: int, title: str, detail: str) -> HTTPException:
    return HTTPException(status_code=status, detail={"title": title, "detail": detail})
