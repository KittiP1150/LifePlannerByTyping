import React, { useState } from 'react';

const Calendar = ({ selectedDate, onSelectDate, locations = [] }) => {
  const [currentMonth, setCurrentMonth] = useState(new Date(selectedDate));
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDayOfMonth = new Date(year, month, 1).getDay();

  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const dayNames = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"];
  
  const days = [];
  for (let i = 0; i < firstDayOfMonth; i++) days.push(null);
  for (let i = 1; i <= daysInMonth; i++) days.push(i);
  
  const formatDate = (d, m, y) => {
    return `${y}-${String(m + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
  };

  const handlePrevMonth = () => setCurrentMonth(new Date(year, month - 1, 1));
  const handleNextMonth = () => setCurrentMonth(new Date(year, month + 1, 1));

  const getLocationForDay = (dateString) => {
    return locations.find(loc => loc.date === dateString);
  };

  return (
    <div className="bg-white p-4 sm:p-6 rounded-2xl shadow-sm border border-gray-100">
      
      {/* Header */}
      <div className="flex justify-between items-center mb-6 px-2">
        <h2 className="text-xl font-semibold text-gray-800">
          {monthNames[month]} {year}
        </h2>
        <div className="flex space-x-1">
          <button onClick={handlePrevMonth} className="p-2 hover:bg-gray-100 rounded-full text-gray-600 transition-colors">
            ◀
          </button>
          <button onClick={handleNextMonth} className="p-2 hover:bg-gray-100 rounded-full text-gray-600 transition-colors">
            ▶
          </button>
        </div>
      </div>

      {/* Days of Week */}
      <div className="grid grid-cols-7 mb-2">
        {dayNames.map(day => (
          <div key={day} className="text-[11px] text-center font-medium text-gray-500 tracking-wider">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar Grid */}
      <div className="grid grid-cols-7 border-t border-l border-gray-100 bg-gray-100 gap-[1px]">
        {days.map((day, index) => {
          if (!day) return <div key={index} className="bg-white min-h-[90px] sm:min-h-[110px]"></div>;

          const dateString = formatDate(day, month, year);
          const todayDate = new Date();
          const todayStr = `${todayDate.getFullYear()}-${String(todayDate.getMonth() + 1).padStart(2, '0')}-${String(todayDate.getDate()).padStart(2, '0')}`;

          const isSelected = dateString === selectedDate;
          const isToday = dateString === todayStr;
          const isPast = dateString < todayStr;
          const locationData = getLocationForDay(dateString);

          return (
            <div
              key={index}
              onClick={() => onSelectDate(dateString)}
              className={`
                bg-white min-h-[90px] sm:min-h-[110px] p-1 flex flex-col items-center cursor-pointer transition-colors
                ${isSelected ? 'bg-blue-50/30' : 'hover:bg-gray-50'}
              `}
            >
              {/* date number */}
              <div className={`
                w-7 h-7 flex items-center justify-center text-sm rounded-full mb-1 mt-1
                ${isToday 
                  ? 'bg-blue-600 text-white font-semibold shadow-sm' 
                  : isSelected 
                    ? 'bg-blue-100 text-blue-700 font-semibold' 
                    : isPast 
                      ? 'text-gray-400' 
                      : 'text-gray-700 font-medium hover:bg-gray-100'}
              `}>
                {day}
              </div>
              
              {/* Highlight Location */}
              {locationData && (
                <div className="w-full mt-1 px-1.5 py-1 bg-blue-500 text-white text-[10px] sm:text-[11px] font-medium rounded-[4px] truncate text-left shadow-sm">
                  {locationData.city}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Calendar;