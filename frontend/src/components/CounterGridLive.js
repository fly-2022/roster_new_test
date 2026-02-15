import React, { useEffect, useState } from "react";

export default function CounterGridLive() {
    const [schedule, setSchedule] = useState({});

    useEffect(() => {
        const ws = new WebSocket("ws://localhost:8000/ws");

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setSchedule(data);
        };

        return () => ws.close();
    }, []);

    return (
        <div className="overflow-auto max-h-screen grid grid-cols-6 gap-2 p-4">
            {Object.entries(schedule).map(([counter, officer]) => (
                <div key={counter} className={`p-2 border rounded text-center ${officer.officer
                        ? officer.type === "regular" ? "bg-green-200"
                            : officer.type === "OT" ? "bg-blue-200"
                                : "bg-orange-200"
                        : "bg-red-200"
                    }`}>
                    <p>{counter}</p>
                    <p>{officer.officer || "Vacant"}</p>
                </div>
            ))}
        </div>
    );
}
