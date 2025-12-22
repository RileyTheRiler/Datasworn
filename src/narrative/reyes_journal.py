"""
Captain Marcus Reyes's Journal System.
Stores and retrieves fragments of the captain's inner thoughts.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class EntryId(str, Enum):
    DYING = "dying"
    YUKI_DISCOVERY = "yuki_discovery"
    YUKI_CHOICE = "yuki_choice"
    DEADLINE = "deadline"
    PEACE = "peace"

@dataclass
class JournalEntry:
    id: str
    title: str
    content: str
    time_period: str # e.g., "Six months before death"

JOURNAL_ENTRIES: Dict[EntryId, JournalEntry] = {
    EntryId.DYING: JournalEntry(
        id=EntryId.DYING.value,
        title="Journal Entry 1",
        time_period="Six months before death",
        content=(
            "The crew doesn't know I'm dying. I want to tell them, but I'm afraid of how they'll look at me. "
            "Torres will become overprotective. Kai will spiral. Dr. Okonkwo already carries too much of my burden.\n\n"
            "Better they remember me as I was, not as I'm becoming."
        )
    ),
    EntryId.YUKI_DISCOVERY: JournalEntry(
        id=EntryId.YUKI_DISCOVERY.value,
        title="Journal Entry 2",
        time_period="Three months before death",
        content=(
            "I found out about Yuki today. What she did for the company. Who she really is.\n\n"
            "My first instinct was to put her off the ship. But that's not who I am. I believe in second chances—I've built my life on them.\n\n"
            "The question is whether she believes. Whether she can own what she did and become someone else."
        )
    ),
    EntryId.YUKI_CHOICE: JournalEntry(
        id=EntryId.YUKI_CHOICE.value,
        title="Journal Entry 3",
        time_period="One month before death",
        content=(
            "I gave Yuki a choice. Confess or face exposure. I thought I was being merciful.\n\n"
            "Maria would have told me I was being controlling. That redemption can't be forced. "
            "That I always need to be the one who saves people, even when they don't ask.\n\n"
            "Maybe she's right. Maybe I'm wrong. But I don't have time to be patient anymore."
        )
    ),
    EntryId.DEADLINE: JournalEntry(
        id=EntryId.DEADLINE.value,
        title="Journal Entry 4",
        time_period="One week before death",
        content=(
            "Yuki hasn't come to me. The deadline is approaching. I'm not sure what I'll do.\n\n"
            "Part of me hopes she'll surprise me. That she'll come to me with honesty and we'll figure it out together.\n\n"
            "But another part of me... another part of me knows how this might end. And I'm not sure I can stop it."
        )
    ),
    EntryId.PEACE: JournalEntry(
        id=EntryId.PEACE.value,
        title="Journal Entry 5",
        time_period="The day before death",
        content=(
            "I'm at peace. Whatever happens tomorrow.\n\n"
            "I've lived a good life. Made mistakes. Hurt people, even when I was trying to help. "
            "But I tried. I tried to give people second chances.\n\n"
            "That has to count for something.\n\n"
            "Maria, I'll see you soon."
        )
    )
}

class ReyesJournalSystem:
    @staticmethod
    def get_entry(entry_id: str) -> Optional[JournalEntry]:
        """Retrieve a specific entry by ID."""
        return JOURNAL_ENTRIES.get(EntryId(entry_id))

    @staticmethod
    def get_all_entries() -> List[JournalEntry]:
        """Retrieve all entries in chronological order."""
        return [
            JOURNAL_ENTRIES[EntryId.DYING],
            JOURNAL_ENTRIES[EntryId.YUKI_DISCOVERY],
            JOURNAL_ENTRIES[EntryId.YUKI_CHOICE],
            JOURNAL_ENTRIES[EntryId.DEADLINE],
            JOURNAL_ENTRIES[EntryId.PEACE]
        ]
