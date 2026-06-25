export default function StatCard({ label,value,icon:Icon}){
  return(
    <div className="bg-white p-4 rounded-xl shadow-sm border">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-xs text-black-400">
            {label}
          </p>
          <h3 className="text-2xl font-bold text-black-800 mt-1">
            {value}
          </h3>
        </div>

        <Icon
          size={22}
          className="text-black-300"
        />
      </div>
    </div>
  );
}