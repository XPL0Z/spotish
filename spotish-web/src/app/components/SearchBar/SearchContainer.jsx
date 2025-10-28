'use client';
import { useState } from "react";
import SearchBar from "./SearchBar";
import SearchResults from "./SearchResults";

export default function SearchContainer() {
  const [tracks, setTracks] = useState([]);

  return (
    <div className="relative flex flex-col items-center">
      <SearchBar setTracks={setTracks} />
      <SearchResults tracks={tracks || []} />
    </div>
  );
}