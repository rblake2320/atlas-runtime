from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


@dataclass(frozen=True)
class Event:
    seq: int
    ts: str
    type: str
    agent: str
    payload: dict[str, Any]
    prev_hash: str
    hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            'seq': self.seq,
            'ts': self.ts,
            'type': self.type,
            'agent': self.agent,
            'payload': self.payload,
            'prev_hash': self.prev_hash,
            'hash': self.hash,
        }


def canonical_hash(seq: int, ts: str, kind: str, agent: str, payload: dict[str, Any], prev_hash: str) -> str:
    body = {
        'seq': seq,
        'ts': ts,
        'type': kind,
        'agent': agent,
        'payload': payload,
        'prev_hash': prev_hash,
    }
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()


def make_event(seq: int, kind: str, agent: str, payload: dict[str, Any], prev_hash: str, ts: str | None = None) -> Event:
    stamp = ts or utc_now()
    return Event(
        seq=seq,
        ts=stamp,
        type=kind,
        agent=agent,
        payload=payload,
        prev_hash=prev_hash,
        hash=canonical_hash(seq, stamp, kind, agent, payload, prev_hash),
    )


class EventStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.witness_path = self.path.with_suffix(self.path.suffix + '.witness.json')

    def read(self) -> list[Event]:
        if not self.path.exists():
            return []
        rows: list[Event] = []
        for raw in self.path.read_text(encoding='utf-8').splitlines():
            if not raw.strip():
                continue
            data = json.loads(raw)
            rows.append(Event(**data))
        return rows

    def write_witness(self, rows: list[Event]) -> None:
        digest_input = '|'.join(event.hash for event in rows)
        witness = {
            'event_count': len(rows),
            'last_seq': rows[-1].seq if rows else 0,
            'last_hash': rows[-1].hash if rows else 'GENESIS',
            'chain_digest': hashlib.sha256(digest_input.encode('utf-8')).hexdigest(),
        }
        self.witness_path.write_text(json.dumps(witness, indent=2) + '\n', encoding='utf-8')

    def append(self, kind: str, agent: str, payload: dict[str, Any]) -> Event:
        rows = self.read()
        prev_hash = rows[-1].hash if rows else 'GENESIS'
        seq = rows[-1].seq + 1 if rows else 1
        event = make_event(seq, kind, agent, payload, prev_hash)
        with self.path.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(event.as_dict()) + '\n')
        self.write_witness(self.read())
        return event

    def verify(self) -> tuple[bool, list[str]]:
        rows = self.read()
        if not rows:
            return True, []
        problems: list[str] = []
        expected_prev = 'GENESIS'
        expected_seq = 1
        seen_seq: set[int] = set()
        for row in rows:
            if row.seq in seen_seq:
                problems.append(f'duplicate_seq:{row.seq}')
            seen_seq.add(row.seq)
            if row.seq != expected_seq:
                problems.append(f'seq_gap:{expected_seq}->{row.seq}')
                expected_seq = row.seq
            if row.prev_hash != expected_prev:
                problems.append(f'prev_hash_mismatch:{row.seq}')
            expected_hash = canonical_hash(row.seq, row.ts, row.type, row.agent, row.payload, row.prev_hash)
            if row.hash != expected_hash:
                problems.append(f'hash_mismatch:{row.seq}')
            expected_prev = row.hash
            expected_seq += 1
        if self.witness_path.exists():
            witness = json.loads(self.witness_path.read_text(encoding='utf-8'))
            digest_input = '|'.join(event.hash for event in rows)
            chain_digest = hashlib.sha256(digest_input.encode('utf-8')).hexdigest()
            if witness.get('event_count') != len(rows):
                problems.append('witness_event_count_mismatch')
            if witness.get('last_seq') != rows[-1].seq:
                problems.append('witness_last_seq_mismatch')
            if witness.get('last_hash') != rows[-1].hash:
                problems.append('witness_last_hash_mismatch')
            if witness.get('chain_digest') != chain_digest:
                problems.append('witness_chain_digest_mismatch')
        return not problems, problems

    def stats(self) -> dict[str, Any]:
        rows = self.read()
        ok, problems = self.verify()
        return {
            'event_count': len(rows),
            'last_seq': rows[-1].seq if rows else 0,
            'chain_ok': ok,
            'problems': problems,
        }
