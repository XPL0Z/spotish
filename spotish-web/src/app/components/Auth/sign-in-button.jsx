"use client";
import { login } from "../../../../lib/actions/auth";

export const SignInButton = ({ className = "" }) => {
  return (
    <button
      className={`${className}`}
      onClick={() => login()}
    >
      Sign In
    </button>
  );
};
