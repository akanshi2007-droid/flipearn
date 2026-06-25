import {
  TrendingUp,
  DollarSign,
  AlignJustify,
  Users,
} from "lucide-react";

import StatCard from "../components/StatCard";
import ListingsTable from "../components/ListingsTable";

const stats = [
  { label: "Total Listings", value: "5", icon: TrendingUp },
  { label: "Total Revenue", value: "$2,980", icon: DollarSign },
  { label: "Active Listings", value: "3", icon: AlignJustify },
  { label: "Total Users", value: "7", icon: Users },
];

export default function Dashboard() {
  return (
    <main className="flex-1 min-h-screen bg-gray-50 p-4 md:p-8">
      
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">
          Admin{" "}
          <span className="text-violet-500">
            Dashboard
          </span>
        </h1>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {stats.map((item) => (
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