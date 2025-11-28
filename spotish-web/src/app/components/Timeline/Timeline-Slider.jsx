"use client"

import { useEffect } from "react";

export default ({ setTimecode, timecode, duration, author }) => {
    console.log("Author envoyé:", author);
    const handleChange = async (event) => {
        console.log("Author envoyé:", author);
        const newValue = event.target.value;
        fetch("/api/timecode", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ timecode: event.target.value, author: author }) // ✅ Envoyer le timecode
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