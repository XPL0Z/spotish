"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
  try {
        // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
        const res = await fetch("http://127.0.0.1:5000/skip", {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
        body: JSON.stringify({a:"b"})
        });

        
        console.log("Données reçues :", res);
        return NextResponse.json(res);
      } catch (error) {
        console.error("Erreur dans la route GET :", error);
        return NextResponse.json(
            { success: false, message: "Erreur serveur" },
            { status: 500 }
    );
  }
}