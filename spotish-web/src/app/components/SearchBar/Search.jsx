'use client';
import {  useState } from "react";

export default () => {
    const [research, setResearch] = useState("");
    const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
        console.log("Envoi de la requete pour le lien : "+research)
        setResearch("");
      fetch("/api/addSong", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ author: "WEB", link: research }) // ✅ Envoyer le volume
    });
    }};
    
    return(
    
        <input
            type="text"
            className="w-96 h-10 px-4 rounded-full bg-gray-800 text-white placeholder-white focus:outline-none focus:ring-2 focus:ring-[#D216DA]"
            placeholder="enter a link and press Enter to add a song"
            value={research}
            onChange={(e) => setResearch(e.target.value)}
            onKeyDown={handleKeyDown}
        />
        
    );
};