import React, { useState, useRef, useEffect } from 'react';

/**
 * DraggableModal - A reusable modal wrapper that supports dragging and resizing
 * @param {boolean} isOpen - Whether the modal is visible
 * @param {function} onClose - Callback when modal is closed
 * @param {string} title - Modal title text
 * @param {React.ReactNode} children - Modal content
 * @param {string} className - Additional CSS classes for content area
 * @param {number} defaultWidth - Default width in pixels (default: 600)
 * @param {number} defaultHeight - Default height in pixels (default: 400)
 * @param {boolean} resizable - Whether the modal can be resized (default: true)
 */
const DraggableModal = ({
    isOpen,
    onClose,
    title,
    children,
    className = '',
    defaultWidth = 600,
    defaultHeight = 400,
    resizable = true
}) => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [size, setSize] = useState({ width: defaultWidth, height: defaultHeight });
    const [isDragging, setIsDragging] = useState(false);
    const [isResizing, setIsResizing] = useState(false);
    const [resizeDirection, setResizeDirection] = useState(null);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [centered, setCentered] = useState(true);

    const modalRef = useRef(null);

    // Center modal on first open
    useEffect(() => {
        if (isOpen && centered && modalRef.current) {
            const rect = modalRef.current.getBoundingClientRect();
            setPosition({
                x: (window.innerWidth - rect.width) / 2,
                y: (window.innerHeight - rect.height) / 2
            });
        }
    }, [isOpen, centered]);

    // Handle dragging
    const handleMouseDown = (e) => {
        if (e.target.closest('.resize-handle')) return;
        if (e.target.closest('.modal-content')) return;

        setCentered(false);
        setIsDragging(true);
        setDragStart({
            x: e.clientX - position.x,
            y: e.clientY - position.y
        });
    };

    // Handle resizing
    const handleResizeMouseDown = (e, direction) => {
        e.stopPropagation();
        setCentered(false);
        setIsResizing(true);
        setResizeDirection(direction);
        setDragStart({
            x: e.clientX,
            y: e.clientY,
            width: size.width,
            height: size.height,
            posX: position.x,
            posY: position.y
        });
    };

    useEffect(() => {
        if (!isDragging && !isResizing) return;

        const handleMouseMove = (e) => {
            if (isDragging) {
                const newX = e.clientX - dragStart.x;
                const newY = e.clientY - dragStart.y;

                // Keep within viewport bounds
                const maxX = window.innerWidth - size.width;
                const maxY = window.innerHeight - size.height;

                setPosition({
                    x: Math.max(0, Math.min(newX, maxX)),
                    y: Math.max(0, Math.min(newY, maxY))
                });
            } else if (isResizing) {
                const deltaX = e.clientX - dragStart.x;
                const deltaY = e.clientY - dragStart.y;

                let newWidth = dragStart.width;
                let newHeight = dragStart.height;
                let newX = position.x;
                let newY = position.y;

                // Calculate new size based on resize direction
                if (resizeDirection.includes('e')) {
                    newWidth = Math.max(300, Math.min(dragStart.width + deltaX, window.innerWidth - position.x));
                }
                if (resizeDirection.includes('w')) {
                    const widthChange = Math.min(deltaX, dragStart.width - 300);
                    newWidth = dragStart.width - widthChange;
                    newX = dragStart.posX + widthChange;
                }
                if (resizeDirection.includes('s')) {
                    newHeight = Math.max(200, Math.min(dragStart.height + deltaY, window.innerHeight - position.y));
                }
                if (resizeDirection.includes('n')) {
                    const heightChange = Math.min(deltaY, dragStart.height - 200);
                    newHeight = dragStart.height - heightChange;
                    newY = dragStart.posY + heightChange;
                }

                setSize({ width: newWidth, height: newHeight });
                setPosition({ x: newX, y: newY });
            }
        };

        const handleMouseUp = () => {
            setIsDragging(false);
            setIsResizing(false);
            setResizeDirection(null);
        };

        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, isResizing, dragStart, position, size, resizeDirection]);

    // Handle ESC key
    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape' && isOpen) {
                onClose();
            }
        };

        if (isOpen) {
            document.addEventListener('keydown', handleKeyDown);
            return () => document.removeEventListener('keydown', handleKeyDown);
        }
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    const modalStyle = centered ? {
        width: `${size.width}px`,
        maxHeight: `${size.height}px`
    } : {
        position: 'fixed',
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: `${size.width}px`,
        height: `${size.height}px`,
        margin: 0
    };

    return (
        <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md animate-fadeIn"
            onClick={onClose}
        >
            <div
                ref={modalRef}
                className={`bg-disco-panel border-2 border-disco-muted/50 rounded-lg shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden ${centered ? '' : 'flex flex-col'}`}
                style={modalStyle}
                onClick={e => e.stopPropagation()}
            >
                {/* Title Bar - Draggable */}
                <div
                    className="bg-disco-dark/60 border-b border-disco-muted/30 px-6 py-3 cursor-move select-none flex items-center justify-between"
                    onMouseDown={handleMouseDown}
                >
                    <h2 className="font-serif text-xl text-disco-paper uppercase tracking-[0.2em]">
                        {title}
                    </h2>
                    <button
                        onClick={onClose}
                        className="text-disco-muted hover:text-disco-paper transition-colors font-mono text-sm px-2"
                    >
                        [ ESC ]
                    </button>
                </div>

                {/* Content Area */}
                <div className={`modal-content flex-1 overflow-auto ${className}`}>
                    {children}
                </div>

                {/* Resize Handles */}
                {resizable && !centered && (
                    <>
                        {/* Corner Handles */}
                        <div
                            className="resize-handle absolute top-0 left-0 w-4 h-4 cursor-nw-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'nw')}
                        />
                        <div
                            className="resize-handle absolute top-0 right-0 w-4 h-4 cursor-ne-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'ne')}
                        />
                        <div
                            className="resize-handle absolute bottom-0 left-0 w-4 h-4 cursor-sw-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'sw')}
                        />
                        <div
                            className="resize-handle absolute bottom-0 right-0 w-4 h-4 cursor-se-resize bg-disco-cyan/20 hover:bg-disco-cyan/40 transition-colors"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'se')}
                        >
                            <div className="absolute bottom-0 right-0 w-3 h-3 border-r-2 border-b-2 border-disco-cyan/60" />
                        </div>

                        {/* Edge Handles */}
                        <div
                            className="resize-handle absolute top-0 left-4 right-4 h-1 cursor-n-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'n')}
                        />
                        <div
                            className="resize-handle absolute bottom-0 left-4 right-4 h-1 cursor-s-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 's')}
                        />
                        <div
                            className="resize-handle absolute left-0 top-4 bottom-4 w-1 cursor-w-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'w')}
                        />
                        <div
                            className="resize-handle absolute right-0 top-4 bottom-4 w-1 cursor-e-resize"
                            onMouseDown={(e) => handleResizeMouseDown(e, 'e')}
                        />
                    </>
                )}
            </div>
        </div>
    );
};

export default DraggableModal;
