import VolumeCutIcon from "./Volume-Cut-Icon";
import VolumeMaxIcon from "./Volume-Max-Icon";
import VolumeSlider from "./Volume-Slider";
import VolumeMinIcon from "./Volume-Min-icon";
import VolumeMidIcon from "./Volume-Mid-icon";

export default ({ setter, value, author }) => {


    return (
        <div>
            <div className="flex items-center">

                <VolumeSlider setter={setter} value={value} author={author} />

                {
                    value == 0 ? <VolumeCutIcon /> :
                        value <= 30 ? <VolumeMinIcon /> :
                            value <= 70 ? <VolumeMidIcon /> :
                                <VolumeMaxIcon />
                }

            </div>
        </div>
    );
};