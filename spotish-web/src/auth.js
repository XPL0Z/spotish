import NextAuth from 'next-auth'
import Github from 'next-auth/providers/github'

export const { auth, handlers, signIn, signOut } = NextAuth({
    providers: [Github],

})