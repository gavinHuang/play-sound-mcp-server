# TypeScript MCP Implementation Guide

## Overview

This document provides a detailed guide for implementing the MCP Play Sound Server using TypeScript and the official MCP TypeScript SDK, including architecture patterns, code examples, and best practices.

## TypeScript MCP SDK Analysis

### SDK Structure and Capabilities

The official TypeScript MCP SDK provides:
- **Server Framework**: `@modelcontextprotocol/sdk/server`
- **Transport Layer**: stdio, SSE, WebSocket transports
- **Type Safety**: Zod schema validation
- **Tool Registration**: Declarative tool definition
- **Error Handling**: Structured error responses

### Key Components

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";
import { z } from "zod";
```

## Architecture Translation from Python

### Comparison: Python FastMCP vs TypeScript MCP SDK

| Feature | Python FastMCP | TypeScript MCP SDK |
|---------|-----------------|-------------------|
| **Tool Definition** | Decorator-based (`@mcp.tool()`) | Method-based (`server.tool()`) |
| **Schema Generation** | From type hints + docstrings | Explicit Zod schemas |
| **Error Handling** | Exception-based | Promise rejection + structured errors |
| **Configuration** | Dataclass + env vars | Interface + env vars |
| **Validation** | Runtime type checking | Compile-time + runtime validation |
| **Transport** | Built-in stdio | Explicit transport setup |

### TypeScript Project Structure

```
mcp-server-play-sound-ts/
├── src/
│   ├── index.ts              # Main entry point
│   ├── server.ts             # MCP server implementation
│   ├── audio/
│   │   ├── player.ts         # Audio player logic
│   │   ├── detector.ts       # System tool detection
│   │   └── types.ts          # Audio-related types
│   ├── config/
│   │   ├── schema.ts         # Configuration schema
│   │   └── loader.ts         # Environment loading
│   └── utils/
│       ├── errors.ts         # Error handling
│       └── validation.ts     # File validation
├── assets/
│   └── default_notification.wav
├── tests/
├── package.json
├── tsconfig.json
└── README.md
```

## Core Implementation

### 1. Main Server Implementation

```typescript
// src/server.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { AudioPlayer } from "./audio/player.js";
import { ServerConfig, loadConfig } from "./config/loader.js";
import { PlaySoundError } from "./utils/errors.js";

export class PlaySoundMcpServer {
  private server: McpServer;
  private audioPlayer: AudioPlayer;
  private config: ServerConfig;

  constructor() {
    this.config = loadConfig();
    this.audioPlayer = new AudioPlayer(this.config);
    
    this.server = new McpServer({
      name: "play-sound",
      version: "1.0.0",
      description: "MCP server for audio playback notifications"
    });

    this.setupTools();
  }

  private setupTools(): void {
    // Play notification sound tool
    this.server.tool(
      "play_notification_sound",
      {
        message: z.string().optional().describe("Custom message to log with the notification"),
        sound_type: z.enum(["default", "custom", "auto"]).optional().describe("Type of sound to play"),
        volume: z.number().min(0).max(1).optional().describe("Volume level (0.0-1.0)")
      },
      async ({ message = "", sound_type = "auto", volume }) => {
        try {
          const result = await this.audioPlayer.playSound({
            type: sound_type,
            volume: volume ?? this.config.volumeLevel,
            message
          });

          return {
            content: [{
              type: "text",
              text: `✅ Notification played successfully. ${message}`
            }]
          };
        } catch (error) {
          const errorMessage = error instanceof PlaySoundError 
            ? error.message 
            : `Unexpected error: ${error}`;

          return {
            content: [{
              type: "text",
              text: `❌ Failed to play notification: ${errorMessage}`
            }],
            isError: true
          };
        }
      }
    );

    // Get audio status tool
    this.server.tool(
      "get_audio_status",
      {},
      async () => {
        const status = await this.audioPlayer.getStatus();
        
        return {
          content: [{
            type: "text",
            text: JSON.stringify(status, null, 2)
          }]
        };
      }
    );
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    
    console.error("🔊 MCP Play Sound Server started");
  }
}
```

### 2. Audio Player Implementation

```typescript
// src/audio/player.ts
import { spawn } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { ServerConfig } from "../config/schema.js";
import { SystemAudioDetector, AudioTool } from "./detector.js";
import { PlaySoundError } from "../utils/errors.js";

export interface PlaySoundOptions {
  type: "default" | "custom" | "auto";
  volume?: number;
  message?: string;
}

export interface PlaybackResult {
  success: boolean;
  tool?: string;
  duration?: number;
  error?: string;
}

export interface AudioStatus {
  availableTools: string[];
  customSoundPath?: string;
  customSoundValid: boolean;
  defaultSoundPath: string;
  lastPlayback?: PlaybackResult;
}

export class AudioPlayer {
  private config: ServerConfig;
  private availableTools: AudioTool[] = [];
  private defaultSoundPath: string;
  private lastPlayback?: PlaybackResult;

  constructor(config: ServerConfig) {
    this.config = config;
    this.defaultSoundPath = this.resolveDefaultSoundPath();
  }

  async initialize(): Promise<void> {
    this.availableTools = await SystemAudioDetector.detectAvailableTools();
    
    if (this.availableTools.length === 0) {
      throw new PlaySoundError("No audio playback tools available on this system");
    }

    // Validate default sound exists
    try {
      await fs.access(this.defaultSoundPath);
    } catch {
      throw new PlaySoundError(`Default sound file not found: ${this.defaultSoundPath}`);
    }

    console.error(`🔊 Audio player initialized with tools: ${this.availableTools.map(t => t.command).join(", ")}`);
  }

  async playSound(options: PlaySoundOptions): Promise<PlaybackResult> {
    const startTime = Date.now();

    try {
      let soundPath: string;

      // Determine which sound to play
      if (options.type === "custom" && this.config.customSoundPath) {
        soundPath = await this.validateCustomSound();
      } else if (options.type === "auto" && this.config.customSoundPath) {
        try {
          soundPath = await this.validateCustomSound();
        } catch {
          if (this.config.enableFallback) {
            soundPath = this.defaultSoundPath;
          } else {
            throw new PlaySoundError("Custom sound invalid and fallback disabled");
          }
        }
      } else {
        soundPath = this.defaultSoundPath;
      }

      // Select appropriate tool
      const tool = this.selectAudioTool(soundPath);
      if (!tool) {
        throw new PlaySoundError(`No compatible audio tool found for ${path.extname(soundPath)}`);
      }

      // Execute playback
      await this.executePlayback(tool, soundPath, options.volume);

      const result: PlaybackResult = {
        success: true,
        tool: tool.command,
        duration: Date.now() - startTime
      };

      this.lastPlayback = result;
      return result;

    } catch (error) {
      const result: PlaybackResult = {
        success: false,
        error: error instanceof Error ? error.message : String(error),
        duration: Date.now() - startTime
      };

      this.lastPlayback = result;

      // Try fallback if enabled and this wasn't already a fallback
      if (this.config.enableFallback && options.type !== "default") {
        try {
          return await this.playSound({ ...options, type: "default" });
        } catch {
          // Fallback also failed, return original error
        }
      }

      throw error;
    }
  }

  async getStatus(): Promise<AudioStatus> {
    const customSoundValid = this.config.customSoundPath 
      ? await this.isCustomSoundValid()
      : false;

    return {
      availableTools: this.availableTools.map(t => t.command),
      customSoundPath: this.config.customSoundPath,
      customSoundValid,
      defaultSoundPath: this.defaultSoundPath,
      lastPlayback: this.lastPlayback
    };
  }

  private async validateCustomSound(): Promise<string> {
    if (!this.config.customSoundPath) {
      throw new PlaySoundError("No custom sound path configured");
    }

    try {
      const stats = await fs.stat(this.config.customSoundPath);
      
      // Check file size
      const sizeMB = stats.size / (1024 * 1024);
      if (sizeMB > this.config.maxFileSizeMB) {
        throw new PlaySoundError(`Custom sound file too large: ${sizeMB.toFixed(1)}MB > ${this.config.maxFileSizeMB}MB`);
      }

      // Check file extension
      const ext = path.extname(this.config.customSoundPath).toLowerCase();
      if (!this.config.allowedAudioExtensions.has(ext)) {
        throw new PlaySoundError(`Unsupported audio format: ${ext}`);
      }

      return this.config.customSoundPath;
    } catch (error) {
      if (error instanceof PlaySoundError) {
        throw error;
      }
      throw new PlaySoundError(`Custom sound file not accessible: ${error}`);
    }
  }

  private async isCustomSoundValid(): Promise<boolean> {
    try {
      await this.validateCustomSound();
      return true;
    } catch {
      return false;
    }
  }

  private selectAudioTool(filePath: string): AudioTool | null {
    const extension = path.extname(filePath).toLowerCase().slice(1);
    
    // Find tools that support this format
    const compatibleTools = this.availableTools.filter(tool =>
      tool.formats.includes(extension)
    );

    if (compatibleTools.length === 0) {
      return null;
    }

    // Prioritize tools by preference
    const toolPriority = ["afplay", "play", "aplay", "paplay", "powershell"];
    
    for (const preferredTool of toolPriority) {
      const tool = compatibleTools.find(t => t.command === preferredTool);
      if (tool) {
        return tool;
      }
    }

    return compatibleTools[0];
  }

  private async executePlayback(tool: AudioTool, filePath: string, volume?: number): Promise<void> {
    return new Promise((resolve, reject) => {
      const args = this.buildAudioCommand(tool, filePath, volume);
      const process = spawn(tool.command, args);

      const timeout = setTimeout(() => {
        process.kill();
        reject(new PlaySoundError(`Audio playback timeout (${this.config.playbackTimeoutSeconds}s)`));
      }, this.config.playbackTimeoutSeconds * 1000);

      process.on("close", (code) => {
        clearTimeout(timeout);
        if (code === 0) {
          resolve();
        } else {
          reject(new PlaySoundError(`Audio tool exited with code ${code}`));
        }
      });

      process.on("error", (error) => {
        clearTimeout(timeout);
        reject(new PlaySoundError(`Audio tool error: ${error.message}`));
      });
    });
  }

  private buildAudioCommand(tool: AudioTool, filePath: string, volume?: number): string[] {
    const args = [...tool.args];

    // Add file path
    if (tool.command === "powershell") {
      // Special case for PowerShell
      const command = `(New-Object Media.SoundPlayer "${filePath}").PlaySync()`;
      args.push(command);
    } else {
      // Add volume control if supported and specified
      if (volume !== undefined && tool.supportsVolume) {
        if (tool.command === "afplay") {
          args.push("-v", volume.toString());
        } else if (tool.command === "play") {
          args.push("-v", volume.toString());
        }
      }
      
      args.push(filePath);
    }

    return args;
  }

  private resolveDefaultSoundPath(): string {
    // In a real implementation, this would resolve to the bundled asset
    return path.join(__dirname, "..", "..", "assets", "default_notification.wav");
  }
}
```

### 3. Configuration Management

```typescript
// src/config/schema.ts
import { z } from "zod";

export const ServerConfigSchema = z.object({
  customSoundPath: z.string().optional(),
  volumeLevel: z.number().min(0).max(1).default(0.8),
  enableFallback: z.boolean().default(true),
  maxFileSizeMB: z.number().int().min(1).max(100).default(10),
  playbackTimeoutSeconds: z.number().int().min(1).max(300).default(30),
  audioBackend: z.enum(["auto", "system", "native"]).default("auto"),
  enableAudioCache: z.boolean().default(true),
  cacheSizeLimit: z.number().int().min(1).max(20).default(5),
  allowedAudioExtensions: z.set(z.string()).default(new Set([".wav", ".mp3", ".flac", ".ogg", ".m4a"])),
  restrictToUserHome: z.boolean().default(true)
});

export type ServerConfig = z.infer<typeof ServerConfigSchema>;

// src/config/loader.ts
import { ServerConfig, ServerConfigSchema } from "./schema.js";
import { PlaySoundError } from "../utils/errors.js";

export function loadConfig(): ServerConfig {
  try {
    const rawConfig = {
      customSoundPath: process.env.CUSTOM_SOUND_PATH,
      volumeLevel: parseFloat(process.env.VOLUME_LEVEL || "0.8"),
      enableFallback: process.env.ENABLE_FALLBACK !== "false",
      maxFileSizeMB: parseInt(process.env.MAX_FILE_SIZE_MB || "10"),
      playbackTimeoutSeconds: parseInt(process.env.PLAYBACK_TIMEOUT_SECONDS || "30"),
      audioBackend: process.env.AUDIO_BACKEND || "auto",
      enableAudioCache: process.env.ENABLE_AUDIO_CACHE !== "false",
      cacheSizeLimit: parseInt(process.env.CACHE_SIZE_LIMIT || "5"),
      allowedAudioExtensions: parseExtensions(process.env.ALLOWED_AUDIO_EXTENSIONS),
      restrictToUserHome: process.env.RESTRICT_TO_USER_HOME !== "false"
    };

    return ServerConfigSchema.parse(rawConfig);
  } catch (error) {
    if (error instanceof z.ZodError) {
      const issues = error.issues.map(issue => `${issue.path.join(".")}: ${issue.message}`);
      throw new PlaySoundError(`Configuration validation failed:\n${issues.join("\n")}`);
    }
    throw error;
  }
}

function parseExtensions(value?: string): Set<string> {
  if (!value) {
    return new Set([".wav", ".mp3", ".flac", ".ogg", ".m4a"]);
  }

  const extensions = value.split(",").map(ext => {
    ext = ext.trim();
    return ext.startsWith(".") ? ext : `.${ext}`;
  });

  return new Set(extensions);
}
```

### 4. Entry Point

```typescript
// src/index.ts
import { PlaySoundMcpServer } from "./server.js";

async function main(): Promise<void> {
  try {
    const server = new PlaySoundMcpServer();
    await server.run();
  } catch (error) {
    console.error("Failed to start MCP Play Sound Server:", error);
    process.exit(1);
  }
}

// Handle graceful shutdown
process.on("SIGINT", () => {
  console.error("Received SIGINT, shutting down gracefully...");
  process.exit(0);
});

process.on("SIGTERM", () => {
  console.error("Received SIGTERM, shutting down gracefully...");
  process.exit(0);
});

main().catch((error) => {
  console.error("Unhandled error:", error);
  process.exit(1);
});
```

## Package Configuration

### package.json

```json
{
  "name": "mcp-server-play-sound",
  "version": "1.0.0",
  "description": "MCP server for audio playback notifications",
  "type": "module",
  "main": "dist/index.js",
  "bin": {
    "mcp-server-play-sound": "dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint src/**/*.ts",
    "format": "prettier --write src/**/*.ts"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "tsx": "^4.0.0",
    "jest": "^29.0.0",
    "@types/jest": "^29.0.0",
    "eslint": "^8.0.0",
    "prettier": "^3.0.0"
  },
  "keywords": ["mcp", "audio", "notifications", "typescript"],
  "license": "MIT"
}
```

### tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Node",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "allowJs": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "declaration": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

## Advantages of TypeScript Implementation

### 1. **Type Safety**
- Compile-time error detection
- Better IDE support and autocomplete
- Zod runtime validation

### 2. **Modern JavaScript Features**
- Native async/await support
- ES modules
- Better error handling with promises

### 3. **Ecosystem Integration**
- NPM package distribution
- Node.js tooling ecosystem
- Jest testing framework

### 4. **Performance**
- V8 JavaScript engine optimization
- Efficient subprocess handling
- Memory management

## Migration Considerations

### From Python to TypeScript

1. **Audio Library Strategy**: Replace simpleaudio with system command approach
2. **Configuration**: Zod schemas instead of dataclasses
3. **Error Handling**: Promise-based instead of exception-based
4. **Testing**: Jest instead of pytest
5. **Distribution**: NPM instead of PyPI

### Effort Estimation

- **Core Implementation**: 2-3 weeks
- **Testing**: 1 week
- **Documentation**: 1 week
- **Total**: 4-5 weeks

## Conclusion

The TypeScript implementation offers excellent type safety and modern JavaScript features, but requires a different approach to audio playback using system commands rather than native libraries. The architecture translates well from Python, with the main differences being in the audio strategy and type system approach.
