# Timelapse Recorder

A Timelapse Recorder plugin for GIMP 3.0+ using FFmpeg (currently only for Windows)

---

## Requirements

Make sure you have the following:

* Windows 10 or newer
* GIMP 3.0 or newer
* FFmpeg

---

### Install FFmpeg (if you don't have it already)

* via winget:
    `winget install ffmpeg`

* or download it from [https://www.ffmpeg.org/download.html#build-windows](https://www.ffmpeg.org/download.html#build-windows)

## Install the plugin

1. Go to the releases section and download the .zip file
 
2. Extract the .zip file

3. Copy the `timelapse_recorder` folder to your plugin folder

---

## Usage

1. Select an output file path
2. Choose a capture mode:
   * Screen - captures your whole screen
   * Window - captures only the GIMP window
   * Area - captures a custom area you can select after starting
3. Adjust Capture FPS and Video FPS
4. (Optional) Enable mouse or area indicators
5. Click **Start** to begin recording
6. Click **Stop** to finish

---

## Notes

* FFmpeg must be available in your system PATH (should be by default)
* Advanced options allow passing custom FFmpeg arguments. Only use it if you know what you're doing!

---