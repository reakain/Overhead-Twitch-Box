// https://github.com/u2takey/ffmpeg-go
// go get -u github.com/u2takey/ffmpeg-go

microscope := ffmpeg.Input("microscope")
overhead := ffmpeg.Input("overhead")
// Then we do our transparency nonsense?

// And send the video to twitch

//and we take that same output and we add twitch chat!
// then we hopefully display it somehow
overlay:= ffmpeg.Input("text stream of data goes here")
err := ffmpeg.Filter(
    []*ffmpeg.Stream{
        ffmpeg.Input("actual stream"),
        overlay,
    }, "overlay", ffmpeg.Args{"10:10"}, ffmpeg.KwArgs{"enable": "gte(t,1)"}).
    Output("to dplay").OverWriteOutput().ErrorToStdOut().Run()


// alternatively just stream directly gfrom go lol: https://github.com/gwuhaolin/livego
// maybe useful: https://medium.com/learning-the-go-programming-language/realtime-video-capture-with-go-65a8ac3a57da

// go video playing
// https://github.com/zergon321/reisen/blob/master/examples/player/main.go
// https://medium.com/@maximgradan/playing-videos-with-golang-83e67447b111

// go twitch: https://github.com/Adeithe/go-twitch
