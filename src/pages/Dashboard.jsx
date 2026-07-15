import { useState, useEffect } from "react";
import {
  TrendingUp,
  DollarSign,
  AlignJustify,
  Users,
} from "lucide-react";

import StatCard from "../components/StatCard";
import ListingsTable from "../components/ListingsTable";
import { fetchDashboardStats } from "../api";

export default function Dashboard() {
  // Stats start as "..." while loading from the backend
  const [stats, setStats] = useState({
    total_listings:  "...",
    active_listings: "...",
    total_users:     "...",
    total_revenue:   "...",
  });

  // When the page loads, fetch real numbers from the backend
  useEffect(() => {
    fetchDashboardStats()
      .then((data) => setStats(data))
      .catch(() => {
        // If backend is offline, fall back to zeros
        setStats({ total_listings: 0, active_listings: 0, total_users: 0, total_revenue: 0 });
      });
  }, []);

  const statCards = [
    { label: "Total Listings",  value: stats.total_listings,               icon: TrendingUp  },
    { label: "Total Revenue",   value: `$${stats.total_revenue}`,          icon: DollarSign  },
    { label: "Active Listings", value: stats.active_listings,              icon: AlignJustify },
    { label: "Total Users",     value: stats.total_users,                  icon: Users       },
  ];

  return (
    <main className="flex-1 min-h-screen bg-gray-50 p-4 md:p-8">

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Admin{" "}
          <span className="text-violet-500">Dashboard</span>
        </h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {statCards.map((item) => (
          <StatCard key={item.label} {...item} />
        ))}
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">
          Recent Listings
        </h2>
        <ListingsTable />
      </div>

    </main>
  );
}