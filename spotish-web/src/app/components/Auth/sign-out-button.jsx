"use client";
import { logout } from "../../../../lib/actions/auth";

export const SignOutButton = ({ className = "" }) => {
  return (
    <button
      className={`${className}`}
      onClick={() => logout()}
    >
      Sign Out
    </button>
  );
};
