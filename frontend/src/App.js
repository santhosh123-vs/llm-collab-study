import React, { useState } from "react";
import GlassBoxAssistant from "./components/GlassBoxAssistant";
import ResearchDashboard from "./components/ResearchDashboard";

function App() {
  const [view, setView] = useState("assistant");

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="bg-slate-800 border-b border-slate-700 px-6 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-xl">🔬</span>
            <span className="text-white font-bold text-lg">LLM Collab Study</span>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setView("assistant")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${view === "assistant" ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"}`}>
              🤖 Assistant
            </button>
            <button onClick={() => setView("dashboard")}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition ${view === "dashboard" ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-300 hover:bg-slate-600"}`}>
              📊 Dashboard
            </button>
          </div>
        </div>
      </nav>
      <main className="py-6">
        {view === "assistant" ? <GlassBoxAssistant /> : <ResearchDashboard />}
      </main>
      <footer className="bg-slate-800 border-t border-slate-700 px-6 py-4 text-center text-slate-500 text-sm">
        Decoding Human-LLM Collaboration in Coding | Research Project
      </footer>
    </div>
  );
}

export default App;
