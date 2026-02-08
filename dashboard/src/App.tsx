import { Header } from "./components/Header";
import { SystemLogsPanel } from "./components/SystemLogsPanel";
import { ThreatAlertsPanel } from "./components/ThreatAlertsPanel";
import { AlertBanner } from "./components/AlertBanner";
import { ChartsSection } from "./components/ChartsSection";
import { AttackAnalysisSection } from "./components/AttackAnalysisSection";
import { DownloadReportButton } from "./components/DownloadReportButton";
import { SystemHealthPanel } from "./components/SystemHealthPanel";
import { UserAccessSection } from "./components/UserAccessSection";

export default function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      <div className="container mx-auto px-4 py-6 max-w-[1600px]">
        <Header />
        
        <div className="space-y-6">
          {/* Alert Banner */}
          <AlertBanner />
          
          {/* Top Row: System Logs + Threat Alerts */}
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <SystemLogsPanel />
            <ThreatAlertsPanel />
          </div>
          
          {/* Charts Section */}
          <ChartsSection />
          
          {/* Bottom Section: Attack Analysis + Sidebar */}
          <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
            <div className="xl:col-span-2 space-y-6">
              <AttackAnalysisSection />
              <div className="flex justify-center">
                <DownloadReportButton />
              </div>
            </div>
            
            <div className="space-y-6">
              <SystemHealthPanel />
              <UserAccessSection />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}