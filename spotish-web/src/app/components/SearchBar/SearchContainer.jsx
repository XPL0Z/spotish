'use client';
import { useState } from "react";
import SearchBar from "./SearchBar";
import SearchResult from "./SearchResult";

export default function SearchContainer() {
  const [tracks, setTracks] = useState([]);

  return (
    <div className="flex flex-col items-center">
      <SearchBar setTracks={setTracks} />
      <SearchResult tracks={tracks || []} />
    </div>
  );
}
