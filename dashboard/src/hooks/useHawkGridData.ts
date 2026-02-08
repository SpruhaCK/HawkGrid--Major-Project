// import { useState, useEffect } from 'react';

// export const useHawkGridData = () => {
//   // Capture the exact time the dashboard was opened to filter out historical logs
//   const [sessionStartTime] = useState(new Date()); 
//   const [alerts, setAlerts] = useState([]);
//   const [metrics, setMetrics] = useState({ totalAttacks: 0, types: {} });

//   const fetchData = async () => {
//     try {
//       // Connect to the Log Bridge server we'll set up on port 3001
//       const response = await fetch('http://localhost:3001/api/live-logs'); 
//       const allLogs = await response.json();
      
//       // Filter logs to only include attacks performed after the dashboard was loaded
//       const sessionAlerts = allLogs.filter((log: any) => {
//         const logTime = new Date(log.timestamp);
//         return logTime >= sessionStartTime;
//       });

//       // Sort by newest first so the latest curl attack appears at the top
//       setAlerts(sessionAlerts.sort((a: any, b: any) => 
//         new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
//       ));

//       // Metrics can still show historical data or be filtered similarly
//       // For now, we update metrics based on session alerts
//       setMetrics({
//         totalAttacks: sessionAlerts.length,
//         types: sessionAlerts.reduce((acc: any, curr: any) => {
//           acc[curr.attack_type] = (acc[curr.attack_type] || 0) + 1;
//           return acc;
//         }, {})
//       });

//     } catch (error) {
//       console.error("HawkGrid: Synchronizing with ledger...", error);
//     }
//   };

//   useEffect(() => {
//     // Poll every 2 seconds to ensure fast updates when you run curl commands
//     const interval = setInterval(fetchData, 2000);
//     return () => clearInterval(interval);
//   }, [sessionStartTime]);

//   return { alerts, metrics };
// };