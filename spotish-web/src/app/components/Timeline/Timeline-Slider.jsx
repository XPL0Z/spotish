"use client"

import { useEffect } from "react";

export default ({ setTimecode, timecode, duration }) => {

    const handleChange = async (event) => {
        const newValue = event.target.value;
        fetch("/api/timecode", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ timecode: event.target.value }) // ✅ Envoyer le timecode
        });
        setTimecode(newValue); // ✅ UI instantanée
    };
    return (
        <input
            type="range"
            className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer dark:bg-gray-700 accent-[#D216DA]"
            min="0"
            max={duration}
            value={timecode}
            onChange={handleChange}
        />
    );
};