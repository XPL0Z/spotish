"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
    try {
        // ✅ Parser le body JSON et récupérer link ET author
        const body = await request.json();
        const { author, link } = body; // ✅ Récupérer les bonnes variables
        
        console.log("Données reçues:", { author, link });
        
        // Appel à ton backend Python/Flask
        const res = await fetch("http://127.0.0.1:5000/addSong", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ author, link }) // ✅ Utiliser les variables du body
        });

        // ✅ Parser la réponse
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