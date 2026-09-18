import React from "react";
import {
  AbsoluteFill,
  Sequence,
  Img,
  Audio,
  staticFile,
  useCurrentFrame,
  interpolate,
  useVideoConfig,
} from "remotion";
import { scenes } from "./scenes";

const FPS = 30;

const Caption: React.FC<{ text: string; big?: boolean }> = ({ text, big }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 10], [0, 1], { extrapolateRight: "clamp" });
  return (
    <div
      style={{
        opacity,
        fontFamily: "sans-serif",
        fontSize: big ? 54 : 34,
        lineHeight: 1.35,
        color: "white",
        textAlign: "center",
        whiteSpace: "pre-line",
        padding: "0 60px",
        textShadow: "0 2px 10px rgba(0,0,0,0.6)",
      }}
    >
      {text}
    </div>
  );
};

const TitleCard: React.FC<{ caption: string }> = ({ caption }) => (
  <AbsoluteFill
    style={{
      background: "linear-gradient(160deg, #0f1226 0%, #1a1f3d 100%)",
      justifyContent: "center",
      alignItems: "center",
    }}
  >
    <Caption text={caption} big />
  </AbsoluteFill>
);

const ImageScene: React.FC<{ file: string; caption: string }> = ({ file, caption }) => {
  const frame = useCurrentFrame();
  const scale = interpolate(frame, [0, 90], [1, 1.03], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: "#111" }}>
      <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: 40 }}>
        <div
          style={{
            width: 480,
            height: 1038,
            overflow: "hidden",
            borderRadius: 28,
            border: "6px solid #333",
            boxShadow: "0 20px 60px rgba(0,0,0,0.6)",
            transform: `scale(${scale})`,
          }}
        >
          <Img src={staticFile(file)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "flex-end", alignItems: "center", paddingBottom: 60 }}>
        <div style={{ maxWidth: 900 }}>
          <Caption text={caption} />
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const TripVideo: React.FC = () => {
  let startFrame = 0;
  return (
    <AbsoluteFill>
      {scenes.map((scene, i) => {
        const durationInFrames = Math.round(scene.seconds * FPS);
        const from = startFrame;
        startFrame += durationInFrames;
        return (
          <Sequence key={i} from={from} durationInFrames={durationInFrames}>
            {scene.kind === "title" ? (
              <TitleCard caption={scene.caption} />
            ) : (
              <ImageScene file={scene.file as string} caption={scene.caption} />
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

export const getTotalDurationInFrames = () =>
  scenes.reduce((acc, s) => acc + Math.round(s.seconds * FPS), 0);

export const VIDEO_FPS = FPS;
