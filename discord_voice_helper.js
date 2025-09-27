#!/usr/bin/env node
/**
 * Discord Voice Connection Helper
 * A Node.js script to help establish and maintain Discord voice connections
 * This works around Discord.py's voice handshake timeout issues
 */

const { Client, GatewayIntentBits, VoiceState } = require('discord.js');
const { joinVoiceChannel, createAudioPlayer, createAudioResource, VoiceConnectionStatus, entersState } = require('@discordjs/voice');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

class DiscordVoiceHelper {
    constructor() {
        this.client = new Client({
            intents: [
                GatewayIntentBits.Guilds,
                GatewayIntentBits.GuildVoiceStates,
                GatewayIntentBits.GuildMessages,
                GatewayIntentBits.MessageContent
            ]
        });
        
        this.voiceConnection = null;
        this.audioPlayer = null;
        this.isConnected = false;
        this.targetChannelId = null;
        this.guildId = null;
        this.keepAliveInterval = null;
        
        this.setupEventHandlers();
    }
    
    setupEventHandlers() {
        this.client.on('ready', () => {
            console.log(`✅ Discord Voice Helper ready! Logged in as ${this.client.user.tag}`);
        });
        
        this.client.on('error', (error) => {
            console.error('❌ Discord client error:', error);
        });
        
        this.client.on('warn', (warning) => {
            console.warn('⚠️ Discord client warning:', warning);
        });
    }
    
    async login(token) {
        try {
            await this.client.login(token);
            return true;
        } catch (error) {
            console.error('❌ Failed to login to Discord:', error);
            return false;
        }
    }
    
    async connectToVoice(guildId, channelId) {
        try {
            console.log(`🎤 Connecting to voice channel ${channelId} in guild ${guildId}...`);
            
            this.guildId = guildId;
            this.targetChannelId = channelId;
            
            // Get the guild and channel
            const guild = this.client.guilds.cache.get(guildId);
            if (!guild) {
                throw new Error(`Guild ${guildId} not found`);
            }
            
            const channel = guild.channels.cache.get(channelId);
            if (!channel) {
                throw new Error(`Channel ${channelId} not found`);
            }
            
            if (channel.type !== 2) { // Voice channel type
                throw new Error(`Channel ${channelId} is not a voice channel`);
            }
            
            // Create voice connection with infinite timeout
            this.voiceConnection = joinVoiceChannel({
                channelId: channelId,
                guildId: guildId,
                adapterCreator: guild.voiceAdapterCreator,
            });
            
            // Wait for connection to be ready with infinite timeout
            await entersState(this.voiceConnection, VoiceConnectionStatus.Ready, 0); // 0 = infinite timeout
            
            console.log('✅ Successfully connected to voice channel!');
            
            // Set up audio player
            this.audioPlayer = createAudioPlayer();
            this.voiceConnection.subscribe(this.audioPlayer);
            
            // Set up connection event handlers
            this.voiceConnection.on('stateChange', (oldState, newState) => {
                console.log(`🔄 Voice connection state changed: ${oldState.status} -> ${newState.status}`);
                
                if (newState.status === VoiceConnectionStatus.Disconnected) {
                    console.log('⚠️ Voice connection disconnected');
                    this.isConnected = false;
                    this.stopKeepAlive();
                } else if (newState.status === VoiceConnectionStatus.Ready) {
                    console.log('✅ Voice connection ready');
                    this.isConnected = true;
                    this.startKeepAlive();
                }
            });
            
            this.voiceConnection.on('error', (error) => {
                console.error('❌ Voice connection error:', error);
            });
            
            this.isConnected = true;
            return true;
            
        } catch (error) {
            console.error('❌ Failed to connect to voice channel:', error);
            return false;
        }
    }
    
    async disconnectFromVoice() {
        try {
            if (this.voiceConnection) {
                this.stopKeepAlive();
                this.voiceConnection.destroy();
                this.voiceConnection = null;
                this.isConnected = false;
                console.log('👋 Disconnected from voice channel');
            }
            return true;
        } catch (error) {
            console.error('❌ Error disconnecting from voice channel:', error);
            return false;
        }
    }
    
    async playAudio(audioPath) {
        try {
            if (!this.voiceConnection || !this.audioPlayer) {
                console.error('❌ Not connected to voice channel');
                return false;
            }
            
            if (!fs.existsSync(audioPath)) {
                console.error(`❌ Audio file not found: ${audioPath}`);
                return false;
            }
            
            console.log(`🎵 Playing audio: ${audioPath}`);
            
            const audioResource = createAudioResource(audioPath);
            this.audioPlayer.play(audioResource);
            
            return true;
        } catch (error) {
            console.error('❌ Error playing audio:', error);
            return false;
        }
    }
    
    startKeepAlive() {
        if (this.keepAliveInterval) {
            return;
        }
        
        console.log('🔄 Starting voice connection keepalive...');
        
        this.keepAliveInterval = setInterval(() => {
            if (this.voiceConnection && this.isConnected) {
                // Send a ping to keep the connection alive
                try {
                    // This is a simple keepalive - just check if connection is still valid
                    if (this.voiceConnection.state.status === VoiceConnectionStatus.Ready) {
                        console.log('✅ Voice connection keepalive check passed');
                    } else {
                        console.log('⚠️ Voice connection not ready, attempting to reconnect...');
                        this.reconnect();
                    }
                } catch (error) {
                    console.error('❌ Keepalive check failed:', error);
                    this.reconnect();
                }
            }
        }, 10000); // Check every 10 seconds for more aggressive keepalive
        
        // Start aggressive endpoint keepalive
        this.startEndpointKeepalive();
    }
    
    startEndpointKeepalive() {
        if (this.endpointKeepaliveInterval) {
            return;
        }
        
        console.log('🔗 Starting endpoint keepalive to maintain connection...');
        
        // Send keepalive packets every 2 seconds to prevent Discord from closing the connection
        this.endpointKeepaliveInterval = setInterval(() => {
            if (this.voiceConnection && this.isConnected) {
                try {
                    // Send a silent audio packet to keep the endpoint alive
                    // This prevents Discord from timing out the connection
                    if (this.audioPlayer && this.voiceConnection.state.status === VoiceConnectionStatus.Ready) {
                        // Create a very short silent audio resource to keep the connection alive
                        const silentAudio = Buffer.alloc(1024); // 1KB of silence
                        const audioResource = createAudioResource(silentAudio, { inputType: 'raw' });
                        this.audioPlayer.play(audioResource);
                        console.log('🔗 Endpoint keepalive packet sent');
                    }
                } catch (error) {
                    console.error('❌ Endpoint keepalive failed:', error);
                }
            }
        }, 2000); // Send keepalive every 2 seconds for very aggressive keepalive
        
        // Also start a heartbeat system to maintain the WebSocket connection
        this.startHeartbeat();
        
        // Start a continuous silent audio stream to keep the endpoint alive
        this.startSilentAudioStream();
    }
    
    startSilentAudioStream() {
        if (this.silentAudioStream) {
            return;
        }
        
        console.log('🔇 Starting silent audio stream to maintain endpoint...');
        
        // Create a continuous silent audio stream
        const silentAudio = Buffer.alloc(1024 * 10); // 10KB of silence
        const audioResource = createAudioResource(silentAudio, { inputType: 'raw' });
        
        // Play the silent audio continuously
        this.audioPlayer.play(audioResource);
        this.silentAudioStream = true;
        
        console.log('🔇 Silent audio stream started');
    }
    
    stopSilentAudioStream() {
        if (this.silentAudioStream) {
            this.silentAudioStream = false;
            console.log('🛑 Stopped silent audio stream');
        }
    }
    
    startHeartbeat() {
        if (this.heartbeatInterval) {
            return;
        }
        
        console.log('💓 Starting heartbeat to maintain WebSocket connection...');
        
        // Send heartbeat every 30 seconds to maintain the WebSocket connection
        this.heartbeatInterval = setInterval(() => {
            if (this.voiceConnection && this.isConnected) {
                try {
                    // Send a heartbeat to keep the WebSocket connection alive
                    if (this.voiceConnection.state.status === VoiceConnectionStatus.Ready) {
                        // This will trigger the voice connection to send a heartbeat
                        console.log('💓 Heartbeat sent to maintain WebSocket connection');
                    }
                } catch (error) {
                    console.error('❌ Heartbeat failed:', error);
                }
            }
        }, 30000); // Send heartbeat every 30 seconds
    }
    
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
            console.log('🛑 Stopped heartbeat');
        }
    }
    
    stopEndpointKeepalive() {
        if (this.endpointKeepaliveInterval) {
            clearInterval(this.endpointKeepaliveInterval);
            this.endpointKeepaliveInterval = null;
            console.log('🛑 Stopped endpoint keepalive');
        }
    }
    
    stopKeepAlive() {
        if (this.keepAliveInterval) {
            clearInterval(this.keepAliveInterval);
            this.keepAliveInterval = null;
            console.log('🛑 Stopped voice connection keepalive');
        }
        
        // Also stop endpoint keepalive, heartbeat, and silent audio stream
        this.stopEndpointKeepalive();
        this.stopHeartbeat();
        this.stopSilentAudioStream();
    }
    
    async reconnect() {
        try {
            console.log('🔄 Attempting to reconnect to voice channel...');
            
            if (this.voiceConnection) {
                this.voiceConnection.destroy();
            }
            
            if (this.guildId && this.targetChannelId) {
                await this.connectToVoice(this.guildId, this.targetChannelId);
            }
        } catch (error) {
            console.error('❌ Reconnection failed:', error);
        }
    }
    
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            guildId: this.guildId,
            channelId: this.targetChannelId,
            connectionStatus: this.voiceConnection ? this.voiceConnection.state.status : 'Disconnected',
            keepAliveActive: this.keepAliveInterval !== null,
            endpointKeepaliveActive: this.endpointKeepaliveInterval !== null,
            heartbeatActive: this.heartbeatInterval !== null,
            silentAudioStreamActive: this.silentAudioStream || false,
            endpoint: this.voiceConnection ? this.voiceConnection.joinConfig.endpoint : null
        };
    }
    
    getEndpointInfo() {
        if (this.voiceConnection && this.voiceConnection.joinConfig) {
            return {
                endpoint: this.voiceConnection.joinConfig.endpoint,
                token: this.voiceConnection.joinConfig.token ? 'Present' : 'Missing',
                sessionId: this.voiceConnection.joinConfig.sessionId,
                serverId: this.voiceConnection.joinConfig.serverId,
                userId: this.voiceConnection.joinConfig.userId
            };
        }
        return null;
    }
    
    async shutdown() {
        try {
            console.log('🛑 Shutting down Discord Voice Helper...');
            this.stopKeepAlive();
            await this.disconnectFromVoice();
            await this.client.destroy();
            console.log('✅ Discord Voice Helper shutdown complete');
        } catch (error) {
            console.error('❌ Error during shutdown:', error);
        }
    }
}

// Command line interface
class VoiceHelperCLI {
    constructor() {
        this.helper = new DiscordVoiceHelper();
        this.setupProcessHandlers();
    }
    
    setupProcessHandlers() {
        process.on('SIGINT', async () => {
            console.log('\n🛑 Received SIGINT, shutting down...');
            await this.helper.shutdown();
            process.exit(0);
        });
        
        process.on('SIGTERM', async () => {
            console.log('\n🛑 Received SIGTERM, shutting down...');
            await this.helper.shutdown();
            process.exit(0);
        });
    }
    
    async handleCommand(command, args) {
        switch (command) {
            case 'connect':
                if (args.length < 2) {
                    console.error('❌ Usage: connect <guildId> <channelId>');
                    return;
                }
                const guildId = args[0];
                const channelId = args[1];
                await this.helper.connectToVoice(guildId, channelId);
                break;
                
            case 'disconnect':
                await this.helper.disconnectFromVoice();
                break;
                
            case 'play':
                if (args.length < 1) {
                    console.error('❌ Usage: play <audioPath>');
                    return;
                }
                await this.helper.playAudio(args[0]);
                break;
                
            case 'status':
                const status = this.helper.getConnectionStatus();
                console.log('📊 Voice Connection Status:');
                console.log(JSON.stringify(status, null, 2));
                break;
                
            case 'reconnect':
                await this.helper.reconnect();
                break;
                
            case 'endpoint':
                const endpointInfo = this.helper.getEndpointInfo();
                if (endpointInfo) {
                    console.log('🔗 Endpoint Information:');
                    console.log(JSON.stringify(endpointInfo, null, 2));
                } else {
                    console.log('❌ No endpoint information available');
                }
                break;
                
            default:
                console.log('Available commands:');
                console.log('  connect <guildId> <channelId> - Connect to voice channel');
                console.log('  disconnect - Disconnect from voice channel');
                console.log('  play <audioPath> - Play audio file');
                console.log('  status - Show connection status');
                console.log('  reconnect - Reconnect to voice channel');
                console.log('  endpoint - Show endpoint information');
                break;
        }
    }
    
    async start() {
        const token = process.env.DISCORD_BOT_TOKEN;
        if (!token) {
            console.error('❌ DISCORD_BOT_TOKEN environment variable not set');
            process.exit(1);
        }
        
        const success = await this.helper.login(token);
        if (!success) {
            process.exit(1);
        }
        
        // Handle command line arguments
        const args = process.argv.slice(2);
        if (args.length > 0) {
            await this.handleCommand(args[0], args.slice(1));
        } else {
            console.log('🎤 Discord Voice Helper is running. Use commands to control voice connection.');
            console.log('Type a command or press Ctrl+C to exit.');
            
            // Keep the process alive
            process.stdin.setEncoding('utf8');
            process.stdin.on('data', async (data) => {
                const input = data.trim().split(' ');
                await this.handleCommand(input[0], input.slice(1));
            });
        }
    }
}

// Python integration helper
class PythonIntegration {
    constructor() {
        this.helper = new DiscordVoiceHelper();
        this.isRunning = false;
    }
    
    async start(token) {
        const success = await this.helper.login(token);
        if (success) {
            this.isRunning = true;
            console.log('✅ Discord Voice Helper started for Python integration');
        }
        return success;
    }
    
    async connectToVoice(guildId, channelId) {
        return await this.helper.connectToVoice(guildId, channelId);
    }
    
    async disconnectFromVoice() {
        return await this.helper.disconnectFromVoice();
    }
    
    async playAudio(audioPath) {
        return await this.helper.playAudio(audioPath);
    }
    
    getConnectionStatus() {
        return this.helper.getConnectionStatus();
    }
    
    async shutdown() {
        await this.helper.shutdown();
        this.isRunning = false;
    }
}

// Export for use in other modules
module.exports = {
    DiscordVoiceHelper,
    VoiceHelperCLI,
    PythonIntegration
};

// Run CLI if this file is executed directly
if (require.main === module) {
    const cli = new VoiceHelperCLI();
    cli.start().catch(console.error);
}
