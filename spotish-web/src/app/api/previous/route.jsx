"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
  try {
        // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
        const res = await fetch(process.env.HOST_CONTROLLER+process.env.CONTROLLER_PORT +"/previous", {
        method: "POST",
        headers: {
        "Content-Type": "application/json"
        },
        body: JSON.stringify({a:"b"})
        });

        
        console.log(res);
        return NextResponse.json(res);
      } catch (error) {
        console.error("Erreur dans la route GET :", error);
        return NextResponse.json(
            { success: false, message: "Erreur serveur" },
            { status: 500 }
    );
  }
}