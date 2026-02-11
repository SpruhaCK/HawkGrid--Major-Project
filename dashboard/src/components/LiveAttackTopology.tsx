import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Shield, Skull, Cloud } from "lucide-react";

export function LiveAttackTopology() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-[#06B6D4]" />
          <span>Live Attack Topology</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="py-8">
        <div className="relative h-80 flex items-center justify-center">
          {/* Left Node - Attacker (Far Left) */}
          <div className="absolute left-4 top-1/2 -translate-y-1/2 flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-[#EF4444]/20 border-2 border-[#EF4444] flex items-center justify-center shadow-lg shadow-[#EF4444]/50 animate-pulse">
              <Skull className="h-10 w-10 text-[#EF4444]" />
            </div>
            <div className="mt-3 text-center">
              <div className="text-sm font-medium text-[#EF4444]">External Attacker</div>
              <div className="text-xs text-gray-400 font-mono">(Kali)</div>
            </div>
          </div>

          {/* Center Node - Orchestrator (Dead Center) */}
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center z-10">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-[#06B6D4]/30 to-purple-500/30 border-2 border-[#06B6D4] flex items-center justify-center shadow-2xl shadow-[#06B6D4]/50">
              <Shield className="h-12 w-12 text-[#06B6D4]" />
            </div>
            <div className="mt-3 text-center">
              <div className="text-sm font-medium text-[#06B6D4]">HawkGrid</div>
              <div className="text-xs text-gray-400">Orchestrator</div>
            </div>
          </div>

          {/* Right Top Node - AWS (Vertically Stacked) */}
          <div className="absolute right-8 top-12 flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-[#F59E0B]/20 border-2 border-[#F59E0B] flex items-center justify-center shadow-lg shadow-[#F59E0B]/50">
              <Cloud className="h-10 w-10 text-[#F59E0B]" />
            </div>
            <div className="mt-3 text-center">
              <div className="text-sm font-medium text-[#F59E0B]">AWS EC2</div>
              <div className="text-xs text-gray-400">(Target)</div>
            </div>
          </div>

          {/* Right Bottom Node - Azure (Vertically Stacked with Clear Separation) */}
          <div className="absolute right-8 bottom-12 flex flex-col items-center">
            <div className="w-20 h-20 rounded-full bg-[#06B6D4]/20 border-2 border-[#06B6D4] flex items-center justify-center shadow-lg shadow-[#06B6D4]/50">
              <Cloud className="h-10 w-10 text-[#06B6D4]" />
            </div>
            <div className="mt-3 text-center">
              <div className="text-sm font-medium text-[#06B6D4]">Azure VM</div>
              <div className="text-xs text-gray-400">(Target)</div>
            </div>
          </div>

          {/* Clean Connection Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
            {/* Red pulsing line: Attacker -> Orchestrator */}
            <line
              x1="20%"
              y1="50%"
              x2="45%"
              y2="50%"
              stroke="#EF4444"
              strokeWidth="3"
              strokeDasharray="8,4"
              className="animate-pulse"
            />
            <text x="28%" y="47%" fill="#EF4444" fontSize="10" className="font-mono">
              DDoS Traffic
            </text>

            {/* Red pulsing line: Orchestrator -> AWS (Clean Upper Path) */}
            <line
              x1="55%"
              y1="42%"
              x2="75%"
              y2="23%"
              stroke="#EF4444"
              strokeWidth="3"
              strokeDasharray="8,4"
              className="animate-pulse"
            />

            {/* Green solid line: Orchestrator -> Azure (Clean Lower Path) */}
            <line
              x1="55%"
              y1="58%"
              x2="75%"
              y2="77%"
              stroke="#22C55E"
              strokeWidth="3"
            />
            <text x="62%" y="72%" fill="#22C55E" fontSize="10" className="font-mono">
              Secure
            </text>
          </svg>

          {/* Animated particles along attack path */}
          <div className="absolute left-[20%] top-1/2 w-2 h-2 rounded-full bg-[#EF4444] animate-ping" style={{ zIndex: 2 }}></div>
        </div>
      </CardContent>
    </Card>
  );
}