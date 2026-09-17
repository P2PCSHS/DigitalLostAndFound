"""API behaviour tests.

Each test gets a fresh in-memory database via the `app` fixture, so they can
run in any order and leave nothing behind.
"""


class TestHealth:
    def test_reports_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.get_json() == {"status": "ok"}


class TestStaticFiles:
    def test_serves_index_at_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["Content-Type"]

    def test_serves_assets_from_the_frontend_directory(self, client):
        assert client.get("/style.css").status_code == 200
        assert client.get("/script.js").status_code == 200


class TestAddItem:
    def test_creates_an_item(self, client):
        response = client.post(
            "/items", json={"type": "Keys", "description": "a blue keychain"}
        )
        assert response.status_code == 201

        body = response.get_json()
        assert body["type"] == "Keys"
        assert body["description"] == "a blue keychain"
        assert body["claimed_at"] is None
        assert body["id"] > 0

    def test_new_item_appears_in_the_listing(self, client, make_item):
        make_item(description="a red beanie")
        descriptions = [i["description"] for i in client.get("/items").get_json()]
        assert "a red beanie" in descriptions

    def test_ids_are_unique_after_a_claim(self, client, make_item):
        first = make_item(description="first")
        make_item(description="second")
        client.post(f"/items/{first['id']}/claim")
        third = make_item(description="third")

        all_ids = [i["id"] for i in client.get("/items?status=all").get_json()]
        assert third["id"] not in (first["id"],)
        assert len(all_ids) == len(set(all_ids))

    def test_rejects_missing_fields(self, client):
        assert client.post("/items", json={"type": "Keys"}).status_code == 400
        assert client.post("/items", json={"description": "x"}).status_code == 400

    def test_rejects_malformed_json(self, client):
        response = client.post(
            "/items", data="not json", content_type="application/json"
        )
        assert response.status_code == 400

    def test_rejects_non_text_fields(self, client):
        response = client.post("/items", json={"type": "Keys", "description": 12345})
        assert response.status_code == 400

    def test_rejects_profanity(self, client):
        response = client.post("/items", json={"type": "Keys", "description": "shit"})
        assert response.status_code == 400
        assert "Inappropriate" in response.get_json()["error"]

    def test_rejects_descriptions_over_the_limit(self, client):
        response = client.post(
            "/items", json={"type": "Keys", "description": "x" * 201}
        )
        assert response.status_code == 400

    def test_accepts_a_description_at_the_limit(self, client):
        response = client.post(
            "/items", json={"type": "Keys", "description": "x" * 200}
        )
        assert response.status_code == 201

    def test_stores_markup_verbatim(self, client, make_item):
        """The API stores text as given; escaping is the frontend's job."""
        payload = "<img src=x onerror=alert(1)>"
        item = make_item(description=payload)
        assert item["description"] == payload


class TestClaimItem:
    def test_marks_the_item_claimed(self, client, make_item):
        item = make_item()
        response = client.post(f"/items/{item['id']}/claim")
        assert response.status_code == 200
        assert response.get_json()["claimed_at"] is not None

    def test_claiming_does_not_delete_the_item(self, client, make_item):
        item = make_item()
        client.post(f"/items/{item['id']}/claim")

        claimed_ids = [i["id"] for i in client.get("/items?status=claimed").get_json()]
        assert item["id"] in claimed_ids

    def test_claimed_items_leave_the_default_listing(self, client, make_item):
        item = make_item()
        client.post(f"/items/{item['id']}/claim")

        unclaimed_ids = [i["id"] for i in client.get("/items").get_json()]
        assert item["id"] not in unclaimed_ids

    def test_claiming_twice_conflicts(self, client, make_item):
        item = make_item()
        assert client.post(f"/items/{item['id']}/claim").status_code == 200
        assert client.post(f"/items/{item['id']}/claim").status_code == 409

    def test_claiming_a_missing_item_is_not_found(self, client):
        assert client.post("/items/999/claim").status_code == 404


class TestListItems:
    def test_defaults_to_unclaimed_only(self, client, make_item):
        unclaimed = make_item(description="still lost")
        claimed = make_item(description="picked up")
        client.post(f"/items/{claimed['id']}/claim")

        ids = [i["id"] for i in client.get("/items").get_json()]
        assert ids == [unclaimed["id"]]

    def test_status_all_returns_both(self, client, make_item):
        first = make_item(description="one")
        second = make_item(description="two")
        client.post(f"/items/{second['id']}/claim")

        ids = {i["id"] for i in client.get("/items?status=all").get_json()}
        assert ids == {first["id"], second["id"]}

    def test_rejects_an_unknown_status(self, client):
        assert client.get("/items?status=bogus").status_code == 400

    def test_empty_listing_is_an_empty_array(self, client):
        assert client.get("/items").get_json() == []

    def test_newest_items_come_first(self, client, make_item):
        first = make_item(description="older")
        second = make_item(description="newer")

        ids = [i["id"] for i in client.get("/items").get_json()]
        assert ids.index(second["id"]) < ids.index(first["id"])


class TestIsolation:
    def test_each_test_starts_with_an_empty_database(self, client, make_item):
        make_item()
        assert len(client.get("/items").get_json()) == 1

    def test_and_the_next_one_does_too(self, client):
        assert client.get("/items").get_json() == []
