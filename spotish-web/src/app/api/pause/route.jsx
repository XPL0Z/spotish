import { NextResponse } from "next/server";

export async function POST(request) {
  try {
    const body = await request.json();
    const { author } = body;

    console.log("Author reçu :", author);

    if (!author) {
      return NextResponse.json(
        { success: false, message: "Author manquant" },
        { status: 400 }
      );
    }

    const Api_url = `${process.env.HOST_CONTROLLER}${process.env.CONTROLLER_PORT}/pause`;

    const res = await fetch(Api_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // ✅ Envoie directement la valeur string
      body: JSON.stringify(author), // ou juste: body: author
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Erreur API :", res.status, errorText);
      return NextResponse.json(
        { success: false, message: errorText },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json({ success: true, data });

  } catch (error) {
    console.error("Erreur dans la route POST :", error);
    return NextResponse.json(
      { success: false, message: error.message },
      { status: 500 }
    );
  }
}