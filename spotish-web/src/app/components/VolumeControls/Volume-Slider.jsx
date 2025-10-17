"use client"

export default ( {setter, value} ) => {
 

    const handleChange = (event) => {
    const newValue = event.target.value;
    setter(newValue); // ✅ UI instantanée
    
    // Envoyer à l'API Next.js
    fetch("/api/volume", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ volume: newValue }) // ✅ Envoyer le volume
    });
}
  
    
    return (
            <input
                onChange={handleChange}
                type="range" 
                min="0" 
                max="100" 
                value={value} 
                className="accent-[#D216DA] w-full h-2 bg-gray-200 rounded-lg cursor-pointer dark:bg-gray-700"
            />
    );
};