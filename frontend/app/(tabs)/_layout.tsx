// app/(tabs)/_layout.tsx
import React from "react";
import { Tabs } from "expo-router";

const BG = "#0f172a";
const TAB_BG = "#0b1220";
const BORDER = "#1e293b";
const TEXT = "#dbeafe";
const MUTED = "#94a3b8";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { backgroundColor: TAB_BG, borderTopColor: BORDER },
        tabBarActiveTintColor: TEXT,
        tabBarInactiveTintColor: MUTED,
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home" }} />
      <Tabs.Screen name="explore" options={{ title: "Explore" }} />
    </Tabs>
  );
}
