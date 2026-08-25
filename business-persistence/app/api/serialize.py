import datetime
import uuid


def row_to_dict(obj) -> dict:
    """Serialize a SQLAlchemy mapped row to a JSON-safe dict, converting
    UUID/datetime to strings. Intentionally simple: response shape mirrors
    the table 1:1 rather than adding a hand-maintained schema per endpoint,
    since this is an internal service boundary (M1/M3/M4 + Dify), not a
    public API with independent versioning needs.
    """

    out = {}
    for col in obj.__table__.columns:
        value = getattr(obj, col.name)
        if isinstance(value, uuid.UUID):
            value = str(value)
        elif isinstance(value, (datetime.datetime, datetime.date)):
            value = value.isoformat()
        out[col.name] = value
    return out
