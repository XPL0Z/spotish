"use server";
import { NextResponse } from "next/server";

export async function GET(request) {
  try {
        // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
        const res = await fetch("http://127.0.0.1:5000/infos", {
        });

        const data = await res.json();
        console.log("Données reçues :", data);
        return NextResponse.json(data);
    } catch (error) {
        console.error("Erreur dans la route GET :", error);
        return NextResponse.json(
            { success: false, message: "Erreur serveur" },
            { status: 500 }
    );
  } 
}     