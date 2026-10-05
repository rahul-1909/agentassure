import React, { useEffect, useRef, useState } from 'react';
import WaveSurfer from 'wavesurfer.js';
import { Play, Pause, RotateCcw, Volume2, VolumeX, FastForward } from 'lucide-react';

export default function WaveformPlayer({
  audioUrl,
  currentTime,
  onTimeUpdate,
  duration = 20.0,
}) {
  const containerRef = useRef(null);
  const wavesurferRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create waveform instance
    const ws = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#475569',
      progressColor: '#6366f1',
      cursorColor: '#38bdf8',
      barWidth: 3,
      barRadius: 2,
      barGap: 2,
      height: 72,
      responsive: true,
      normalize: true,
    });

    wavesurferRef.current = ws;

    // Load audio or render synthetic audio buffer
    if (audioUrl && !audioUrl.includes('assets.agentassure.internal')) {
      ws.load(audioUrl);
    } else {
      // Synthesize realistic audio waveform buffer in WebAudio for mock audio
      try {
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const sampleRate = audioCtx.sampleRate;
        const totalSamples = Math.floor(sampleRate * Math.max(5, duration));
        const audioBuffer = audioCtx.createBuffer(1, totalSamples, sampleRate);
        const channelData = audioBuffer.getChannelData(0);

        for (let i = 0; i < totalSamples; i++) {
          const t = i / sampleRate;
          // Generate conversational burst envelope
          const envelope = Math.sin((t % 3) * Math.PI / 3) * (Math.sin(t * 12) * 0.4 + Math.cos(t * 40) * 0.2);
          channelData[i] = envelope * (Math.random() * 0.2 + 0.8) * 0.5;
        }

        // Load synthetic buffer
        ws.loadAudioBuffer(audioBuffer);
      } catch (err) {
        console.warn('AudioContext unavailable, waveform rendered statically:', err);
      }
    }

    ws.on('timeupdate', (time) => {
      if (onTimeUpdate) onTimeUpdate(time);
    });

    ws.on('play', () => setIsPlaying(true));
    ws.on('pause', () => setIsPlaying(false));
    ws.on('finish', () => setIsPlaying(false));

    return () => {
      ws.destroy();
    };
  }, [audioUrl, duration]);

  // Handle external seek requests
  useEffect(() => {
    if (wavesurferRef.current && currentTime !== undefined) {
      const wsDuration = wavesurferRef.current.getDuration() || duration;
      if (wsDuration > 0) {
        const targetProgress = Math.min(1.0, Math.max(0.0, currentTime / wsDuration));
        const currentProgress = (wavesurferRef.current.getCurrentTime() || 0) / wsDuration;
        if (Math.abs(targetProgress - currentProgress) > 0.05) {
          wavesurferRef.current.seekTo(targetProgress);
        }
      }
    }
  }, [currentTime, duration]);

  const togglePlay = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  const handleRestart = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.seekTo(0);
      wavesurferRef.current.play();
    }
  };

  const toggleMute = () => {
    if (wavesurferRef.current) {
      const nextMuted = !isMuted;
      wavesurferRef.current.setMuted(nextMuted);
      setIsMuted(nextMuted);
    }
  };

  const cycleSpeed = () => {
    const speeds = [1.0, 1.25, 1.5, 2.0];
    const nextIdx = (speeds.indexOf(playbackRate) + 1) % speeds.length;
    const nextSpeed = speeds[nextIdx];
    setPlaybackRate(nextSpeed);
    if (wavesurferRef.current) {
      wavesurferRef.current.setPlaybackRate(nextSpeed);
    }
  };

  const formatTime = (seconds = 0) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
      <div className="flex items-center justify-between mb-3 text-xs text-slate-400 font-mono">
        <span className="flex items-center gap-1.5 font-semibold text-slate-300">
          <span className="w-2 h-2 rounded-full bg-indigo-500 animate-ping" />
          Acoustic Waveform Analysis
        </span>
        <div className="flex items-center gap-2">
          <span>{formatTime(currentTime)}</span>
          <span>/</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* WaveSurfer Container */}
      <div
        ref={containerRef}
        className="w-full bg-slate-950/60 rounded-lg p-2 border border-slate-800/80 mb-3 cursor-pointer"
      />

      {/* Playback Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <button
            onClick={togglePlay}
            className="p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-md transition-all active:scale-95 flex items-center justify-center"
            title="Play/Pause (Space)"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
          </button>
          <button
            onClick={handleRestart}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-all"
            title="Restart Audio"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
          <button
            onClick={toggleMute}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-all"
            title="Mute / Unmute"
          >
            {isMuted ? <VolumeX className="w-4 h-4 text-red-400" /> : <Volume2 className="w-4 h-4" />}
          </button>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={cycleSpeed}
            className="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono font-semibold transition-all flex items-center gap-1"
            title="Cycle Playback Rate"
          >
            <FastForward className="w-3.5 h-3.5 text-indigo-400" />
            {playbackRate}x
          </button>
          <span className="text-[11px] text-slate-500 hidden sm:inline">
            Shortcuts: <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">Space</kbd> Play/Pause
          </span>
        </div>
      </div>
    </div>
  );
}
