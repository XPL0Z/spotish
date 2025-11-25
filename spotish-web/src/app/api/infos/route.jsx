"use server";
import { NextResponse } from "next/server";

export async function GET(request) {
  try {
    const Api_url = process.env.HOST_CONTROLLER + process.env.CONTROLLER_PORT + "/infos";
    // Ici, ton code backend (pause une action, enregistrer en DB, etc.)
    const res = await fetch(Api_url, {
    });

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Erreur dans la route GET :", error);
    return NextResponse.json(
      { success: false, message: "Erreur serveur" },
      { status: 500 }
    );
  }
}     