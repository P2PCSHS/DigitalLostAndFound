from sqlalchemy.orm import Mapped, mapped_column
import extensions
from datetime import datetime, timezone


class Item(extensions.db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column()
    description: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    claimed_at: Mapped[datetime | None] = mapped_column(default=None)

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "claimed_at": self.claimed_at.isoformat() if self.claimed_at else None,
        }
