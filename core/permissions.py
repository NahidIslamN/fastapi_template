from fastapi import Request, HTTPException, status

def IsAuthenticated(request: Request):
    if not request.state.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

def IsAdmin(request: Request):
    user = request.state.user
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin only Can access the method",
        )
