import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readFile } from 'fs/promises';

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

  // Parse PM2 system logs (format: PM2        | timestamp message)
  const pm2Match = cleanLine.match(/PM2\s+\|\s+(\d{4}-\d{2}-\d{2}T[\d:]+):\s+(.+)/);
  if (pm2Match) {
    return {
      timestamp: pm2Match[1],
      process: 'PM2',
      processId: 'SYSTEM',
      level: 'PM2',
      message: pm2Match[2]
    };
  }

  // Parse process logs (format: 0|gmail-wa | timestamp message)
  const procMatch = cleanLine.match(/(\d+)\|([a-zA-Z0-9_-]+)\s+\|\s+(\d{4}-\d{2}-\d{2}[\sT][\d:]+):\s+(.+)/);
  if (procMatch) {
    const message = procMatch[4];
    let level: 'info' | 'error' | 'warn' = 'info';

    if (message.toLowerCase().includes('error') || message.toLowerCase().includes('exception')) {
      level = 'error';
    } else if (message.toLowerCase().includes('warn')) {
      level = 'warn';
    }

    return {
      timestamp: procMatch[3],
      process: procMatch[2],
      processId: procMatch[1],
      level,
      message
    };
  }

  return null;
}

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const lines = parseInt(searchParams.get('lines') || '50');
    const processName = searchParams.get('process');

    // Get logs from PM2
    const { stdout, stderr } = await execAsync(`pm2 logs --nostream --lines ${lines}`);

    const allLogs: LogLine[] = [];
    const logLines = stdout.split('\n');

    for (const line of logLines) {
      const parsed = parsePM2LogLine(line);
      if (parsed) {
        if (!processName || parsed.process === processName || parsed.process === 'PM2') {
          allLogs.push(parsed);
        }
      }
    }

    // Sort by timestamp (newest first)
    allLogs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));

    return NextResponse.json({
      logs: allLogs.slice(0, lines),
      total: allLogs.length,
      processes: [...new Set(allLogs.map(l => l.process))]
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message, logs: [], processes: [] }, { status: 500 });
  }
}
