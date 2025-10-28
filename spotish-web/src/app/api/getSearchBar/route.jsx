// ✅ Forcer l’exécution côté Node.js (pas Edge)
export const runtime = "nodejs";

import { NextResponse } from "next/server";

// ✅ Handler GET
export async function GET(request) {
  const q = new URL(request.url).searchParams.get("q");

  if (!q) {
    return NextResponse.json({ error: "Le paramètre 'q' est requis." }, { status: 400 });
  }

  try {
    // 1️⃣ Récupérer un access token avec le flow Client Credentials
    const tokenRes = await fetch("https://accounts.spotify.com/api/token", {
      method: "POST",
      headers: {
        Authorization:
          "Basic " +
          Buffer.from(
            process.env.CLIENT_ID + ":" + process.env.CLIENT_SECRET
          ).toString("base64"),
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
      cache: "no-store",
    });

    if (!tokenRes.ok) {
      const text = await tokenRes.text();
      throw new Error("Erreur lors de la récupération du token : " + text);
    }

    const { access_token } = await tokenRes.json();

    // 2️⃣ Appeler l’API Spotify pour la recherche
    const searchRes = await fetch(
      `https://api.spotify.com/v1/search?q=${encodeURIComponent(q)}&type=track&limit=5`,
      {
        headers: { Authorization: `Bearer ${access_token}` },
        cache: "no-store",
      }
    );

    if (!searchRes.ok) {
      const text = await searchRes.text();
      throw new Error("Erreur de recherche Spotify : " + text);
    }

    const data = await searchRes.json();
    // 3️⃣ Retourner les résultats
    const tracks = data.tracks.items.map((track) => ({
    name: track.name,
    artist: track.artists.map((a) => a.name).join(", "),
    cover: track.album.images[0]?.url || null,
    duration_ms: track.duration_ms,
    link: track.external_urls.spotify,
  }));
    console.log(tracks)
    return NextResponse.json(tracks);
  } catch (error) {
    console.error("Erreur Spotify :", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
