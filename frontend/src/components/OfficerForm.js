import React, { useState } from "react";

export default function OfficerForm() {
    const [id, setId] = useState("");
    const [name, setName] = useState("");
    const [type, setType] = useState("SOS");
    const [start, setStart] = useState("");
    const [end, setEnd] = useState("");
    const [RA, setRA] = useState("");
    const [RO, setRO] = useState("");

    const addOfficer = () => {
        fetch("http://localhost:8000/officer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                id: parseInt(id),
                name,
                type,
                start_time: start,
                end_time: end,
                actual_arrival: RA || start,
                actual_leave: RO || end
            })
        });
    };

    return (
        <div className="mb-4 flex gap-2">
            <input placeholder="ID" value={id} onChange={e => setId(e.target.value)} />
            <input placeholder="Name" value={name} onChange={e => setName(e.target.value)} />
            <select value={type} onChange={e => setType(e.target.value)}>
                <option value="SOS">SOS</option>
                <option value="OT">OT</option>
                <option value="regular">Regular</option>
            </select>
            <input type="datetime-local" value={start} onChange={e => setStart(e.target.value)} />
            <input type="datetime-local" value={end} onChange={e => setEnd(e.target.value)} />
            <input type="datetime-local" placeholder="RA" value={RA} onChange={e => setRA(e.target.value)} />
            <input type="datetime-local" placeholder="RO" value={RO} onChange={e => setRO(e.target.value)} />
            <button onClick={addOfficer} className="bg-blue-500 text-white px-2 rounded">Add/Update</button>
        </div>
    );
}
