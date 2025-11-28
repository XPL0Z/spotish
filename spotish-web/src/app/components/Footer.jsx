"use client";
import ResumeButton from "./PlayerControls/Resume-Button";
import PauseButton from "./PlayerControls/Pause-Button";
import ActualSongContainer from "./ActualSong/ActualSong-Container";
import TimelineContainer from "./Timeline/Timeline-Container";
import TrackNavigator from "./PlayerControls/TrackNavigator";
import VolumeContainer from "./VolumeControls/Volume-Container";
import { useEffect, useState } from "react";

export default ({ author }) => {
  const [volume, setVolume] = useState(70);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [timecode, setTimecode] = useState(0);
  const [cover, setCover] = useState("https://github.com/XPL0Z/spotish/blob/main/images/spotish_icon_logo_no_bg.png?raw=true");
  const [name, setName] = useState("Loading...");
  const [artist, setArtist] = useState("Loading...");
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
    setName(data.name);
    setCover(data.cover);
    setArtist(data.artist);  // Met
    setIsPlaying(data.paused != isPlaying ? isPlaying : data.paused)  // Met à jour isPlaying seulement si le status a changé;
  };
  useEffect(() => {
    const interval = setInterval(() => {
      Getinfos();

    }, 1000) // Log toutes les 1000ms (1 seconde)
    return () => clearInterval(interval) // Nettoie l'intervalle au démontage
  }, [])

  return (
    <div className="flex justify-center fixed bottom-0 w-full h-24 bg-black bg-opacity-70 backdrop-blur-md text-white space-x-8 items-center px-4 mb-2.5">

      <ActualSongContainer author={artist} link={cover} title={name} />

      <div className="flex flex-col items-center justify-center w-full ">

        <div className="flex ">

          <TrackNavigator className="rotate-180" api="previous" author={author} />

          {
            isPlaying ? <ResumeButton setter={setIsPlaying} author={author} /> : <PauseButton setter={setIsPlaying} author={author} />
          }

          <TrackNavigator api="skip" author={author} />

        </div>

        <TimelineContainer setTimecode={setTimecode} timecode={timecode} duration={duration} author={author} />

      </div>

      <VolumeContainer setter={setVolume} value={volume} author={author} />

    </div>
  );
};