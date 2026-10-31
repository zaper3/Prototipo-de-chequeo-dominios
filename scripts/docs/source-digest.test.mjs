import assert from "node:assert/strict";
import test from "node:test";
import { sourceDigest } from "./source-digest.mjs";

test("LF and CRLF versions have the same source digest", () => {
  assert.equal(sourceDigest("one\ntwo\n"), sourceDigest("one\r\ntwo\r\n"));
});
test("content changes are not hidden by newline normalization", () => {
  assert.notEqual(sourceDigest("one\ntwo\n"), sourceDigest("one\nthree\n"));
});
test("meaningful blank lines remain part of the digest", () => {
  assert.notEqual(sourceDigest("one\ntwo\n"), sourceDigest("one\n\ntwo\n"));
});
