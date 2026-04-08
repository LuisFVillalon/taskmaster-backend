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
    """Return a cached JWKS client for the Supabase project.

    URL resolution order:
      1. SUPABASE_JWKS_URL env var  — explicit override (set this if the default
                                      path doesn't work for your Supabase tier)
      2. {SUPABASE_URL}/auth/v1/.well-known/jwks.json  — standard OpenID Connect
                                                          discovery path
    """
    # Allow explicit override in case Supabase changes the well-known path.
    jwks_url = os.getenv("SUPABASE_JWKS_URL", "").strip()
    if not jwks_url:
        supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
        if not supabase_url:
            raise RuntimeError(
                "SUPABASE_URL is not set. "
                "Add it via: fly secrets set SUPABASE_URL=https://<project>.supabase.co"
            )
        jwks_url = f"{supabase_url}/auth/v1/.well-known/jwks.json"

    import logging
    logging.getLogger(__name__).info("JWKS endpoint: %s", jwks_url)
    return PyJWKClient(jwks_url, cache_keys=True)


def _decode_token(token: str) -> dict:
    """
    Decode and verify a Supabase JWT regardless of the signing algorithm.

    • HS256  → symmetric verify with SUPABASE_JWT_SECRET
    • others → asymmetric verify via the Supabase JWKS endpoint

    All non-JWT errors (network failures, missing env vars, unparseable JWKS
    responses) are converted to jwt.InvalidTokenError so callers only need to
    handle one exception hierarchy.
    """
    # Peek at the header without verifying so we know the algorithm.
    unverified_header = jwt.get_unverified_header(token)
    alg = unverified_header.get("alg", "")

    decode_options = {"verify_aud": False}

    if alg == "HS256":
        secret = os.getenv("SUPABASE_JWT_SECRET", "")
        if not secret:
            raise jwt.InvalidTokenError(
                "SUPABASE_JWT_SECRET is not configured on this server. "
                "Add it via: fly secrets set SUPABASE_JWT_SECRET=<value>"
            )
        return jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options=decode_options,
        )

    # Asymmetric algorithm (ES256, RS256, …) — fetch the matching public key.
    # Wrap every step so a network blip or malformed JWKS response becomes a
    # clean 401 instead of an unhandled 500 crash.
    try:
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except jwt.PyJWKClientError as exc:
        raise jwt.InvalidTokenError(
            f"Could not retrieve signing key from JWKS endpoint: {exc}"
        ) from exc
    except Exception as exc:
        raise jwt.InvalidTokenError(
            f"Unexpected JWKS error ({type(exc).__name__}): {exc}"
        ) from exc

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
    except Exception as exc:
        # Catches any residual errors (e.g. RuntimeError from missing env vars,
        # unexpected library exceptions) so they return 401 rather than 500.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {type(exc).__name__}: {exc}",
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
