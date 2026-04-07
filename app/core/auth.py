"""
FastAPI authentication dependency using Supabase-issued JWTs.

How it works
────────────
1. The frontend (Supabase JS client) signs the user in and receives a JWT
   from Supabase Auth.  Supabase may sign tokens with HS256 (symmetric, using
   the project JWT secret) or with an asymmetric algorithm such as ES256/RS256
   (using a key-pair whose public keys are published at the JWKS endpoint).
2. Every protected API request includes the header:
       Authorization: Bearer <jwt>
3. get_current_user() inspects the token header to determine the algorithm,
   then verifies accordingly:
     • HS256 → verified with SUPABASE_JWT_SECRET
     • ES256 / RS256 (or any other alg) → verified via the Supabase JWKS
       endpoint: {SUPABASE_URL}/auth/v1/.well-known/jwks.json
4. The decoded payload's "sub" claim is the user's UUID (matches auth.users.id
   in Supabase). This UUID is used as the user_id FK in tasks, notes, tags, and
   calendar_settings.

Environment variables required
───────────────────────────────
SUPABASE_JWT_SECRET  — found in Supabase dashboard → Project Settings → API
                       → JWT Settings → JWT Secret
SUPABASE_URL         — your project URL (e.g. https://xyz.supabase.co)
"""

import os
from dataclasses import dataclass
from functools import lru_cache

import jwt  # PyJWT
from jwt import PyJWKClient
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class UserInfo:
    """Minimal user identity extracted from the verified JWT."""
    id: str        # Supabase auth UUID (e.g. "a1b2c3d4-...")
    email: str     # from the JWT "email" claim
    provider: str  # primary auth provider: "email" | "google" | etc.
                   # sourced from app_metadata.provider in the JWT payload


def _get_jwt_secret() -> str:
    secret = os.getenv("SUPABASE_JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "SUPABASE_JWT_SECRET is not set. "
            "Find it at: Supabase dashboard → Project Settings → API → JWT Secret"
        )
    return secret


@lru_cache(maxsize=1)
def _get_jwks_client() -> PyJWKClient:
    """Return a cached JWKS client for the Supabase project."""
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    if not supabase_url:
        raise RuntimeError("SUPABASE_URL is not set.")
    jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url, cache_keys=True)


def _decode_token(token: str) -> dict:
    """
    Decode and verify a Supabase JWT regardless of the signing algorithm.

    • HS256  → symmetric verify with SUPABASE_JWT_SECRET
    • others → asymmetric verify via the Supabase JWKS endpoint
    """
    # Peek at the header without verifying so we know the algorithm.
    unverified_header = jwt.get_unverified_header(token)
    alg = unverified_header.get("alg", "")

    decode_options = {"verify_aud": False}

    if alg == "HS256":
        return jwt.decode(
            token,
            _get_jwt_secret(),
            algorithms=["HS256"],
            options=decode_options,
        )

    # Asymmetric algorithm (ES256, RS256, …) — fetch the matching public key.
    jwks_client = _get_jwks_client()
    signing_key = jwks_client.get_signing_key_from_jwt(token)
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        options=decode_options,
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> UserInfo:
    """
    FastAPI dependency — extracts and validates the Bearer JWT.

    Usage in a router:
        @router.get("/get-tasks")
        def read_tasks(current_user: UserInfo = Depends(get_current_user), ...):
            ...
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = _decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub", "")
    email: str = payload.get("email", "")
    # app_metadata.provider is set by Supabase and is not user-editable.
    # Falls back to "email" so downstream code can safely compare strings.
    app_meta = payload.get("app_metadata") or {}
    provider: str = app_meta.get("provider", "email")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing 'sub' claim",
        )

    return UserInfo(id=user_id, email=email, provider=provider)
