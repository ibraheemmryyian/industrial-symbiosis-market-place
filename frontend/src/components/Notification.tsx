import React from 'react';

interface NotificationProps {
    message: string;
    onClose: () => void;
}

export function Notification({ message, onClose }: NotificationProps) {
    return (
        <div className="fixed top-4 right-4 bg-white shadow-lg rounded-lg p-4">
            <p>{message}</p>
            <button onClick={onClose} className="text-red-500">Close</button>
        </div>
    );
} 