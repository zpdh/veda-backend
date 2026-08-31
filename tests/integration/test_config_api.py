from httpx import AsyncClient


class TestConfigEndpoints:
    async def test_get_config(self, client: AsyncClient):
        res = await client.get("/v1/api/config/")
        assert res.status_code == 200
        data = res.json()
        assert "config" in data
        assert isinstance(data["config"], list)
        assert len(data["config"]) == 3

        item = data["config"][0]
        assert "leaderboardName" in item
        assert "leaderboardId" in item
        assert "pages" in item
        assert item["pages"] == 50
