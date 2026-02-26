import React, { useEffect, useState, useRef } from 'react';
import * as Collapsible from '@radix-ui/react-collapsible';
import { Terminal, Activity, ChevronUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

interface NetLog {
  TimeGenerated: string;
  SrcIP: string;
  DestIP: string;
  DestPort: number;
  FlowStatus: string;
}

export const LiveConsole = () => {
  const [open, setOpen] = useState(false);
  const [logs, setLogs] = useState<NetLog[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/network-logs');
        const data = await res.json();
        setLogs(data);
      } catch (e) { 
        console.error("Fetch error:", e); 
      }
    };
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (scrollRef.current && open) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs, open]);

  return (
    <div className="w-full max-w-[1600px] mx-auto px-4">
      {/* Card Wrapper: Exact match for AttackAnalysisSection */}
      <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm rounded-b-none border-b-0 shadow-2xl">
        <Collapsible.Root open={open} onOpenChange={setOpen}>
          
          <Collapsible.Trigger asChild>
            <CardHeader className="cursor-pointer hover:bg-gray-700/30 transition-colors py-4">
              <div className="flex items-center justify-between w-full">
                <CardTitle className="flex items-center space-x-2 text-base">
                  <Terminal className="h-5 w-5 text-blue-400" />
                  <span className="text-gray-100 uppercase tracking-tight">Core Network Logs</span>
                  <div className="flex items-center space-x-2 pl-4 border-l border-gray-700 ml-2">
                    <Activity className="h-4 w-4 text-green-500 animate-pulse" />
                    <span className="text-[10px] font-mono text-green-500 font-bold uppercase tracking-widest">Live Feed</span>
                  </div>
                </CardTitle>
                
                <div className="flex items-center space-x-4">
                  <span className="text-[10px] font-mono text-gray-500 uppercase">
                    {logs.length} Packets Captured
                  </span>
                  <ChevronUp className={`h-5 w-5 text-gray-400 transition-transform duration-300 ${open ? 'rotate-180' : ''}`} />
                </div>
              </div>
            </CardHeader>
          </Collapsible.Trigger>

          <Collapsible.Content className="transition-all">
            <CardContent className="p-0 border-t border-gray-700">
              <div 
                ref={scrollRef} 
                className="h-72 overflow-y-auto bg-black/20"
              >
                <Table>
                  <TableHeader className="sticky top-0 bg-gray-900/90 backdrop-blur-md z-10">
                    <TableRow className="border-gray-700 hover:bg-transparent">
                      <TableHead className="text-gray-400 text-[11px] py-2 uppercase">Timestamp</TableHead>
                      <TableHead className="text-gray-400 text-[11px] py-2 uppercase">Source IP</TableHead>
                      <TableHead className="text-gray-400 text-[11px] py-2 uppercase text-center">Direction</TableHead>
                      <TableHead className="text-gray-400 text-[11px] py-2 uppercase">Destination Asset</TableHead>
                      <TableHead className="text-gray-400 text-[11px] py-2 uppercase text-right">Flow Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {logs.length > 0 ? logs.map((log, i) => (
                      <TableRow key={i} className="border-gray-800/50 hover:bg-gray-700/20">
                        <TableCell className="font-mono text-[10px] text-gray-400 py-1">
                          {new Date(log.TimeGenerated).toLocaleTimeString()}
                        </TableCell>
                        <TableCell className="font-mono text-[11px] text-[#06B6D4] py-1">
                          {log.SrcIP}
                        </TableCell>
                        <TableCell className="text-center text-gray-600 py-1">
                          →
                        </TableCell>
                        <TableCell className="font-mono text-[11px] text-purple-400 py-1">
                          {log.DestIP}:{log.DestPort}
                        </TableCell>
                        <TableCell className="text-right py-1">
                          <Badge className={`text-[9px] px-2 py-0 h-4 border ${
                            log.FlowStatus === 'Allowed' 
                            ? 'bg-green-500/10 text-green-500 border-green-500/30' 
                            : 'bg-red-500/10 text-red-500 border-red-500/30'
                          }`}>
                            {log.FlowStatus}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    )) : (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-20 text-gray-500 font-mono text-xs italic animate-pulse">
                          Establishing secure handshake with HawkGrid Log Engine...
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Collapsible.Content>
        </Collapsible.Root>
      </Card>
    </div>
  );
};