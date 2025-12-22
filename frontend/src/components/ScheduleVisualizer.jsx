import React, { useState, useEffect } from 'react';
import api from '../utils/api';

/**
 * ScheduleVisualizer - Visualizes an NPC's daily schedule
 * 
 * Features:
 * - Timeline view of tasks
 * - Highlights current task
 * - Shows interruptions
 * - Tooltips for task details
 */
const ScheduleVisualizer = ({ npcId, scheduleData, className = "" }) => {
    const [schedule, setSchedule] = useState(scheduleData || null);
    const [loading, setLoading] = useState(!scheduleData);
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        if (npcId && !scheduleData) {
            fetchSchedule();
        }
    }, [npcId, scheduleData]);

    const fetchSchedule = async () => {
        try {
            setLoading(true);
            const data = await api.get(`/npc/schedule/${npcId}`);
            setSchedule(data);
        } catch (err) {
            console.error("Failed to fetch schedule:", err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className={`flex items-center justify-center p-8 ${className}`}>
                <div className="w-6 h-6 border-2 border-disco-cyan border-t-transparent rounded-full animate-spin"></div>
            </div>
        );
    }

    if (!schedule || !schedule.tasks) {
        return (
            <div className={`text-disco-muted italic p-4 text-center ${className}`}>
                No active schedule found for this NPC.
            </div>
        );
    }

    // Sort tasks by time
    const sortedTasks = [...schedule.tasks].sort((a, b) => {
        const timeA = parseInt(a.time.replace(':', ''));
        const timeB = parseInt(b.time.replace(':', ''));
        return timeA - timeB;
    });

    const currentTaskIndex = schedule.current_task_index;
    const isInterrupted = !!schedule.active_interruption;

    return (
        <div className={`bg-black/20 rounded-lg p-4 border border-disco-muted/20 ${className}`}>
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-sm font-mono text-disco-cyan uppercase tracking-wider">
                    Daily Routine
                    {schedule.archetype && <span className="text-disco-muted ml-2">({schedule.archetype})</span>}
                </h3>
                {isInterrupted && (
                    <span className="text-xs bg-disco-red/20 text-disco-red px-2 py-1 rounded border border-disco-red/30 animate-pulse">
                        ⚠ INTERRUPTED
                    </span>
                )}
            </div>

            <div className="relative pl-4 border-l border-disco-muted/20 space-y-6">
                {sortedTasks.map((task, index) => {
                    const isActive = index === currentTaskIndex;
                    const isPast = index < currentTaskIndex;

                    return (
                        <div key={index} className={`relative group ${isActive ? 'opacity-100' : 'opacity-60 hover:opacity-100 transition-opacity'}`}>
                            {/* Timeline Dot */}
                            <div className={`absolute -left-[21px] top-1 w-3 h-3 rounded-full border-2 
                                ${isActive ? 'bg-disco-cyan border-disco-cyan shadow-[0_0_10px_rgba(0,255,255,0.5)]' :
                                    isPast ? 'bg-disco-muted border-disco-muted' : 'bg-transparent border-disco-muted'} 
                                transition-all`}
                            />

                            {/* Time & Location */}
                            <div className="flex justify-between items-baseline mb-1">
                                <span className={`font-mono text-xs ${isActive ? 'text-disco-cyan' : 'text-disco-muted'}`}>
                                    {task.time}
                                </span>
                                <span className="text-[10px] text-disco-muted/70 uppercase tracking-wide">
                                    {task.location}
                                </span>
                            </div>

                            {/* Task Content */}
                            <div className={`p-3 rounded border text-sm
                                ${isActive
                                    ? 'bg-disco-cyan/10 border-disco-cyan/30 text-disco-paper'
                                    : 'bg-black/20 border-disco-muted/20 text-disco-paper/70'}
                            `}>
                                <div className="font-bold mb-1">{task.behavior}</div>
                                <div className="text-xs italic opacity-80">{task.description}</div>

                                {isActive && isInterrupted && schedule.active_interruption && (
                                    <div className="mt-2 pt-2 border-t border-disco-red/30 text-xs text-disco-red">
                                        <span className="font-bold uppercase">Current Action:</span> {schedule.active_interruption.behavior}
                                        <br />
                                        <span className="italic">Reason: {schedule.active_interruption.reason}</span>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default ScheduleVisualizer;
