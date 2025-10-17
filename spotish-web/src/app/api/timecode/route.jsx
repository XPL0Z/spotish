"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
  try {
        // ✅ Parser le body JSON
        const body = await request.json();
        const { timecode } = body;
        
        console.log("timecode reçu:", timecode);
        
        // Appel à ton backend Python/Flask
        const res = await fetch("http://127.0.0.1:7000/timecode", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ timecode: timecode})
        });

        // ✅ Parser la réponse aussi
        const data = await res.json();
        
        console.log("Réponse backend:", data);
        return NextResponse.json({ success: true, data });
        
  } catch (error) {
        console.error("Erreur dans la route POST:", error);
        return NextResponse.json(
            { success: false, message: "Erreur serveur" },
            { status: 500 }
        );
  }
}