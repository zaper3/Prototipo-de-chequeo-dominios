import { createHash } from "node:crypto";

// Git may check out CRLF on Windows and LF on CI; text provenance is logical.
export function sourceDigest(text) {
  return createHash("sha256").update(text.replace(/\r\n/g, "\n")).digest("hex");
}
