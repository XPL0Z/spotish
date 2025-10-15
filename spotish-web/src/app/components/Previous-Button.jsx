
"use client"; 

export default ({disabled}) => {
  // Fonction déclenchée au clic
  // const handleClick = async () => {
  //   const res = await fetch("/api/pause", {
  //     method: "POST",
  //   });

  //   const data = await res.json();
  //   console.log("Réponse backend :", data);
  // };


  return (
    <button
      // onClick={handleClick}
      className={`p-4 rounded rotate-180 ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
      disabled={disabled}
    >
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
  <path strokeLinecap="round" strokeLinejoin="round" d="M3 8.689c0-.864.933-1.406 1.683-.977l7.108 4.061a1.125 1.125 0 0 1 0 1.954l-7.108 4.061A1.125 1.125 0 0 1 3 16.811V8.69ZM12.75 8.689c0-.864.933-1.406 1.683-.977l7.108 4.061a1.125 1.125 0 0 1 0 1.954l-7.108 4.061a1.125 1.125 0 0 1-1.683-.977V8.69Z" />
</svg>
    </button>
  );
};