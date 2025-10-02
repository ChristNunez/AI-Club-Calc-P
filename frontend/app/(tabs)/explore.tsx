// app/(tabs)/explore.tsx
import React from "react";
import { SafeAreaView, Text, StyleSheet } from "react-native";

export default function ExploreTab() {
  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.text}>🔍 Explore (coming soon)</Text>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#0f172a", alignItems: "center", justifyContent: "center" },
  text: { color: "#dbeafe", fontSize: 18 },
});
