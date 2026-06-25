import React, { useState } from "react";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-gray-50 font-sans">
      <Sidebar
        mobileOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col min-w-0">
        {/* Mobile topbar */}
        <header className="md:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-gray-100">
          <span className="text-lg font-bold text-violet-600 tracking-tight">
            flip<span className="text-gray-900">earn</span>
            <span className="text-violet-500">.</span>
          </span>
          <button
            onClick={() => setSidebarOpen((v) => !v)}
            className="p-2 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
            aria-label="Toggle menu"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </header>

        <Dashboard />
      </div>
    </div>
  );
}
