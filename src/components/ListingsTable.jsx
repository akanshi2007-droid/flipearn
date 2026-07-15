import { useState, useEffect } from "react";
import { fetchListings } from "../api";

export default function ListingsTable() {
  const [listings, setListings] = useState([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState(null);

  // Fetch real listings from the backend when this component loads
  useEffect(() => {
    fetchListings()
      .then((data) => { setListings(data); setLoading(false); })
      .catch(() =>   { setError("Could not load listings. Is the backend running?"); setLoading(false); });
  }, []);

  if (loading) return <p className="text-gray-400 py-8 text-center">Loading listings...</p>;
  if (error)   return <p className="text-red-400 py-8 text-center">{error}</p>;
  if (listings.length === 0) return <p className="text-gray-400 py-8 text-center">No active listings yet.</p>;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[700px]">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left py-4 px-5 text-xs font-semibold text-black-500 uppercase">#</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">Title</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">Niche</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">Platform</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">Username</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">Price</th>
            </tr>
          </thead>
          <tbody>
            {listings.map((item, index) => (
              <tr key={item.id} className="border-b border-gray-50 hover:bg-gray-50 transition">
                <td className="py-4 px-5 text-gray-700">{index + 1}.</td>
                <td className="py-4 px-4 text-gray-700 font-medium">{item.title}</td>
                <td className="py-4 px-4 text-gray-700">{item.niche}</td>
                <td className="py-4 px-4 text-gray-700">{item.platform}</td>
                <td className="py-4 px-4 text-gray-700">{item.account_username}</td>
                <td className="py-4 px-4 text-gray-700">${item.asking_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}