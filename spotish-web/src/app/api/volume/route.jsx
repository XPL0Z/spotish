"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
  try {
        // ✅ Parser le body JSON
        const body = await request.json();
        const { volume } = body;
        
        console.log("Volume reçu:", volume);
        
        // Appel à ton backend Python/Flask
        const res = await fetch(process.env.HOST_CONTROLLER+process.env.CONTROLLER_PORT +"/volume", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ newvolume: volume })
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