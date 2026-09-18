import React from "react";
import { Composition } from "remotion";
import { TripVideo, getTotalDurationInFrames, VIDEO_FPS } from "./TripVideo";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="TripVideo"
      component={TripVideo}
      durationInFrames={getTotalDurationInFrames()}
      fps={VIDEO_FPS}
      width={1080}
      height={1350}
    />
  );
};
