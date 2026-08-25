import React, {useState, useEffect } from 'react';
import ChatInterface from './components/chatInterface';
import TaskBoard from './components/taskBoard';
import Calendar from './components/calender';
import { sendChatToBackend, getTasksByDate} from './services/apiClient';

function App() {
  const [tasks, setTasks] = useState([]);
  const [reply, setReply] = useState('Hello, I am your secretary. How can I assist you today?');
  const [isLoading, setIsLoading] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [isKeySaved, setIsKeySaved] = useState(false);

  const getLocalDateString = () => {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };
  const [selectedDate, setSelectedDate] = useState(getLocalDateString());
  const [locations  , setLocations] = useState([]);

  useEffect(() => {
    const savedKey = localStorage.getItem('GROQ_API_KEY');
    if (savedKey) {
      setApiKey(savedKey);
      setIsKeySaved(true);
    }
  }, []);

  const handleSaveKey = () => {
    if (apiKey.trim() === '') {
      alert('กรุณากรอก API Key ก่อนบันทึกครับ');
      return;
    }
    localStorage.setItem('GROQ_API_KEY', apiKey.trim());
    setIsKeySaved(true);
  };

  useEffect(() => {
    const fetchDailyTasks = async () => {
      try {
        const data = await getTasksByDate(selectedDate);
        setTasks(data.tasks || []);
        setLocations(data.locations || []);
      } catch (error) {
        console.error("Error loading tasks:", error);
        setTasks([]);
        setLocations([]);
      }
    };
    fetchDailyTasks();
  }, [selectedDate]);

  const handleProcessMessage = async (message) => {
    setIsLoading(true);
    try {
      const data = await sendChatToBackend(message, selectedDate);
      setTasks(data.tasks || []);
      setLocations(data.locations || []);
      setReply(data.reply_message);
    } catch (error) {
      setReply('An error occurred while connecting to the server. Please try again.');
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
      <div className="min-h-screen bg-gray-50 p-6 lg:p-8 font-sans">
        <header className="max-w-6xl mx-auto mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Workspace</h1>
          <p className="text-gray-500 mt-2">Life Planner</p>
        </header>

        {/* Left : Calender / Right : Chat + Task */}
        <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left */}
          <aside className="lg:col-span-1">
            <Calendar 
              selectedDate={selectedDate} 
              onSelectDate={setSelectedDate} 
              locations={locations}
            />
          </aside>

          {/* Right: Chat + Task */}
          <main className="lg:col-span-2 space-y-8">
            
            {/* Chat */}

            <section className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
              {/* api key */}
              <div className="bg-gray-50 p-3 mb-4 flex gap-3 items-center border border-gray-200 rounded-lg">
                <span className="text-sm font-semibold text-gray-700 whitespace-nowrap">
                  GROQ API Key:
                </span>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setIsKeySaved(false);
                  }}
                  placeholder="gsk-xxxxxxxxxxxxxxxx..."
                  className="flex-1 p-2 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
                <button 
                  onClick={handleSaveKey}
                  className={`px-4 py-2 text-sm font-medium text-white rounded transition-colors ${
                    isKeySaved ? 'bg-green-500 hover:bg-green-600' : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {isKeySaved ? 'บันทึกแล้ว ✔️' : 'บันทึก'}
                </button>
              </div>
              <div className="bg-blue-50 text-blue-800 p-4 rounded-lg mb-4 flex items-start gap-3">
                <span className="text-xl">🤖</span>
                <div>
                  <strong className="block mb-1">Secretary</strong>
                  {reply}
                </div>
              </div>
              <ChatInterface onSendMessage={handleProcessMessage} isLoading={isLoading} />
            </section>

            {/* Table */}
            <section>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">
                  Tasks for {selectedDate}
                </h2>
                {/*<div className="text-xs text-gray-400">Debug Loc: {JSON.stringify(locations)}</div>*/}
                <p className="text-sm text-blue-600 font-medium mt-1">
                  Location: {(() => {
                      const todaysLocs = (locations || []).filter(loc => loc.date === selectedDate);
                      if (todaysLocs.length === 0) return 'Bangkok';
                      const uniqueCities = [...new Set(todaysLocs.map(l => l.city))];
                      return uniqueCities.join(', ');
                  })()}
                </p>
              </div>
              <TaskBoard tasks={tasks} />
            </section>

          </main>
        </div>
      </div>
    );
  }

export default App;