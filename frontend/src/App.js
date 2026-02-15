import React from "react";
import OfficerForm from "./components/OfficerForm";
import CounterGridLive from "./components/CounterGridLive";

export default function App() {
    return (
        <div className="p-4">
            <h1 className="text-2xl font-bold mb-4">Dynamic Counter Dashboard</h1>
            <OfficerForm />
            <CounterGridLive />
        </div>
    );
}
