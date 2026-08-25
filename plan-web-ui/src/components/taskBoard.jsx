import React from 'react';

const TaskBoard = ({ tasks }) => {
  if (!tasks || tasks.length === 0) {
    return <div className="text-gray-400 p-4 text-center border-dashed border-2 rounded-lg">No tasks scheduled yet.</div>;
  }

  return (
    <div className="grid gap-4">
      {tasks.map((task, index) => (
        <div key={index} className="p-4 bg-white shadow rounded-lg border-l-4 border-blue-500">
          <div className="flex justify-between items-start">
            <h3 className="font-semibold text-lg text-gray-800">{task.title}</h3>
            <span className={`px-2 py-1 text-xs rounded-full ${task.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
              {task.priority}
            </span>
          </div>
          <p className="text-sm text-gray-500 mt-1">
            {task.start_time || 'N/A'} - {task.end_time || 'N/A'} | 📂 {task.category}
          </p>
        </div>
      ))}
    </div>
  );
};

export default TaskBoard;