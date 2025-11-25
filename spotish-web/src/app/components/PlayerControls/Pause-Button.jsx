"use client";

export default ({ setter }) => {
  // Fonction déclenchée au clic
  const handleClick = async () => {
    const res = await fetch("/api/pause", {
      method: "POST",
    });

    const data = await res.json();
    console.log("Réponse backend :", data);
    setter(false);
  };

  return (
    <button
      id="pause-button"
      onClick={handleClick}
      className="p-4 rounded "
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-10">
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 5.25v13.5m-7.5-13.5v13.5" />
      </svg>
    </button>
  );
};