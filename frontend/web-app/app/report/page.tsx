'use client'

import React, { useEffect, useState } from "react";

const API = `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:5000"}/api`;

interface Brand {
  id: number;
  name: string;
}

interface Campaign {
  id: number;
  title: string;
  description: string;
  budget: number;
  start_date: string;
  end_date: string;
  brand_name: string;
  platform: string;
  status: string;
  influencers: { id: number; name: string; platform: string; follower_count: number }[];
}

interface Statistics {
  total_campaigns: number;
  average_budget: number;
  total_budget: number;
  average_influencers_per_campaign: number;
  total_influencers_assigned: number;
}

const PLATFORMS = ["Instagram", "YouTube", "TikTok", "Twitter"];
const STATUSES = ["draft", "active", "completed", "cancelled"];

export default function ReportPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loaded, setLoaded] = useState(false);

  // Filters
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [brandId, setBrandId] = useState("");
  const [platform, setPlatform] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch(`${API}/brands`).then((r) => r.json()).then(setBrands);
  }, []);

  const runReport = async () => {
    const params = new URLSearchParams();
    if (startDate) params.set("start_date", startDate);
    if (endDate) params.set("end_date", endDate);
    if (brandId) params.set("brand_id", brandId);
    if (platform) params.set("platform", platform);
    if (status) params.set("status", status);

    const res = await fetch(`${API}/reports/campaigns?${params.toString()}`);
    const data = await res.json();
    setCampaigns(data.campaigns);
    setStats(data.statistics);
    setLoaded(true);
  };

  const clearFilters = () => {
    setStartDate("");
    setEndDate("");
    setBrandId("");
    setPlatform("");
    setStatus("");
    setCampaigns([]);
    setStats(null);
    setLoaded(false);
  };

  const inputClass = "w-full border border-gray-600 bg-gray-800 text-white rounded px-3 py-2 text-sm";
  const labelClass = "block text-sm font-medium text-gray-300 mb-1";

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Campaign Report</h1>

      {/* ---- Filters ---- */}
      <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8">
        <h2 className="font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <label className={labelClass}>Start Date</label>
            <input type="date" className={inputClass} value={startDate}
              onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div>
            <label className={labelClass}>End Date</label>
            <input type="date" className={inputClass} value={endDate}
              onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <div>
            <label className={labelClass}>Brand</label>
            <select className={inputClass} value={brandId}
              onChange={(e) => setBrandId(e.target.value)}>
              <option value="">All Brands</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Platform</label>
            <select className={inputClass} value={platform}
              onChange={(e) => setPlatform(e.target.value)}>
              <option value="">All Platforms</option>
              {PLATFORMS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>Status</label>
            <select className={inputClass} value={status}
              onChange={(e) => setStatus(e.target.value)}>
              <option value="">All Statuses</option>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4 flex gap-3">
          <button onClick={runReport}
            className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">
            Generate Report
          </button>
          <button onClick={clearFilters}
            className="bg-gray-700 text-gray-200 px-6 py-2 rounded hover:bg-gray-600">
            Clear
          </button>
        </div>
      </div>

      {/* ---- Statistics ---- */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          {[
            { label: "Total Campaigns", value: stats.total_campaigns },
            { label: "Average Budget", value: `$${stats.average_budget.toLocaleString()}` },
            { label: "Total Budget", value: `$${stats.total_budget.toLocaleString()}` },
            { label: "Avg Influencers/Campaign", value: stats.average_influencers_per_campaign },
            { label: "Total Influencers Assigned", value: stats.total_influencers_assigned },
          ].map((s) => (
            <div key={s.label} className="bg-gray-900 border border-gray-700 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold">{s.value}</div>
              <div className="text-xs text-gray-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      )}

      {/* ---- Results Table ---- */}
      {loaded && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-gray-800 text-left">
                <th className="p-3 border-b">Title</th>
                <th className="p-3 border-b">Brand</th>
                <th className="p-3 border-b">Platform</th>
                <th className="p-3 border-b">Budget</th>
                <th className="p-3 border-b">Dates</th>
                <th className="p-3 border-b">Status</th>
                <th className="p-3 border-b">Influencers</th>
              </tr>
            </thead>
            <tbody>
              {campaigns.map((c) => (
                <tr key={c.id} className="border-b hover:bg-gray-800">
                  <td className="p-3 font-medium">{c.title}</td>
                  <td className="p-3">{c.brand_name}</td>
                  <td className="p-3">{c.platform}</td>
                  <td className="p-3">${c.budget.toLocaleString()}</td>
                  <td className="p-3 text-xs">{c.start_date} to {c.end_date}</td>
                  <td className="p-3">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      c.status === "active" ? "bg-green-100 text-green-800" :
                      c.status === "completed" ? "bg-blue-100 text-blue-800" :
                      c.status === "cancelled" ? "bg-red-100 text-red-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="p-3 text-xs">{c.influencers.map((i) => i.name).join(", ") || "—"}</td>
                </tr>
              ))}
              {campaigns.length === 0 && (
                <tr><td colSpan={7} className="p-6 text-center text-gray-500">No campaigns match your filters.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
