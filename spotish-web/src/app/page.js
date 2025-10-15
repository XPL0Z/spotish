"use client"
import { useEffect, useState } from "react";
import PauseButton from "./components/Pause-Button";
import ResumeButton from "./components/Resume-Button";

export default function Home() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [data, setData] = useState(null); // obligatoire pour stocker les données et acceder dans le render au data.status
  const Getinfos = async () => {
    const res = await fetch("/api/infos", {
      method: "GET",
    });

    const data = await res.json();
    console.log("Réponse backend :", data);
    console.log(data.status)

    setIsPlaying(data.status != isPlaying ? data.status : isPlaying)  // Met à jour isPlaying seulement si le status a changé;
  };
  useEffect(()=>{
  const interval = setInterval(() => {
    Getinfos();

  }, 1000) // Log toutes les 1000ms (1 seconde)
  return () => clearInterval(interval) // Nettoie l'intervalle au démontage
}, [])

  return (

    <main className="flex flex-col items-center justify-center min-h-screen space-y-6">

      <div className="flex space-x-8">
      {
        isPlaying ? <ResumeButton setter={setIsPlaying} /> : <PauseButton setter={setIsPlaying} />
      }
      {/* <IsPlaying status={data?.status} /> */}
      {/* le ? est pour vérifier si status existe avant d'accéder à status */}
      </div>

    </main>
  
  );
}
