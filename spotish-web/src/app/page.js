"use server"
import { auth } from "@/auth";
import SearchContainer from "./components/SearchBar/SearchContainer";
import Footer from "./components/Footer";
import Image from "next/image";

export default async function Home() {
  const session = await auth();
  console.log(session)

  return (
    <div>

      <header className="flex justify-center align-center ">
        <SearchContainer author={session.user.name} className="pt-2.5" />
        <div className="flex items-center absolute right-0">
          <a href="/login" className="hover:text-gray-400">{session.user.username}</a>
          <Image
            src={session.user.image}
            width={75}
            height={75}
            alt={session.user.name ?? "Avatar le dernier maître de l'air <3"}
            style={{ borderRadius: "50%", padding: "10px" }} />
        </div>
      </header>


      <Footer author={session.user.username} />
    </div>
  );
}
