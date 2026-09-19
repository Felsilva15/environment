import { execFileSync } from "node:child_process";
import { userInfo } from "node:os";

export const KEYCHAIN_SERVICE = "codex-jev-typesafe";

function keychainAccount() {
  return process.env.USER || userInfo().username;
}

function readKeychainKey() {
  if (process.platform !== "darwin") return "";

  try {
    return execFileSync(
      "/usr/bin/security",
      [
        "find-generic-password",
        "-a",
        keychainAccount(),
        "-s",
        KEYCHAIN_SERVICE,
        "-w",
      ],
      { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] },
    ).trim();
  } catch {
    return "";
  }
}

export function credentialStatus() {
  if (process.env.TYPESAFE_API_KEY?.trim()) {
    return { configured: true, source: "environment" };
  }
  if (readKeychainKey()) {
    return { configured: true, source: "macOS Keychain" };
  }
  return { configured: false, source: null };
}

export function readApiKey() {
  const fromEnvironment = process.env.TYPESAFE_API_KEY?.trim();
  if (fromEnvironment) return fromEnvironment;

  const fromKeychain = readKeychainKey();
  if (fromKeychain) return fromKeychain;

  throw new Error(
    "TypeSafe API key is not configured. Run `node scripts/configure-key.mjs` in the Jev plugin folder, or set TYPESAFE_API_KEY before starting Codex.",
  );
}
