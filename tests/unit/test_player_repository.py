"""Regression tests for case-insensitive player upserts.

Production raised ``UniqueViolationError`` on ``idx_player_name_lower`` because
the ``ON CONFLICT`` clauses targeted the plain ``name`` column instead of the
functional unique index ``lower(name)``. These tests compile the generated SQL
to assert the conflict target matches the expression index, which is what
makes case-only-different names upsert instead of crashing.
"""

from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.dialects import postgresql

from app.features.player.repositories.postgres import PlayerRepository

_PG_DIALECT = postgresql.dialect()


async def _compiled_statement(repo_call):
    """Run a repo coroutine against a mock session and return compiled SQL."""
    session = AsyncMock()
    session.execute.return_value = MagicMock()

    repo = PlayerRepository(session=session)
    await repo_call(repo)

    session.execute.assert_awaited_once()
    statement = session.execute.await_args.args[0]

    return str(statement.compile(dialect=_PG_DIALECT))


class TestUpsertConflictTargetsLowerNameIndex:
    async def test_upsert_many_conflicts_on_lower_name(self):
        sql = await _compiled_statement(
            lambda repo: repo.upsert_many({"Moagle", "Moagle"})
        )

        assert "ON CONFLICT (lower(name)) DO NOTHING" in sql

    async def test_upsert_many_does_not_conflict_on_bare_name(self):
        sql = await _compiled_statement(lambda repo: repo.upsert_many({"Moagle"}))

        assert "ON CONFLICT (name)" not in sql

    async def test_update_weights_conflicts_on_lower_name(self):
        sql = await _compiled_statement(
            lambda repo: repo.update_weights_for_many({"Moagle": 1.5})
        )

        assert "ON CONFLICT (lower(name))" in sql
        assert "DO UPDATE SET weight = excluded.weight" in sql

    async def test_upsert_many_empty_is_noop(self):
        session = AsyncMock()
        repo = PlayerRepository(session=session)

        await repo.upsert_many(set())

        session.execute.assert_not_awaited()
