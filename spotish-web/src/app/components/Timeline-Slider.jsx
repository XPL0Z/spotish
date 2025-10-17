"use client"

export default ({setTimecode, timecode, duration} ) => {
 

    const handleChange = (event) => {
        
        const newValue = event.target.value;

        setTimecode(newValue); // ✅ UI instantanée
    // Envoyer à l'API Next.js
    fetch("/api/timecode", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ timecode: timecode }) // ✅ Envoyer le timecode
    });
    }
  
    
    return (
           <input   
            type="range" 
            className="w-full h-2 bg-gray-200 rounded-lg cursor-pointer dark:bg-gray-700 accent-[#D216DA]"
            min="0" 
            max={duration}  
            value={timecode}
            onChange={handleChange}
            />
    );
};