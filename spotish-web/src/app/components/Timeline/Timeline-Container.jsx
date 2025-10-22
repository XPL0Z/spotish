import TimelineSlider from "./Timeline-Slider";
export default ({ setTimecode, timecode, duration }) => {  
    const MsToSecond = (timeinms) => {
        let result ="";
        if (timeinms === -1) return "00:00";
        let timeins= Math.floor(timeinms / 1000);
        
        if (timeins > 60){
            if (timeins >= 3600){
                let minutes = Math.floor(timeins / 60);
                result += minutes + ":";
                let seconds = timeins - (minutes * 60);
                result += seconds.toString()
                return result;  
            }

            let minutes = Math.floor(timeins / 60);
            result += "0" + minutes + ":";
            let seconds = timeins - (minutes * 60);
            if (seconds < 10){
                result += "0";
            }
            
            result += seconds.toString()
        }else{
            if (timeins < 10){
                timeins = "0" + timeins.toString();
            }
            result = "00:" + timeins.toString();
        }
        return  result;
        
    };  
  return (                
    <div className="w-2/7 flex items-center space-x-4"> 
        <span>{MsToSecond(timecode)}</span>
        <TimelineSlider setTimecode={setTimecode} timecode={timecode ===-1 ? 0 : timecode} duration={duration===-1 ? 0 :duration}/>
        <span>{MsToSecond(duration)}</span>
    </div>
  );
};  