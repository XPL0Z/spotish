'use client';
import { useEffect } from "react";
import { Toaster, toast } from "sonner";
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
    <div className="absolute top-full mt-2 w-96 flex flex-col max-h-96 overflow-y-auto bg-gray-900 rounded-lg shadow-xl z-50">
      <Toaster position="bottom-right" />
      {tracks.map(track => (
        <div 
          key={track.link} 
          className="flex items-center gap-2 p-2 rounded-lg border-2 border-transparent hover:bg-gray-800 hover:border-[#D216DA] cursor-pointer transition-all" 
          onClick={() => {
            handleClick(track.link)
            toast(`Added: ${track.name} by ${track.artist}`);
          }}>
          <img
            src={track.cover} 
            alt={track.name} 
            className="w-12 h-12 object-cover rounded" 
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