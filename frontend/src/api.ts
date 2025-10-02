// src/api.ts
import { Platform } from "react-native";

export const BASE_URL =
  Platform.OS === "android" ? "http://10.0.2.2:8005" : "http://127.0.0.1:8005";

export type NewProblemResp = { problem_id: string | number; prompt: string };
export type AnswerResp = { ok: boolean; feedback?: string };

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} ${txt || ""}`.trim());
  }
  return res.json();
}

export function newProblem(difficulty = "easy") {
  return json<NewProblemResp>("/new-problem", {
    method: "POST",
    body: JSON.stringify({ difficulty }),
  });
}

export function submitAnswer(problem_id: string | number, answer: string) {
  return json<AnswerResp>("/answer", {
    method: "POST",
    body: JSON.stringify({ problem_id, answer }),
  });
}
