import React, { useState, useEffect } from "react";
import axios from "axios";

function StatCard({ title, value, subtitle, color = "blue" }) {
  const colors = {
    blue: "border-blue-500 bg-blue-500/10", green: "border-green-500 bg-green-500/10",
    red: "border-red-500 bg-red-500/10", yellow: "border-yellow-500 bg-yellow-500/10",
    purple: "border-purple-500 bg-purple-500/10",
  };
  return (
    <div className={`p-4 rounded-xl border-l-4 ${colors[color]} bg-slate-800`}>
      <div className="text-slate-400 text-xs uppercase tracking-wide">{title}</div>
      <div className="text-3xl font-bold text-white mt-1">{value}</div>
      {subtitle && <div className="text-slate-400 text-sm mt-1">{subtitle}</div>}
    </div>
  );
}

function BarChart({ data, title }) {
  if (!data || Object.keys(data).length === 0) return null;
  const maxVal = Math.max(...Object.values(data), 1);
  const colors = {
    linear_flow: "bg-green-500", iterative_refinement: "bg-blue-500",
    instruction_failure: "bg-red-500", over_trust: "bg-yellow-500",
    generation: "bg-cyan-500", debugging: "bg-orange-500", refactoring: "bg-purple-500",
  };
  return (
    <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
      <h3 className="text-white font-semibold mb-4">{title}</h3>
      <div className="space-y-3">
        {Object.entries(data).map(([key, val]) => (
          <div key={key}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-300">{key.replace(/_/g, " ")}</span>
              <span className="text-slate-400">{typeof val === "number" && val % 1 !== 0 ? val.toFixed(1) : val}</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-4">
              <div className={`h-4 rounded-full ${colors[key] || "bg-blue-500"} transition-all duration-500`}
                style={{ width: `${(val / maxVal) * 100}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ResearchDashboard() {
  const [report, setReport] = useState(null);
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [reportRes, sessionsRes] = await Promise.all([
        axios.get("/api/report"),
        axios.get("/api/sessions"),
      ]);
      setReport(reportRes.data);
      setSessions(sessionsRes.data);
    } catch (err) { setError(err.message); }
    setLoading(false);
  };

  if (loading) return <div className="max-w-6xl mx-auto p-8 text-center text-slate-400"><div className="text-4xl mb-4">📊</div>Loading...</div>;
  if (error) return <div className="max-w-6xl mx-auto p-8 text-center text-red-400"><div className="text-4xl mb-4">⚠️</div>Error: {error}<div className="mt-4"><button onClick={fetchData} className="bg-blue-600 text-white px-4 py-2 rounded">Retry</button></div></div>;
  if (!report || report.error) return <div className="max-w-6xl mx-auto p-8 text-center text-slate-400"><div className="text-4xl mb-4">📭</div>No data yet.</div>;

  const rq1 = report.rq1_pattern_distribution || {};
  const rq2 = report.rq2_per_task_stats || {};
  const rq3 = report.rq3_failure_analysis || {};
  const rq4 = report.rq4_trust_calibration || {};

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="bg-slate-800 rounded-xl p-6 mb-6 border border-slate-700">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">📊 Research Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">Decoding Human-LLM Collaboration in Coding</p>
          </div>
          <button onClick={fetchData} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm">🔄 Refresh</button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        <StatCard title="Total Sessions" value={report.total_sessions} color="blue" />
        <StatCard title="Success Rate" value={`${((rq3.success_metrics?.count || 0) / Math.max(report.total_sessions, 1) * 100).toFixed(0)}%`} color="green" />
        <StatCard title="Avg Fluency" value={rq4.avg_fluency || "N/A"} subtitle="/5" color="purple" />
        <StatCard title="Avg Correctness" value={rq4.avg_correctness || "N/A"} subtitle="/5" color="yellow" />
        <StatCard title="Over-Trust Risk" value={`${rq4.over_trust_percentage || 0}%`} color="red" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <BarChart title="RQ1: Pattern Distribution (%)" data={rq1.percentages || {}} />
        <BarChart title="RQ2: Sessions per Task Type" data={Object.fromEntries(Object.entries(rq2).map(([k, v]) => [k, v.count || 0]))} />
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
        <h3 className="text-white font-semibold mb-4">RQ2: Per-Task Metrics</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-slate-400 border-b border-slate-700">
              <tr><th className="py-2 pr-4">Task</th><th className="py-2 pr-4">Count</th><th className="py-2 pr-4">Avg Turns</th><th className="py-2 pr-4">Success %</th><th className="py-2 pr-4">Retry Rate</th><th className="py-2 pr-4">Fluency</th><th className="py-2 pr-4">Correctness</th></tr>
            </thead>
            <tbody>
              {Object.entries(rq2).map(([task, m]) => (
                <tr key={task} className="border-b border-slate-700/50 text-slate-300">
                  <td className="py-2 pr-4 font-semibold capitalize">{task}</td>
                  <td className="py-2 pr-4">{m.count}</td>
                  <td className="py-2 pr-4">{m.avg_turns}</td>
                  <td className="py-2 pr-4">{(m.success_rate * 100).toFixed(0)}%</td>
                  <td className="py-2 pr-4">{(m.avg_retry_rate * 100).toFixed(1)}%</td>
                  <td className="py-2 pr-4">{m.avg_fluency}</td>
                  <td className="py-2 pr-4">{m.avg_correctness}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">RQ3: Failure Analysis</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between text-slate-300"><span>Successful sessions avg turns</span><span className="text-green-400 font-bold">{rq3.success_metrics?.avg_turns || "N/A"}</span></div>
            <div className="flex justify-between text-slate-300"><span>Failed sessions avg turns</span><span className="text-red-400 font-bold">{rq3.failure_metrics?.avg_turns || "N/A"}</span></div>
            <div className="flex justify-between text-slate-300"><span>High correction success rate</span><span className="text-yellow-400 font-bold">{typeof rq3.high_correction_success_rate === "number" ? `${(rq3.high_correction_success_rate * 100).toFixed(0)}%` : rq3.high_correction_success_rate}</span></div>
            <div className="flex justify-between text-slate-300"><span>Low correction success rate</span><span className="text-green-400 font-bold">{typeof rq3.low_correction_success_rate === "number" ? `${(rq3.low_correction_success_rate * 100).toFixed(0)}%` : rq3.low_correction_success_rate}</span></div>
            <hr className="border-slate-700" />
            <div className="flex justify-between text-slate-300"><span>Success count</span><span className="text-green-400">{rq3.success_metrics?.count || 0}</span></div>
            <div className="flex justify-between text-slate-300"><span>Failure count</span><span className="text-red-400">{rq3.failure_metrics?.count || 0}</span></div>
            <div className="flex justify-between text-slate-300"><span>Partial count</span><span className="text-yellow-400">{rq3.partial_metrics?.count || 0}</span></div>
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-white font-semibold mb-4">RQ4: Trust Calibration</h3>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between text-slate-300"><span>Average Fluency</span><span className="text-purple-400 font-bold">{rq4.avg_fluency}/5</span></div>
            <div className="flex justify-between text-slate-300"><span>Average Correctness</span><span className="text-yellow-400 font-bold">{rq4.avg_correctness}/5</span></div>
            <div className="flex justify-between text-slate-300"><span>Fluency-Correctness Correlation</span><span className={`font-bold ${rq4.fluency_correctness_correlation < 0 ? "text-red-400" : "text-green-400"}`}>{rq4.fluency_correctness_correlation}</span></div>
            <div className="flex justify-between text-slate-300"><span>Over-Trust Cases</span><span className="text-red-400 font-bold">{rq4.over_trust_count}</span></div>
            <hr className="border-slate-700" />
            <div className="p-3 bg-slate-700/50 rounded-lg">
              <p className="text-xs text-slate-400">
                {rq4.fluency_correctness_correlation < 0 ? "Warning: Negative correlation means higher fluency does NOT mean higher correctness." : "Fluency and correctness have a positive relationship in this dataset."}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
        <h3 className="text-white font-semibold mb-4">All Sessions ({sessions.length})</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-slate-400 border-b border-slate-700">
              <tr><th className="py-2 pr-4">ID</th><th className="py-2 pr-4">Task</th><th className="py-2 pr-4">Pattern</th><th className="py-2 pr-4">Turns</th><th className="py-2 pr-4">Outcome</th><th className="py-2 pr-4">Fluency</th><th className="py-2 pr-4">Correctness</th></tr>
            </thead>
            <tbody>
              {sessions.map((s) => {
                const oc = { success: "text-green-400", failure: "text-red-400", partial: "text-yellow-400" };
                const pc = { linear_flow: "bg-green-500/20 text-green-400", iterative_refinement: "bg-blue-500/20 text-blue-400", instruction_failure: "bg-red-500/20 text-red-400", over_trust: "bg-yellow-500/20 text-yellow-400" };
                return (
                  <tr key={s.session_id} className="border-b border-slate-700/50 text-slate-300">
                    <td className="py-2 pr-4 font-mono text-xs">{s.session_id}</td>
                    <td className="py-2 pr-4 capitalize">{s.task_type}</td>
                    <td className="py-2 pr-4"><span className={`text-xs px-2 py-1 rounded ${pc[s.final_pattern] || ""}`}>{s.final_pattern?.replace(/_/g, " ")}</span></td>
                    <td className="py-2 pr-4">{s.num_turns}</td>
                    <td className={`py-2 pr-4 font-semibold ${oc[s.outcome] || ""}`}>{s.outcome}</td>
                    <td className="py-2 pr-4">{s.avg_fluency}</td>
                    <td className="py-2 pr-4">{s.avg_correctness}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 mb-6">
        <h3 className="text-white font-semibold mb-4">Raw Report JSON</h3>
        <pre className="bg-slate-900 p-4 rounded-lg text-xs text-slate-300 overflow-x-auto max-h-96">
          {JSON.stringify(report, null, 2)}
        </pre>
      </div>
    </div>
  );
}
