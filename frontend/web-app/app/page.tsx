'use client'

import Link from "next/link";

export default function Home() {
  return (
    <div className="mt-12 text-center">
      <h1 className="text-4xl font-bold mb-4">InfluenceHub</h1>
      <p className="text-lg text-gray-600 mb-8">
        Manage influencer marketing campaigns — create, track, and report on brand partnerships.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          href="/campaigns"
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 text-lg"
        >
          Manage Campaigns
        </Link>
        <Link
          href="/report"
          className="bg-gray-700 text-white px-6 py-3 rounded-lg hover:bg-gray-800 text-lg"
        >
          View Reports
        </Link>
      </div>
    </div>
  );
}
