// app/index.tsx
import React, { useEffect, useRef, useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  Pressable,
  StyleSheet,
  ActivityIndicator,
  Alert,
  Platform,
} from "react-native";
import { newProblem, submitAnswer } from "../src/api";

const BG = "#0f172a";
const CARD = "#0b1220";
const BORDER = "#1e293b";
const TEXT = "#dbeafe";
const MUTED = "#94a3b8";
const BTN = "#1e3a8a";
const BTN2 = "#1d4ed8";
const BTN_TEXT = "#e2e8f0";

export default function Home() {
  const [prompt, setPrompt] = useState("Loading…");
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("");
  const [loading, setLoading] = useState(false);

  // keep the live problem id here to avoid stale ids / expired errors
  const problemIdRef = useRef<string | null>(null);

  // prevent StrictMode double fetch in dev
  const didInit = useRef(false);
  // ignore late responses from /new-problem
  const loadSeq = useRef(0);

  async function loadProblem() {
    const seq = ++loadSeq.current;
    setLoading(true);
    setFeedback("");
    setAnswer("");
    try {
      const data = await newProblem("easy");
      if (seq !== loadSeq.current) return; // ignore outdated response
      problemIdRef.current = String(data.problem_id);
      setPrompt(data.prompt || "No prompt.");
    } catch (e) {
      console.error(e);
      setPrompt("Unable to reach the server. Is FastAPI on http://127.0.0.1:8005 ?");
    } finally {
      if (seq === loadSeq.current) setLoading(false);
    }
  }

  async function onCheck() {
    if (loading) return;
    const pid = problemIdRef.current;
    if (!pid) {
      setFeedback("No problem loaded. Fetching a new one…");
      await loadProblem();
      return;
    }
    setLoading(true);
    try {
      const res = await submitAnswer(pid, answer);
      const msg = res.feedback || (res.ok ? "Correct!" : "Incorrect");

      if (!res.ok && /expired/i.test(msg)) {
        setFeedback("That question expired. Fetching a fresh one…");
        await loadProblem();
        return;
      }

      setFeedback(res.ok ? `✅ ${msg}` : `❌ ${msg}`);

      if (res.ok) {
        Platform.OS === "web" ? alert(`✅ ${msg}`) : Alert.alert("✅ Correct", msg);
        await loadProblem();
      } else {
        Platform.OS === "web" ? alert(`❌ ${msg}`) : Alert.alert("❌ Try again", msg);
      }
    } catch (e) {
      console.error(e);
      Platform.OS === "web"
        ? alert("Network error. Check the backend.")
        : Alert.alert("Network error", "Check the backend.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (didInit.current) return;
    didInit.current = true;
    loadProblem();
  }, []);

  return (
    <SafeAreaView style={styles.screen}>
      <View style={styles.container}>
        <Text style={styles.title}>Calcduo</Text>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Problem</Text>
          <Text style={styles.prompt}>{prompt}</Text>
        </View>

        <View style={{ marginTop: 12 }}>
          <Text style={styles.sectionLabel}>Your Answer</Text>
          <TextInput
            placeholder="Type here, e.g. 1+12cos(3x-3)"
            placeholderTextColor={MUTED}
            value={answer}
            onChangeText={setAnswer}
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.input}
          />
        </View>

        <View style={styles.row}>
          <Pressable
            onPress={onCheck}
            disabled={loading}
            style={({ pressed }) => [
              styles.button,
              { backgroundColor: BTN, opacity: loading ? 0.85 : pressed ? 0.9 : 1 },
              Platform.OS === "web" ? { cursor: "pointer" } : null,
            ]}
          >
            {loading ? <ActivityIndicator /> : <Text style={styles.buttonText}>CHECK ANSWER</Text>}
          </Pressable>

          <Pressable
            onPress={loadProblem}
            disabled={loading}
            style={({ pressed }) => [
              styles.button,
              { backgroundColor: BTN2, marginLeft: 8, marginRight: 0, opacity: loading ? 0.85 : pressed ? 0.9 : 1 },
              Platform.OS === "web" ? { cursor: "pointer" } : null,
            ]}
          >
            <Text style={styles.buttonText}>NEW PROBLEM</Text>
          </Pressable>
        </View>

        {!!feedback && <Text style={styles.feedback}>{feedback}</Text>}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: BG },
  container: { flex: 1, padding: 20 },
  title: { fontSize: 24, fontWeight: "700", color: TEXT, marginBottom: 12 },
  card: { borderWidth: 1, borderColor: BORDER, backgroundColor: CARD, borderRadius: 12, padding: 12 },
  sectionLabel: { color: TEXT, opacity: 0.85, fontSize: 14 },
  prompt: { fontSize: 18, color: TEXT, marginTop: 6 },
  input: {
    borderWidth: 1,
    borderColor: BORDER,
    backgroundColor: CARD,
    color: TEXT,
    borderRadius: 10,
    padding: 12,
    fontSize: 16,
    marginTop: 6,
  },
  row: { flexDirection: "row", marginTop: 12 },
  button: { flex: 1, paddingVertical: 12, borderRadius: 10, alignItems: "center", marginRight: 8 },
  buttonText: { color: BTN_TEXT, fontWeight: "700", letterSpacing: 0.5 },
  feedback: { marginTop: 12, color: TEXT },
});
