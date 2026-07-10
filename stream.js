const VIDEO = "";
const STREAM_KEY = "";
const RTMP_SERVER = "";

const ffmpeg = require("fluent-ffmpeg");

function stream() {
  ffmpeg(VIDEO)
    .inputOptions(["-re"])
    .videoCodec("copy")
    .audioCodec("copy")
    .output(`${RTMP_SERVER}${STREAM_KEY}`)
    .outputOptions(["-f flv", "-flvflags no_duration_filesize"])
    .run();
}
stream();