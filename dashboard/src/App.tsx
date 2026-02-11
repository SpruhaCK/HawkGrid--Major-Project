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

export default function App() {
  return (
    <div className="min-h-screen bg-[#0F172A] text-gray-100">
      <div className="container mx-auto px-4 py-6 max-w-[1600px]">
        <Header />
        
        <div className="space-y-6">
          {/* Alert Banner */}
          <AlertBanner />
          
          {/* Main Layout: Left Panel + Right Panel */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {/* LEFT PANEL */}
            <div className="space-y-6">
              {/* TOP LEFT: Live Attack Topology */}
              <LiveAttackTopology />
              
              {/* MIDDLE LEFT: Orchestrator System Health */}
              <SystemHealthPanel />
              
              {/* BOTTOM LEFT: Monitored Cloud Assets */}
              <MonitoredCloudAssets />
              
              {/* Active Countermeasures (Below Cloud Assets) */}
              <ActiveCountermeasures />
            </div>
            
            {/* RIGHT PANEL */}
            <div className="space-y-6">
              {/* TOP: Active Threat Analysis */}
              <ThreatAlertsPanel />
              
              {/* BOTTOM: Immutable Forensic Ledger */}
              <BlockchainForensicLedger />
            </div>
          </div>
          
          {/* Charts Section */}
          <ChartsSection />
          
          {/* Full-Width Attack Analysis Table */}
          <AttackAnalysisSection />
          
          {/* Centered Download Button */}
          <div className="flex justify-center">
            <DownloadReportButton />
          </div>
        </div>
      </div>
    </div>
  );
}