"use client";

import { Activity, BrainCircuit, Gauge, LockKeyhole, Route, WalletCards } from "lucide-react";
import { motion } from "framer-motion";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const forecast = [
  { week: "W1", spend: 62000, optimized: 18000 },
  { week: "W2", spend: 72000, optimized: 29000 },
  { week: "W3", spend: 88000, optimized: 41000 },
  { week: "W4", spend: 106000, optimized: 52000 }
];

const metrics = [
  ["Monthly savings", "$2.8M", "46% lower run rate", WalletCards],
  ["Token reduction", "38%", "compression + context pruning", BrainCircuit],
  ["Cache hit rate", "31%", "exact and semantic layers", Activity],
  ["SLA compliance", "99.4%", "provider failover armed", Gauge]
] as const;

export default function Page() {
  return (
    <main className="min-h-screen px-6 py-6 lg:px-10">
      <header className="flex flex-col gap-4 border-b border-border pb-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-bold uppercase text-primary">Autonomous LLM Cost Optimization</p>
          <h1 className="mt-1 text-4xl font-black tracking-normal md:text-6xl">Right LLM</h1>
        </div>
        <div className="rounded-md border border-border bg-white px-4 py-2 text-sm text-muted">Gateway live</div>
      </header>

      <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map(([label, value, detail, Icon]) => (
          <motion.article
            key={label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-lg border border-border bg-white p-5"
          >
            <Icon className="h-5 w-5 text-primary" />
            <p className="mt-4 text-sm text-muted">{label}</p>
            <strong className="mt-1 block text-3xl">{value}</strong>
            <span className="text-sm text-accent">{detail}</span>
          </motion.article>
        ))}
      </section>

      <section className="mt-6 grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
        <article className="rounded-lg border border-border bg-white p-5">
          <div className="mb-4 flex items-center gap-2">
            <Route className="h-5 w-5 text-primary" />
            <h2 className="font-bold">Intelligent routing</h2>
          </div>
          <div className="grid gap-3">
            {["Classification → Gemini Flash", "RAG Search → Bedrock Haiku", "Code Generation → GPT-4o", "Summarization → Groq Llama 70B"].map((row) => (
              <div key={row} className="rounded-md bg-slate-100 p-3 text-sm">{row}</div>
            ))}
          </div>
        </article>

        <article className="rounded-lg border border-border bg-white p-5">
          <div className="mb-4 flex items-center gap-2">
            <LockKeyhole className="h-5 w-5 text-primary" />
            <h2 className="font-bold">Policy center</h2>
          </div>
          <div className="grid gap-3 text-sm text-muted">
            <p>RBAC model restrictions</p>
            <p>Token budget enforcement</p>
            <p>Provider compliance controls</p>
            <p>Runaway spend protection</p>
          </div>
        </article>
      </section>

      <section className="mt-6 rounded-lg border border-border bg-white p-5">
        <h2 className="mb-4 font-bold">Spend forecast and optimization contribution</h2>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={forecast}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis />
              <Tooltip />
              <Area dataKey="spend" stroke="#2563eb" fill="#bfdbfe" />
              <Area dataKey="optimized" stroke="#12805c" fill="#bbf7d0" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>
    </main>
  );
}
