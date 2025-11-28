"use server";
import { auth } from "@/auth";
import { SignInButton } from "../components/Auth/sign-in-button";
import { SignOutButton } from "../components/Auth/sign-out-button";
import Image from "next/image";



export default async function Login() {
    const session = await auth();
    console.log(session)

    if (session?.user) {
        return (
            <div className="flex h-screen ">
                <div className="m-auto border-4 border-[#D216DA]  rounded-2xl ">
                    <h3 className="text-5xl  text-center p-4">You are sign in as : </h3>
                    <div className="flex justify-center flex-col items-center">
                        {session.user.image && (
                            <Image
                                src={session.user.image}
                                width={250}
                                height={100}
                                alt={session.user.name ?? "AVATAR"}
                                style={{ borderRadius: "50%", padding: "10px" }} />
                        )}
                        <p className="text-5xl ">{session.user.username}</p>
                        <SignOutButton className="w-3/4 h-10 m-3 bg-red-500 rounded-lg cursor-pointer" />
                        <a className="bg-[#D216DA] w-3/4 h-10 m-3 rounded-lg  flex items-center justify-center " href="/">Continue</a>

                    </div>
                </div>
            </div>
        )
    }

    return (
        <div className="flex h-screen ">
            <div className="m-auto border-4 border-[#D216DA]  rounded-2xl flex justify-center flex-col items-center">
                <h3 className="text-3xl  text-center pt-10 p-4">You aren't sign in</h3>
                <SignInButton className="w-3/4 h-10 m-7 bg-[#D216DA] rounded-lg cursor-pointer" />
            </div>
        </div>
    );
}