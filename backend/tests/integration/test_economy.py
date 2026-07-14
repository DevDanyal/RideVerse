"""Integration tests for the Economy & Banking System (TASK 9).

Tests the full economy and bank API flows with a real database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.database.base import Base
from app.dependencies import get_db_session
from app.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

_ECONOMY_INT_TABLES = [
    Base.metadata.tables[name]
    for name in (
        "player_accounts",
        "player_sessions",
        "refresh_tokens",
        "players",
        "player_statistics",
        "player_settings",
        "inventories",
        "wallets",
        "transactions",
        "daily_rewards",
        "atms",
        "bank_accounts",
    )
    if name in Base.metadata.tables
]


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_ECONOMY_INT_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_ECONOMY_INT_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_engine) -> AsyncGenerator[AsyncClient, None]:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

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


async def _register_and_get_token(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"econ_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"econ_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 1: Wallet API
# ══════════════════════════════════════════════════════════════════════════════


class TestWalletAPI:
    """Test wallet retrieval via API with registered user."""

    @pytest.mark.asyncio
    async def test_get_wallet(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/economy/wallet",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "cash" in data
        assert "bank_balance" in data

    @pytest.mark.asyncio
    async def test_get_wallet_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/me/economy/wallet")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 2: Deposit & Withdraw via API
# ══════════════════════════════════════════════════════════════════════════════


class TestDepositWithdrawAPI:
    """Test deposit and withdraw through the API."""

    @pytest.mark.asyncio
    async def test_deposit(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            "/api/v1/players/me/economy/deposit",
            json={"amount": 100.0},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["deposited"] == 100.0

    @pytest.mark.asyncio
    async def test_withdraw(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        await client.post(
            "/api/v1/players/me/economy/deposit",
            json={"amount": 500.0},
            headers=headers,
        )
        resp = await client.post(
            "/api/v1/players/me/economy/withdraw",
            json={"amount": 200.0},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["withdrawn"] == 200.0


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 3: Transfer API
# ══════════════════════════════════════════════════════════════════════════════


class TestTransferAPI:
    """Test player-to-player transfer through the API."""

    @pytest.mark.asyncio
    async def test_transfer_endpoint_exists(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/players/me/economy/transfer",
            json={
                "target_player_id": str(uuid.uuid4()),
                "amount": 1.0,
            },
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (200, 400, 404)


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 4: Salary Claim API
# ══════════════════════════════════════════════════════════════════════════════


class TestSalaryAPI:
    """Test salary claim through the API."""

    @pytest.mark.asyncio
    async def test_claim_salary(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/players/me/economy/salary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "salary_amount" in data


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 5: Daily Reward API
# ══════════════════════════════════════════════════════════════════════════════


class TestDailyRewardAPI:
    """Test daily reward claim through the API."""

    @pytest.mark.asyncio
    async def test_claim_daily_reward(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/players/me/economy/daily-rewards/claim",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["day_number"] == 1
        assert data["reward_amount"] == 500

    @pytest.mark.asyncio
    async def test_get_reward_status(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/economy/daily-rewards",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data) == 7


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 6: Economy Summary API
# ══════════════════════════════════════════════════════════════════════════════


class TestEconomySummaryAPI:
    """Test economy summary through the API."""

    @pytest.mark.asyncio
    async def test_get_summary(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/economy/summary",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "cash" in data
        assert "bank_balance" in data
        assert "total_wealth" in data


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 7: ATM API
# ══════════════════════════════════════════════════════════════════════════════


class TestATMAPI:
    """Test ATM listing through the API."""

    @pytest.mark.asyncio
    async def test_list_atms(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.get(
            "/api/v1/players/me/economy/atms",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 8: Bank Account API
# ══════════════════════════════════════════════════════════════════════════════


class TestBankAccountAPI:
    """Test bank account creation and operations through the API."""

    @pytest.mark.asyncio
    async def test_create_bank_account(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.post(
            "/api/v1/players/me/bank",
            json={"account_type": "checking", "initial_deposit": 0.0},
            headers=headers,
        )
        assert resp.status_code == 201
        assert resp.json()["data"]["balance"] == 0.0

    @pytest.mark.asyncio
    async def test_list_bank_accounts(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post(
            "/api/v1/players/me/bank",
            json={"account_type": "checking"},
            headers=headers,
        )
        resp = await client.get(
            "/api/v1/players/me/bank",
            headers=headers,
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 9: Transaction History API
# ══════════════════════════════════════════════════════════════════════════════


class TestTransactionHistoryAPI:
    """Test transaction history through the API."""

    @pytest.mark.asyncio
    async def test_transactions_after_deposit(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        await client.post(
            "/api/v1/players/me/economy/deposit",
            json={"amount": 500.0},
            headers=headers,
        )
        resp = await client.get(
            "/api/v1/players/me/economy/transactions",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()["data"]["data"]
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_transactions_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/me/economy/transactions")
        assert resp.status_code == 401


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION 10: Loan API (disabled)
# ══════════════════════════════════════════════════════════════════════════════


class TestLoanAPI:
    """Test loan endpoint returns disabled message."""

    @pytest.mark.asyncio
    async def test_loan_disabled(self, client: AsyncClient):
        token = await _register_and_get_token(client)
        resp = await client.post(
            "/api/v1/players/me/economy/loan",
            json={"amount": 10000, "term_days": 30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert "not yet enabled" in resp.json()["data"]["message"]
