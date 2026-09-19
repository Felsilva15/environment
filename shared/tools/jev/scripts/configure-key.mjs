import { execFileSync } from "node:child_process";
import { userInfo } from "node:os";
import { stdin, stdout } from "node:process";

import { KEYCHAIN_SERVICE } from "./credentials.mjs";

function readSecret(prompt) {
  if (!stdin.isTTY || typeof stdin.setRawMode !== "function") {
    throw new Error("This setup command must run in an interactive terminal");
  }

  stdout.write(prompt);
  stdin.setRawMode(true);
  stdin.resume();

  return new Promise((resolve, reject) => {
    let value = "";

    function finish() {
      stdin.off("data", onData);
      stdin.setRawMode(false);
      stdin.pause();
      stdout.write("\n");
    }

    function onData(buffer) {
      for (const character of buffer.toString("utf8")) {
        if (character === "\r" || character === "\n") {
          finish();
          resolve(value);
          return;
        }
        if (character === "\u0003") {
          finish();
          reject(new Error("Setup cancelled"));
          return;
        }
        if (character === "\u007f" || character === "\b") {
          value = value.slice(0, -1);
        } else if (character >= " ") {
          value += character;
        }
      }
    }

    stdin.on("data", onData);
  });
}

if (process.platform !== "darwin") {
  console.error("Keychain setup is available on macOS only. Set TYPESAFE_API_KEY instead.");
  process.exitCode = 1;
} else {
  const apiKey = (await readSecret("Paste your TypeSafe API key (input hidden): ")).trim();

  if (!apiKey) {
    console.error("No key was provided.");
    process.exitCode = 1;
  } else {
    const account = process.env.USER || userInfo().username;
    execFileSync(
      "/usr/bin/security",
      [
        "add-generic-password",
        "-U",
        "-a",
        account,
        "-s",
        KEYCHAIN_SERVICE,
        "-w",
        apiKey,
      ],
      { stdio: ["ignore", "ignore", "inherit"] },
    );
    console.log(`Saved the TypeSafe API key in macOS Keychain for ${account}.`);
  }
}
