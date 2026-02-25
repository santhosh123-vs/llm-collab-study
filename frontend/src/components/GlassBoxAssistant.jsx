import React, { useState, useRef, useEffect } from "react";
import axios from "axios";

const GROQ_MODELS = {
  "LLaMA 3.3 70B": "llama-3.3-70b-versatile",
  "LLaMA 3.1 8B": "llama-3.1-8b-instant",
  "Mixtral 8x7B": "mixtral-8x7b-32768",
  "Gemma2 9B": "gemma2-9b-it",
};

const TASK_TYPES = ["generation", "debugging", "refactoring"];

function ConfidenceBadge({ score }) {
  const colors = { 1: "bg-red-600", 2: "bg-orange-500", 3: "bg-yellow-500", 4: "bg-blue-500", 5: "bg-green-500" };
  return (
    <span className={`${colors[score] || "bg-gray-500"} text-white text-xs px-2 py-1 rounded-full`}>
      Confidence: {score}/5
    </span>
  );
}

function MetaPanel({ meta }) {
  if (!meta || Object.keys(meta).length === 0) return null;
  return (
    <div className="mt-2 p-3 bg-slate-800 rounded-lg border border-slate-600 text-sm">
      <div className="text-slate-400 font-semibold mb-1">Glass-Box Metadata</div>
      {meta.confidence && <ConfidenceBadge score={meta.confidence} />}
      {meta.uncertainty_areas && meta.uncertainty_areas.length > 0 && (
        <div className="mt-2">
          <span className="text-yellow-400">Uncertainty:</span>
          <ul className="list-disc list-inside text-slate-300 ml-2">
            {meta.uncertainty_areas.map((u, i) => <li key={i}>{u}</li>)}
          </ul>
        </div>
      )}
      {meta.constraints_followed && meta.constraints_followed.length > 0 && (
        <div className="mt-2">
          <span className="text-green-400">Constraints followed:</span>
          <ul className="list-disc list-inside text-slate-300 ml-2">
            {meta.constraints_followed.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        </div>
      )}
    </div>
  );
}

export default function GlassBoxAssistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState("llama-3.3-70b-versatile");
  const [taskType, setTaskType] = useState("generation");
  const [taskDesc, setTaskDesc] = useState("");
  const [turnAnnotations, setTurnAnnotations] = useState({});
  const chatEndRef = useRef(null);

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input.trim() };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setLoading(true);

    try {
      const apiMessages = updated.map((m) => ({ role: m.role, content: m.content }));
      const resp = await axios.post("http://localhost:5001/api/chat", { messages: apiMessages, model });
      const cleanContent = resp.data.content.replace(/<meta>[\s\S]*?<\/meta>/g, "").trim();
      setMessages([...updated, { role: "assistant", content: cleanContent, meta: resp.data.meta || {} }]);
    } catch (err) {
      setMessages([...updated, { role: "assistant", content: `Error: ${err.response?.data?.error || err.message}`, meta: {} }]);
    }
    setLoading(false);
  };

  const handleKeyDown = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); } };

  const annotateTurn = (idx, field, value) => {
    setTurnAnnotations((prev) => ({ ...prev, [idx]: { ...prev[idx], [field]: value } }));
  };

  const exportSession = async (outcome = "success") => {
    const turns = messages.map((m, i) => ({
      turn_id: i, role: m.role, content: m.content,
      has_correction: turnAnnotations[i]?.has_correction || false,
      has_constraint: turnAnnotations[i]?.has_constraint || false,
      instruction_violated: turnAnnotations[i]?.instruction_violated || false,
      fluency_score: turnAnnotations[i]?.fluency_score || null,
      correctness_score: turnAnnotations[i]?.correctness_score || null,
    }));

    try {
      const resp = await axios.post("http://localhost:5001/api/sessions", {
        task_type: taskType, turns, outcome, task_description: taskDesc,
      });
      alert(`Session saved!\nID: ${resp.data.session_id}\nPattern: ${resp.data.pattern}`);
      setMessages([]); setTurnAnnotations({}); setTaskDesc("");
    } catch (err) { alert("Failed to save: " + err.message); }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-slate-800 rounded-xl p-6 mb-6 border border-slate-700">
        <h1 className="text-2xl font-bold text-white mb-1">Glass-Box Coding Assistant</h1>
        <p className="text-slate-400 text-sm">Transparent AI assistant for human-LLM collaboration research</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Model</label>
            <select value={model} onChange={(e) => setModel(e.target.value)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm border border-slate-600">
              {Object.entries(GROQ_MODELS).map(([name, id]) => <option key={id} value={id}>{name}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Task Type</label>
            <select value={taskType} onChange={(e) => setTaskType(e.target.value)}
              className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm border border-slate-600">
              {TASK_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Task Description</label>
            <input type="text" value={taskDesc} onChange={(e) => setTaskDesc(e.target.value)}
              placeholder="e.g., Write a binary search"
              className="w-full bg-slate-700 text-white rounded px-3 py-2 text-sm border border-slate-600" />
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl border border-slate-700 flex flex-col" style={{ height: "500px" }}>
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-slate-500 mt-20">
              <p className="text-4xl mb-4">🤖</p>
              <p>Start a coding conversation to begin data collection</p>
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-[80%] rounded-xl p-4 ${m.role === "user" ? "bg-blue-600 text-white" : "bg-slate-700 text-slate-100"}`}>
                <div className="text-xs text-slate-300 mb-1 font-semibold">{m.role === "user" ? "You" : "Assistant"}</div>
                <div className="whitespace-pre-wrap text-sm">{m.content}</div>
                {m.meta && <MetaPanel meta={m.meta} />}
                <div className="mt-2 flex flex-wrap gap-2 text-xs">
                  {m.role === "user" && (
                    <>
                      <button onClick={() => annotateTurn(i, "has_correction", !turnAnnotations[i]?.has_correction)}
                        className={`px-2 py-1 rounded ${turnAnnotations[i]?.has_correction ? "bg-orange-500 text-white" : "bg-slate-600 text-slate-300"}`}>
                        {turnAnnotations[i]?.has_correction ? "✓ Correction" : "Mark Correction"}
                      </button>
                      <button onClick={() => annotateTurn(i, "has_constraint", !turnAnnotations[i]?.has_constraint)}
                        className={`px-2 py-1 rounded ${turnAnnotations[i]?.has_constraint ? "bg-purple-500 text-white" : "bg-slate-600 text-slate-300"}`}>
                        {turnAnnotations[i]?.has_constraint ? "✓ Constraint" : "Mark Constraint"}
                      </button>
                    </>
                  )}
                  {m.role === "assistant" && (
                    <>
                      <button onClick={() => annotateTurn(i, "instruction_violated", !turnAnnotations[i]?.instruction_violated)}
                        className={`px-2 py-1 rounded ${turnAnnotations[i]?.instruction_violated ? "bg-red-500 text-white" : "bg-slate-600 text-slate-300"}`}>
                        {turnAnnotations[i]?.instruction_violated ? "✓ Violation" : "Mark Violation"}
                      </button>
                      <select value={turnAnnotations[i]?.fluency_score || ""}
                        onChange={(e) => annotateTurn(i, "fluency_score", parseInt(e.target.value) || null)}
                        className="bg-slate-600 text-slate-300 rounded px-2 py-1">
                        <option value="">Fluency</option>
                        {[1,2,3,4,5].map((v) => <option key={v} value={v}>Fluency: {v}</option>)}
                      </select>
                      <select value={turnAnnotations[i]?.correctness_score || ""}
                        onChange={(e) => annotateTurn(i, "correctness_score", parseInt(e.target.value) || null)}
                        className="bg-slate-600 text-slate-300 rounded px-2 py-1">
                        <option value="">Correct.</option>
                        {[1,2,3,4,5].map((v) => <option key={v} value={v}>Correct: {v}</option>)}
                      </select>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
          {loading && <div className="flex justify-start"><div className="bg-slate-700 rounded-xl p-4 text-slate-400">Thinking...</div></div>}
          <div ref={chatEndRef} />
        </div>

        <div className="border-t border-slate-700 p-4">
          <div className="flex gap-2">
            <textarea value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown}
              placeholder="Type your coding question..." rows={2}
              className="flex-1 bg-slate-700 text-white rounded-lg px-4 py-2 text-sm border border-slate-600 resize-none focus:outline-none focus:border-blue-500" />
            <button onClick={sendMessage} disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white px-6 py-2 rounded-lg text-sm font-semibold">Send</button>
          </div>
        </div>
      </div>

      {messages.length > 0 && (
        <div className="mt-4 bg-slate-800 rounded-xl p-4 border border-slate-700 flex gap-3 items-center flex-wrap">
          <span className="text-slate-400 text-sm">Save session ({messages.length} turns):</span>
          <button onClick={() => exportSession("success")} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm">Success</button>
          <button onClick={() => exportSession("failure")} className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded text-sm">Failure</button>
          <button onClick={() => exportSession("partial")} className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded text-sm">Partial</button>
        </div>
      )}
    </div>
  );
}
