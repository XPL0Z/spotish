'use client';
import { useEffect } from "react";

export default function SearchResults({ tracks }) {
  useEffect(() => {
    console.log("🎵 SearchResults - tracks reçus:", tracks);
    if (!tracks || !tracks.length) {
      console.log("❌ Aucun track à afficher");
    }
  }, [tracks]);

  if (!tracks || !tracks.length) {
    return null;
  }

  const handleClick = async (link) => {
    try {
      await fetch("/api/addSong", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ author: "WEB", link: link })
      });
      console.log("✅ Chanson ajoutée :", link);
    } catch (err) {
      console.error("❌ Erreur lors de l'ajout:", err);
    }
  };

  return (
    <div className="mt-4 w-96 flex flex-col">
      {tracks.map(track => (
        <div 
          key={track.link} 
          className="flex items-center gap-2 mb-2 bg-gray-700 p-2 rounded hover:bg-gray-800 cursor-pointer transition-colors" 
          onClick={() => handleClick(track.link)}
        >
          <img
            src={track.cover} 
            alt={track.name} 
            className="w-12 h-12 object-cover rounded border-2 border-[#D216DA]" 
          />
          <div className="text-white">
            <span className="font-semibold">{track.name}</span>
            <br />
            <span className="text-gray-300 text-sm">{track.artist}</span>
          </div>
        </div>
      ))}
    </div>
  );
}