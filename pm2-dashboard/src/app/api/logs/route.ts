import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile, readdir } from 'fs/promises';
import { existsSync } from 'fs';
import path from 'path';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const execAsync = promisify(exec);

interface LogLine {
  timestamp: string;
  process: string;
  processId: string;
  level: 'info' | 'error' | 'warn' | 'PM2';
  message: string;
}

function parsePM2LogLine(line: string): LogLine | null {
  if (!line || line.trim().length === 0) return null;

  // Remove ANSI color codes
  const cleanLine = line.replace(/\x1b\[[0-9;]*m/g, '');

  // Skip PM2 header lines
  if (cleanLine.includes('[TAILING]') ||
      cleanLine.includes('last') ||
      cleanLine.includes('.log last') ||
      cleanLine.startsWith('C:\\') ||
      cleanLine.match(/^\[90m/)) {
    return null;
  }

  // Try to match process logs with various formats
  // Format 1: "2026-01-21 17:46:21 - ProcessName - LEVEL - message"
  const standardMatch = cleanLine.match(/(\d{4}-\d{2}-\d{2}\s+[\d:]+)\s+-\s+([a-zA-Z0-9_]+)\s+-\s+(INFO|ERROR|WARN|WARNING)\s+-\s+(.+)/i);
  if (standardMatch) {
    let level: 'info' | 'error' | 'warn' = 'info';
    const levelStr = standardMatch[3].toUpperCase();
    if (levelStr.includes('ERROR')) level = 'error';
    else if (levelStr.includes('WARN')) level = 'warn';

    return {
      timestamp: standardMatch[1],
      process: standardMatch[2],
      processId: '1',
      level,
      message: standardMatch[4]
    };
  }

  // Format 2: Simple timestamp format "2026-01-21 17:46:21, message"
  const simpleMatch = cleanLine.match(/(\d{4}-\d{2}-\d{2}\s+[\d:,]+),?\s*(.+)/);
  if (simpleMatch) {
    const message = simpleMatch[2];
    let level: 'info' | 'error' | 'warn' = 'info';

    if (message.toLowerCase().includes('error') || message.toLowerCase().includes('exception')) {
      level = 'error';
    } else if (message.toLowerCase().includes('warn')) {
      level = 'warn';
    }

    return {
      timestamp: simpleMatch[1],
      process: 'SYSTEM',
      processId: '0',
      level,
      message
    };
  }

  // Format 3: Python logging format "2026-01-21 15:40:19 - ProcessName - message"
  const pythonMatch = cleanLine.match(/(\d{4}-\d{2}-\d{2}\s+[\d:]+)\s+-\s+([a-zA-Z0-9_]+)\s+-\s+(.+)/);
  if (pythonMatch) {
    const message = pythonMatch[3];
    let level: 'info' | 'error' | 'warn' = 'info';

    if (message.toLowerCase().includes('error') || message.toLowerCase().includes('exception')) {
      level = 'error';
    } else if (message.toLowerCase().includes('warn')) {
      level = 'warn';
    }

    return {
      timestamp: pythonMatch[1],
      process: pythonMatch[2],
      processId: '1',
      level,
      message
    };
  }

  // If nothing matches, treat as a generic log line
  if (cleanLine.length > 10) {
    let level: 'info' | 'error' | 'warn' = 'info';
    if (cleanLine.toLowerCase().includes('error') || cleanLine.toLowerCase().includes('exception')) {
      level = 'error';
    } else if (cleanLine.toLowerCase().includes('warn')) {
      level = 'warn';
    }

    return {
      timestamp: new Date().toISOString(),
      process: 'UNKNOWN',
      processId: '0',
      level,
      message: cleanLine.substring(0, 500) // Limit message length
    };
  }

  return null;
}

async function readLogFromFile(filePath: string, processName: string): Promise<LogLine[]> {
  if (!existsSync(filePath)) {
    return [];
  }

  try {
    const content = await readFile(filePath, 'utf-8');
    const lines = content.split('\n');
    const logs: LogLine[] = [];

    for (const line of lines) {
      const parsed = parsePM2LogLine(line);
      if (parsed) {
        parsed.process = processName;
        logs.push(parsed);
      }
    }

    return logs;
  } catch (error) {
    console.error(`Error reading log file ${filePath}:`, error);
    return [];
  }
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const lines = parseInt(searchParams.get('lines') || '50');
    const processName = searchParams.get('process');

    // Get list of PM2 processes (use jlist command)
    const { stdout: pm2List } = await execAsync('pm2 jlist');
    const processes = JSON.parse(pm2List || '[]');

    const allLogs: LogLine[] = [];

    // Read logs from each process's log files
    const pm2LogPath = path.join(process.env.USERPROFILE || '', '.pm2', 'logs');

    for (const proc of processes) {
      if (proc.name === 'ad-dashboard') continue; // Skip dashboard logs

      const outLog = path.join(pm2LogPath, `${proc.name}-out.log`);
      const errorLog = path.join(pm2LogPath, `${proc.name}-error.log`);

      // Read out log
      const outLogs = await readLogFromFile(outLog, proc.name);
      allLogs.push(...outLogs);

      // Read error log
      const errorLogs = await readLogFromFile(errorLog, proc.name);
      allLogs.push(...errorLogs);
    }

    // Also try to get logs from the main Logs directory
    const vaultLogsPath = path.join(process.cwd(), '..', 'Logs');
    if (existsSync(vaultLogsPath)) {
      const logFiles = await readdir(vaultLogsPath);

      for (const file of logFiles) {
        if (file.endsWith('.log') && !file.includes('pm2')) {
          const filePath = path.join(vaultLogsPath, file);
          const logs = await readLogFromFile(filePath, file.replace('.log', '').replace('_', '-'));
          allLogs.push(...logs);
        }
      }
    }

    // Filter by process if specified
    let filteredLogs = allLogs;
    if (processName && processName !== 'all') {
      filteredLogs = allLogs.filter(l =>
        l.process.toLowerCase().includes(processName.toLowerCase()) ||
        l.processId === processName
      );
    }

    // Sort by timestamp (newest first) and limit
    filteredLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
    const limitedLogs = filteredLogs.slice(0, lines);

    // Get unique process names
    const uniqueProcesses = [...new Set(allLogs.map(l => l.process))];

    return NextResponse.json({
      logs: limitedLogs,
      total: filteredLogs.length,
      processes: uniqueProcesses
    });
  } catch (error: any) {
    console.error('Error in logs API:', error);
    return NextResponse.json({
      error: error.message,
      logs: [],
      processes: [],
      total: 0
    }, { status: 500 });
  }
}
