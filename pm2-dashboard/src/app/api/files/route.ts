import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import { readdir, stat, readFile, writeFile, unlink, mkdir } from 'fs/promises';
import { join } from 'path';
import { existsSync } from 'fs';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const execAsync = promisify(exec);

interface FileItem {
  name: string;
  path: string;
  type: 'file' | 'directory';
  size: number;
  modified: string;
}

// GET - List files
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const dir = searchParams.get('dir') || '';
    const basePath = join(process.cwd(), '..');

    // Security check - prevent directory traversal
    const resolvedPath = basePath;
    const targetDir = dir ? join(resolvedPath, dir).normalize() : resolvedPath;

    if (!targetDir.startsWith(resolvedPath)) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    const files = await readdir(targetDir, { withFileTypes: true });

    const fileList: FileItem[] = [];
    for (const file of files) {
      if (file.name.startsWith('.') || file.name === 'node_modules') continue;

      const filePath = join(targetDir, file.name);
      const stats = await stat(filePath);

      fileList.push({
        name: file.name,
        path: filePath.replace(resolvedPath, '').replace(/\\/g, '/').replace(/^\//, ''),
        type: file.isDirectory() ? 'directory' : 'file',
        size: stats.size,
        modified: stats.mtime.toISOString(),
      });
    }

    // Sort: directories first, then files, both alphabetically
    fileList.sort((a, b) => {
      if (a.type === b.type) {
        return a.name.localeCompare(b.name);
      }
      return a.type === 'directory' ? -1 : 1;
    });

    return NextResponse.json({
      files: fileList,
      currentDir: dir,
      parentDir: dir ? dir.split('/').slice(0, -1).join('/') : '',
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message, files: [], currentDir: '', parentDir: '' }, { status: 500 });
  }
}

// POST - Read file content or create directory
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, path, name, content } = body;
    const basePath = join(process.cwd(), '..');
    const targetPath = join(basePath, path).normalize();

    if (!targetPath.startsWith(basePath)) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    if (action === 'read') {
      const content = await readFile(targetPath, 'utf-8');
      return NextResponse.json({ content });
    }

    if (action === 'createDir') {
      const newDirPath = join(targetPath, name);
      await mkdir(newDirPath, { recursive: true });
      return NextResponse.json({ success: true, message: 'Directory created' });
    }

    if (action === 'createFile') {
      const newFilePath = join(targetPath, name);
      await writeFile(newFilePath, content || '', 'utf-8');
      return NextResponse.json({ success: true, message: 'File created' });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// PUT - Update file
export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const { path, content } = body;
    const basePath = join(process.cwd(), '..');
    const targetPath = join(basePath, path).normalize();

    if (!targetPath.startsWith(basePath)) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    await writeFile(targetPath, content, 'utf-8');
    return NextResponse.json({ success: true, message: 'File updated' });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// DELETE - Delete file or directory
export async function DELETE(request: NextRequest) {
  try {
    const body = await request.json();
    const { path } = body;
    const basePath = join(process.cwd(), '..');
    const targetPath = join(basePath, path).normalize();

    if (!targetPath.startsWith(basePath)) {
      return NextResponse.json({ error: 'Access denied' }, { status: 403 });
    }

    // Use shell command for recursive delete
    await execAsync(`rm -rf "${targetPath}"`);

    return NextResponse.json({ success: true, message: 'Deleted successfully' });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
