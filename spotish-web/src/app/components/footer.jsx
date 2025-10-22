import ActualSongContainer from "./ActualSong/ActualSong-Container";
import TimelineContainer from "./Timeline/Timeline-Container";
import TrackNavigator from "./PlayerControls/TrackNavigator";
import VolumeContainer from "./VolumeControls/Volume-Container";

export default ({artist,cover,name,setIsPlaying,setVolume,volume,setTimecode}) => {    
    
    
  return (
    <div className="flex justify-center ">
        
        <ActualSongContainer author={artist} link={cover} title={name}/>

        <div className="flex flex-col items-center justify-center w-full ">

          <div className="flex ">

            <TrackNavigator className="rotate-180" api="previous"/>
            
            {
              isPlaying ?  <ResumeButton setter={setIsPlaying} />: <PauseButton setter={setIsPlaying} />
            }

            <TrackNavigator api="skip"/>
        
          </div>
        
          <TimelineContainer setTimecode={setTimecode} timecode={timecode} duration={duration}/>
        
        </div>
        
        <VolumeContainer setter={setVolume} value={volume}/>

    </div>
  );
};