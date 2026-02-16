// import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
// import { Button } from "./ui/button";
// import { Link, CheckCircle2, ArrowRight } from "lucide-react";

// const forensicBlocks = [
//   {
//     id: 1,
//     event: "DDoS Attack Detected",
//     time: "14:32:01",
//     hash: "0x8f2a...9d",
//     prevHash: "0xe3b0...42",
//     eventType: "DDOS_VOLUMETRIC",
//     status: "Verified"
//   },
//   {
//     id: 2,
//     event: "Unauthorized SSH Access",
//     time: "14:30:55",
//     hash: "0x4c1b...2a",
//     prevHash: "0x8f2a...9d",
//     eventType: "SSH_BRUTE_FORCE",
//     status: "Verified"
//   },
//   {
//     id: 3,
//     event: "SQL Injection Attempt",
//     time: "14:28:33",
//     hash: "0xe3b0...42",
//     prevHash: "0x9a12...41",
//     eventType: "SQL_INJECTION",
//     status: "Verified"
//   },
//   {
//     id: 4,
//     event: "Port Scan Detected",
//     time: "14:25:12",
//     hash: "0x9a12...41",
//     prevHash: "0x7f3c...1e",
//     eventType: "PORT_SCAN_TCP",
//     status: "Verified"
//   }
// ];

// export function BlockchainForensicLedger() {
//   return (
//     <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
//       <CardHeader>
//         <CardTitle className="flex items-center space-x-2">
//           <Link className="h-5 w-5 text-[#06B6D4]" />
//           <span>Immutable Forensic Ledger</span>
//         </CardTitle>
//       </CardHeader>
//       <CardContent>
//         <div className="space-y-1 mb-4">
//           <div className="grid grid-cols-3 gap-2 text-xs text-gray-400 uppercase tracking-wider font-mono px-3">
//             <div>Block Hash</div>
//             <div>Prev Hash</div>
//             <div>Event Type</div>
//           </div>
//         </div>

//         <div className="space-y-3 relative">
//           {/* Vertical blockchain line */}
//           <div className="absolute left-[6px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-[#06B6D4] via-[#06B6D4]/50 to-[#06B6D4]/20"></div>

//           {forensicBlocks.map((block, index) => (
//             <div 
//               key={block.id}
//               className="relative pl-6 pb-4"
//             >
//               {/* Chain link dot */}
//               <div className="absolute left-0 top-2 w-[14px] h-[14px] rounded-full bg-[#06B6D4] border-2 border-[#0F172A] shadow-lg shadow-[#06B6D4]/50"></div>

//               <div className="p-4 rounded-lg border border-gray-700/50 bg-gradient-to-br from-gray-800/40 to-gray-900/40 hover:border-[#06B6D4]/30 transition-all">
//                 <div className="flex items-start justify-between mb-3">
//                   <div className="flex-1">
//                     <h4 className="text-sm font-medium text-gray-200 mb-1">{block.event}</h4>
//                     <div className="flex items-center space-x-2 text-xs text-gray-400">
//                       <span className="font-mono">{block.time}</span>
//                     </div>
//                   </div>
//                   <div className="flex items-center space-x-1 text-[#22C55E]">
//                     <CheckCircle2 className="h-4 w-4" />
//                     <span className="text-xs">{block.status}</span>
//                   </div>
//                 </div>

//                 <div className="grid grid-cols-3 gap-2 text-xs">
//                   <div>
//                     <div className="text-gray-500 mb-1">Hash</div>
//                     <div className="font-mono text-[#22C55E]">{block.hash}</div>
//                   </div>
//                   <div>
//                     <div className="text-gray-500 mb-1">Prev</div>
//                     <div className="font-mono text-[#22C55E]">{block.prevHash}</div>
//                   </div>
//                   <div>
//                     <div className="text-gray-500 mb-1">Type</div>
//                     <div className="font-mono text-[#06B6D4] text-[10px]">{block.eventType}</div>
//                   </div>
//                 </div>
//               </div>
//             </div>
//           ))}
//         </div>

//         {/* Footer Button */}
//         <div className="flex justify-end mt-6 pt-4 border-t border-gray-700/50">
//           <Button 
//             variant="outline" 
//             className="border-[#06B6D4]/30 text-[#06B6D4] hover:bg-[#06B6D4]/10 hover:border-[#06B6D4]/50"
//           >
//             View Historical Forensics
//             <ArrowRight className="ml-2 h-4 w-4" />
//           </Button>
//         </div>
//       </CardContent>
//     </Card>
//   );
// }

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Link, CheckCircle2, ArrowRight, ShieldAlert } from "lucide-react";

export function BlockchainForensicLedger() {
  const [blocks, setBlocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // FETCH & VERIFY CHAIN LOGIC
  const fetchAndVerifyChain = async () => {
    try {
      const response = await fetch("http://localhost:3001/api/live-logs");
      const rawData = await response.json();

      // 1. Sort by Time (Oldest First) to reconstruct the chain
      rawData.sort((a: any, b: any) => {
        const tA = new Date(a.incident?.timestamp || 0).getTime();
        const tB = new Date(b.incident?.timestamp || 0).getTime();
        return tA - tB;
      });

      // 2. Verify the Chain Integrity
      const processedBlocks = rawData.map((block: any, index: number) => {
        if (index === 0) {
          return { ...block, integrityStatus: "Genesis" };
        }
        const previousBlock = rawData[index - 1];
        const isValid = block.previous_hash === previousBlock.hash;

        return { 
          ...block, 
          integrityStatus: isValid ? "Verified" : "Tampered" 
        };
      });

      // 3. Reverse for Display (Show Newest First)
      setBlocks(processedBlocks.reverse());
      setLoading(false);

    } catch (error) {
      console.error("Blockchain Fetch Error:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAndVerifyChain();
    const interval = setInterval(fetchAndVerifyChain, 5000); 
    return () => clearInterval(interval);
  }, []);

  const handleDownloadHistory = () => {
    const headers = [
      "Timestamp", "Source IP", "Destination IP", "Attack Type", 
      "Asset Name", "Previous Hash", "Current Hash", "Integrity Status"
    ];

    const csvRows = [
      headers.join(","),
      ...blocks.map(block => {
        const inc = block.incident || {};
        return [
          `"${inc.timestamp || ''}"`,
          inc.src_ip || "Unknown",
          inc.dst_ip || "Unknown",
          inc.attack_type || "Unknown",
          inc.node_id || "Unknown Asset",
          block.previous_hash || "GENESIS",
          block.hash || "MISSING",
          block.integrityStatus
        ].join(",");
      })
    ];

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `HawkGrid_Blockchain_Audit_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    // CHANGED: Removed 'h-full'. Now it fits the content exactly.
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm w-full">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Link className="h-5 w-5 text-[#06B6D4]" />
          <span>Immutable Forensic Ledger</span>
        </CardTitle>
      </CardHeader>
      
      {/* CHANGED: Removed flex properties that forced stretching */}
      <CardContent>
        <div className="space-y-1 mb-4">
          <div className="grid grid-cols-3 gap-2 text-xs text-gray-400 uppercase tracking-wider font-mono px-3">
            <div>Block Event</div>
            <div className="text-center">Hash / Prev</div>
            <div className="text-right">Status</div>
          </div>
        </div>

        {/* CHANGED: Removed 'flex-1' and 'overflow'. It will just render the 5 items naturally. */}
        <div className="space-y-4 relative">
          {/* Vertical blockchain line - Matches height of this container exactly */}
          <div className="absolute left-[6px] top-0 bottom-0 w-[2px] bg-gradient-to-b from-[#06B6D4] via-[#06B6D4]/50 to-[#06B6D4]/20"></div>

          {loading ? (
             <div className="text-center text-gray-500 py-10">Syncing Ledger...</div>
          ) : (
            blocks.slice(0, 5).map((block, index) => { 
              const inc = block.incident || {};
              const isTampered = block.integrityStatus === "Tampered";
              const isGenesis = block.integrityStatus === "Genesis";

              return (
                <div key={block.hash || index} className="relative pl-6">
                  {/* Chain link dot */}
                  <div className={`
                    absolute left-0 top-6 w-[14px] h-[14px] rounded-full border-2 
                    ${isTampered ? "bg-red-500 border-red-900 shadow-red-500/50" : "bg-[#06B6D4] border-[#0F172A] shadow-[#06B6D4]/50"}
                    shadow-lg z-10
                  `}></div>

                  <div className={`
                    p-3 rounded-lg border transition-all
                    ${isTampered 
                      ? "border-red-500/50 bg-red-900/10 hover:border-red-500" 
                      : "border-gray-700/50 bg-gradient-to-br from-gray-800/40 to-gray-900/40 hover:border-[#06B6D4]/30"}
                  `}>
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className={`text-sm font-medium mb-0.5 ${isTampered ? "text-red-400" : "text-gray-200"}`}>
                          {inc.attack_type || "System Event"}
                        </h4>
                        <div className="font-mono text-[10px] text-gray-500">
                           {inc.timestamp ? new Date(inc.timestamp).toLocaleTimeString() : "Time Unknown"}
                        </div>
                      </div>

                      <div className={`flex items-center space-x-1 text-xs font-bold px-2 py-1 rounded border
                        ${isTampered 
                          ? "text-red-400 border-red-900 bg-red-900/20" 
                          : isGenesis 
                            ? "text-blue-400 border-blue-900 bg-blue-900/20"
                            : "text-[#22C55E] border-green-900 bg-green-900/20"
                        }
                      `}>
                        {isTampered ? <ShieldAlert className="h-3 w-3" /> : <CheckCircle2 className="h-3 w-3" />}
                        <span>{block.integrityStatus.toUpperCase()}</span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-1 text-[10px] font-mono bg-black/20 p-2 rounded">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Hash:</span>
                        <span className={isTampered ? "text-red-300" : "text-[#22C55E]"}>
                          {block.hash ? `${block.hash.substring(0, 10)}...${block.hash.slice(-4)}` : "N/A"}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Prev:</span>
                        <span className="text-gray-400">
                          {block.previous_hash ? `${block.previous_hash.substring(0, 10)}...${block.previous_hash.slice(-4)}` : "GENESIS"}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer Button - Sits naturally at the bottom now */}
        <div className="flex justify-end mt-4 pt-3 border-t border-gray-700/50">
          <Button 
            onClick={handleDownloadHistory}
            variant="outline" 
            className="border-[#06B6D4]/30 text-[#06B6D4] hover:bg-[#06B6D4]/10 hover:border-[#06B6D4]/50 text-xs h-8"
          >
            View Historical Forensics
            <ArrowRight className="ml-2 h-3 w-3" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}