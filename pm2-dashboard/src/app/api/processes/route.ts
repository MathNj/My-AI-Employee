import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  try {
    // Use PM2 CLI via child_process to avoid module bundling issues
    const { stdout, stderr } = await execAsync('pm2 jlist');

    if (stderr && !stdout) {
      return NextResponse.json({ error: stderr }, { status: 500 });
    }

    const processes = JSON.parse(stdout);

    const formatted = processes.map((p: any) => ({
      id: p.pm2_env.pm_id,
      pid: p.pid,
      name: p.name,
      status: p.pm2_env.status,
      cpu: p.monit?.cpu || 0,
      memory: p.monit?.memory || 0,
      uptime: p.pm2_env.uptime,
      restarts: p.pm2_env.restart_time || 0,
      mode: p.pm2_env.exec_mode,
    }));

    return NextResponse.json(formatted);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
