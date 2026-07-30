import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Bell, Wallet, User, MessageSquare, 
  Menu, X, Shield, CheckCircle, AlertCircle, BarChart2, Settings, LogOut 
} from 'lucide-react';

export default function TradingApp() {
  // Navigation States
  const [activeTab, setActiveTab] = useState('trade'); // 'trade', 'profile', 'more'
  const [isAuth, setIsAuth] = useState(true); // Toggle Login/Signup Screen
  const [accountType, setAccountType] = useState('LIVE'); // 'LIVE' or 'DEMO'
  
  // User Data State
  const [user, setUser] = useState({
    email: 'torikul310861@gmail.com',
    id: '91252094',
    verified: false,
    liveBalance: 0.00,
    demoBalance: 10000.00,
    firstName: '',
    lastName: '',
    country: 'Bangladesh',
    twoFactor: true
  });

  // Trading Input States
  const [selectedAsset, setSelectedAsset] = useState('EUR/USD (OTC)');
  const [payoutRate, setPayoutRate] = useState(92);
  const [timer, setTimer] = useState('00:01:00');
  const [investment, setInvestment] = useState(1);

  return (
    <div className="flex flex-col h-screen bg-[#0e131f] text-white font-sans select-none overflow-hidden">
      
      {/* ----------------- TOP HEADER BAR ----------------- */}
      <header className="h-14 bg-[#181f2e] border-b border-gray-800 flex items-center justify-between px-3 z-50">
        <div className="flex items-center space-x-2">
          {/* Account Selector */}
          <div className="bg-[#0e131f] border border-gray-700 rounded-md px-2 py-1 flex items-center space-x-2 cursor-pointer">
            <span className={`text-xs font-bold px-1 rounded ${accountType === 'LIVE' ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'}`}>
              {accountType}
            </span>
            <span className="font-bold text-sm">
              ${accountType === 'LIVE' ? user.liveBalance.toFixed(2) : user.demoBalance.toFixed(2)}
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="relative cursor-pointer">
            <Bell size={20} className="text-gray-300" />
            <span className="absolute -top-1 -right-1 bg-red-500 text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">1</span>
          </div>
          
          <button className="bg-[#00b964] hover:bg-[#00a358] text-white px-4 py-1.5 rounded-md font-bold text-sm shadow-lg transition">
            Deposit
          </button>
        </div>
      </header>

      {/* ----------------- PROMO BANNER ----------------- */}
      <div className="bg-gradient-to-r from-emerald-600 to-teal-700 px-3 py-1.5 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          <span>🚀 Get a <span className="font-bold">50% bonus</span> on your deposit!</span>
          <span className="bg-white/20 px-1.5 py-0.5 rounded font-bold text-[10px]">50%</span>
        </div>
        <X size={14} className="cursor-pointer opacity-70 hover:opacity-100" />
      </div>

      {/* ----------------- MAIN VIEW AREA ----------------- */}
      <div className="flex-1 overflow-y-auto relative">
        
        {/* VIEW 1: TRADING TERMINAL */}
        {activeTab === 'trade' && (
          <div className="flex flex-col h-full justify-between">
            {/* Chart Container Placeholder (TradingView / Canvas integration area) */}
            <div className="flex-1 bg-[#090d16] relative flex items-center justify-center border-b border-gray-800">
              <div className="absolute top-3 left-3 bg-[#181f2e]/80 p-2 rounded border border-gray-700 text-xs">
                <div className="text-gray-400">Spot Price</div>
                <div className="text-emerald-400 font-mono font-bold text-lg">1.15081</div>
              </div>
              
              {/* Chart Placeholder Graphic */}
              <div className="text-center text-gray-600">
                <BarChart2 size={48} className="mx-auto mb-2 opacity-40 animate-pulse" />
                <p className="text-xs">Real-Time High Frequency Candle Chart Active</p>
              </div>
            </div>

            {/* Trading Control Panel */}
            <div className="bg-[#181f2e] p-3 space-y-3">
              {/* Asset Selector & Payout */}
              <div className="flex justify-between items-center bg-[#0e131f] p-2 rounded-lg border border-gray-800">
                <div className="flex items-center space-x-2">
                  <span className="font-bold text-sm">{selectedAsset}</span>
                  <span className="text-emerald-400 font-bold text-xs">{payoutRate}%</span>
                </div>
                <span className="text-xs text-blue-400 cursor-pointer">Pending Trade</span>
              </div>

              {/* Timer & Investment Inputs */}
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-[#0e131f] p-2 rounded-lg border border-gray-800">
                  <label className="text-[10px] text-gray-400 block">Timer</label>
                  <input 
                    type="text" 
                    value={timer} 
                    onChange={(e) => setTimer(e.target.value)}
                    className="bg-transparent font-mono font-bold w-full text-sm outline-none" 
                  />
                </div>
                <div className="bg-[#0e131f] p-2 rounded-lg border border-gray-800 flex justify-between items-center">
                  <div>
                    <label className="text-[10px] text-gray-400 block">Investment</label>
                    <input 
                      type="number" 
                      value={investment} 
                      onChange={(e) => setInvestment(Number(e.target.value))}
                      className="bg-transparent font-mono font-bold w-20 text-sm outline-none" 
                    />
                  </div>
                  <div className="flex space-x-1">
                    <button onClick={() => setInvestment(prev => Math.max(1, prev - 1))} className="bg-gray-800 w-6 h-6 rounded flex items-center justify-center font-bold text-xs">-</button>
                    <button onClick={() => setInvestment(prev => prev + 1)} className="bg-gray-800 w-6 h-6 rounded flex items-center justify-center font-bold text-xs">+</button>
                  </div>
                </div>
              </div>

              {/* Payout Calculation */}
              <div className="flex justify-between text-xs px-1 text-gray-400">
                <span>Payout</span>
                <span className="text-emerald-400 font-bold font-mono">${(investment * (1 + payoutRate/100)).toFixed(2)}</span>
              </div>

              {/* Up/Down Action Buttons */}
              <div className="grid grid-cols-2 gap-2 pt-1">
                <button className="bg-[#00b964] hover:bg-[#00a358] active:scale-95 transition py-3 rounded-lg font-bold text-white flex items-center justify-center space-x-1 shadow-lg">
                  <TrendingUp size={18} />
                  <span>Up</span>
                </button>
                <button className="bg-[#f23645] hover:bg-[#d92b39] active:scale-95 transition py-3 rounded-lg font-bold text-white flex items-center justify-center space-x-1 shadow-lg">
                  <TrendingDown size={18} />
                  <span>Down</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 2: PROFILE & KYC (Matching Screenshot 2) */}
        {activeTab === 'profile' && (
          <div className="p-4 space-y-4 max-w-lg mx-auto">
            <h2 className="text-lg font-bold border-b border-gray-800 pb-2">My account</h2>
            
            {/* Personal Data */}
            <div className="bg-[#181f2e] p-4 rounded-xl space-y-3 border border-gray-800">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center font-bold text-lg">
                  {user.email[0].toUpperCase()}
                </div>
                <div>
                  <div className="text-sm font-bold">{user.email}</div>
                  <div className="text-xs text-gray-400">ID: {user.id}</div>
                  <span className="inline-flex items-center space-x-1 bg-red-500/20 text-red-400 text-[10px] px-2 py-0.5 rounded border border-red-500/30 mt-1">
                    <AlertCircle size={10} />
                    <span>Not verified</span>
                  </span>
                </div>
              </div>

              <div className="space-y-2 pt-2">
                <div>
                  <label className="text-xs text-gray-400">Nickname</label>
                  <input type="text" value={`#${user.id}`} disabled className="w-full bg-[#0e131f] border border-gray-800 p-2 rounded text-sm text-gray-400" />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="text-xs text-gray-400">First Name</label>
                    <input type="text" placeholder="Empty" className="w-full bg-[#0e131f] border border-gray-700 p-2 rounded text-sm" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-400">Last Name</label>
                    <input type="text" placeholder="Empty" className="w-full bg-[#0e131f] border border-gray-700 p-2 rounded text-sm" />
                  </div>
                </div>
                <div>
                  <label className="text-xs text-gray-400">Country</label>
                  <select className="w-full bg-[#0e131f] border border-gray-700 p-2 rounded text-sm">
                    <option>Bangladesh</option>
                    <option>India</option>
                    <option>United States</option>
                  </select>
                </div>
                <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-bold text-sm transition">
                  Save Changes
                </button>
              </div>
            </div>

            {/* Documents Verification Notice */}
            <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-xl flex items-center space-x-3 text-red-400 text-xs">
              <AlertCircle size={24} className="shrink-0" />
              <span>You need to fill identity information before verifying your account.</span>
            </div>

            {/* Security Section */}
            <div className="bg-[#181f2e] p-4 rounded-xl space-y-3 border border-gray-800">
              <h3 className="font-bold text-sm">Security</h3>
              <div className="flex justify-between items-center text-xs">
                <span>Two-step verification</span>
                <input type="checkbox" checked={user.twoFactor} onChange={() => {}} className="toggle" />
              </div>
            </div>
          </div>
        )}

        {/* VIEW 3: MORE MENU (Matching Screenshot 3) */}
        {activeTab === 'more' && (
          <div className="p-4 space-y-2 max-w-lg mx-auto">
            <div className="bg-[#181f2e] rounded-xl border border-gray-800 divide-y divide-gray-800 text-sm">
              <div className="p-3 flex justify-between items-center hover:bg-gray-800/50 cursor-pointer">
                <span>Market</span>
                <span className="bg-blue-600 text-[10px] px-1.5 py-0.5 rounded-full font-bold">4</span>
              </div>
              <div className="p-3 flex justify-between items-center hover:bg-gray-800/50 cursor-pointer">
                <span>Analytics</span>
              </div>
              <div className="p-3 flex justify-between items-center hover:bg-gray-800/50 cursor-pointer">
                <span>TOP Traders</span>
              </div>
              <div className="p-3 flex justify-between items-center hover:bg-gray-800/50 cursor-pointer">
                <span>Signals</span>
              </div>
            </div>

            <div className="bg-[#181f2e] rounded-xl border border-gray-800 divide-y divide-gray-800 text-sm pt-2">
              <div className="p-3 hover:bg-gray-800/50 cursor-pointer">Deposit</div>
              <div className="p-3 hover:bg-gray-800/50 cursor-pointer">Withdrawal</div>
              <div className="p-3 hover:bg-gray-800/50 cursor-pointer">Payments</div>
              <div className="p-3 hover:bg-gray-800/50 cursor-pointer">Trades History</div>
            </div>

            <div className="flex justify-between items-center pt-4 text-sm text-gray-400 px-2">
              <span className="flex items-center space-x-1 cursor-pointer hover:text-white"><Settings size={16}/><span>Settings</span></span>
              <span className="flex items-center space-x-1 text-red-400 cursor-pointer hover:text-red-300"><LogOut size={16}/><span>Logout</span></span>
            </div>
          </div>
        )}
      </div>

      {/* ----------------- BOTTOM NAVIGATION BAR ----------------- */}
      <nav className="h-14 bg-[#181f2e] border-t border-gray-800 grid grid-cols-4 items-center text-center text-xs text-gray-400 z-50">
        <button onClick={() => setActiveTab('trade')} className={`flex flex-col items-center justify-center space-y-1 ${activeTab === 'trade' ? 'text-blue-500' : ''}`}>
          <BarChart2 size={18} />
          <span>Trades</span>
        </button>
        <button className="flex flex-col items-center justify-center space-y-1 hover:text-white">
          <MessageSquare size={18} />
          <span>Support</span>
        </button>
        <button onClick={() => setActiveTab('profile')} className={`flex flex-col items-center justify-center space-y-1 ${activeTab === 'profile' ? 'text-blue-500' : ''}`}>
          <User size={18} />
          <span>Profile</span>
        </button>
        <button onClick={() => setActiveTab('more')} className={`flex flex-col items-center justify-center space-y-1 ${activeTab === 'more' ? 'text-blue-500' : ''}`}>
          <Menu size={18} />
          <span>More</span>
        </button>
      </nav>

    </div>
  );
}
