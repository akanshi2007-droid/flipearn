import { listings } from "../data/listings";
export default function ListingsTable(){
  return(
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-800">Recent Listings</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[700px]">
          <thead>
            <tr className="border-b border-gray-100">
              <th className="text-left py-4 px-5 text-xs font-semibold text-black-500 uppercase">
                #</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">
                Title</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">
                Niche</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">
                Platform</th>
              <th className="text-left py-4 px-4 text-xs font-semibold text-black-500 uppercase">
                Username
              </th>
            </tr>
          </thead>
          <tbody>
            {listings.map((item) => (
              <tr
                key={item.id}
                className="border-b border-gray-50 hover:bg-gray-50 transition">
                <td className="py-4 px-5 text-gray-700">
                  {item.id}.</td>
                <td className="py-4 px-4 text-gray-700 font-medium">
                  {item.title}</td>
                <td className="py-4 px-4 text-gray-700">
                  {item.niche}</td>
                <td className="py-4 px-4 text-gray-700">
                  {item.platform}</td>
                <td className="py-4 px-4 text-gray-700">
                  {item.username}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}