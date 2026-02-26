import { Header } from "./components/Header";
import { LiveAttackTopology } from "./components/LiveAttackTopology";
import { MonitoredCloudAssets } from "./components/MonitoredCloudAssets";
import { ThreatAlertsPanel } from "./components/ThreatAlertsPanel";
import { AlertBanner } from "./components/AlertBanner";
import { ChartsSection } from "./components/ChartsSection";
import { AttackAnalysisSection } from "./components/AttackAnalysisSection";
import { DownloadReportButton } from "./components/DownloadReportButton";
import { SystemHealthPanel } from "./components/SystemHealthPanel";
import { BlockchainForensicLedger } from "./components/BlockchainForensicLedger";
import { ActiveCountermeasures } from "./components/ActiveCountermeasures";
import { LiveConsole } from './components/LiveConsole';

export default function App() {
  return (
    <div className="min-h-screen bg-[#0F172A] text-gray-100 pb-32 relative">
      <div className="container mx-auto px-4 py-6 max-w-[1600px]">
        <Header />
        
        <div className="space-y-6">
          {/* Alert Banner */}
          <AlertBanner />
          
          {/* Main Layout: Left Panel + Right Panel */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* LEFT PANEL */}
            <div className="space-y-6">
              <LiveAttackTopology />
              <SystemHealthPanel />
              <MonitoredCloudAssets />
              <ActiveCountermeasures />
            </div>
            
            {/* RIGHT PANEL */}
            <div className="space-y-6">
              <ThreatAlertsPanel />
              <BlockchainForensicLedger />
            </div>
          </div>
          
          {/* Bottom Visual Sections */}
          <ChartsSection />
          <AttackAnalysisSection />
        </div>
      </div>

      {/* --- FIXED INTERFACE ELEMENTS --- */}

      {/* 1. Live Console: Sits above the button bar (bottom-16) */}
      <div className="fixed bottom-16 left-0 right-0 z-50">
        <LiveConsole />
      </div>

      {/* 2. Global Action Bar: Sits at the very bottom (bottom-0) */}
      <div className="fixed bottom-0 left-0 right-0 z-[60] p-3 bg-slate-900/90 backdrop-blur-md border-t border-slate-800 flex justify-center shadow-2xl">
         <DownloadReportButton />
      </div>
    </div>
  );
}