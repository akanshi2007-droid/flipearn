import {
  LayoutDashboard,
  CheckCircle,
  RefreshCw,
  List,
  CreditCard,
  Wallet,
  User,
} from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, active: true },
  { label: "Verify", icon: CheckCircle },
  { label: "Change", icon: RefreshCw },
  { label: "Listings", icon: List },
  { label: "Transactions", icon: CreditCard },
  { label: "Withdrawal", icon: Wallet },
];

export default function Sidebar() {
  return (
    <aside className="w-20 md:w-64 bg-white border-r min-h-[calc(100vh-56px)] flex flex-col">
      <div className="flex flex-col items-center py-6">
        <div className="w-12 h-12 rounded-full bg-violet-100 flex items-center justify-center">
          <User className="text-violet-500" />
        </div>

        <p className="hidden md:block mt-2 text-sm font-medium">
          John Doe
        </p>
      </div>

      <nav className="flex-1 px-2">
        {navItems.map(({ label, icon: Icon, active }) => (
          <div
            key={label}
            className={`flex items-center gap-3 p-3 rounded-lg mb-2 cursor-pointer ${
              active
                ? "bg-violet-50 text-violet-600"
                : "text-gray-700 hover:bg-gray-50"
            }`}
          >
            <Icon size={18} />
            <span className="hidden md:block">{label}</span>
          </div>
        ))}
      </nav>
    </aside>
  );
}