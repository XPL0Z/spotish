"use server"
import { auth } from "@/auth";
import SearchContainer from "./components/SearchBar/SearchContainer";
import Footer from "./components/Footer";

export default async function Home() {
  const session = await auth();
  console.log(session)

  return (
    <div>
      {/* // Search Bar */}
      <div className="flex justify-center pt-4">
        <SearchContainer author={session.user.name} />
      </div>

      <Footer />
    </div>
  );
}
