"use client"
import { useEffect, useState } from "react";
import PauseButton from "./components/PlayerControls/Pause-Button";
import ResumeButton from "./components/PlayerControls/Resume-Button";
import VolumeContainer from "./components/VolumeControls/Volume-Container";
import TimelineContainer from "./components/Timeline/Timeline-Container";
import TrackNavigator from "./components/PlayerControls/TrackNavigator";
import ActualSongContainer from "./components/ActualSong/ActualSong-Container";

export default function Home() {
  const [volume, setVolume] = useState(70);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration,setDuration] = useState(0);
  const [timecode, setTimecode] = useState(0);
  const [cover, setCover] = useState(null);
  const [name, setName] = useState(null);
  const [artist, setArtist] = useState(null);
  const [data, setData] = useState(null); // obligatoire pour stocker les données et acceder dans le render au data.status
  const Getinfos = async () => {
    const res = await fetch("/api/infos", {
      method: "GET",
    });

    const data = await res.json();
    console.log(data);
    setVolume(data.volume);
    setDuration(data.length);
    setTimecode(Number(data.timecode));
    setCover(data.cover);
    setName(data.name);
    setArtist(data.artist);
    setIsPlaying(data.paused != isPlaying ? data.paused : isPlaying)  // Met à jour isPlaying seulement si le status a changé;
  };
  useEffect(()=>{
  const interval = setInterval(() => {
    Getinfos();

  }, 1000) // Log toutes les 1000ms (1 seconde)
  return () => clearInterval(interval) // Nettoie l'intervalle au démontage
}, [])

  return (
// className="flex flex-col items-center justify-center min-h-screen space-y-6"
    <main className="flex items-center justify-center min-h-screen">
      
      <ActualSongContainer author={artist} link={cover} title={name}/>
      
      <div className="flex flex-col items-center justify-center w-full ">

        <div className="flex ">

          <TrackNavigator className="rotate-180" api="previous"/>

          {
            isPlaying ?  <ResumeButton setter={setIsPlaying} />: <PauseButton setter={setIsPlaying} />
          }

          <TrackNavigator api={"skip"}/>
        
        </div>

        <TimelineContainer setTimecode={setTimecode} timecode={timecode} duration={duration}/>
 
      </div>

      <VolumeContainer setter={setVolume} value={volume}/>

    </main>
  
  );
}
