'use client';

export default function SearchBar({ setTracks, author }) {
  const changeresult = async (e) => {
    const value = e.target.value;

    if (!value) {
      setTracks([]);
      return;
    }

    try {
      const res = await fetch("/api/getSearchBar?q=" + encodeURIComponent(value));
      const data = await res.json();
      setTracks(data);
    } catch (err) {
      console.error("Erreur fetch:", err);
    }
  };

  const handleKeyDown = async (event) => {
    if (event.key === 'Enter') {
      const value = event.target.value;
      console.log("Envoi de la requête pour le lien :", value);

      await fetch("/api/addSong", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ author: author, link: value })
      });

      event.target.value = ""; // vider l'input
      setTracks([]); // vider les résultats
    }
  };

  return (
    <input
      type="text"
      className="w-96 h-10 px-4 rounded-full bg-gray-800 text-white placeholder-white focus:outline-none focus:ring-2 focus:ring-[#D216DA]"
      placeholder="enter a link and press Enter to add a song"
      onChange={changeresult}
      onKeyDown={handleKeyDown}
    />
  );
}