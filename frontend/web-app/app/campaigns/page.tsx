'use client'

import React, { useEffect, useState } from "react";

const API = `${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:5000"}/api`;

interface Brand {
  id: number;
  name: string;
}

interface Influencer {
  id: number;
  name: string;
  platform: string;
  follower_count: number;
}

interface Campaign {
  id: number;
  title: string;
  description: string;
  budget: number;
  start_date: string;
  end_date: string;
  brand_id: number;
  brand_name: string;
  platform: string;
  status: string;
  influencers: Influencer[];
}

const PLATFORMS = ["Instagram", "YouTube", "TikTok", "Twitter"];
const STATUSES = ["draft", "active", "completed", "cancelled"];

const emptyForm = {
  title: "",
  description: "",
  budget: 0,
  start_date: "",
  end_date: "",
  brand_id: 0,
  platform: "Instagram",
  status: "draft",
  influencer_ids: [] as number[],
};

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [brands, setBrands] = useState<Brand[]>([]);
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [form, setForm] = useState({ ...emptyForm });
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showForm, setShowForm] = useState(false);

  const fetchAll = async () => {
    const [cRes, bRes, iRes] = await Promise.all([
      fetch(`${API}/campaigns`),
      fetch(`${API}/brands`),
      fetch(`${API}/influencers`),
    ]);
    setCampaigns(await cRes.json());
    setBrands(await bRes.json());
    setInfluencers(await iRes.json());
  };

  useEffect(() => { fetchAll(); }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const url = editingId ? `${API}/campaigns/${editingId}` : `${API}/campaigns`;
    const method = editingId ? "PUT" : "POST";

    await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });

    setForm({ ...emptyForm });
    setEditingId(null);
    setShowForm(false);
    fetchAll();
  };

  const handleEdit = (c: Campaign) => {
    setForm({
      title: c.title,
      description: c.description,
      budget: c.budget,
      start_date: c.start_date,
      end_date: c.end_date,
      brand_id: c.brand_id,
      platform: c.platform,
      status: c.status,
      influencer_ids: c.influencers.map((i) => i.id),
    });
    setEditingId(c.id);
    setShowForm(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this campaign?")) return;
    await fetch(`${API}/campaigns/${id}`, { method: "DELETE" });
    fetchAll();
  };

  const toggleInfluencer = (id: number) => {
    setForm((prev) => ({
      ...prev,
      influencer_ids: prev.influencer_ids.includes(id)
        ? prev.influencer_ids.filter((i) => i !== id)
        : [...prev.influencer_ids, id],
    }));
  };

  const inputClass = "w-full border border-gray-600 bg-gray-800 text-white rounded px-3 py-2 text-sm";
  const labelClass = "block text-sm font-medium text-gray-300 mb-1";

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Campaigns</h1>
        <button
          onClick={() => { setForm({ ...emptyForm }); setEditingId(null); setShowForm(!showForm); }}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ New Campaign"}
        </button>
      </div>

      {/* ---- Form ---- */}
      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-900 border border-gray-700 rounded-lg p-6 mb-8 grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>Title</label>
            <input className={inputClass} required value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>

          <div>
            <label className={labelClass}>Brand</label>
            <select className={inputClass} required value={form.brand_id}
              onChange={(e) => setForm({ ...form, brand_id: Number(e.target.value) })}>
              <option value={0} disabled>Select a brand</option>
              {brands.map((b) => (
                <option key={b.id} value={b.id}>{b.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Platform</label>
            <select className={inputClass} value={form.platform}
              onChange={(e) => setForm({ ...form, platform: e.target.value })}>
              {PLATFORMS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Status</label>
            <select className={inputClass} value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className={labelClass}>Budget ($)</label>
            <input type="number" className={inputClass} required min={0} value={form.budget}
              onChange={(e) => setForm({ ...form, budget: Number(e.target.value) })} />
          </div>

          <div>
            <label className={labelClass}>Start Date</label>
            <input type="date" className={inputClass} required value={form.start_date}
              onChange={(e) => setForm({ ...form, start_date: e.target.value })} />
          </div>

          <div>
            <label className={labelClass}>End Date</label>
            <input type="date" className={inputClass} required value={form.end_date}
              onChange={(e) => setForm({ ...form, end_date: e.target.value })} />
          </div>

          <div className="col-span-2">
            <label className={labelClass}>Description</label>
            <textarea className={inputClass} rows={2} value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>

          <div className="col-span-2">
            <label className={labelClass}>Assign Influencers</label>
            <div className="flex flex-wrap gap-2 mt-1">
              {influencers.map((inf) => (
                <button type="button" key={inf.id}
                  onClick={() => toggleInfluencer(inf.id)}
                  className={`px-3 py-1 rounded-full text-sm border ${
                    form.influencer_ids.includes(inf.id)
                      ? "bg-blue-600 text-white border-blue-600"
                      : "bg-gray-800 text-gray-300 border-gray-600 hover:border-blue-400"
                  }`}
                >
                  {inf.name} ({inf.platform})
                </button>
              ))}
            </div>
          </div>

          <div className="col-span-2">
            <button type="submit"
              className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
              {editingId ? "Update Campaign" : "Create Campaign"}
            </button>
          </div>
        </form>
      )}

      {/* ---- Table ---- */}
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
              <th className="p-3 border-b">Actions</th>
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
                <td className="p-3 flex gap-2">
                  <button onClick={() => handleEdit(c)}
                    className="text-blue-600 hover:underline text-xs">Edit</button>
                  <button onClick={() => handleDelete(c.id)}
                    className="text-red-600 hover:underline text-xs">Delete</button>
                </td>
              </tr>
            ))}
            {campaigns.length === 0 && (
              <tr><td colSpan={8} className="p-6 text-center text-gray-500">No campaigns yet.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
