"use server";
import { NextResponse } from "next/server";

export async function GET(request) {
  try {
        console.log("SECRETS :", process.env.HOST_CONTROLLER);
        let Api_url = process.env.HOST_CONTROLLER+process.env.CONTROLLER_PORT + "/infos";
        console.log("Appel à l'API infos :", Api_url);
        // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
        const res = await fetch(Api_url, {
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