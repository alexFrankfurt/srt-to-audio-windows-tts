#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Automates the complete SRT-to-Audio pipeline using Windows TTS.

.DESCRIPTION
    This script automates the entire workflow:
    1. Generates SRT subtitles from audio using OpenAI Whisper
    2. Processes the SRT file to generate timed audio using Windows TTS
    3. Produces the final output audio file

.PARAMETER InputAudioFile
    Path to the input audio file to process

.PARAMETER WhisperModel
    Whisper model to use for transcription (default: medium)

.PARAMETER OutputAudio
    Name of the final output audio file (default: final_output.mp3)

.PARAMETER KeepIntermediateFiles
    Switch to keep intermediate files for debugging

.EXAMPLE
    .\run_pipeline.ps1 -InputAudioFile "my_audio.mp3"
    
.EXAMPLE
    .\run_pipeline.ps1 -InputAudioFile "my_audio.wav" -WhisperModel "large" -OutputAudio "result.mp3"
#>

param(
    [Parameter(Mandatory=$true, HelpMessage="Path to the input audio file")]
    [string]$InputAudioFile,
    
    [Parameter(Mandatory=$false)]
    [ValidateSet("tiny", "base", "small", "medium", "large")]
    [string]$WhisperModel = "medium",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputAudio = "final_output.mp3",
    
    [Parameter(Mandatory=$false)]
    [switch]$KeepIntermediateFiles
)

# Function to write colored output
function Write-ColorOutput($ForegroundColor, $Message) {
    $originalColor = $Host.UI.RawUI.ForegroundColor
    $Host.UI.RawUI.ForegroundColor = $ForegroundColor
    Write-Host $Message
    $Host.UI.RawUI.ForegroundColor = $originalColor
}

# Function to check if a command exists
function Test-Command($CommandName) {
    try {
        $null = Get-Command $CommandName -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

# Function to check dependencies
function Test-Dependencies {
    Write-ColorOutput "Cyan" "🔍 Checking dependencies..."
    
    $missingDeps = @()
    
    # Check Python
    if (-not (Test-Command "python")) {
        $missingDeps += "Python"
    }
    
    # Check FFmpeg
    if (-not (Test-Command "ffmpeg")) {
        $missingDeps += "FFmpeg"
    }
    
    # Check Whisper
    if (-not (Test-Command "whisper")) {
        $missingDeps += "OpenAI Whisper"
    }
    
    # Check Python packages
    if (Test-Command "python") {
        try {
            $result = python -c "import srt, edge_tts; print('OK')" 2>$null
            if ($LASTEXITCODE -ne 0 -or $result -ne "OK") {
                $missingDeps += "Python packages (srt, edge-tts)"
            }
        }
        catch {
            $missingDeps += "Python packages (srt, edge-tts)"
        }
    }
    
    if ($missingDeps.Count -gt 0) {
        Write-ColorOutput "Red" "❌ Missing dependencies:"
        foreach ($dep in $missingDeps) {
            Write-ColorOutput "Red" "   - $dep"
        }
        Write-ColorOutput "Yellow" ""
        Write-ColorOutput "Yellow" "💡 Installation instructions:"
        Write-ColorOutput "Yellow" "   - Python: Download from python.org"
        Write-ColorOutput "Yellow" "   - FFmpeg: Download from ffmpeg.org or use 'winget install ffmpeg'"
        Write-ColorOutput "Yellow" "   - Whisper: pip install openai-whisper"
        Write-ColorOutput "Yellow" "   - Python packages: pip install srt edge-tts"
        return $false
    }
    
    Write-ColorOutput "Green" "✅ All dependencies found!"
    return $true
}

# Main script execution
try {
    Write-ColorOutput "Cyan" "🚀 Starting SRT-to-Audio Pipeline"
    Write-ColorOutput "Cyan" "================================="
    
    # Check dependencies first
    if (-not (Test-Dependencies)) {
        Write-ColorOutput "Red" "❌ Please install missing dependencies before running this script."
        exit 1
    }
    
    # Validate input file exists
    if (-not (Test-Path $InputAudioFile)) {
        Write-ColorOutput "Red" "❌ Input audio file not found: $InputAudioFile"
        exit 1
    }
    
    # Get absolute paths
    $InputAudioFile = Resolve-Path $InputAudioFile
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
    $SrtFile = Join-Path $ScriptDir "your_subtitles.srt"
    $PythonScript = Join-Path $ScriptDir "srt_to_timed_audio.py"
    $FinalOutput = Join-Path $ScriptDir $OutputAudio
    
    Write-ColorOutput "Cyan" "📁 Working directory: $ScriptDir"
    Write-ColorOutput "Cyan" "🎵 Input audio: $InputAudioFile"
    Write-ColorOutput "Cyan" "🎯 Final output: $FinalOutput"
    Write-ColorOutput "Cyan" ""
    
    # Step 1: Generate SRT using Whisper
    Write-ColorOutput "Yellow" "📝 Step 1: Generating SRT subtitles using Whisper ($WhisperModel model)..."
    $whisperArgs = @(
        $InputAudioFile,
        "--task", "translate",
        "--model", $WhisperModel,
        "--output_dir", $ScriptDir
    )
    
    Write-ColorOutput "Gray" "Running: whisper $($whisperArgs -join ' ')"
    & whisper @whisperArgs
    
    if ($LASTEXITCODE -ne 0) {
        Write-ColorOutput "Red" "❌ Whisper failed with exit code $LASTEXITCODE"
        exit 1
    }
    
    # Find the generated SRT file
    $InputBaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputAudioFile)
    $GeneratedSrt = Join-Path $ScriptDir "$InputBaseName.srt"
    
    if (-not (Test-Path $GeneratedSrt)) {
        Write-ColorOutput "Red" "❌ Expected SRT file not found: $GeneratedSrt"
        Write-ColorOutput "Yellow" "Looking for SRT files in directory..."
        $srtFiles = Get-ChildItem -Path $ScriptDir -Filter "*.srt"
        foreach ($file in $srtFiles) {
            Write-ColorOutput "Gray" "   Found: $($file.Name)"
        }
        exit 1
    }
    
    Write-ColorOutput "Green" "✅ SRT file generated: $GeneratedSrt"
    
    # Step 2: Copy SRT to expected location
    Write-ColorOutput "Yellow" "📋 Step 2: Preparing SRT file..."
    Copy-Item $GeneratedSrt $SrtFile -Force
    Write-ColorOutput "Green" "✅ SRT file copied to: $SrtFile"
    
    # Step 3: Run Python script to generate timed audio
    Write-ColorOutput "Yellow" "🔊 Step 3: Generating timed audio using Windows TTS..."
    Write-ColorOutput "Gray" "Running: python $PythonScript"
    
    Push-Location $ScriptDir
    try {
        python $PythonScript
        
        if ($LASTEXITCODE -ne 0) {
            Write-ColorOutput "Red" "❌ Python script failed with exit code $LASTEXITCODE"
            exit 1
        }
    }
    finally {
        Pop-Location
    }
    
    # Check if final output was created
    if (-not (Test-Path (Join-Path $ScriptDir "final_output.mp3"))) {
        Write-ColorOutput "Red" "❌ Final output file was not created"
        exit 1
    }
    
    # Rename final output if different name requested
    if ($OutputAudio -ne "final_output.mp3") {
        Move-Item (Join-Path $ScriptDir "final_output.mp3") $FinalOutput -Force
        Write-ColorOutput "Green" "✅ Output renamed to: $OutputAudio"
    }
    
    # Cleanup intermediate files if requested
    if (-not $KeepIntermediateFiles) {
        Write-ColorOutput "Yellow" "🧹 Cleaning up intermediate files..."
        
        # Remove Whisper generated files (except our target SRT)
        $filesToClean = @(
            "$InputBaseName.txt",
            "$InputBaseName.vtt",
            "$InputBaseName.tsv",
            "$InputBaseName.json"
        )
        
        foreach ($file in $filesToClean) {
            $fullPath = Join-Path $ScriptDir $file
            if (Test-Path $fullPath) {
                Remove-Item $fullPath -Force
                Write-ColorOutput "Gray" "   Removed: $file"
            }
        }
        
        # Remove output_audio directory
        $outputDir = Join-Path $ScriptDir "output_audio"
        if (Test-Path $outputDir) {
            Remove-Item $outputDir -Recurse -Force
            Write-ColorOutput "Gray" "   Removed: output_audio directory"
        }
        
        # Remove concat list
        $concatList = Join-Path $ScriptDir "concat_list.txt"
        if (Test-Path $concatList) {
            Remove-Item $concatList -Force
            Write-ColorOutput "Gray" "   Removed: concat_list.txt"
        }
        
        # Remove generated SRT if different from target location
        if ($GeneratedSrt -ne $SrtFile -and (Test-Path $GeneratedSrt)) {
            Remove-Item $GeneratedSrt -Force
            Write-ColorOutput "Gray" "   Removed: $($InputBaseName).srt"
        }
    }
    
    Write-ColorOutput "Green" ""
    Write-ColorOutput "Green" "🎉 Pipeline completed successfully!"
    Write-ColorOutput "Green" "📁 Final audio file: $OutputAudio"
    
    # Show file info
    if (Test-Path $FinalOutput) {
        $fileInfo = Get-Item $FinalOutput
        Write-ColorOutput "Cyan" "📊 File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB"
        Write-ColorOutput "Cyan" "🕐 Created: $($fileInfo.CreationTime)"
    }
}
catch {
    Write-ColorOutput "Red" "❌ An error occurred: $($_.Exception.Message)"
    Write-ColorOutput "Red" "Stack trace: $($_.ScriptStackTrace)"
    exit 1
}