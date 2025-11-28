import NextAuth from "next-auth";
import GitHubProvider from "next-auth/providers/github";

export const { auth, handlers, signIn, signOut } = NextAuth({
    providers: [
        GitHubProvider({
            profile(profile) {
                return {
                    id: profile.id + "",
                    name: profile.name || profile.login, // fallback to login if no display name
                    email: profile.email,
                    image: profile.avatar_url,
                    username: profile.login, // the GitHub username (login)
                };
            },
        }),
    ],
    callbacks: {
        async jwt({ token, account, profile }) {
            if (account && account.access_token) {
                token.accessToken = account.access_token;
            }
            if (profile && profile.login) {
                token.username = profile.login;
            }
            return token;
        },
        async session({ session, token }) {
            session.user.username = token.username;
            session.accessToken = token.accessToken;
            return session;
        },
    },
});
