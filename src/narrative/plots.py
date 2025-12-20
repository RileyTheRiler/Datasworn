"""
Parallel Plot Threads.

This module manages multiple concurrent storylines (A-Plot, B-Plot, Character Arcs),
allowing the narrator to switch focus and keep the world feeling alive.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class PlotType(Enum):
    MAIN_ARC = "A-Plot"
    SUB_PLOT = "B-Plot"
    CHARACTER_ARC = "C-Plot"
    BACKGROUND_EVENT = "Background"

@dataclass
class PlotThread:
    """A single narrative thread."""
    thread_id: str
    title: str
    plot_type: PlotType
    description: str
    active: bool = True
    resolved: bool = False
    scene_count: int = 0  # How many scenes have focused on this?
    last_scene_index: int = -1 # When was this last touched?

@dataclass
class PlotManager:
    """
    Orchestrates multiple plot threads.
    """
    threads: Dict[str, PlotThread] = field(default_factory=dict)
    active_thread_id: Optional[str] = None
    
    def create_thread(self, thread_id: str, title: str, 
                     plot_type: PlotType, description: str):
        self.threads[thread_id] = PlotThread(
            thread_id=thread_id,
            title=title,
            plot_type=plot_type,
            description=description
        )
        if not self.active_thread_id and plot_type == PlotType.MAIN_ARC:
            self.active_thread_id = thread_id

    def advance_plot(self, thread_id: str, current_scene: int):
        """
        Mark a plot as being advanced in the current scene.
        """
        if thread_id in self.threads:
            self.threads[thread_id].scene_count += 1
            self.threads[thread_id].last_scene_index = current_scene
            self.active_thread_id = thread_id

    def suggest_next_thread(self, current_scene: int) -> Optional[PlotThread]:
        """
        Suggest which plot thread to focus on next.
        """
        if not self.threads:
            return None
            
        # Basic logic: If A-Plot has been focus for 3+ scenes, switch to B-Plot
        
        main_arc = next((t for t in self.threads.values() if t.plot_type == PlotType.MAIN_ARC), None)
        sub_plots = [t for t in self.threads.values() if t.plot_type != PlotType.MAIN_ARC and t.active and not t.resolved]
        
        if main_arc and main_arc.last_scene_index == current_scene:
            # We just did main arc
            # If we did it for a long time? (Not tracking consecutive yet, but assume variety is good)
            if sub_plots:
                 # Suggest a B-plot
                 # Sort by "staleness" (longest time since update)
                 sub_plots.sort(key=lambda t: t.last_scene_index)
                 return sub_plots[0]
                 
        # Default back to Main Arc if available
        return main_arc 

    def to_dict(self) -> dict:
        return {
            "threads": {
                tid: {
                    "thread_id": t.thread_id,
                    "title": t.title,
                    "plot_type": t.plot_type.value,
                    "description": t.description,
                    "active": t.active,
                    "resolved": t.resolved,
                    "scene_count": t.scene_count,
                    "last_scene_index": t.last_scene_index
                }
                for tid, t in self.threads.items()
            },
            "active_thread_id": self.active_thread_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlotManager":
        manager = cls()
        manager.active_thread_id = data.get("active_thread_id")
        for tid, t_data in data.get("threads", {}).items():
            manager.threads[tid] = PlotThread(
                thread_id=t_data["thread_id"],
                title=t_data["title"],
                plot_type=PlotType(t_data["plot_type"]),
                description=t_data["description"],
                active=t_data["active"],
                resolved=t_data["resolved"],
                scene_count=t_data.get("scene_count", 0),
                last_scene_index=t_data.get("last_scene_index", -1)
            )
        return manager
