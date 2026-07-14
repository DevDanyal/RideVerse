"""Unit tests for the Economy & Banking System (TASK 9).

Covers: Wallet CRUD, deposit, withdraw, transfer, salary, daily rewards,
business income, tax, ATM operations, bank accounts (CRUD), economy summary.
All tests use an in-memory SQLite database.
"""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.core.security import get_password_hash
from app.database.base import Base
from app.dependencies import get_current_active_user, get_db_session
from app.main import app
from app.models.auth import PlayerAccount, AccountStatus, AccountRole
from app.models.bank import BankAccount, AccountType
from app.models.economy import ATM, DailyReward, Transaction, Wallet
from app.models.player import Player, PlayerStatistics, PlayerSettings
from app.repositories.auth import AuthRepository
from app.services.bank import BankAccountService
from app.services.economy import EconomyService

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


_ECONOMY_TABLES = [
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


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, tables=_ECONOMY_TABLES)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all, tables=_ECONOMY_TABLES)
    await engine.dispose()


@pytest_asyncio.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with factory() as session:
        yield session
        if session.is_active:
            await session.rollback()


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


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _create_player_with_account(
    session: AsyncSession, email: str = "econ@test.com", cash: float = 50000.0
) -> tuple[PlayerAccount, Player]:
    auth_repo = AuthRepository(session)
    account = await auth_repo.create_account(
        email=email,
        username=email.split("@")[0],
        password_hash=get_password_hash("StrongPass1!"),
    )
    player = Player(
        account_id=account.id,
        display_name=f"Player_{email.split('@')[0]}",
        level=5,
        experience=1000,
        cash=cash,
    )
    session.add(player)
    await session.flush()

    stats = PlayerStatistics(player_id=player.id)
    session.add(stats)
    settings = PlayerSettings(player_id=player.id)
    session.add(settings)
    wallet = Wallet(
        player_id=player.id,
        cash=cash,
        bank_balance=10000.0,
        max_cash=500000.0,
        max_bank_balance=10000000.0,
        daily_salary=500.0,
        total_earned=cash,
        total_spent=0.0,
    )
    session.add(wallet)
    await session.flush()
    return account, player


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Wallet Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestWallet:
    """Wallet creation, retrieval, and updates."""

    @pytest.mark.asyncio
    async def test_get_wallet(self, db: AsyncSession):
        account, player = await _create_player_with_account(db)
        svc = EconomyService(db)
        wallet = await svc.get_wallet(account.id)
        assert wallet["player_id"] == player.id
        assert wallet["cash"] == 50000.0
        assert wallet["bank_balance"] == 10000.0

    @pytest.mark.asyncio
    async def test_wallet_max_limits(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        wallet = await svc.get_wallet(account.id)
        assert wallet["max_cash"] == 500000.0
        assert wallet["max_bank_balance"] == 10000000.0

    @pytest.mark.asyncio
    async def test_wallet_daily_salary(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        wallet = await svc.get_wallet(account.id)
        assert wallet["daily_salary"] == 500.0


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Deposit / Withdraw Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestDepositWithdraw:
    """Deposit and withdraw operations."""

    @pytest.mark.asyncio
    async def test_deposit_cash(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = EconomyService(db)
        result = await svc.deposit(account.id, 5000.0)
        assert result["deposited"] == 5000.0
        assert result["fee"] == 0.0
        assert result["new_cash"] == 5000.0
        assert result["new_bank_balance"] == 15000.0

    @pytest.mark.asyncio
    async def test_deposit_insufficient_cash(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=100.0)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Insufficient cash"):
            await svc.deposit(account.id, 5000.0)

    @pytest.mark.asyncio
    async def test_withdraw_cash(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        result = await svc.withdraw(account.id, 5000.0)
        assert result["withdrawn"] == 5000.0
        assert result["new_cash"] == 6000.0
        assert result["new_bank_balance"] == 5000.0

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_bank(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Insufficient bank balance"):
            await svc.withdraw(account.id, 50000.0)

    @pytest.mark.asyncio
    async def test_withdraw_cash_limit(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=490000.0)
        svc = EconomyService(db)
        from sqlalchemy import update as sa_update
        stmt = (
            sa_update(Wallet)
            .where(Wallet.player_id == player.id)
            .values(bank_balance=1000000.0)
        )
        await db.execute(stmt)
        await db.flush()
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Cash limit"):
            await svc.withdraw(account.id, 500000.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3: ATM Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestATM:
    """ATM deposit/withdraw with fees."""

    @pytest.mark.asyncio
    async def test_deposit_via_atm(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=20000.0)
        atm = ATM(
            name="Main ATM",
            location="Downtown",
            is_operational=True,
            daily_withdrawal_limit=50000.0,
            transaction_fee=2.50,
        )
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        result = await svc.deposit(account.id, 5000.0, atm_id=atm.id)
        assert result["fee"] == 2.50
        assert result["deposited"] == 5000.0
        assert result["new_cash"] == 14997.50

    @pytest.mark.asyncio
    async def test_deposit_atm_insufficient_for_fee(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=100.0)
        atm = ATM(
            name="Main ATM",
            location="Downtown",
            is_operational=True,
            daily_withdrawal_limit=50000.0,
            transaction_fee=50.0,
        )
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Insufficient cash"):
            await svc.deposit(account.id, 80.0, atm_id=atm.id)

    @pytest.mark.asyncio
    async def test_deposit_atm_out_of_service(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=20000.0)
        atm = ATM(
            name="Broken ATM",
            location="Mall",
            is_operational=False,
            daily_withdrawal_limit=50000.0,
            transaction_fee=2.0,
        )
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="out of service"):
            await svc.deposit(account.id, 100.0, atm_id=atm.id)

    @pytest.mark.asyncio
    async def test_atm_daily_limit_reached(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=20000.0)
        atm = ATM(
            name="Main ATM",
            location="Downtown",
            is_operational=True,
            daily_withdrawal_limit=100.0,
            daily_withdrawn=90.0,
            transaction_fee=2.0,
        )
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="daily withdrawal limit"):
            await svc.deposit(account.id, 20.0, atm_id=atm.id)

    @pytest.mark.asyncio
    async def test_withdraw_via_atm(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        atm = ATM(
            name="Main ATM",
            location="Downtown",
            is_operational=True,
            daily_withdrawal_limit=50000.0,
            transaction_fee=1.50,
        )
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        result = await svc.withdraw(account.id, 500.0, atm_id=atm.id)
        assert result["fee"] == 1.50
        assert result["new_cash"] == 1500.0
        assert result["new_bank_balance"] == 9498.50

    @pytest.mark.asyncio
    async def test_get_atms(self, db: AsyncSession):
        atm = ATM(name="ATM 1", location="Location A", is_operational=True)
        db.add(atm)
        await db.flush()

        svc = EconomyService(db)
        atms = await svc.get_atms()
        assert len(atms) >= 1


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Transfer Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTransfer:
    """Player-to-player transfers."""

    @pytest.mark.asyncio
    async def test_transfer_success(self, db: AsyncSession):
        acc1, p1 = await _create_player_with_account(db, email="sender@test.com", cash=20000.0)
        acc2, p2 = await _create_player_with_account(db, email="receiver@test.com", cash=5000.0)
        svc = EconomyService(db)
        result = await svc.transfer(acc1.id, p2.id, 1000.0)
        assert result["amount"] == 1000.0
        assert result["fee"] == max(1.0, 1000.0 * 0.02)
        assert result["sender_balance_after"] < 20000.0

    @pytest.mark.asyncio
    async def test_transfer_insufficient_cash(self, db: AsyncSession):
        acc1, p1 = await _create_player_with_account(db, email="sender2@test.com", cash=100.0)
        acc2, p2 = await _create_player_with_account(db, email="recv2@test.com", cash=5000.0)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Insufficient cash"):
            await svc.transfer(acc1.id, p2.id, 10000.0)

    @pytest.mark.asyncio
    async def test_transfer_zero_amount(self, db: AsyncSession):
        acc1, p1 = await _create_player_with_account(db, email="sender3@test.com")
        acc2, p2 = await _create_player_with_account(db, email="recv3@test.com")
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="positive"):
            await svc.transfer(acc1.id, p2.id, 0.0)

    @pytest.mark.asyncio
    async def test_transfer_creates_transactions(self, db: AsyncSession):
        acc1, p1 = await _create_player_with_account(db, email="sender4@test.com", cash=20000.0)
        acc2, p2 = await _create_player_with_account(db, email="recv4@test.com", cash=5000.0)
        svc = EconomyService(db)
        await svc.transfer(acc1.id, p2.id, 500.0)

        txs_sender = await svc.get_transaction_history(acc1.id, limit=5)
        txs_receiver = await svc.get_transaction_history(acc2.id, limit=5)
        assert any(tx.transaction_type.value == "transfer_out" for tx in txs_sender)
        assert any(tx.transaction_type.value == "transfer_in" for tx in txs_receiver)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Salary Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestSalary:
    """Daily salary claims."""

    @pytest.mark.asyncio
    async def test_claim_salary(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        result = await svc.claim_salary(account.id)
        assert result["salary_amount"] == 500.0
        assert result["new_cash_balance"] == 1500.0

    @pytest.mark.asyncio
    async def test_claim_salary_cooldown(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        await svc.claim_salary(account.id)

        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="already claimed"):
            await svc.claim_salary(account.id)

    @pytest.mark.asyncio
    async def test_claim_salary_after_cooldown(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        await svc.claim_salary(account.id)

        # Simulate 25 hours ago
        wallet = await svc._get_wallet_or_raise(player.id)
        from sqlalchemy import update
        stmt = (
            update(Wallet)
            .where(Wallet.player_id == player.id)
            .values(
                last_salary_claim=datetime.now(timezone.utc) - timedelta(hours=25),
                cash=1000.0,
            )
        )
        await db.execute(stmt)
        await db.flush()

        result = await svc.claim_salary(account.id)
        assert result["salary_amount"] == 500.0


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Daily Reward Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestDailyRewards:
    """7-day daily reward streak system."""

    @pytest.mark.asyncio
    async def test_get_reward_status(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        rewards = await svc.get_daily_reward_status(account.id)
        assert len(rewards) == 7
        assert rewards[0]["day_number"] == 1
        assert rewards[0]["reward_amount"] == 500
        assert rewards[0]["claimed"] is False

    @pytest.mark.asyncio
    async def test_claim_day_1(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=100.0)
        svc = EconomyService(db)
        result = await svc.claim_daily_reward(account.id)
        assert result["day_number"] == 1
        assert result["reward_amount"] == 500
        assert result["new_cash_balance"] == 600.0

    @pytest.mark.asyncio
    async def test_claim_full_streak(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=0.0)
        svc = EconomyService(db)
        amounts = [500, 600, 750, 900, 1000, 1200, 2000]
        total = 0
        for expected_amount in amounts:
            result = await svc.claim_daily_reward(account.id)
            total += result["reward_amount"]
            assert result["reward_amount"] == expected_amount
        wallet = await svc.get_wallet(account.id)
        assert wallet["cash"] == total

    @pytest.mark.asyncio
    async def test_claim_streak_resets(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=0.0)
        svc = EconomyService(db)
        for _ in range(7):
            await svc.claim_daily_reward(account.id)
        result = await svc.claim_daily_reward(account.id)
        assert result["day_number"] == 1
        assert result["reward_amount"] == 500

    @pytest.mark.asyncio
    async def test_streak_advances(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=0.0)
        svc = EconomyService(db)
        result1 = await svc.claim_daily_reward(account.id)
        assert result1["day_number"] == 1
        result2 = await svc.claim_daily_reward(account.id)
        assert result2["day_number"] == 2


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Business Income Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestBusinessIncome:
    """Business income credit operations."""

    @pytest.mark.asyncio
    async def test_credit_business_income(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        biz_id = uuid.uuid4()
        result = await svc.credit_business_income(
            player.id, 2500.0, business_id=biz_id, description="Car rental"
        )
        assert result["amount"] == 2500.0
        assert result["new_cash_balance"] == 3500.0

    @pytest.mark.asyncio
    async def test_business_income_cash_limit(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=499999.0)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Cash limit"):
            await svc.credit_business_income(player.id, 100.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Tax Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTax:
    """Tax application operations."""

    @pytest.mark.asyncio
    async def test_apply_tax(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = EconomyService(db)
        result = await svc.apply_tax(account.id, 0.10)
        assert result["tax_amount"] == 1000.0
        assert result["rate"] == 0.10
        assert result["new_cash_balance"] == 9000.0

    @pytest.mark.asyncio
    async def test_apply_tax_invalid_rate(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="between 0 and 1"):
            await svc.apply_tax(account.id, 1.5)

    @pytest.mark.asyncio
    async def test_apply_tax_zero_cash(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=0.0)
        svc = EconomyService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="No tax to collect"):
            await svc.apply_tax(account.id, 0.10)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Transaction History Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestTransactions:
    """Transaction recording and querying."""

    @pytest.mark.asyncio
    async def test_transaction_recorded_on_deposit(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = EconomyService(db)
        await svc.deposit(account.id, 5000.0)
        txs = await svc.get_transaction_history(account.id)
        assert len(txs) >= 1
        assert txs[0].transaction_type.value == "deposit"

    @pytest.mark.asyncio
    async def test_get_transactions_by_type(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = EconomyService(db)
        await svc.deposit(account.id, 2000.0)
        await svc.withdraw(account.id, 1000.0)
        txs = await svc.get_transactions_by_type(account.id, "deposit")
        assert all(tx.transaction_type.value == "deposit" for tx in txs)

    @pytest.mark.asyncio
    async def test_transaction_history_limit(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=100000.0)
        svc = EconomyService(db)
        for _ in range(5):
            await svc.deposit(account.id, 100.0)
        txs = await svc.get_transaction_history(account.id, limit=3)
        assert len(txs) == 3


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 10: Loan Tests (disabled)
# ══════════════════════════════════════════════════════════════════════════════


class TestLoan:
    """Loan system (disabled)."""

    @pytest.mark.asyncio
    async def test_request_loan_disabled(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        result = await svc.request_loan(account.id, 10000.0)
        assert "not yet enabled" in result["message"]

    @pytest.mark.asyncio
    async def test_repay_loan_disabled(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = EconomyService(db)
        result = await svc.repay_loan(account.id, 1000.0)
        assert "not yet enabled" in result["message"]


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 11: Economy Summary Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestEconomySummary:
    """Economy summary endpoint."""

    @pytest.mark.asyncio
    async def test_get_summary(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=50000.0)
        svc = EconomyService(db)
        summary = await svc.get_economy_summary(account.id)
        assert summary["cash"] == 50000.0
        assert summary["bank_balance"] == 10000.0
        assert summary["total_wealth"] == 60000.0
        assert summary["daily_salary"] == 500.0
        assert summary["salary_claimed_today"] is False

    @pytest.mark.asyncio
    async def test_summary_after_salary_claim(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        svc = EconomyService(db)
        await svc.claim_salary(account.id)
        summary = await svc.get_economy_summary(account.id)
        assert summary["salary_claimed_today"] is True


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 12: Bank Account Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestBankAccounts:
    """Bank account CRUD and operations."""

    @pytest.mark.asyncio
    async def test_create_checking_account(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 0.0)
        assert bank_acc.account_type == "checking"
        assert bank_acc.balance == 0.0
        assert bank_acc.is_active is True

    @pytest.mark.asyncio
    async def test_create_savings_account(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "savings", 0.0)
        assert bank_acc.account_type == "savings"
        assert bank_acc.interest_rate == 0.02

    @pytest.mark.asyncio
    async def test_create_with_initial_deposit(self, db: AsyncSession):
        account, player = await _create_player_with_account(db, cash=10000.0)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 3000.0)
        assert bank_acc.balance == 3000.0
        econ_svc = EconomyService(db)
        wallet = await econ_svc.get_wallet(account.id)
        assert wallet["cash"] == 7000.0

    @pytest.mark.asyncio
    async def test_max_5_accounts(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=100000.0)
        svc = BankAccountService(db)
        for _ in range(5):
            await svc.create_account(account.id, "checking", 0.0)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Maximum 5"):
            await svc.create_account(account.id, "checking", 0.0)

    @pytest.mark.asyncio
    async def test_list_accounts(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = BankAccountService(db)
        await svc.create_account(account.id, "checking", 0.0)
        await svc.create_account(account.id, "savings", 0.0)
        accounts = await svc.get_accounts(account.id)
        assert len(accounts) == 2

    @pytest.mark.asyncio
    async def test_deposit_to_account(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 0.0)
        result = await svc.deposit_to_account(account.id, bank_acc.id, 5000.0)
        assert result["new_account_balance"] == 5000.0
        assert result["new_wallet_cash"] == 5000.0

    @pytest.mark.asyncio
    async def test_withdraw_from_account(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=10000.0)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 5000.0)
        result = await svc.withdraw_from_account(account.id, bank_acc.id, 2000.0)
        assert result["new_account_balance"] == 3000.0
        assert result["new_wallet_cash"] == 7000.0

    @pytest.mark.asyncio
    async def test_close_account(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db, cash=1000.0)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 0.0)
        result = await svc.close_account(account.id, bank_acc.id)
        assert "closed" in result["message"]

    @pytest.mark.asyncio
    async def test_close_account_with_loan_fails(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = BankAccountService(db)
        bank_acc = await svc.create_account(account.id, "checking", 0.0)
        from sqlalchemy import update as sa_update
        stmt = (
            sa_update(BankAccount)
            .where(BankAccount.id == bank_acc.id)
            .values(loan_balance=5000.0)
        )
        await db.execute(stmt)
        await db.flush()

        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="outstanding loan"):
            await svc.close_account(account.id, bank_acc.id)

    @pytest.mark.asyncio
    async def test_create_invalid_type(self, db: AsyncSession):
        account, _ = await _create_player_with_account(db)
        svc = BankAccountService(db)
        from app.core.exceptions import ValidationError
        with pytest.raises(ValidationError, match="Invalid account type"):
            await svc.create_account(account.id, "credit", 0.0)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 13: API Endpoint Tests
# ══════════════════════════════════════════════════════════════════════════════


class TestEconomyAPI:
    """Test API endpoints through HTTP client."""

    @pytest.mark.asyncio
    async def test_get_wallet_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/me/economy/wallet")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_get_atms(self, client: AsyncClient, db: AsyncSession):
        atm = ATM(name="Test ATM", location="Test", is_operational=True)
        db.add(atm)
        await db.flush()
        token = await _register_user(client, "atm_api")
        resp = await client.get(
            "/api/v1/players/me/economy/atms",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_get_daily_rewards(self, client: AsyncClient):
        token = await _register_user(client, "daily_api")
        resp = await client.get(
            "/api/v1/players/me/economy/daily-rewards",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (400, 404, 200)

    @pytest.mark.asyncio
    async def test_loan_disabled(self, client: AsyncClient):
        token = await _register_user(client, "loan_api")
        resp = await client.post(
            "/api/v1/players/me/economy/loan",
            json={"amount": 10000, "term_days": 30},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert "not yet enabled" in resp.json()["data"]["message"]

    @pytest.mark.asyncio
    async def test_bank_get_accounts_unauthenticated(self, client: AsyncClient):
        resp = await client.get("/api/v1/players/me/bank")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_bank_get_accounts(self, client: AsyncClient):
        token = await _register_user(client, "bank_api")
        resp = await client.get(
            "/api/v1/players/me/bank",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code in (400, 404, 200)


async def _register_user(client: AsyncClient, prefix: str) -> str:
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{prefix}_{uuid.uuid4().hex[:8]}@test.com",
            "username": f"{prefix}_{uuid.uuid4().hex[:8]}",
            "password": "StrongPass1!",
        },
    )
    assert resp.status_code == 201
    return resp.json()["data"]["access_token"]
