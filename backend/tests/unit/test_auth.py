"""Unit tests for the authentication system.

Covers: register, login, logout, refresh token, current user, role gates.
All tests use an in-memory SQLite database — no external services required.
"""
from __future__ import annotations

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.base import Base
from app.dependencies import get_current_active_user, get_current_user, get_db_session
from app.main import app
from app.models.auth import AccountRole, AccountStatus, PlayerAccount, PlayerSession, RefreshToken
from app.repositories.auth import AuthRepository
from app.services.auth import AuthenticationService

# ── Test Settings ──────────────────────────────────────────────────────────────

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


def _test_settings() -> Settings:
    return Settings(
        DATABASE_URL=TEST_DB_URL,
        REDIS_URL="redis://localhost:6379/15",
        SECRET_KEY="test-secret",
        JWT_SECRET_KEY="test-jwt-secret",
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30,
        JWT_REFRESH_TOKEN_EXPIRE_DAYS=7,
        ENVIRONMENT="testing",
        DEBUG=True,
    )


# ── Auth-only tables list (avoids duplicate-index issues in other models) ──────

_AUTH_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "wallets",
        "inventories",
        "garages",
        "garage_slots",
    )
    if name in Base.metadata.tables
]


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_AUTH_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_AUTH_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session
        if session.is_active:
            await session.rollback()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    factory = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

    async def _override():
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Security Tests ─────────────────────────────────────────────────────────────


class TestPasswordHashing:
    def test_hash_and_verify(self):
        plain = "SuperSecret123!"
        hashed = get_password_hash(plain)
        assert hashed != plain
        assert verify_password(plain, hashed) is True

    def test_wrong_password_fails(self):
        hashed = get_password_hash("correct-password")
        assert verify_password("wrong-password", hashed) is False


class TestJWT:
    def test_create_and_verify_access_token(self):
        payload = {"sub": str(uuid.uuid4()), "type": "access"}
        token = create_access_token(payload)
        from app.core.security import verify_token
        decoded = verify_token(token)
        assert decoded is not None
        assert decoded["sub"] == payload["sub"]
        assert decoded["type"] == "access"

    def test_invalid_token_returns_none(self):
        from app.core.security import verify_token
        assert verify_token("not-a-real-token") is None


# ── Repository Tests ───────────────────────────────────────────────────────────


class TestAuthRepository:
    async def test_create_and_get_account(self, db: AsyncSession):
        repo = AuthRepository(db)
        account = await repo.create_account(
            email="repo@test.com",
            username="repouser",
            password_hash=get_password_hash("pass1234"),
        )
        assert account.id is not None
        fetched = await repo.get_account_by_id(account.id)
        assert fetched is not None
        assert fetched.email == "repo@test.com"

    async def test_get_by_email(self, db: AsyncSession):
        repo = AuthRepository(db)
        await repo.create_account("a@b.com", "user_a", get_password_hash("pass"))
        found = await repo.get_account_by_email("a@b.com")
        assert found is not None
        assert found.username == "user_a"

    async def test_get_by_username(self, db: AsyncSession):
        repo = AuthRepository(db)
        await repo.create_account("x@y.com", "unique_user", get_password_hash("pass"))
        found = await repo.get_account_by_username("unique_user")
        assert found is not None

    async def test_create_and_revoke_refresh_token(self, db: AsyncSession):
        from datetime import datetime, timedelta, timezone
        repo = AuthRepository(db)
        account = await repo.create_account("r@t.com", "revoke_user", get_password_hash("pass"))
        token = await repo.create_refresh_token(
            account_id=account.id,
            token="test-refresh-token-123",
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        assert token.revoked is False
        await repo.revoke_refresh_token("test-refresh-token-123")
        await db.flush()
        refreshed = await repo.get_refresh_token("test-refresh-token-123")
        assert refreshed is None

    async def test_revoke_all_account_tokens(self, db: AsyncSession):
        from datetime import datetime, timedelta, timezone
        repo = AuthRepository(db)
        account = await repo.create_account("bulk@t.com", "bulk_user", get_password_hash("pass"))
        await repo.create_refresh_token(account.id, "token-a", datetime.now(timezone.utc) + timedelta(days=7))
        await repo.create_refresh_token(account.id, "token-b", datetime.now(timezone.utc) + timedelta(days=7))
        await repo.revoke_all_account_tokens(account.id)
        await db.flush()
        assert await repo.get_refresh_token("token-a") is None
        assert await repo.get_refresh_token("token-b") is None

    async def test_update_last_login(self, db: AsyncSession):
        repo = AuthRepository(db)
        account = await repo.create_account("ll@t.com", "login_user", get_password_hash("pass"))
        assert account.last_login is None
        await repo.update_last_login(account.id)
        await db.flush()
        updated = await repo.get_account_by_id(account.id)
        assert updated is not None
        assert updated.last_login is not None

    async def test_update_account_status(self, db: AsyncSession):
        repo = AuthRepository(db)
        account = await repo.create_account("st@t.com", "status_user", get_password_hash("pass"))
        await repo.update_account_status(account.id, AccountStatus.SUSPENDED)
        await db.flush()
        updated = await repo.get_account_by_id(account.id)
        assert updated is not None
        assert updated.account_status == AccountStatus.SUSPENDED


# ── Service Tests ──────────────────────────────────────────────────────────────


class TestAuthenticationService:
    async def test_register_success(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        result = await svc.register("new@test.com", "newuser", "StrongPass1!")
        assert "access_token" in result
        assert "refresh_token" in result
        assert result["username"] == "newuser"
        assert result["role"] == AccountRole.PLAYER.value

    async def test_register_duplicate_email_fails(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("dup@test.com", "user1", "StrongPass1!")
        with pytest.raises(Exception, match="already exists"):
            await svc.register("dup@test.com", "user2", "StrongPass1!")

    async def test_register_duplicate_username_fails(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("a@test.com", "same_name", "StrongPass1!")
        with pytest.raises(Exception, match="already taken"):
            await svc.register("b@test.com", "same_name", "StrongPass1!")

    async def test_login_success(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("login@test.com", "loginuser", "StrongPass1!")
        result = await svc.login("login@test.com", "StrongPass1!")
        assert "access_token" in result
        assert result["username"] == "loginuser"

    async def test_login_wrong_password(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("wrong@test.com", "wronguser", "StrongPass1!")
        with pytest.raises(Exception, match="Invalid email or password"):
            await svc.login("wrong@test.com", "WrongPassword!")

    async def test_login_nonexistent_email(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        with pytest.raises(Exception, match="Invalid email or password"):
            await svc.login("ghost@test.com", "StrongPass1!")

    async def test_login_suspended_account(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        account = await repo.create_account(
            "sus@test.com", "suspended_user", get_password_hash("StrongPass1!")
        )
        await repo.update_account_status(account.id, AccountStatus.SUSPENDED)
        await db.flush()
        with pytest.raises(Exception, match="not active"):
            await svc.login("sus@test.com", "StrongPass1!")

    async def test_refresh_token_success(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("refresh@test.com", "refreshuser", "StrongPass1!")
        login_result = await svc.login("refresh@test.com", "StrongPass1!")
        new_tokens = await svc.refresh_token(login_result["refresh_token"])
        assert "access_token" in new_tokens
        assert new_tokens["refresh_token"] != login_result["refresh_token"]

    async def test_refresh_token_revoked_fails(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("rev@test.com", "revuser", "StrongPass1!")
        login_result = await svc.login("rev@test.com", "StrongPass1!")
        await svc.logout(login_result["refresh_token"])
        with pytest.raises(Exception, match="revoked"):
            await svc.refresh_token(login_result["refresh_token"])

    async def test_logout_revokes_token(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        await svc.register("out@test.com", "outuser", "StrongPass1!")
        login_result = await svc.login("out@test.com", "StrongPass1!")
        await svc.logout(login_result["refresh_token"])
        stored = await repo.get_refresh_token(login_result["refresh_token"])
        assert stored is None

    async def test_logout_all(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        account = await repo.create_account("all@test.com", "alluser", get_password_hash("StrongPass1!"))
        await svc.login("all@test.com", "StrongPass1!")
        await svc.login("all@test.com", "StrongPass1!")
        await svc.logout_all(account.id)
        await db.flush()
        from sqlalchemy import select
        stmt = select(RefreshToken).where(
            RefreshToken.account_id == account.id,
            RefreshToken.revoked.is_(False),
        )
        result = await db.execute(stmt)
        assert result.scalar_one_or_none() is None

    async def test_get_account(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        result = await svc.register("get@test.com", "getuser", "StrongPass1!")
        account = await svc.get_account(uuid.UUID(result["account_id"]))
        assert account["email"] == "get@test.com"
        assert account["role"] == AccountRole.PLAYER.value

    async def test_get_account_not_found(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        with pytest.raises(Exception, match="not found"):
            await svc.get_account(uuid.uuid4())


# ── API Endpoint Tests ─────────────────────────────────────────────────────────


class TestRegisterEndpoint:
    async def test_register_returns_201(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "api@test.com",
            "username": "apiuser",
            "password": "StrongPass1!",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["access_token"] is not None

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "dup_api@test.com",
            "username": "dup_api_user1",
            "password": "StrongPass1!",
        })
        response = await client.post("/api/v1/auth/register", json={
            "email": "dup_api@test.com",
            "username": "dup_api_user2",
            "password": "StrongPass1!",
        })
        assert response.status_code == 409

    async def test_register_weak_password_returns_422(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "weak@test.com",
            "username": "weakuser",
            "password": "short",
        })
        assert response.status_code == 422


class TestLoginEndpoint:
    async def test_login_returns_200(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "login_api@test.com",
            "username": "login_api_user",
            "password": "StrongPass1!",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "login_api@test.com",
            "password": "StrongPass1!",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["access_token"] is not None

    async def test_login_wrong_credentials_returns_401(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/login", json={
            "email": "nonexistent@test.com",
            "password": "WrongPass1!",
        })
        assert response.status_code == 401


class TestRefreshEndpoint:
    async def test_refresh_returns_200(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "refresh_api@test.com",
            "username": "refresh_api_user",
            "password": "StrongPass1!",
        })
        refresh_token = reg.json()["data"]["refresh_token"]
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        assert response.json()["data"]["access_token"] is not None

    async def test_refresh_revoked_token_returns_401(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "rev_api@test.com",
            "username": "rev_api_user",
            "password": "StrongPass1!",
        })
        refresh_token = reg.json()["data"]["refresh_token"]
        await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
        response = await client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 401


class TestLogoutEndpoint:
    async def test_logout_returns_200(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "logout_api@test.com",
            "username": "logout_api_user",
            "password": "StrongPass1!",
        })
        refresh_token = reg.json()["data"]["refresh_token"]
        response = await client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"


class TestMeEndpoint:
    async def test_me_returns_200(self, client: AsyncClient):
        reg = await client.post("/api/v1/auth/register", json={
            "email": "me_api@test.com",
            "username": "me_api_user",
            "password": "StrongPass1!",
        })
        access_token = reg.json()["data"]["access_token"]
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "me_api@test.com"
        assert data["data"]["role"] == "player"

    async def test_me_no_token_returns_401(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401


# ── Role Tests ─────────────────────────────────────────────────────────────────


class TestRoleSystem:
    async def test_new_account_gets_player_role(self, db: AsyncSession):
        repo = AuthRepository(db)
        svc = AuthenticationService(repo)
        result = await svc.register("role@test.com", "roleuser", "StrongPass1!")
        assert result["role"] == AccountRole.PLAYER.value

    async def test_model_default_role_is_player(self, db: AsyncSession):
        repo = AuthRepository(db)
        account = await repo.create_account("def@test.com", "defuser", get_password_hash("pass"))
        assert account.role == AccountRole.PLAYER

    async def test_role_hierarchy_ordering(self):
        from app.dependencies import _ROLE_HIERARCHY
        assert _ROLE_HIERARCHY[AccountRole.GUEST] < _ROLE_HIERARCHY[AccountRole.PLAYER]
        assert _ROLE_HIERARCHY[AccountRole.PLAYER] < _ROLE_HIERARCHY[AccountRole.MODERATOR]
        assert _ROLE_HIERARCHY[AccountRole.MODERATOR] < _ROLE_HIERARCHY[AccountRole.ADMIN]
        assert _ROLE_HIERARCHY[AccountRole.ADMIN] < _ROLE_HIERARCHY[AccountRole.DEVELOPER]

    async def test_all_roles_are_valid(self):
        for role in AccountRole:
            assert role.value in ("guest", "player", "moderator", "admin", "developer")
