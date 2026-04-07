from pathlib import Path

from atlas_runtime.core.events import EventStore


def test_event_store_hash_chain(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.jsonl")
    store.append("system.init", "HELM", {"ok": True})
    store.append("task.delivered", "FORGE", {"task_id": "AR-1"})
    stats = store.stats()
    assert stats["event_count"] == 2
    assert stats["chain_ok"] is True


def test_event_store_detects_tamper(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.jsonl")
    store.append("system.init", "HELM", {"ok": True})
    rows = store.read()
    tampered = rows[0].as_dict()
    tampered["payload"] = {"ok": False}
    store.path.write_text(__import__("json").dumps(tampered) + "\n", encoding="utf-8")
    ok, problems = store.verify()
    assert ok is False
    assert any("hash_mismatch" in item for item in problems)
