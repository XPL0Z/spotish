import VolumeCutIcon from "./Volume-Cut-Icon";
import VolumeMaxIcon from "./Volume-Max-Icon";
import VolumeSlider from "./Volume-Slider";
import VolumeMinIcon from "./Volume-Min-icon";
import VolumeMidIcon from "./Volume-Mid-icon";
import { useState } from "react";

export default ({setter, value}) => {    
    
    
  return (
  <div>           
      <div className="flex items-center">
          
          <VolumeSlider setter={setter} value={value}/>
          
          {
          value == 0 ? <VolumeCutIcon /> : 
              value <= 30 ?<VolumeMinIcon />:
                 value <= 70? <VolumeMidIcon /> :
                      <VolumeMaxIcon />
          }
           
      </div>
  </div>
  );                      
};