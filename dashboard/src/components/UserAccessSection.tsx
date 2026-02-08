import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Users, Clock, Shield, User, Crown, Settings } from "lucide-react";

const activeUsers = [
  {
    id: 1,
    username: "admin1",
    role: "Administrator",
    lastLogin: "14:26:34",
    ip: "192.168.1.45",
    status: "online",
    icon: Crown
  },
  {
    id: 2,
    username: "security_ops",
    role: "Security Analyst",
    lastLogin: "13:45:22",
    ip: "192.168.1.67",
    status: "online",
    icon: Shield
  },
  {
    id: 3,
    username: "monitor1",
    role: "SOC Operator",
    lastLogin: "12:15:08",
    ip: "192.168.1.89",
    status: "idle",
    icon: User
  },
  {
    id: 4,
    username: "sys_admin",
    role: "System Admin",
    lastLogin: "11:30:45",
    ip: "192.168.1.12",
    status: "offline",
    icon: Settings
  }
];

const getRoleColor = (role: string) => {
  switch (role) {
    case "Administrator": return "bg-purple-600/20 text-purple-400 border-purple-500/30";
    case "Security Analyst": return "bg-red-600/20 text-red-400 border-red-500/30";
    case "SOC Operator": return "bg-blue-600/20 text-blue-400 border-blue-500/30";
    case "System Admin": return "bg-green-600/20 text-green-400 border-green-500/30";
    default: return "bg-gray-600/20 text-gray-400 border-gray-500/30";
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case "online": return { color: "text-green-400", bg: "bg-green-500" };
    case "idle": return { color: "text-yellow-400", bg: "bg-yellow-500" };
    case "offline": return { color: "text-gray-400", bg: "bg-gray-500" };
    default: return { color: "text-gray-400", bg: "bg-gray-500" };
  }
};

export function UserAccessSection() {
  return (
    <Card className="bg-gray-800/50 border-gray-700 backdrop-blur-sm">
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Users className="h-5 w-5 text-blue-400" />
          <span>User Access</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-2 bg-gray-800/30 rounded border border-gray-700/30">
              <div className="text-lg font-mono text-cyan-400">4</div>
              <div className="text-xs text-gray-400">Total Users</div>
            </div>
            <div className="text-center p-2 bg-gray-800/30 rounded border border-gray-700/30">
              <div className="text-lg font-mono text-green-400">2</div>
              <div className="text-xs text-gray-400">Online</div>
            </div>
            <div className="text-center p-2 bg-gray-800/30 rounded border border-gray-700/30">
              <div className="text-lg font-mono text-yellow-400">1</div>
              <div className="text-xs text-gray-400">Idle</div>
            </div>
          </div>

          {/* User List */}
          <div className="space-y-3">
            {activeUsers.map((user) => {
              const IconComponent = user.icon;
              const statusInfo = getStatusColor(user.status);
              
              return (
                <div 
                  key={user.id}
                  className="p-3 rounded border bg-gray-800/30 border-gray-700/30 hover:bg-gray-800/40 transition-colors"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <IconComponent className="h-4 w-4 text-gray-400" />
                      <span className="text-sm text-gray-300">{user.username}</span>
                      <div className={`w-2 h-2 rounded-full ${statusInfo.bg}`}></div>
                    </div>
                    <span className={`text-xs uppercase tracking-wide ${statusInfo.color}`}>
                      {user.status}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <Badge className={getRoleColor(user.role)}>
                      {user.role}
                    </Badge>
                    
                    <div className="text-xs text-gray-500 space-y-1">
                      <div className="flex items-center space-x-1">
                        <Clock className="h-3 w-3" />
                        <span>Last login: {user.lastLogin}</span>
                      </div>
                      <div className="font-mono text-cyan-400">
                        {user.ip}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}