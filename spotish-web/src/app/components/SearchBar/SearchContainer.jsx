'use client';
import { useState } from "react";
import SearchBar from "./SearchBar";
import SearchResults from "./SearchResults";

export default function SearchContainer({ author, className }) {
  const [tracks, setTracks] = useState([]);
  return (
    <div className={`relative flex flex-col items-center${className ? ` ${className}` : ""}`}>
      <SearchBar setTracks={setTracks} author={author} />
      <SearchResults tracks={tracks || []} author={author} />
    </div>
  );
}