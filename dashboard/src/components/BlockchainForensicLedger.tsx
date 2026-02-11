import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Link, CheckCircle2, ArrowRight } from "lucide-react";

const forensicBlocks = [
  {
    id: 1,
    event: "DDoS Attack Detected",
    time: "14:32:01",
    hash: "0x8f2a...9d",
    prevHash: "0xe3b0...42",
    eventType: "DDOS_VOLUMETRIC",
    status: "Verified"
  },
  {
    id: 2,
    event: "Unauthorized SSH Access",
    time: "14:30:55",
    hash: "0x4c1b...2a",
    prevHash: "0x8f2a...9d",
    eventType: "SSH_BRUTE_FORCE",
    status: "Verified"
  },
  {
    id: 3,
    event: "SQL Injection Attempt",
    time: "14:28:33",
    hash: "0xe3b0...42",
    prevHash: "0x9a12...41",
    eventType: "SQL_INJECTION",
    status: "Verified"
  },
  {
    id: 4,
    event: "Port Scan Detected",
    time: "14:25:12",
    hash: "0x9a12...41",
    prevHash: "0x7f3c...1e",
    eventType: "PORT_SCAN_TCP",
    status: "Verified"
  }
];

export function BlockchainForensicLedger() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Link className="h-5 w-5 text-[#06B6D4]" />
          <span>Immutable Forensic Ledger</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 mb-4">
          <div className="grid grid-cols-3 gap-2 text-xs text-gray-400 uppercase tracking-wider font-mono px-3">
            <div>Block Hash</div>
            <div>Prev Hash</div>
            <div>Event Type</div>
          </div>
        </div>

        <div className="space-y-3 relative">
          {/* Vertical blockchain line */}
          <div className="absolute left-[6px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-[#06B6D4] via-[#06B6D4]/50 to-[#06B6D4]/20"></div>

          {forensicBlocks.map((block, index) => (
            <div 
              key={block.id}
              className="relative pl-6 pb-4"
            >
              {/* Chain link dot */}
              <div className="absolute left-0 top-2 w-[14px] h-[14px] rounded-full bg-[#06B6D4] border-2 border-[#0F172A] shadow-lg shadow-[#06B6D4]/50"></div>

              <div className="p-4 rounded-lg border border-gray-700/50 bg-gradient-to-br from-gray-800/40 to-gray-900/40 hover:border-[#06B6D4]/30 transition-all">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="text-sm font-medium text-gray-200 mb-1">{block.event}</h4>
                    <div className="flex items-center space-x-2 text-xs text-gray-400">
                      <span className="font-mono">{block.time}</span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-1 text-[#22C55E]">
                    <CheckCircle2 className="h-4 w-4" />
                    <span className="text-xs">{block.status}</span>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <div className="text-gray-500 mb-1">Hash</div>
                    <div className="font-mono text-[#22C55E]">{block.hash}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 mb-1">Prev</div>
                    <div className="font-mono text-[#22C55E]">{block.prevHash}</div>
                  </div>
                  <div>
                    <div className="text-gray-500 mb-1">Type</div>
                    <div className="font-mono text-[#06B6D4] text-[10px]">{block.eventType}</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer Button */}
        <div className="flex justify-end mt-6 pt-4 border-t border-gray-700/50">
          <Button 
            variant="outline" 
            className="border-[#06B6D4]/30 text-[#06B6D4] hover:bg-[#06B6D4]/10 hover:border-[#06B6D4]/50"
          >
            View Historical Forensics
            <ArrowRight className="ml-2 h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}