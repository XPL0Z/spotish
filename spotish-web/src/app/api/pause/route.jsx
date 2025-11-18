"use server";
import { NextResponse } from "next/server";

export async function POST(request) {
  try {
        // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
        console.log("Pause demandée !");
        Api_url = process.env.HOST_CONTROLLER+ +process.env.CONTROLLER_PORT +"/pause"
        const res = await fetch(Api_url, {
        method: "POST",          // <-- méthode POST
        headers: {
          "Content-Type": "application/json", // si tu envoies du JSON
        },
        body: JSON.stringify({ action: "pause" }), // corps de la requête
        }); 
        return NextResponse.json({
        success: true,
        message: "Action backend exécutée",
        });
    } catch (error) {
        console.error("Erreur dans la route POST :", error);
        return NextResponse.json(
            { success: false, message: "Erreur serveur" },
            { status: 500 }
    );
  }
}
