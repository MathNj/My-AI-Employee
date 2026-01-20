import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const execAsync = promisify(exec);

interface ActionRequestBody {
  action: 'start' | 'stop' | 'restart' | 'reload' | 'delete';
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { id } = params;
    const body: ActionRequestBody = await request.json();
    const { action } = body;

    const processId = parseInt(id);
    const validActions = ['start', 'stop', 'restart', 'reload', 'delete'];

    if (!validActions.includes(action)) {
      return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

    // Use PM2 CLI via child_process
    const { stdout, stderr } = await execAsync(`pm2 ${action} ${processId}`);

    if (stderr && !stdout) {
      return NextResponse.json({ error: stderr }, { status: 500 });
    }

    return NextResponse.json({ success: true, action, processId });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
