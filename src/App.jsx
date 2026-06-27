import React, { useState } from "react";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      {/* Top Header */}
      <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6">
        <span className="text-2xl font-bold text-violet-600">
          flip<span className="text-black">earn</span>
          <span className="text-violet-500">.</span>
        </span>
        {/* Mobile Menu Button */}
        <button
          onClick={() => setSidebarOpen((v) => !v)}
          className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100"
          aria-label="Toggle menu"
        >
          {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </header>
      {/* Body */}
      <div className="flex">
        <Sidebar
          mobileOpen={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
        />
        <main className="flex-1">
          <Dashboard />
        </main>
      </div>
    </div>
  );
}