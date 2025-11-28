"use server";

import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    // ✅ Parser le body JSON
    const body = await request.json();
    const { timecode } = body;
    const { author } = body;
    console.log("timecode reçu:", timecode);
    console.log("Author reçu:", author);

    // Appel à ton backend Python/Flask
    const res = await fetch(process.env.HOST_PLAYER + process.env.PLAYER_PORT + "/timecode", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ timecode: timecode, author: author })
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