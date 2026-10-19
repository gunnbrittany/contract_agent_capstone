import React, { useState, useEffect } from 'react';
import { Button } from '../shared/ui/button';

export type PageType = 'intelligence' | 'mcp' | 'search' | 'chat' | 'agents';

interface NavigationProps {
  currentPage: PageType;
  onNavigate: (page: PageType) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ currentPage, onNavigate }) => {
  // Toggle for showing/hiding the MCP Layer Inspector page
  const [showMcpTab, setShowMcpTab] = useState<boolean>(() => {
    return localStorage.getItem('show_mcp_tab') === 'true';
  });

  const handleToggleMcp = () => {
    const nextState = !showMcpTab;
    setShowMcpTab(nextState);
    localStorage.setItem('show_mcp_tab', String(nextState));

    if (nextState) {
      // Switched ON: navigate to MCP page to inspect
      onNavigate('mcp');
    } else if (currentPage === 'mcp') {
      // Switched OFF: if currently on MCP page, navigate back to Document Analysis
      onNavigate('intelligence');
    }
  };

  return (
    <nav className="mb-8 border-b border-slate-200 bg-white rounded-lg shadow-sm">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <h1 className="text-2xl font-bold text-slate-800">Contract Intelligence</h1>
            <div className="flex space-x-1">
              {/* Only shown when toggle is ON */}
              {showMcpTab && (
                <Button
                  variant={currentPage === 'mcp' ? 'default' : 'ghost'}
                  onClick={() => onNavigate('mcp')}
                  className={`px-4 py-2 font-semibold transition-all ${
                    currentPage === 'mcp'
                      ? 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm'
                      : 'bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200'
                  }`}
                >
                  ⚡ Knowledge + MCP Layer
                </Button>
              )}

              <Button
                variant={currentPage === 'intelligence' ? 'default' : 'ghost'}
                onClick={() => onNavigate('intelligence')}
                className={`px-4 py-2 ${
                  currentPage === 'intelligence'
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200'
                }`}
              >
                Document Analysis
              </Button>
              <Button
                variant={currentPage === 'chat' ? 'default' : 'ghost'}
                onClick={() => onNavigate('chat')}
                className={`px-4 py-2 ${
                  currentPage === 'chat'
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-green-50 hover:bg-green-100 text-green-700 border border-green-200'
                }`}
              >
                Contract Chat
              </Button>
              <Button
                variant={currentPage === 'search' ? 'default' : 'ghost'}
                onClick={() => onNavigate('search')}
                className={`px-4 py-2 ${
                  currentPage === 'search'
                    ? 'bg-teal-600 hover:bg-teal-700 text-white'
                    : 'bg-teal-50 hover:bg-teal-100 text-teal-700 border border-teal-200'
                }`}
              >
                Enhanced Search
              </Button>
              <Button
                variant={currentPage === 'agents' ? 'default' : 'ghost'}
                onClick={() => onNavigate('agents')}
                className={`px-4 py-2 ${
                  currentPage === 'agents'
                    ? 'bg-purple-600 hover:bg-purple-700 text-white'
                    : 'bg-purple-50 hover:bg-purple-100 text-purple-700 border border-purple-200'
                }`}
              >
                Documentation
              </Button>
            </div>
          </div>

          {/* Right Controls: MCP Inspector Toggle */}
          <div className="flex items-center space-x-3">
            <button
              onClick={handleToggleMcp}
              title="Toggle MCP Inspector view on/off"
              className={`flex items-center space-x-2 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors cursor-pointer ${
                showMcpTab
                  ? 'bg-indigo-50 border-indigo-300 text-indigo-700 hover:bg-indigo-100'
                  : 'bg-slate-100 border-slate-200 text-slate-500 hover:bg-slate-200'
              }`}
            >
              <span className="flex items-center gap-1.5">
                <span
                  className={`w-2 h-2 rounded-full ${
                    showMcpTab ? 'bg-indigo-600 animate-pulse' : 'bg-slate-400'
                  }`}
                />
                MCP Inspector:
              </span>
              <span className={`font-bold ${showMcpTab ? 'text-indigo-800' : 'text-slate-600'}`}>
                {showMcpTab ? 'ON' : 'OFF'}
              </span>
            </button>

            <span className="text-xs text-slate-400 hidden sm:inline">
              | AI-Powered Legal Platform
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};