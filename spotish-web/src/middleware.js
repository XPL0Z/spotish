import { NextResponse } from "next/server";
import { auth } from "@/auth";

// Seule la racine est protégée
const protectedRoutes = ["/"];

export default async function middleware(request) {
    const session = await auth();
    const { pathname } = request.nextUrl;

    // Vérifie uniquement la racine
    const isProtected = protectedRoutes.includes(pathname);

    if (isProtected && !session) {
        // Redirige vers la page de connexion si non connecté
        return NextResponse.redirect(new URL("/login", request.url));
    }

    return NextResponse.next();
}
